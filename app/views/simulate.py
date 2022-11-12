from fastapi import APIRouter, Header, HTTPException
from pony.orm import db_session

from app.game.board import Board
from app.models.robot import Robot
from app.models.user import User
from app.schemas.match import RobotInMatch
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.util.assets import ASSETS_DIR, get_robot_avatar
from app.util.auth import get_current_user
from app.util.errors import *

DEFAULT_ROUNDS = 100
BOT_DIR = f"{ASSETS_DIR}/robots"

router = APIRouter()


@router.post("/")
def simulate(schema: SimulationRequest, token: str = Header()):
    username = get_current_user(token)

    robots = {}

    with db_session:
        cur_user = User.get(name=username)
        if cur_user is None:
            raise USER_NOT_FOUND_ERROR

        for i, bot in enumerate(schema.robots):
            r = Robot.get(id=bot)
            if r is None:
                raise ROBOT_NOT_FOUND_ERROR
            if r.owner != cur_user:
                raise HTTPException(
                    status_code=403,
                    detail=f"robot requested is not owned by user {username}",
                )

            r_avatar = get_robot_avatar(r)
            robots[i] = RobotInMatch(
                name=r.name, avatar_url=r_avatar, username=r.owner.name
            )

    rounds = schema.rounds if schema.rounds is not None else DEFAULT_ROUNDS

    b = Board(schema.robots)
    g = [b.to_round_schema()]
    for _ in range(rounds):
        b.next_round()
        g.append(b.to_round_schema())
        if len(b.robots) == 0 and len(b.missiles) == 0:
            break

    return SimulationResponse(robots=robots, rounds=g)
