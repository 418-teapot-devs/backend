from core.models.match import Match
from core.models.robot import Robot
from core.models.user import User
from core.schemas.match import Create
from fastapi import APIRouter, Header, HTTPException, Response
from pony.orm import commit, db_session, select
from views import get_current_user

router = APIRouter()


@router.get("/created")
def get_created_matches(token: str = Header()):

    username = get_current_user(token)
    with db_session:

        host = User.get(name=username)
        if host is None:
            raise HTTPException(status_code=404, detail="User not found")

        matches = select(
            m for m in Match if m.state == "Lobby" and m.host is User.get(name=username)
        )[:]
        res = []
        for m in matches:
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
def upload_match(form_data: Create, token: str = Header()):
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
            state=form_data.state,
        )
        commit()

    return Response(status_code=201)