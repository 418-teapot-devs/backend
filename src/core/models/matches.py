from pony.orm import PrimaryKey, Required, Set

from core.models.database import db


class Match(db.Entity):
    host = Required("User", reverse="matches_hosts")
    name = Required(str, 32)
    robot_count = Required(int, default=1)
    game_count = Required(int, default=100)
    round_count = Required(int, default=10000)
    plays = Set("Robot", reverse="matches_in")
    state = Required(str, 6, default="Lobby")
