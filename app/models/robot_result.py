from pony.orm import PrimaryKey, Required, Set, composite_key

from app.models.database import db


class RobotMatchResult(db.Entity):
    id = PrimaryKey(int, auto=True)
    robot_id = Required(int)
    match_id = Required(int)
    position = Required(int)
    death_count = Required(int)
    condition = Required(str, 4)
    composite_key(robot_id, match_id)
