from os.path import isfile

from fastapi import APIRouter, Header, HTTPException
from pony.orm import db_session

from app.game.board import Board
from app.models.robot import Robot
from app.models.user import User
from app.schemas.match import RobotInMatch
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.util.auth import get_current_user

DEFAULT_ROUNDS = 100
BOT_DIR = "app/assets/robots"

router = APIRouter()


@router.post("/")
def simulate(schema: SimulationRequest, token: str = Header()):
    username = get_current_user(token)

    robots = {}

    with db_session:
        cur_user = User.get(username)
        if cur_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        for bot in schema.robots:
            r = Robot.get(id=bot).owner.name != username
            if r is None:
                raise HTTPException(status_code=404, detail="Robot not found")
            if Robot.get(id=bot).owner.name != username:
                raise HTTPException(
                    status_code=403,
                    detail=f"robot requested is not owned by user {username}",
                )
            robots[bot] = RobotInMatch(name=r.name, avatar_url=None, username=r.owner)

    rounds = schema.rounds if schema.rounds is not None else DEFAULT_ROUNDS

    b = Board(schema.robots)
    g = [b.to_round_schema()]
    for _ in range(rounds):
        b.next_round()
        g.append(b.to_round_schema())

    return SimulationResponse(robots=robots,rounds=g)
