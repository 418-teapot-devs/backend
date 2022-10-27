from pony.orm import PrimaryKey, Required, Set, composite_key

from app.models.database import db


class Robot(db.Entity):
    id = PrimaryKey(int, auto=True)
    owner = Required("User")
    name = Required(str, 32)
    # if robot has avatar, it is stord in /assets/avatars/robots/{owner.name}_{name}.png
    # otherwise, it uses /assets/defaults/robot_avatar.png
    has_avatar = Required(bool, default=False)
    played_matches = Required(int, default=0)
    won_matches = Required(int, default=0)
    lost_matches = Required(int, default=0)
    matches_in = Set("Match", reverse="plays")
    composite_key(owner, name)
