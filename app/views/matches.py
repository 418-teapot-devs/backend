from enum import Enum
from typing import Dict

from fastapi import APIRouter, Header, HTTPException, Response
from pony.orm import commit, db_session, select

from app.models.match import Match
from app.models.robot import Robot
from app.models.user import User
from app.schemas.match import Host, MatchCreateRequest, MatchResponse, RobotInMatch
from app.util.auth import get_current_user

router = APIRouter()


class MatchType(str, Enum):
    created = "created"
    started = "started"
    joined = "joined"
    public = "public"


query_base = select((m, r) for m in Match for r in m.plays)


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
                # this will be used after merge with the refactor repository
                # avatar_url =  f"assets/robots/{r.id}.png" if r.has_avatar else None

                robots.append(
                    RobotInMatch(name=r.name, avatar_url=None, username=r.owner.name)
                )

            matches.append(
                MatchResponse(
                    id=m.id,
                    host=Host(username=username, avatar_url=None),
                    name=m.name,
                    max_players=m.max_players,
                    min_players=m.min_players,
                    games=m.game_count,
                    rounds=m.round_count,
                    is_private=False,
                    robots=robots,
                )
            )

    return matches


@router.post("/")
def upload_match(form_data: MatchCreateRequest, token: str = Header()):
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
