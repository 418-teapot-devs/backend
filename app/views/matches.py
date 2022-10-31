import asyncio
from enum import Enum
from typing import Dict, Any

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Response,
    WebSocket,
)
from pony.orm import commit, db_session, select

from app.models.match import Match
from app.models.robot import Robot
from app.models.user import User
from app.schemas.match import Host, MatchCreateRequest, MatchResponse, RobotInMatch
from app.util.auth import get_current_user
from app.util.room import Room
from app.util.assets import get_user_avatar, get_robot_avatar

router = APIRouter()


class MatchType(str, Enum):
    created = "created"
    started = "started"
    joined = "joined"
    public = "public"


query_base = select((m, r) for m in Match for r in m.plays)


def match_to_dict(match: Match) -> Dict[str, Any]:
    robots = []
    for robot in match.plays:
        avatar_url = get_robot_avatar(robot)
        robots.append(
            {"name": robot.name, "avatar_url": avatar_url, "username": robot.owner.name}
        )

    host_avatar_url = get_user_avatar(match.host)

    return {
        "id": match.id,
        "host": {"username": match.host.name, "avatar_url": host_avatar_url},
        "name": match.name,
        "max_players": match.max_players,
        "min_players": match.min_players,
        "games": match.game_count,
        "rounds": match.round_count,
        "robots": robots,
        "is_private": False,
        "status": match.state,
    }


@router.get("/")
def get_matches(match_type: MatchType, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        cur_user = User.get(name=username)
        if cur_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        queries: Dict = {
            MatchType.created: query_base.filter(
                lambda m, _: m.state == "Lobby" and m.host is cur_user
            ),
            MatchType.started: query_base.filter(
                lambda m, r: (m.state == "InGame" or m.state == "Finished")
                and r.owner is cur_user
            ),
            MatchType.joined: query_base.filter(
                lambda m, r: m.state == "Lobby" and r.owner is cur_user
            ),
            MatchType.public: query_base.filter(
                lambda m, _: m.state == "Lobby" and m.host is not cur_user
            ),
        }

        queried_matches = queries[match_type][:]

        matches = []
        for m, _ in queried_matches:
            robots = []
            for r in m.plays:
                r_avatar = get_robot_avatar(r)
                robots.append(
                    RobotInMatch(
                        name=r.name, avatar_url=r_avatar, username=r.owner.name
                    )
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
                    is_private=False,
                    robots=robots,
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
        )
        commit()

    return Response(status_code=201)


@router.get("/{match_id}")
def get_match(match_id: int, token: str = Header()):
    username = get_current_user(token)

    if username is None:
        raise HTTPException(status_code=404, detail="User not found")

    with db_session:
        m = Match.get(id=match_id)

        if m is None:
            raise HTTPException(status_code=404, detail="Match not found")

        robots = []
        for r in m.plays:
            r_avatar_url = get_robot_avatar(r)
            robots.append(
                RobotInMatch(name=r.name, avatar_url=r_avatar_url, username=r.owner.name)
            )

        host_avatar_url = get_user_avatar(m.host)
        return MatchResponse(
            id=m.id,
            host=Host(username=m.host.name, avatar_url=host_avatar_url),
            name=m.name,
            max_players=m.max_players,
            min_players=m.min_players,
            games=m.game_count,
            rounds=m.round_count,
            is_private=False,
            robots=robots,
            status=m.state,
        )


rooms: Dict[int, Room] = {}


@router.put("/{match_id}/join", status_code=201)
def join_match(match_id: int, robot_id: int, token: str = Header()):
    username = get_current_user(token)

    if username is None:
        raise HTTPException(status_code=404, detail="User not found")

    with db_session:
        m = Match.get(id=match_id)

        if m is None:
            raise HTTPException(status_code=404, detail="Match not found")

        r = Robot.get(id=robot_id)

        if r is None:
            raise HTTPException(status_code=404, detail="Robot not found")

        if r.owner.name != username:
            raise HTTPException(status_code=403, detail="Robot does not belong to user")

        robot_from_owner = m.plays.select(lambda robot: r.owner.name == robot.owner.name)
        if m.robot_count >= m.max_players and not robot_from_owner:
            raise HTTPException(status_code=403, detail="Match is full")

        if robot_from_owner:
            m.plays.remove(robot_from_owner)

        m.plays.add(r)
        m.robot_count += 1

        match = match_to_dict(m)

    room = rooms.get(match_id)
    asyncio.run(room.broadcast(match))
    room.event.clear()


@router.websocket("/{match_id}/ws")
async def websocket_endpoint(ws: WebSocket, match_id: int): #pragma: no cover
    with db_session:
        match = match_to_dict(Match.get(id=match_id))

    if rooms.get(match_id) is None:
        rooms[match_id] = Room()

    await rooms[match_id].connect(ws)

    try:
        while True:
            await rooms[match_id].event.wait()
            await rooms[match_id].broadcast(match)
            rooms[match_id].event.clear()

    except Exception as _:
        rooms[match_id].disconnect(ws)
        if not rooms[match_id].clients:
            rooms.pop(match_id)


@router.post("/{match_id}/event")
def set_event(match_id: int): #pragma: no cover
    if rooms.get(match_id) is None:
        raise HTTPException(status_code=404)
    rooms[match_id].event.set()

    return Response(status_code=200)
