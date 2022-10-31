import importlib
import inspect
import math
import random
from typing import List, Tuple

import app.schemas.simulation as schemas
from app.game import MAX_DMG, ROBOT_MODULE


def generate_init_positions(n: int) -> List[Tuple[float, float]]:
    dirs = [i * 360 / n + random.uniform(-120 / n, 120 / n) for i in range(n)]
    dirs = [(math.cos(math.radians(d)), math.sin(math.radians(d)), random.uniform(50, 450)) for d in dirs]
    dirs = [(500 + x*d, 500 + y*d) for (x, y, d) in dirs]
    random.shuffle(dirs)
    return dirs


class Board:
    def __init__(self, robot_ids: List):
        self.robots = []
        self.missiles = []

        init_pos = generate_init_positions(len(robot_ids))
        for i, r_id in enumerate(robot_ids):
            module = importlib.import_module(f".{r_id}", ROBOT_MODULE)
            classes = inspect.getmembers(module, inspect.isclass)
            classes = list(filter(lambda c: c[0] != "Robot", classes))
            assert len(classes) == 1
            robotName = classes[0][0]
            # getattr returns a class, which we immediately initialize
            r = getattr(module, robotName)(r_id, init_pos[i])
            r.initialize()
            self.robots.append(r)

    def next_round(self):
        for r in self.robots:
            # okey to do in the same loop since only scheduling movement
            # neither scan nor attack are affected by internal logic of others
            r.respond()
            # r._scan()
            # r._attack()
        for i in range(len(self.robots)):
            # Only check for collisions against `_move`d robots
            self.robots[i]._move_and_check_crash(self.robots[:i])
        # Clean up dead robots
        self.robots = list(filter(lambda r: r._dmg < MAX_DMG, self.robots))

    def to_round_schema(self) -> schemas.Round:
        r_summary = {
            r._id: schemas.RobotInRound(x=r._pos[0], y=r._pos[1], dmg=r._dmg)
            for r in self.robots
        }
        m_summary = []
        return schemas.Round(robots=r_summary, missiles=m_summary)
