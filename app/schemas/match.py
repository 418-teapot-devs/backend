from typing import List, Dict

from pydantic import BaseModel


class MatchCreateRequest(BaseModel):
    name: str
    robot_id: int
    max_players: int
    min_players: int
    rounds: int
    games: int
    password: str


class MatchJoinRequest(BaseModel):
    robot_id: int
    password: str | None


class Host(BaseModel):
    username: str
    avatar_url: str | None


class RobotInMatch(BaseModel):
    name: str
    avatar_url: str | None
    username: str


class RobotResult(BaseModel):
    robot_pos: int
    death_count: int


class MatchResponse(BaseModel):
    id: int
    name: str
    host: Host
    max_players: int
    min_players: int
    games: int
    rounds: int
    is_private: bool
    robots: Dict[int, RobotInMatch]
    state: str
    results: Dict[int, RobotResult] | None
