from pony.orm import PrimaryKey, Required, Set

from src.core.models.database import db

class User(db.Entity):
    name = PrimaryKey(str, 32)
    e_mail = Required(str, unique=True)
    password = Required(str)
    has_avatar = Required(bool, default=False)
    is_verified = Required(bool, default=False)

