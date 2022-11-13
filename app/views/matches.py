import asyncio
from enum import Enum
from typing import Dict

from fastapi import APIRouter, Header, HTTPException, WebSocket
from pony.orm import commit, db_session, select

from app.game.executor import Executor
from app.models.match import Match
from app.models.robot import Robot
from app.models.robot_result import RobotMatchResult
from app.models.user import User
from app.schemas.match import MatchCreateRequest, MatchJoinRequest
from app.util.auth import get_current_user
from app.util.db_access import match_id_to_schema
from app.util.errors import *
from app.util.ws import Notifier

router = APIRouter()


class MatchType(str, Enum):
    created = "created"
    started = "started"
    joined = "joined"
    public = "public"


@router.get("/")
def get_matches(match_type: MatchType, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        cur_user = User.get(name=username)
        if cur_user is None:
            raise USER_NOT_FOUND_ERROR

        queries: Dict = {
            MatchType.created: select(
                m.id for m in Match if m.state == "Lobby" and m.host is cur_user
            ),
            MatchType.started: select(
                m.id
                for m in Match
                if (m.state == "InGame" or m.state == "Finished")
                and cur_user in m.plays.owner
            ),
            MatchType.joined: select(
                m.id
                for m in Match
                if m.state == "Lobby"
                and cur_user in m.plays.owner
                and m.host is not cur_user
            ),
            MatchType.public: select(
                m.id for m in Match if m.state == "Lobby" and m.host is not cur_user
            ),
        }

        queried_matches = queries[match_type][:]

        matches = []
        for m in queried_matches:
            matches.append(match_id_to_schema(m))

    return matches


@router.post("/", status_code=201)
def create_match(form_data: MatchCreateRequest, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        host = User.get(name=username)

        if host is None:
            raise USER_NOT_FOUND_ERROR

        host_robot = Robot.get(id=form_data.robot_id)
        if host_robot is None:
            raise ROBOT_NOT_FOUND_ERROR

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


@router.get("/{match_id}/")
def get_match(match_id: int, token: str = Header()):
    get_current_user(token)

    with db_session:
        match = Match.get(id=match_id)

        if match is None:
            raise MATCH_NOT_FOUND_ERROR
        match_id = match.id

    return match_id_to_schema(match_id)


channels: Dict[int, Notifier] = {}


@router.put("/{match_id}/join/", status_code=201)
def join_match(match_id: int, form: MatchJoinRequest, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        m = Match.get(id=match_id)

        if m is None:
            raise MATCH_NOT_FOUND_ERROR

        if m.state != "Lobby":
            raise MATCH_STARTED_ERROR

        r = Robot.get(id=form.robot_id)
        if r is None:
            raise ROBOT_NOT_FOUND_ERROR

        if r.owner.name != username:
            raise ROBOT_NOT_FROM_USER_ERROR

        robot_from_owner = m.plays.select(
            lambda robot: r.owner.name == robot.owner.name
        )
        if m.plays.count() >= m.max_players and not robot_from_owner:
            raise MATCH_FULL_ERROR

        if m.password and form.password != m.password:
            raise MATCH_PASSWORD_INCORRECT_ERROR

        if robot_from_owner:
            m.plays.remove(robot_from_owner)

        m.plays.add(r)

    # Notify websockets
    chan = channels.get(match_id)

    if chan:
        match = match_id_to_schema(match_id)
        asyncio.run(chan.push(match.json()))


@router.put("/{match_id}/start/", status_code=201)
def start_match(match_id: int, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        if User.get(name=username) is None:
            raise USER_NOT_FOUND_ERROR

        m = Match.get(id=match_id)

        if m is None:
            raise MATCH_NOT_FOUND_ERROR

        if m.state != "Lobby":
            raise MATCH_STARTED_ERROR

        if m.host != User.get(name=username):
            raise MATCH_CAN_ONLY_BE_STARTED_BY_HOST_ERROR

        if len(m.plays) < m.min_players:
            raise MATCH_MINIMUM_PLAYERS_NOT_REACHED_ERROR

        if len(m.plays) > m.max_players:
            raise MATCH_FULL_ERROR

        m.state = "InGame"
        commit()

    # Notify websockets
    chan = channels.get(match_id)

    if chan:
        match = match_id_to_schema(match_id)
        asyncio.run(chan.push(match.json()))

    with db_session:
        m = Match.get(id=match_id)
        robot_ids = [r.id for r in m.plays]
        game_count, round_count = m.game_count, m.round_count

    exec = Executor(robot_ids)
    for _ in range(game_count):
        exec.execute_game(round_count)

    robots_by_pos, death_counts = exec.generate_stats()

    with db_session:
        m = Match.get(id=match_id)
        m.state = "Finished"
        commit()

    for rid in robot_ids:
        with db_session:
            RobotMatchResult(
                robot_id=rid,
                match_id=match_id,
                position=robots_by_pos.index(rid) + 1,
                death_count=death_counts[rid],
            )
            r = Robot[rid]
            r.played_matches += 1
            commit()

    with db_session:
        Robot[robots_by_pos[0]].won_matches += 1

    # Notify websockets
    chan = channels.get(match_id)

    if chan:
        match = match_id_to_schema(match_id)
        asyncio.run(chan.push(match))


@router.put("/{match_id}/leave/", status_code=201)
def leave_match(match_id: int, token: str = Header()):
    username = get_current_user(token)

    with db_session:
        m = Match.get(id=match_id)

        if m is None:
            raise MATCH_NOT_FOUND_ERROR

        if m.host.name == username:
            raise MATCH_CANNOT_BE_LEFT_BY_HOST_ERROR

        if m.state != "Lobby":
            raise MATCH_STARTED_ERROR

        robot_from_owner = m.plays.select(lambda robot: robot.owner.name == username)

        if not robot_from_owner:
            raise USER_WAS_NOT_IN_MATCH_ERROR

        m.plays.remove(robot_from_owner)

    # Notify websockets
    chan = channels.get(match_id)

    if chan:
        match = match_id_to_schema(match_id)
        asyncio.run(chan.push(match.json()))


@router.websocket("/{match_id}/ws")
async def websocket_endpoint(ws: WebSocket, match_id: int):  # pragma: no cover

    with db_session:
        m = Match.get(id=match_id)
        if not m:
            raise MATCH_NOT_FOUND_ERROR
        m_state = m.state

    chan = channels.get(match_id)

    # Only create channel if match is not finished
    if m_state != "Finished":
        if not chan:
            chan = Notifier()
            channels[match_id] = chan
            # Prime the push notification generator
            await chan.generator.asend(None)

        await chan.connect(ws)

    await ws.send_json(match_id_to_schema(match_id).json())

    try:
        while True:
            # only to raise exception when ws disconnects
            await ws.receive_text()
    except:
        if chan:
            chan.remove(ws)
            if len(chan.connections) == 0:
                channels.pop(match_id)
