from pony.orm import *
from src.core.settings import db_config

db = Database()

db.bind(**db_config)

