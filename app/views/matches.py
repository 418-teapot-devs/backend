import asyncio
from enum import Enum
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException, Response, WebSocket
from pony.orm import commit, db_session, select

from app.game.board import Board
from app.models.match import Match
from app.models.robot import Robot
from app.models.robot_result import RobotMatchResult
from app.models.user import User
from app.schemas.match import (
    Host,
    MatchCreateRequest,
    MatchJoinRequest,
    MatchResponse,
    RobotInMatch,
    RobotResult,
)
from app.util.assets import get_robot_avatar, get_user_avatar
from app.util.auth import get_current_user
from app.util.ws import Notifier

router = APIRouter()


class MatchType(str, Enum):
    created = "created"
    started = "started"
    joined = "joined"
    public = "public"


def match_to_dict(match: Match) -> Dict[str, Any]:
    robots = {}
    for robot in match.plays:
        avatar_url = get_robot_avatar(robot)
        robots[robot.id] = {
            "name": robot.name,
            "avatar_url": avatar_url,
            "username": robot.owner.name,
        }

    host_avatar_url = get_user_avatar(match.host)

    results = None
    if match.state == "Finished":
        results = {}
        for r in match.plays:
            res = RobotMatchResult.get(match_id=match.id, robot_id=r.id)
            results[r.id] = {"robot_pos": res.position, "death_count": res.death_count}

    return {
        "id": match.id,
        "host": {"username": match.host.name, "avatar_url": host_avatar_url},
        "name": match.name,
        "max_players": match.max_players,
        "min_players": match.min_players,
        "games": match.game_count,
        "rounds": match.round_count,
        "robots": robots,
        "is_private": match.password != "",
        "state": match.state,
        "results": results,
    }


