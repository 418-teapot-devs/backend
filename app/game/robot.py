import abc
import math
from typing import List, Tuple

from app.game import *


def clamp(x, lo, hi):
    return min(max(lo, x), hi)


# Based on
# https://stackoverflow.com/questions/37600118/test-if-point-inside-angle/37601169
def orientation(a, b, c):
    # consider the angle por formed by the points a, b and c
    # k==0: Collinear
    # k>0 : Clockwise rotation
    # k<0 : Counterclockwise rotation
    return (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[0])


class Missile:
    def __init__(self, src: Tuple[float, float], dir: float, dist: float):
        self._pos = src
        self._dir = (math.cos(dir), math.sin(dir))
        self._dist = dist

    def _advance(self):
        if self._dist > 0:
            delta_pos = min(self._dist, MISSILE_D_DELTA)
            self._dist -= delta_pos
            delta_pos = (self._dir[0] * delta_pos, self._dir[1] * delta_pos)
            self._pos = (self._pos[0] + delta_pos[0], self._pos[1] + delta_pos[1])

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
    def __init__(self, id, init_pos: Tuple[float, float]):
        self._id = id
        self._pos = init_pos
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

        # Scanning all board
        if res >= math.pi:
            return min(
                (math.dist(self._pos, pos) for pos in scan_positions), default=math.inf
            )

        # calculate scan_l, scan_r: points in the lines that define the scan zone
        scan_r, scan_l = (dir - res, dir + res)
        scan_r = (math.cos(scan_r), math.sin(scan_r))
        scan_l = (math.cos(scan_l), math.sin(scan_l))
        scan_r = (self._pos[0] + scan_r[0], self._pos[1] + scan_r[1])
        scan_l = (self._pos[0] + scan_l[0], self._pos[1] + scan_l[1])

        def in_acute(l, r, pt):
            return (
                orientation(self._pos, l, pt) > 0 and orientation(self._pos, r, pt) < 0
            )

        if res <= math.pi / 2:  # scanning an acute angle
            scan_positions = [
                pos for pos in scan_positions if in_acute(scan_l, scan_r, pos)
            ]
        else:  # scanning an obtuse angle
            scan_positions = [
                pos for pos in scan_positions if not in_acute(scan_r, scan_l, pos)
            ]

        return min(
            (math.dist(self._pos, pos) for pos in scan_positions), default=math.inf
        )

    def _launch_missile(self, missiles: List[Missile]):
        if self._cannon_cooldown == 0 and self._cannon_params is not None:
            dir, dist = self._cannon_params
            missiles.append(Missile(self._pos, dir, dist))
            self._cannon_cooldown = CANNON_COOLDOWN
        self._cannon_cooldown -= 0
        self._shooting = False

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
        delta_pos = (delta_x, delta_y)
        self._pos = (self._pos[0] + delta_pos[0], self._pos[0] + delta_pos[0])
        # Check against other robots and take collision damage
        for r in others:
            if math.dist(self._pos, r._pos) < ROBOT_DIAMETER:
                r._dmg += COLLISION_DMG
                self._dmg += COLLISION_DMG
        # Check for collisions against walls
        if not (0 < self._pos[0] < BOARD_SZ and 0 < self._pos[1] < BOARD_SZ):
            self._pos = (
                clamp(self._pos[0], 0, BOARD_SZ),
                clamp(self._pos[0], 0, BOARD_SZ),
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
        self._cannon_params = (math.radians(degree % 360), distance)

    def point_scanner(self, direction, resolution_in_degrees):
        self._scanner_params = (
            math.radians(direction % 360),
            math.radians(clamp(resolution_in_degrees, 0, 180)),
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
