import os

db_file = os.environ["PYROBOTS_DBFILE"]
db_config = {"provider": "sqlite", "filename": db_file, "create_db": True}
