import math

import pytest

from app.game.entities import *


def test_invalid_bot():
    class Bad1(Robot):
        def respond(self):
            return

    class Bad2(Robot):
        def initialize(self):
            return

    with pytest.raises(TypeError):
        Robot(0, (0, 0))
    with pytest.raises(TypeError):
        Bad1(0, (0, 0))
    with pytest.raises(TypeError):
        Bad2(0, (0, 0))


class RoboTest(Robot):
    def initialize(self):
        self.var = 90

    def respond(self):
        self.var /= 2
        self.drive(self.var, 400)
        self.var *= 3


def test_init_bot():
    r = RoboTest(1, 0, (2, 3))
    r.initialize()
    assert r._id == 1
    assert r._board_id == 0
    assert r.get_position() == (2, 3)
    assert r.get_direction() == 0
    assert r.get_velocity() == 0
    assert r.var == 90


def test_bot_vars():
    r = RoboTest(1, 0, (2, 3))
    r.initialize()
    r.respond()
    r._move_and_check_crash([])
    assert r.get_direction() == 45
    assert r.get_velocity() == min(100, ACC_FACTOR)
    assert r.var == 135


def test_bot_move():
    r = RoboTest(1, 0, (500, 500))
    r.initialize()
    r.respond()
    r._move_and_check_crash([])
    new_pos = (
        500 + ACC_FACTOR * DELTA_TIME * math.cos(math.radians(45)),
        500 + ACC_FACTOR * DELTA_TIME * math.sin(math.radians(45)),
    )
    # assert r.get_position() == new_pos
    r._dmg = MAX_DMG
    r.respond()
    r._move_and_check_crash([])
    # assert r.get_position() == new_pos


def test_bot_crash():
    r1 = RoboTest(1, 0, (500, 500))
    r2 = RoboTest(2, 1, (500, 500))
    r1.initialize()
    r2.initialize()
    r1.respond()
    r2.respond()
    r1._move_and_check_crash([r2])
    assert r1.get_damage() == r2.get_damage() == COLLISION_DMG


class NoMove(Robot):
    def initialize(self):
        return

    def respond(self):
        return


def test_bot_wall():
    r1 = NoMove(1, 0, (-1, -1))
    r1.initialize()
    r1.respond()
    r1._move_and_check_crash([])
    assert r1.get_damage() == COLLISION_DMG


def test_scan_no_robots():
    r = NoMove(1, 0, (500, 500))
    r.point_scanner(175, 5)
    r._scan([])
    assert r.scanned() == math.inf


def test_scan_one_found():
    r = NoMove(1, 0, (400, 300))
    r.point_scanner(63, 3)
    r._scan([(600, 725)])
    assert r.scanned() == math.dist((400, 300), (600, 725))

    r.point_scanner(302, 10)
    r._scan([(409, 290)])
    assert r.scanned() == math.dist((400, 300), (409, 290))


def test_scan_none_found():
    r = NoMove(1, 0, (400, 300))
    r.point_scanner(302, 10)
    r._scan([(100, 100)])
    assert r.scanned() == math.inf


def test_scan_many():
    r = NoMove(1, 0, (400, 300))
    r.point_scanner(302, 10)
    r._scan([(409, 290), (406, 286), (415, 285)])
    assert r.scanned() == math.dist((400, 300), (409, 290))


def test_scan_res_underflow():
    r = NoMove(1, 0, (400, 300))
    r.point_scanner(1, 10)
    r._scan([(410, 299)])
    assert r.scanned() == math.dist((400, 300), (410, 299))


def test_scan_res_overflow():
    r = NoMove(1, 0, (400, 300))
    r.point_scanner(356, 10)
    r._scan([(410, 301)])
    assert r.scanned() == math.dist((400, 300), (410, 301))


def test_bot_cannon():
    r = NoMove(1, 0, (404, 502))
    m = {}
    assert r.is_cannon_ready() == True
    r.cannon(60, 300)
    m[0] = r._launch_missile()
    assert m[0] is not None
    assert r.is_cannon_ready() == False
    assert r._cannon_cooldown == CANNON_COOLDOWN
    assert len(m) == 1
    m = m[0]
    assert m._sender == 0
    assert m._pos == (404, 502)
    assert m._dist == 300
    assert m._dir == (math.cos(math.radians(60)), math.sin(math.radians(60)))


def test_missile_advance():
    m = Missile(234, (500, 500), math.radians(90), 1000)
    m._advance()
    assert m._pos == (500, 500 + MISSILE_D_DELTA)
    assert m._dir == (math.cos(math.radians(90)), 1)
    assert m._dist == 1000 - MISSILE_D_DELTA


def test_missile_explode():
    dists = [500, 510, 530, 550]
    dmgs = [NEAR_EXPLOSION_DMG, MID_EXPLOSION_DMG, FAR_EXPLOSION_DMG, 0]
    m = Missile(234, (500, 500), 0, 0)
    robots: List[Robot] = [NoMove(i, i, (500, i)) for i in dists]
    m._explode(robots)
    assert all(r._dmg == d for r, d in zip(robots, dmgs))
