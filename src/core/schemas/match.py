from pydantic import BaseModel, EmailStr, HttpUrl, validator
from typing import List

class Create(BaseModel):
    name: str
    name_robot: str
    max_player: int
    min_players: int
    creator_name: str
    rounds: int
    games: int
    password: str
    status: str
    robotId: int
#    robots: List[Create]

