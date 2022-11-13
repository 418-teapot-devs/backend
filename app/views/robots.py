from fastapi import APIRouter, Header, HTTPException, UploadFile
from pony.orm import commit, db_session, select

from app.models.robot import Robot
from app.models.user import User
from app.schemas.robot import RobotResponse
from app.util.assets import ASSETS_DIR, get_robot_avatar
from app.util.auth import get_current_user
from app.util.errors import *

router = APIRouter()


@router.get("/")
def get_robots(token: str = Header()):
    username = get_current_user(token)

    with db_session:

        user = User.get(name=username)
        if user is None:
            raise USER_NOT_FOUND_ERROR

        robots = []
        for robot in select(r for r in Robot if r.owner.name == username):
            won_matches = robot.won_matches
            played_matches = robot.played_matches
            mmr = 30 * played_matches - 10 * won_matches

            robots.append(
                RobotResponse(
                    robot_id=robot.id,
                    name=robot.name,
                    avatar_url=get_robot_avatar(robot),
                    played_matches=played_matches,
                    won_matches=won_matches,
                    mmr=mmr,
                )
            )
    return robots


@router.post("/", status_code=201)
def create_robot(
    name: str, code: UploadFile, avatar: UploadFile | None = None, token: str = Header()
):
    username = get_current_user(token)

    with db_session:

        user = User.get(name=username)
        if user is None:
            raise USER_NOT_FOUND_ERROR

        if Robot.exists(owner=user, name=name):
            raise HTTPException(
                status_code=409,
                detail=f"Robot with name {name} already exists for user {user.name}",
            )

        robot = Robot(owner=user, name=name, has_avatar=avatar is not None)
        commit()

    with open(f"{ASSETS_DIR}/robots/code/{robot.id}.py", "wb") as f:
        f.write(code.file.read())

    if avatar:
        with open(f"{ASSETS_DIR}/robots/avatars/{robot.id}.png", "wb") as f:
            f.write(avatar.file.read())
