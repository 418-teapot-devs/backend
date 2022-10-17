from pydantic import BaseModel, EmailStr, HttpUrl, validator
from typing import List

class Create(BaseModel):
    name: str
    name_robot: str
    max_players: int
    min_players: int
    rounds: int
    games: int
    password: str
    state: str
    robotId: int

