from pydantic import BaseModel, validator
from typing import List, Any, Dict

MAX_BOTS = 2
MAX_ROUNDS = 1000

class SimulationRequest(BaseModel):
    rounds: int | None
    robots: List[Any]

    @validator("rounds")
    def validate_rounds(cls, v):
        if v is None or 0 < v < MAX_ROUNDS:
            return v
        raise ValueError("invalid amount of rounds")

    @validator("robots")
    def validate_robots(cls, v):
        if 0 < len(v) < MAX_BOTS:
            return v
        raise ValueError("invalid amount of robots")


class SimulationResults(BaseModel):
    robots: Dict[int, Dict[str, List[float]]]

