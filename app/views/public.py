from fastapi import APIRouter, Header, HTTPException
from pony.orm import db_session, select

from core.models.match import Match
from core.models.user import User
from views import get_current_user

router = APIRouter()


@router.get("/public")
def get_public(token: str = Header()):
    username = get_current_user(token)
    with db_session:

        host = User.get(name=username)
        if host is None:
            raise HTTPException(status_code=404, detail="User not found")

        matches = select(
            m for m in Match if m.state == "Lobby" and (m.host is not host)
        )[:]
        res = []
        for m in matches:
            robots = []
            for r in m.plays:
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
