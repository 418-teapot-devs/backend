from pony.orm import PrimaryKey, Required, Set

from app.models.database import db


class User(db.Entity):
    name = PrimaryKey(str, 32)
    email = Required(str, unique=True)
    password = Required(str)
    # if user has avatar, it is stored in /assets/avatars/users/{name}.png
    # otherwise, it uses /assets/defaults/avatar.png
    has_avatar = Required(bool, default=False)
    is_verified = Required(bool, default=False)
    robots = Set("Robot")
    matches_hosts = Set("Match", reverse="host")
