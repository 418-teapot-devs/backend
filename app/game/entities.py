import abc
import math
from typing import List, Tuple

from app.game import *


def clamp(x, lo, hi):
    return min(max(lo, x), hi)


# Compute de determinant (signed area) of the matrix defined by
# the vectors `ba` and `bc`
    # =0 : the transformation has area 0: points are collinear
    # >0 : the matrix squishes and stretches space: clockwise rotation
    # <0 : the matrix "flips" the orientation of the plane: counterclockwise rotation
def orientation(a, b, c):
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    return ba[0] * bc[1] - ba[1] * bc[0]


class Missile:
    def __init__(self, sender, src: Tuple[float, float], dir: float, dist: float):
        self._sender = sender
        self._pos = src
        self._dir = (math.cos(dir), math.sin(dir))
        self._dist = dist

    def _advance(self):
        if self._dist > 0:
            delta_pos = min(self._dist, MISSILE_D_DELTA)
            self._dist -= delta_pos
            delta_pos = (self._dir[0] * delta_pos, self._dir[1] * delta_pos)
            self._pos = (self._pos[0] + delta_pos[0], self._pos[1] + delta_pos[1])

        if not (0 < self._pos[0] < BOARD_SZ and 0 < self._pos[1] < BOARD_SZ):
            # force the misile to explode
            self._dist = 0

    def _explode(self, robots: List["Robot"]):
        if self._dist <= 0:
            for r in robots:
                d = math.dist(self._pos, r._pos)
                if d < 5:
                    r._dmg += NEAR_EXPLOSION_DMG
                elif d < 20:
                    r._dmg += MID_EXPLOSION_DMG
                elif d < 40:
                    r._dmg += FAR_EXPLOSION_DMG


class Robot(abc.ABC):
    def __init__(self, id, board_id, init_pos: Tuple[float, float]):
        self._id = id
        self._pos = init_pos
        self._board_id = board_id
        self._dmg = 0
        self._dir = 0
        self._desired_vel = 0
        self._current_vel = 0

        self._scanner_params = None
        self._scanner_result = math.inf

        self._cannon_params = None
        self._cannon_cooldown = 0

    def _scan(self, scan_positions: List[Tuple[float, float]]):
        if self._scanner_params is None:
            return
        dir, res = self._scanner_params
        # Reset scanner
        self._scanner_params = None

        # calculate scan_l, scan_r: points in the lines that define the scan zone
        scan_r, scan_l = (dir - res, dir + res)
        scan_r = (math.cos(scan_r), math.sin(scan_r))
        scan_l = (math.cos(scan_l), math.sin(scan_l))
        scan_r = (self._pos[0] + scan_r[0], self._pos[1] + scan_r[1])
        scan_l = (self._pos[0] + scan_l[0], self._pos[1] + scan_l[1])

        # valid since the angle is always acute
        def in_scan_area(pt):
            right_of_left = orientation(self._pos, scan_l, pt) >= 0
            left_of_right = orientation(self._pos, scan_r, pt) <= 0
            return right_of_left and left_of_right

        scan_positions = [pos for pos in scan_positions if in_scan_area(pos)]

        self._scanner_result = min(
            (math.dist(self._pos, pos) for pos in scan_positions), default=math.inf
        )

    def _launch_missile(self) -> Missile | None:
        self._cannon_cooldown -= 1
        if self._cannon_cooldown > 0 or self._cannon_params is None:
            self._cannon_params = None
            return None
        self._cannon_cooldown = CANNON_COOLDOWN
        dir, dist = self._cannon_params
        self._cannon_params = None
        return Missile(self._board_id, self._pos, dir, dist)

    def _move_and_check_crash(self, others: List["Robot"]):
        # Robot is dead
        if self._dmg >= MAX_DMG:
            return
        # Update velocity
        self._current_vel = clamp(
            self._desired_vel,
            self._current_vel - ACC_FACTOR,
            self._current_vel + ACC_FACTOR,
        )
        # Update position
        delta_pos = self._current_vel * DELTA_TIME * DELTA_VEL
        delta_x = math.cos(self._dir) * delta_pos
        delta_y = math.sin(self._dir) * delta_pos
        self._pos = (self._pos[0] + delta_x, self._pos[1] + delta_y)
        # Check against other robots and take collision damage
        for r in others:
            if math.dist(self._pos, r._pos) < ROBOT_DIAMETER:
                r._dmg += COLLISION_DMG
                self._dmg += COLLISION_DMG
        # Check for collisions against walls
        radius = ROBOT_DIAMETER / 2
        lbound = radius
        ubound = BOARD_SZ - radius
        if not (lbound < self._pos[0] < ubound and lbound < self._pos[1] < ubound):
            self._pos = (
                clamp(self._pos[0], lbound, ubound),
                clamp(self._pos[1], lbound, ubound),
            )
            self._dmg += COLLISION_DMG

    def get_direction(self):
        return math.degrees(self._dir)

    def get_velocity(self):
        return self._current_vel

    def get_position(self):
        return self._pos

    def get_damage(self):
        return self._dmg

    def is_cannon_ready(self):
        return self._cannon_cooldown == 0

    def cannon(self, degree, distance):
        self._cannon_params = (
            math.radians(degree % 360),
            clamp(distance, 0, 700)
        )

    def point_scanner(self, direction, resolution_in_degrees):
        self._scanner_params = (
            math.radians(direction % 360),
            math.radians(clamp(resolution_in_degrees, 0, 10)),
        )

    def scanned(self):
        return self._scanner_result

    def drive(self, direction: float, velocity: float):
        if self._current_vel <= 50:
            self._dir = math.radians(direction % 360)  # forgive for higher values
        self._desired_vel = clamp(velocity, 0, 100)  # clamp in range [0,100]

    @abc.abstractmethod
    def initialize(self):
        return

    @abc.abstractmethod
    def respond(self):
        return
