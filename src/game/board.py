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


def board2dict(board: Board) -> Dict[int, Tuple[float, float]]:
    return { r._id: r._pos for r in board }


def game2dict(game: List[Dict[int, Tuple[float, float]]]) -> Dict[int, Dict[str, List[float]]]:
    summary = { r_id: { 'x': [], 'y': [] } for r_id in game[0].keys() }
    # summary = { r_id: ([r_pos[0]], [r_pos[0]]) for r_id, r_pos in game[0].items() }
    for round in game:
        for r_id, pos in round.items():
            summary[r_id]['x'].append(pos[0])
            summary[r_id]['y'].append(pos[1])
    return summary
