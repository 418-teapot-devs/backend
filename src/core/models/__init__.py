from .database import *
from .matches import *
from .robot import *
from .user import *

db.generate_mapping(create_tables=True)
