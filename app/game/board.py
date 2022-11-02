import importlib
import inspect
import math
import random
from typing import List, Tuple

import app.schemas.simulation as schemas
from app.game import *

DISP_FACTOR = math.tau / 3


def generate_init_positions(n: int) -> List[Tuple[float, float]]:
    dirs = [
        i * math.tau / n + random.uniform(-DISP_FACTOR / n, DISP_FACTOR / n)
        for i in range(n)
    ]
    dirs = [(math.cos(d), math.sin(d), random.uniform(50, 475)) for d in dirs]
    dirs = [(500 + x * d, 500 + y * d) for (x, y, d) in dirs]
    random.shuffle(dirs)
    return dirs


class Board:
    def __init__(self, robot_ids: List):
        self.robots = []
        self.missiles = {}
        self.cur_missile = 0

        init_pos = generate_init_positions(len(robot_ids))
        for i, r_id in enumerate(robot_ids):
            module = importlib.import_module(f".{r_id}", ROBOT_MODULE)
            classes = inspect.getmembers(module, inspect.isclass)
            classes = list(filter(lambda c: c[0] != "Robot", classes))
            assert len(classes) == 1
            robotName = classes[0][0]
            # getattr returns a class, which we immediately initialize
            r = getattr(module, robotName)(r_id, i, init_pos[i])
            r.initialize()
            self.robots.append(r)

    def next_round(self):
        for r in self.robots:
            # respond only schedules movement
            # neither scan nor attack depend on internal logic of others
            r.respond()
            r._scan(other._pos for other in self.robots if other is not r)
            maybe_missile = r._launch_missile()
            if maybe_missile is not None:
                self.missiles[self.cur_missile] = maybe_missile
                self.cur_missile += 1

        self.missiles = {k: m for k, m in self.missiles.items() if m._dist > 0}
        for m in self.missiles.values():
            m._advance()
        self.missiles = {
            k: m
            for k, m in self.missiles.items()
            if 0 < m._pos[0] < BOARD_SZ and 0 < m._pos[1] < BOARD_SZ
        }
        for m in self.missiles.values():
            m._explode(self.robots)

        for i in range(len(self.robots)):
            # Only check for collisions against `_move`d robots
            self.robots[i]._move_and_check_crash(self.robots[:i])
        # Clean up dead robots
        self.robots = [r for r in self.robots if r._dmg < MAX_DMG]

    def execute_game(self, rounds: int):
        winner = []

        for _ in range(rounds):
            self.next_round()

            if len(self.robots) <= 1:
                break

        winner = list(map(lambda x: x._id, self.robots))

        return winner

    def to_round_schema(self) -> schemas.Round:
        r_summary = {
            r._board_id: schemas.RobotInRound(x=r._pos[0], y=r._pos[1], dmg=r._dmg)
            for r in self.robots
        }
        m_summary = {
            k: schemas.MissileInRound(
                sender_id=m._sender, x=m._pos[0], y=m._pos[1], exploding=m._dist <= 0
            )
            for k, m in self.missiles.items()
        }
        return schemas.Round(robots=r_summary, missiles=m_summary)
