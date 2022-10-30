from typing import Any, Dict, List

from pydantic import BaseModel, validator

from app.schemas.match import RobotInMatch

MAX_BOTS = 4
MAX_ROUNDS = 1000


class SimulationRequest(BaseModel):
    rounds: int | None
    robots: List[Any]

    @validator("rounds")
    def validate_rounds(cls, v):
        if v is None or 0 < v <= MAX_ROUNDS:
            return v
        raise ValueError("invalid amount of rounds")

    @validator("robots")
    def validate_robots(cls, v):
        if 0 < len(v) <= MAX_BOTS:
            return v
        raise ValueError("invalid amount of robots")


class RobotInRound(BaseModel):
    x: int
    y: int
    dmg: int


class Round(BaseModel):
    robots: Dict[Any, RobotInRound]
    missiles: List


class SimulationResponse(BaseModel):
    robots: Dict[Any, RobotInMatch]
    rounds: List[Round]
