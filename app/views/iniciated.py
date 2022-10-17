from core.models.match import Match
from core.models.robot import Robot
from core.models.user import User
from fastapi import APIRouter, Header, HTTPException
from jose import jwt
from pony.orm import commit, db_session, select
from views import JWT_ALGORITHM, JWT_SECRET_KEY, get_current_user

router = APIRouter()


@router.get("/iniciated")
def get_iniciated(token: str = Header()):
    username = get_current_user(token)
    with db_session:

        host = User.get(name=username)
        if host is None:
            raise HTTPException(status_code=404, detail="User not found")

        matches = select(
            m
            for m in Match
            for r in m.plays
            if (m.state == "InGame" or m.state == "Finished") and r.owner is host
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
                    "raking_position": None,
                    "MMR_WOM": None,
                }
            )
    return res
