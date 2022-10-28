from pydantic import BaseModel
from typing import List

class MatchCreateRequest(BaseModel):
    name: str
    name_robot: str
    max_players: int
    min_players: int
    rounds: int
    games: int
    password: str
    # use this instead of name_robot once we
    # figure out how to reset the database
    # between tests
    # robot_id: int

class Host(BaseModel):
    username: str
    avatar_url: str | None

class RobotInMatch(BaseModel):
    name: str
    avatar_url: str | None
    username: str

class MatchResponse(BaseModel):
    id: int
    name: str
    host: Host
    max_players: int
    min_players: int
    games: int
    rounds: int
    is_private: bool | None
    robots: List[RobotInMatch]
