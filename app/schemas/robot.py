from pydantic import BaseModel


class RobotResponse(BaseModel):
    robot_id: int
    name: str
    avatar_url: str | None
    played_matches: int
    won_matches: int
    mmr: int


class RobotDetails(BaseModel):
    robot_info: RobotResponse
    code: str


class RobotCode(BaseModel):
    code: str
