from unittest import mock

from app.game import BOARD_SZ, entities
from app.game.board import *
from app.game.executor import Executor
from app.schemas.simulation import RobotInRound, Round


class IdBot(entities.Robot):
    def initialize(self):
        return

    def respond(self):
        return


class LoopBot(entities.Robot):
    def initialize(self):
        self.var = 0
        return

    def respond(self):
        self.var += 90
        self.drive(self.var, 50)
        return


def test_init_positions():
    for i in [1, 5, 10, 50]:
        positions = generate_init_positions(i)
        assert all(0 < x < BOARD_SZ and 0 < y < BOARD_SZ for x, y in positions)


@mock.patch("app.game.board.generate_init_positions", lambda n: [(500, 500)] * n)
def test_board_init():
    b = Board([(1, IdBot)])
    assert len(b.robots) == 1
    assert issubclass(type(b.robots[0]), entities.Robot)


@mock.patch("app.game.board.generate_init_positions", lambda n: [(500, 500)] * n)
def test_game_missiles():
    b = Board([(1, IdBot)])
    b.missiles[1] = entities.Missile(b.robots[0]._board_id, (2000, 2000), 2, 60)

    b.next_round()
    assert len(b.missiles) == 1

    b.next_round()
    assert len(b.missiles) == 0

    b.missiles[2] = entities.Missile(
        345, (500 - MISSILE_D_DELTA, 500), 0, MISSILE_D_DELTA
    )

    b.next_round()
    assert len(b.missiles) == 1
    assert b.missiles[2]._pos == (500, 500)
    assert b.missiles[2]._dist == 0
    assert b.robots[0].get_damage() == NEAR_EXPLOSION_DMG


@mock.patch("app.game.board.generate_init_positions", lambda n: [(500, 500)] * n)
def test_game_exec():
    b = Board([(1, LoopBot)])
    g = [b.to_round_schema()]
    for _ in range(5):
        b.next_round()
        g.append(b.to_round_schema())

    expected_x = [500, 500, 496, 496, 503, 503]
    expected_y = [500, 501, 501, 496, 496, 505]

    expected = [
        Round(
            robots={b.robots[0]._board_id: RobotInRound(x=x_l, y=y_l, dmg=0)},
            missiles={},
        )
        for x_l, y_l in zip(expected_x, expected_y)
    ]
    assert g == expected


def test_robot_invalid_init():
    class TimeoutOnInit(IdBot):
        def initialize(self):
            while True:
                pass

    class ExceptionOnInit(IdBot):
        def initialize(self):
            assert False

    b = Board([(1, TimeoutOnInit), (2, ExceptionOnInit)])
    assert len(b.robots) == 0


def test_robot_invalid_respond():
    class TimeoutOnRespond(IdBot):
        def respond(self):
            while True:
                pass

    class ExceptionOnRespond(IdBot):
        def respond(self):
            assert False

    b = Board([(1, TimeoutOnRespond), (2, ExceptionOnRespond)])
    assert len(b.robots) == 2

    b.next_round()
    assert len(b.robots) == 0


@mock.patch("app.game.board.generate_init_positions", lambda n: [(500, 500)] * n)
def test_game_execute():
    e = Executor(["test_id_bot", "test_aggressive_bot"])

    e.execute_game(1000)

    assert e.survived_games["test_aggressive_bot"] == 1
    assert e.won_games["test_aggressive_bot"] == 1
