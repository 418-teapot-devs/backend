from pony.orm import Database

from core.settings import db_config

db = Database()

db.bind(**db_config)
