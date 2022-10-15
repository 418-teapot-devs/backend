import inspect, importlib
from typing import Dict, List, Tuple
from robot import Robot, MAX_DMG

Board = List[Robot]

def nextRound(board: Board) -> Board:
    for r in board:
        r.respond()
    for i in range(len(board)):
        # Only check for collisions against `_move`d robots
        board[i]._move_and_check_crash(board[:i])
    # Clean up dead robots
    board = list(filter(lambda r: r._dmg <= MAX_DMG, board))
    return board


def initBoard(files: List[str]) -> Board:
    board = []
    for file in files:
        module = importlib.import_module(file)
        classes = inspect.getmembers(module, inspect.isclass)
        classes = list(filter(lambda c: c[0] != 'Robot', classes))
        assert len(classes) == 1
        robotName = classes[0][0]
        # getattr returns a class, which we immediately initialize
        r = getattr(module, robotName)(0, (500, 500))
        r.initialize()
        board.append(r)
    return board
