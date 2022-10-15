import math

import pytest

from .robot import *


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
    r = RoboTest(1, (2, 3))
    r.initialize()
    assert r._id == 1
    assert r._pos == (2, 3)
    assert r._dir == 0
    assert r._vel == 0
    assert r.var == 90


def test_bot_vars():
    r = RoboTest(1, (2, 3))
    r.initialize()
    r.respond()
    assert r._dir == 45
    assert r._vel == 100
    assert r.var == 135


def test_bot_move():
    r = RoboTest(1, (500, 500))
    r.initialize()
    r.respond()
    r._move_and_check_crash([])
    assert r._pos == (
        500 + 100 * DELTA_TIME * math.cos(math.radians(45)),
        500 + 100 * DELTA_TIME * math.sin(math.radians(45)),
    )


def test_bot_crash():
    r1 = RoboTest(1, (500, 500))
    r2 = RoboTest(2, (500, 500))
    r1.initialize()
    r2.initialize()
    r1.respond()
    r2.respond()
    r1._move_and_check_crash([r2])
    assert r1._dmg == r2._dmg == COLLISION_DMG


class NoMove(Robot):
    def initialize(self):
        return

    def respond(self):
        return


def test_bot_wall():
    r1 = NoMove(1, (-1, -1))
    r1.initialize()
    r1.respond()
    r1._move_and_check_crash([])
    assert r1._dmg == COLLISION_DMG
