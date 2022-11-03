from fastapi import APIRouter, Header, HTTPException, Response, UploadFile
from pony.orm import commit, db_session, select

from app.models.robot import Robot
from app.models.user import User
from app.schemas.robot import RobotResponse
from app.util.assets import ASSETS_DIR, get_robot_avatar
from app.util.auth import get_current_user

router = APIRouter()


@router.get("/")
def get_robot(token: str = Header()):
    username = get_current_user(token)

    with db_session:
        robots = []
        for robot in select(r for r in Robot if r.owner.name == username):
            robots.append(
                RobotResponse(
                    robot_id=robot.id,
                    name=robot.name,
                    avatar_url=get_robot_avatar(robot),
                    win_rate=0,
                    mmr=0,
                )
            )
    return robots


@router.post("/")
def create_robot(
    name: str, code: UploadFile, avatar: UploadFile | None = None, token: str = Header()
):
    with db_session:
        username = get_current_user(token)

        user = User.get(name=username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

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

    return Response(status_code=201)
