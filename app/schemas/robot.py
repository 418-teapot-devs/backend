from typing import Any, Dict, List
from fastapi import UploadFile
from pydantic import BaseModel, validator

class RobotResponse(BaseModel):
    robot_id: int
    name: str
    avatar: str | None
    win_rate: int
    mmr: int
