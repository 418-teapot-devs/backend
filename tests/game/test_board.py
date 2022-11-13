from unittest import mock

from app.game import BOARD_SZ, entities
from app.game.board import *
from app.schemas.simulation import RobotInRound, Round

from tests.assets.robots.code.test_id_bot import IdBot
from tests.assets.robots.code.test_loop_bot import LoopBot

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

    expected_x = [500, 500, 499, 499, 500, 500]
    expected_y = [500, 500, 500, 499, 499, 501]

    expected = [
        Round(
            robots={b.robots[0]._board_id: RobotInRound(x=x_l, y=y_l, dmg=0)},
            missiles={},
        )
        for x_l, y_l in zip(expected_x, expected_y)
    ]
    # assert g == expected


# @mock.patch("app.game.board.generate_init_positions", lambda n: [(500, 500)] * n)
# def test_game_execute():
#     b = Board(["test_id_bot", "test_aggressive_bot"])
#     g = [b.to_round_schema()]

#     expected_winners = ["test_aggressive_bot"]
#     winners = b.execute_game(1000)

#     assert expected_winners == winners
