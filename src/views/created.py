
from fastapi import Header, APIRouter, HTTPException
from jose import jwt
from pony.orm import commit, db_session, select

from core.schemas.match import Create
from core.models.match import Match
from core.models.user import User
from core.models.robot import Robot
from core.schemas.user import Login, Register, Token
from views import get_current_user,JWT_ALGORITHM, JWT_SECRET_KEY


router = APIRouter()

@router.get("/created")
def register(token:str = Header()):
    username = get_current_user(token)
    with db_session:
        matches = select(m for m in Match if m.state == "Lobby" and m.host is User.get(name=username))[:]
        res = []
        for m in matches:
            robots = []
            for r in m.plays:
                # avatqar_url is missing
                # min, max_mlayer, is priviate missing
                robots.append({"name": r.name,"username": r.owner.name})

            print(type(m.plays))
            res.append({"name": m.name, "games": m.game_count,"rounds": m.round_count, "robots": robots})

    return res

@router.post("/created")
def upload_match(form_data: Create, token:str = Header()):
    username =  get_current_user(token)

    with db_session:

        host_robot = Robot.get(name=form_data.name_robot, owner=User.get(name=username))
        if host_robot is None:
            raise HTTPException(status_code=404,detail="Host robot not found")

        m1 = Match(host=User.get(name=username),name=form_data.name,plays=[host_robot])
        commit()

    return {}
