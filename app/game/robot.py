import abc
import math
from typing import List, Tuple

MAX_DMG = 100
COUNTDOWN_INIT = 10
DELTA_TIME = 0.1
ROBOT_DIAMETER = 50
COLLISION_DMG = 2
BOARD_SZ = 1000
ACC_FACTOR = 10


def clamp(x, lo, hi):
    return min(max(lo, x), hi)


class Robot(abc.ABC):
    def __init__(self, id, init_pos: Tuple[float, float]):
        self._id = id
        self._pos = init_pos
        self._dmg = 0
        self._dir = 0
        self._desired_vel = 0
        self._current_vel = 0

    def _move_and_check_crash(self, others: List["Robot"]):
        # Robot is dead
        if self._dmg >= MAX_DMG:
            return
        # Update position
        delta_pos = self._current_vel * DELTA_TIME
        delta_x = math.cos(math.radians(self._dir)) * delta_pos
        delta_y = math.sin(math.radians(self._dir)) * delta_pos
        delta_pos = (delta_x, delta_y)
        self._pos = tuple(map(lambda a, b: a + b, self._pos, delta_pos))
        # Check against other robots and take collision damage
        for r in others:
            if math.dist(self._pos, r._pos) < ROBOT_DIAMETER:
                r._dmg += COLLISION_DMG
                self._dmg += COLLISION_DMG
        # Check for collisions against walls
        if not (0 < self._pos[0] < BOARD_SZ and 0 < self._pos[1] < BOARD_SZ):
            self._pos = tuple(map(lambda x: clamp(x, 0, 100), self._pos))
            self._dmg += COLLISION_DMG

    def get_direction(self):
        return self._dir

    def get_velocity(self):
        return self._current_vel

    def get_position(self):
        return self._pos

    def get_damage(self):
        return self._dmg

    def is_cannon_ready(self):
        pass

    def cannon(self, degree, distance):
        pass

    def point_scanner(self, direction, resolution_in_degrees):
        pass

    def scanned(self):
        pass

    def drive(self, direction: float, velocity: float):
        if self._current_vel <= 50:
            self._dir = direction % 360  # forgive for higher values
        self._desired_vel = clamp(velocity, 0, 100)  # clamp in range [0,100]
        self._current_vel = clamp(
            self._desired_vel,
            self._current_vel - ACC_FACTOR,
            self._current_vel + ACC_FACTOR,
        )

    @abc.abstractmethod
    def initialize(self):
        return

    @abc.abstractmethod
    def respond(self):
        return
