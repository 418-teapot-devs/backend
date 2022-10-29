import sys

from pony.orm import Database

from app.dbconfig import *

db = Database()
db.bind(**db_config)
