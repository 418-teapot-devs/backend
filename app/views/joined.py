from fastapi import Header, APIRouter, HTTPException
from jose import jwt
from pony.orm import commit, db_session, select

from core.models.match import Match
from core.models.user import User
from core.models.robot import Robot
from views import get_current_user,JWT_ALGORITHM, JWT_SECRET_KEY


router = APIRouter()

@router.get("/joined")
def get_joined(token:str = Header()):


    username = get_current_user(token)
    with db_session:
        select(m for m in Match).show()


        matches = select(m for m in Match for r in m.plays 
                        if (m.state == "Lobby") and
                        (r.owner is User.get(name=username) ) )[:]
        res = []
        for m in matches:
            robots = []
            for r in m.plays:
                # this will be used after merge with the refactor repository
                # avatar_url =  f"assets/robots/{r.id}.png" if r.has_avatar else None

                robots.append({"name": r.name, "avatar_url": None,
                               "username": r.owner.name})

            res.append({"name": m.name, "max_players": m.max_players,
                        "min_players": m.min_players,"games": m.game_count,
                        "rounds": m.round_count, "is_private": False,
                        "robots": robots})
    return res
