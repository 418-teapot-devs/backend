from pony.orm import PrimaryKey, Required, Set

from core.models.database import db


class Robot(db.Entity):
    owner = Required("User")
    name = Required(str, 32)
    has_avatar = Required(bool, default=False)
    played_matches = Required(int, default=0)
    won_matches = Required(int, default=0)
    lost_matches = Required(int, default=0)
    PrimaryKey(owner, name)
