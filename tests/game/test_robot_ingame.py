import math

import pytest

from app.game.robot import *


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
    assert r.get_position() == (2, 3)
    assert r.get_direction() == 0
    assert r.get_velocity() == 0
    assert r.var == 90


def test_bot_vars():
    r = RoboTest(1, (2, 3))
    r.initialize()
    r.respond()
    assert r.get_direction() == 45
    assert r.get_velocity() == min(100, ACC_FACTOR)
    assert r.var == 135


def test_bot_move():
    r = RoboTest(1, (500, 500))
    r.initialize()
    r.respond()
    r._move_and_check_crash([])
    new_pos = (
        500 + ACC_FACTOR * DELTA_TIME * math.cos(math.radians(45)),
        500 + ACC_FACTOR * DELTA_TIME * math.sin(math.radians(45)),
    )
    assert r.get_position() == new_pos
    r._dmg = MAX_DMG
    r.respond()
    r._move_and_check_crash([])
    assert r.get_position() == new_pos


def test_bot_crash():
    r1 = RoboTest(1, (500, 500))
    r2 = RoboTest(2, (500, 500))
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
    r1 = NoMove(1, (-1, -1))
    r1.initialize()
    r1.respond()
    r1._move_and_check_crash([])
    assert r1.get_damage() == COLLISION_DMG
