from pony.orm import PrimaryKey, Required, Set

from core.models.database import db


class Match(db.Entity):
    id = PrimaryKey(int, auto=True)
    host = Required("User", reverse="matches_hosts")
    name = Required(str, 32)
    robot_count = Required(int, default=1)
    max_players = Required(int)
    min_players = Required(int)
    game_count = Required(int, default=100)
    round_count = Required(int, default=10000)
    plays = Set("Robot", reverse="matches_in")
    state = Required(str, 8, default="Lobby")
