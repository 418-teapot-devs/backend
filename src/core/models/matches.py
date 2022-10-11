from pony.orm import PrimaryKey, Required, Set

from core.models.database import db


class Match(db.Entity):
    hosts = Required("User", reverse="matches_hosts")
    name = Required(str, 32)
    robot_count = Required(int)
    game_count = Required(int, default=100)
    round_count = Required(int, default=10000)
    plays = Set("Robot", reverse="matches_in")
    state = Required(str, 6)