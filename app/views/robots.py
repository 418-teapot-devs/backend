from fastapi import APIRouter, Header, HTTPException, Response, UploadFile
from pony.orm import commit, db_session, select

from app.models.robot import Robot
from app.models.user import User
from app.schemas.robot import RobotResponse
from app.views import get_current_user

router = APIRouter()


@router.get("/")
def get_robot(token: str = Header()):
    username = get_current_user(token)

    with db_session:
        robots = []
        for robot in select(r for r in Robot if r.owner.name == username):
            avatar = f"app/assets/robots/{robot.id}.png" if robot.has_avatar else None
            robots.append(RobotResponse(robot_id=robot.id, name=robot.name, avatar=avatar))
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

        with open(f"app/assets/robots/{robot.id}.py", "wb") as f:
            f.write(code.file.read())

        if avatar:
            with open(f"app/assets/robots/{robot.id}.png", "wb") as f:
                f.write(avatar.file.read())

    return Response(status_code=201)
