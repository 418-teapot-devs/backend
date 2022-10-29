from typing import List

from pydantic import BaseModel


class MatchCreateRequest(BaseModel):
    name: str
    robot_id: int
    max_players: int
    min_players: int
    rounds: int
    games: int
    password: str
    # use this instead of name_robot once we
    # figure out how to reset the database
    # between tests


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