from pony.orm import PrimaryKey, Required, Set

from src.core.models.database import db


class User(db.Entity):
    username = PrimaryKey(str, 32)
    password = Required(str)
    has_avatar = Required(bool, default=False)
    e_mail = Required(str)
    is_verified = Required(bool, default=False)
