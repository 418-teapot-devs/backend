from .database import *
from .match import *
from .robot import *
from .robot_result import *
from .user import *

db.generate_mapping(create_tables=True)
