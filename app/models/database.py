import sys

from pony.orm import Database

from app.dbconfig import *

db = Database()

if "pytest" in sys.modules:
    db.bind(**db_test_config)
else:
    db.bind(**db_config)
