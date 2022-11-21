from fastapi import APIRouter, Header, HTTPException, UploadFile
from pony.orm import commit, db_session, select

from app.models.robot import Robot
from app.models.user import User
from app.schemas.robot import RobotCode, RobotDetails, RobotResponse
from app.util.assets import ASSETS_DIR, get_robot_avatar
from app.util.auth import get_current_user
from app.util.check_code import check_code
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
            robots.append(
                RobotResponse(
                    robot_id=robot.id,
                    name=robot.name,
                    avatar_url=get_robot_avatar(robot),
                    played_matches=robot.played_matches,
                    won_matches=robot.won_matches,
                    mmr=robot.mmr,
                )
            )
    return robots


@router.post("/", status_code=201)
def create_robot(
    name: str, code: UploadFile, avatar: UploadFile | None = None, token: str = Header()
):
    username = get_current_user(token)

    src = code.file.read()

    try:
        check_code(src)
    except SyntaxError:
        raise ROBOT_CODE_SYNTAX_ERROR

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
        f.write(b"from app.game.entities import Robot\n")
        f.write(src)

    if avatar:
        with open(f"{ASSETS_DIR}/robots/avatars/{robot.id}.png", "wb") as f:
            f.write(avatar.file.read())


@router.get("/{robot_id}/")
def get_robot_details(robot_id: int, token: str = Header()):
    username = get_current_user(token)

    with db_session:

        user = User.get(name=username)
        if user is None:
            raise USER_NOT_FOUND_ERROR

        robot = Robot.get(id=robot_id)
        if robot is None:
            raise ROBOT_NOT_FOUND_ERROR
        if robot.owner != user:
            raise ROBOT_NOT_FROM_USER_ERROR

        info = RobotResponse(
            robot_id=robot.id,
            name=robot.name,
            avatar_url=get_robot_avatar(robot),
            played_matches=robot.played_matches,
            won_matches=robot.won_matches,
            mmr=robot.mmr,
        )

    with open(f"{ASSETS_DIR}/robots/code/{robot_id}.py") as code:
        code.readline()  # do not send line with `Robot` import
        return RobotDetails(robot_info=info, code=code.read())


@router.put("/{robot_id}/", status_code=200)
def update_robot_code(robot_id: int, code: RobotCode, token: str = Header()):
    username = get_current_user(token)

    with db_session:

        user = User.get(name=username)
        if user is None:
            raise USER_NOT_FOUND_ERROR

        robot = Robot.get(id=robot_id)
        if robot is None:
            raise ROBOT_NOT_FOUND_ERROR
        if robot.owner != user:
            raise ROBOT_NOT_FROM_USER_ERROR

    try:
        pass
        check_code(code.code)
    except SyntaxError:
        raise ROBOT_CODE_SYNTAX_ERROR

    with open(f"{ASSETS_DIR}/robots/code/{robot_id}.py", "w") as f:
        f.write("from app.game.entities import Robot\n")
        f.write(code.code)
