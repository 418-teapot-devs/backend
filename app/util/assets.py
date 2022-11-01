import os

from app.models import Robot, User

ASSETS_DIR = os.environ["PYROBOTS_ASSETS"]
ASSETS_MODULE = ASSETS_DIR.replace("/", ".")


def get_user_avatar(user: User) -> str | None:
    return f"/assets/avatars/user/{user.name}.png" if user.has_avatar else None


def get_robot_avatar(robot: Robot) -> str | None:
    return f"/assets/avatars/robot/{robot.id}.png" if robot.has_avatar else None
