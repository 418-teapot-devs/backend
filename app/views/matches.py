from enum import Enum
from typing import Callable, Dict
from fastapi import APIRouter, Header, HTTPException, Response
from pony.orm import commit, db_session, select

from app.models.match import Match
from app.models.robot import Robot
from app.models.user import User
from app.schemas.match import MatchCreateRequest
from app.views import get_current_user

router = APIRouter()

class ModelName(str, Enum):
    created = "created"
    iniciated = "iniciated"
    joined = "joined"
    public = "public"

query_base = select((m, r) for m in Match for r in m.plays)


@router.get("/{model_name}")
def get_matches(model_name: ModelName, token: str = Header()):
    username = get_current_user(token)
    with db_session:

        cur_user = User.get(name=username)
        if cur_user is None:
            raise HTTPException(status_code=404, detail="User not found")


        queries: Dict = {
            ModelName.created: query_base.filter(lambda m, _: m.state == "Lobby" and m.host is cur_user),
            ModelName.iniciated: query_base.filter(lambda m, r: (m.state == "InGame" or m.state == "Finished") and r.owner is cur_user),
            ModelName.joined: query_base.filter(lambda m, r: m.state == "Lobby" and r.owner is cur_user),
            ModelName.public: query_base.filter(lambda m, _: m.state == "Lobby" and m.host is not cur_user),
        }
        print(queries[ModelName.iniciated].get_sql())

        matches = queries[model_name][:]

        res = []
        for m, _ in matches:
            robots = []
            for r in m.plays:
                # this will be used after merge with the refactor repository
                # avatar_url =  f"assets/robots/{r.id}.png" if r.has_avatar else None

                robots.append(
                    {"name": r.name, "avatar_url": None, "username": r.owner.name}
                )

            res.append(
                {
                    "name": m.name,
                    "max_players": m.max_players,
                    "min_players": m.min_players,
                    "games": m.game_count,
                    "rounds": m.round_count,
                    "is_private": False,
                    "robots": robots,
                }
            )
    return res


@router.post("/created")
def upload_match(form_data: MatchCreateRequest, token: str = Header()):
    username = get_current_user(token)

    with db_session:

        host = User.get(name=username)

        if host is None:
            raise HTTPException(status_code=404, detail="User not found")

        host_robot = Robot.get(name=form_data.name_robot, owner=host)
        if host_robot is None:
            raise HTTPException(status_code=404, detail="Host robot not found")

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
