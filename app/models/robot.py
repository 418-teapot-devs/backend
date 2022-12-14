from pony.orm import PrimaryKey, Required, Set, composite_key

from app.models.database import db


class Robot(db.Entity):
    id = PrimaryKey(int, auto=True)
    owner = Required("User")
    name = Required(str, 32)
    has_avatar = Required(bool, default=False)
    played_matches = Required(int, default=0)
    won_matches = Required(int, default=0)
    mmr = Required(int, default=0)
    matches_in = Set("Match", reverse="plays")
    composite_key(owner, name)
