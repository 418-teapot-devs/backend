from .database import *
from .match import *
from .robot import *
from .user import *
from .robot_result import *

db.generate_mapping(create_tables=True)
