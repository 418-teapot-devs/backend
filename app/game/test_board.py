from .board import *
import game.robot

def test_board_init():
    b = initBoard([".id_bot"])
    assert len(b) == 1
    assert issubclass(type(b[0]), game.robot.Robot)


def test_game_exec():
    b = initBoard([".id_bot", ".loop_bot"])
    g = [board2dict(b)]
    for _ in range(5):
        b = nextRound(b)
        g.append(board2dict(b))

    expected = {0: {"x": [500] * 6, "y": [500] * 6},
        1: {"x": [500, 500.0, 490.0, 490.0, 500.0, 500.0], "y": [500, 510.0, 510.0, 500.0, 500.0, 510.0]}}
    assert game2dict(g) == expected