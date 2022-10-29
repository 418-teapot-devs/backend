from fastapi import UploadFile
from pydantic import BaseModel


class RobotResponse(BaseModel):
    robot_id: int
    name: str
    avatar: str | None
    win_rate: int
    mmr: int
