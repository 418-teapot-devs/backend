from os.path import isfile
from fastapi import APIRouter, HTTPException

from game.board import board2dict, game2dict, initBoard, nextRound
from core.schemas.simulation import SimulationRequest

DEFAULT_ROUNDS = 100
BOT_DIR = "app/assets/robots"

router = APIRouter()


@router.post("/")
def simulate(schema: SimulationRequest):
    for bot in schema.robots:
        if not isfile(f"{BOT_DIR}/{bot}.py"):
            raise HTTPException(status_code=404, detail=f"robot {bot} not found")
    rounds = schema.rounds if schema.rounds is not None else DEFAULT_ROUNDS
    b = initBoard(list(f".{bot}" for bot in schema.robots))
    g = [board2dict(b)]
    for _ in range(rounds):
        b = nextRound(b)
        g.append(board2dict(b))
    return game2dict(g)
