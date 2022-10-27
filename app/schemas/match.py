from pydantic import BaseModel


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