@router.get("/")
def get_matches(match_type: MatchType, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        cur_user = User.get(name=username)
        if cur_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        queries: Dict = {
            MatchType.created: Match.select().filter(
                lambda m: m.state == "Lobby" and m.host is cur_user
            ),
            MatchType.started: Match.select().filter(
                lambda m: (m.state == "InGame" or m.state == "Finished")
                and cur_user in m.plays.owner
            ),
            MatchType.joined: Match.select().filter(
                lambda m: m.state == "Lobby"
                and cur_user in m.plays.owner
                and m.host is not cur_user
            ),
            MatchType.public: Match.select().filter(
                lambda m: m.state == "Lobby" and m.host is not cur_user
            ),
        }

        queried_matches = queries[match_type][:]

        matches = []
        for m in queried_matches:
            robots = {}
            for r in m.plays:
                r_avatar = get_robot_avatar(r)
                robots[r.id] = RobotInMatch(
                    name=r.name, avatar_url=r_avatar, username=r.owner.name
                )

            h_avatar = get_user_avatar(m.host)
            matches.append(
                MatchResponse(
                    id=m.id,
                    host=Host(username=m.host.name, avatar_url=h_avatar),
                    name=m.name,
                    max_players=m.max_players,
                    min_players=m.min_players,
                    games=m.game_count,
                    rounds=m.round_count,
                    state=m.state,
                    is_private=m.password != "",
                    robots=robots,
                    results=None,
                )
            )

    return matches


@router.post("/")
def create_match(form_data: MatchCreateRequest, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        host = User.get(name=username)

        if host is None:
            raise HTTPException(status_code=404, detail="User not found")

        host_robot = Robot.get(id=form_data.robot_id)
        if host_robot is None:
            raise HTTPException(status_code=404, detail="Robot not found")
        if host_robot.owner is not host:
            raise HTTPException(status_code=401, detail="Robot does not belong to user")

        Match(
            host=host,
            name=form_data.name,
            plays=[host_robot],
            max_players=form_data.max_players,
            min_players=form_data.min_players,
            game_count=form_data.games,
            round_count=form_data.rounds,
            state="Lobby",
            password=form_data.password,
        )
        commit()

    return Response(status_code=201)


@router.get("/{match_id}/")
def get_match(match_id: int, token: str = Header()):
    get_current_user(token)

    with db_session:
        m = Match.get(id=match_id)

        if m is None:
            raise HTTPException(status_code=404, detail="Match not found")

        robots = {}
        for r in m.plays:
            r_avatar_url = get_robot_avatar(r)
            robots[r.id] = RobotInMatch(
                name=r.name, avatar_url=r_avatar_url, username=r.owner.name
            )

        results = None
        if m.state == "Finished":
            robot_results = select(
                r for r in RobotMatchResult if r.match_id == match_id
            )
            results = {
                r.robot_id: RobotResult(
                    robot_pos=r.position,
                    death_count=r.death_count,
                )
                for r in robot_results
            }

        host_avatar_url = get_user_avatar(m.host)
        return MatchResponse(
            id=m.id,
            host=Host(username=m.host.name, avatar_url=host_avatar_url),
            name=m.name,
            max_players=m.max_players,
            min_players=m.min_players,
            games=m.game_count,
            rounds=m.round_count,
            is_private=m.password != "",
            robots=robots,
            state=m.state,
            results=results,
        )


channels: Dict[int, Notifier] = {}


@router.put("/{match_id}/join/", status_code=201)
def join_match(match_id: int, form: MatchJoinRequest, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        m = Match.get(id=match_id)

        if m is None:
            raise HTTPException(status_code=404, detail="Match not found")

        if m.state != "Lobby":
            raise HTTPException(status_code=403, detail="Match has already started")

        r = Robot.get(id=form.robot_id)
        if r is None:
            raise HTTPException(status_code=404, detail="Robot not found")

        if r.owner.name != username:
            raise HTTPException(status_code=403, detail="Robot does not belong to user")

        robot_from_owner = m.plays.select(
            lambda robot: r.owner.name == robot.owner.name
        )
        if m.plays.count() >= m.max_players and not robot_from_owner:
            raise HTTPException(status_code=403, detail="Match is full")

        if m.password and form.password != m.password:
            raise HTTPException(status_code=403, detail="Match password is incorrect")

        if robot_from_owner:
            m.plays.remove(robot_from_owner)

        m.plays.add(r)

        match = match_to_dict(m)

    chan = channels.get(match_id)

    # Notify websockets
    if chan:
        asyncio.run(chan.push(match))


@router.put("/{match_id}/start/", status_code=201)
def start_match(match_id: int, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        if User.get(name=username) is None:
            raise HTTPException(status_code=404, detail="User not found")

        m = Match.get(id=match_id)

        if m is None:
            raise HTTPException(status_code=404, detail="Match not found")

        if m.state != "Lobby":
            raise HTTPException(status_code=403, detail="Match has already started")

        if m.host != User.get(name=username):
            raise HTTPException(status_code=403, detail="Host must start the match")

        if len(m.plays) < m.min_players:
            raise HTTPException(
                status_code=403, detail="The minimum number of players was not reached"
            )

        if len(m.plays) > m.max_players:
            raise HTTPException(status_code=403, detail="Match is full")

        m.state = "InGame"
        commit()

        match = match_to_dict(m)

        chan = channels.get(match_id)

        if chan:
            asyncio.run(chan.push(match))

        games_results = []
        robots = [r.id for r in m.plays]
        for _ in range(m.game_count):
            b = Board(robots)
            games_results.append(b.execute_game(m.round_count))

        deaths_count = {key: 0 for key in robots}
        for survivors in games_results:
            for r in robots:
                if r not in survivors:
                    deaths_count[r] = deaths_count[r] + 1

        games_results = [x[0] for x in games_results if len(x) == 1]
        winners_pairs = list(zip(robots, [games_results.count(i) for i in robots]))
        result_match = {key: value for (key, value) in winners_pairs}
        result_match = {
            k: v for k, v in sorted(result_match.items(), key=lambda item: item[1])
        }
        ordered_result_match = list(reversed(result_match.keys()))

        m.state = "Finished"
        commit()

        match["state"] = "Finished"
        match["results"] = []

        def get_condition(robot_id, dictionary):
            condition = "Lost"
            greater = {k: v > dictionary[robot_id] for k, v in dictionary.items()}
            greater.pop(robot_id)

            if not any(greater.values()):
                equal = {k: v == dictionary[robot_id] for k, v in dictionary.items()}
                equal.pop(robot_id)
                if any(equal.values()):
                    condition = "Tied"
                else:
                    condition = "Won"

            return condition

        for r in robots:
            RobotMatchResult(
                robot_id=r,
                match_id=match_id,
                position=ordered_result_match.index(r) + 1,
                death_count=deaths_count[r],
                condition=get_condition(r, result_match),
            )
            match["results"].append(
                {
                    "robot_id": r,
                    "position": ordered_result_match.index(r) + 1,
                    "death_count": deaths_count[r],
                }
            )

        commit()

        chan = channels.get(match_id)

        if chan:
            asyncio.run(chan.push(match))


@router.put("/{match_id}/leave/", status_code=201)
def leave_match(match_id: int, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        m = Match.get(id=match_id)

        if m is None:
            raise HTTPException(status_code=404, detail="Match not found")

        if m.host.name == username:
            raise HTTPException(status_code=403, detail="Host cannot leave own match")

        if m.state != "Lobby":
            raise HTTPException(status_code=403, detail="Match has already started")

        robot_from_owner = m.plays.select(lambda robot: robot.owner.name == username)

        if not robot_from_owner:
            raise HTTPException(status_code=403, detail="User was not in match")

        m.plays.remove(robot_from_owner)
        match = match_to_dict(m)

    chan = channels.get(match_id)

    # Notify websockets
    if chan:
        asyncio.run(chan.push(match))


@router.websocket("/{match_id}/ws")
async def websocket_endpoint(ws: WebSocket, match_id: int):  # pragma: no cover
    chan = channels.get(match_id)
    if not chan:
        chan = Notifier()
        channels[match_id] = chan
        # Prime the push notification generator
        await chan.generator.asend(None)

    await chan.connect(ws)

    with db_session:
        match = match_to_dict(Match.get(id=match_id))

    await ws.send_json(match)

    try:
        while True:
            # only to raise exception when ws disconnects
            await ws.receive_text()
    except:
        chan.remove(ws)
        if len(chan.connections) == 0:
            channels.pop(match_id)
