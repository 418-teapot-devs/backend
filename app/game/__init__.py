import os

ROBOT_MODULE = os.environ["PYROBOTS_ASSETS"].replace("/", ".") + ".robots"

# Physics
FPS = 30
DELTA_TIME = 1 / FPS
DELTA_VEL = 1  # 1% of maximum velocity
ACC_FACTOR = 10  # TODO: express in terms of DELTA_TIME as (m/s^2)

# Damage
MAX_DMG = 100
COLLISION_DMG = 2
FAR_EXPLOSION_DMG = 3
MID_EXPLOSION_DMG = 5
NEAR_EXPLOSION_DMG = 10

# Robot things
CANNON_COOLDOWN = 10
ROBOT_DIAMETER = 50

BOARD_SZ = 1000
