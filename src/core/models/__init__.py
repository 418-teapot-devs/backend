from .database import *
from .robot import *
from .user import *
from .matches import *

db.generate_mapping(create_tables=True)
