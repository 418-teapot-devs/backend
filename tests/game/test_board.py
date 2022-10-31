from unittest import mock

from app.game import BOARD_SZ, entities
from app.game.board import *
from app.schemas.simulation import RobotInRound, Round


def test_init_positions():
    for i in [1, 5, 10, 50]:
        positions = generate_init_positions(i)
        assert all(0 < x < BOARD_SZ and 0 < y < BOARD_SZ for x, y in positions)


@mock.patch("app.game.board.generate_init_positions", lambda n: [(500, 500)] * n)
def test_board_init():
    b = Board(["test_id_bot"])
    assert len(b.robots) == 1
    assert issubclass(type(b.robots[0]), entities.Robot)


@mock.patch("app.game.board.generate_init_positions", lambda n: [(500, 500)] * n)
def test_game_exec():
    b = Board(["test_loop_bot"])
    g = [b.to_round_schema()]
    for _ in range(5):
        b.next_round()
        g.append(b.to_round_schema())

    expected_x = [500, 500, 499, 499, 500, 500]
    expected_y = [500, 500, 499, 499, 500, 500]

    expected = [
        Round(robots={"test_loop_bot": RobotInRound(x=x_l, y=y_l, dmg=0)}, missiles=[])
        for x_l, y_l in zip(expected_x, expected_y)
    ]
    assert g == expected
