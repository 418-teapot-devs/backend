import math
import random
from typing import List, Tuple

from func_timeout import func_timeout

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
    def __init__(self, robot_classes: List):
        self.robots = []
        self.missiles = {}
        self.cur_missile = 0

        init_pos = generate_init_positions(len(robot_classes))
        for i, (r_id, rc) in enumerate(robot_classes):
            try:
                r = rc(r_id, i, init_pos[i])
                func_timeout(INIT_TIMEOUT, r.initialize)
                self.robots.append(r)
            except:
                pass

    def next_round(self):
        for r in self.robots:
            # respond only schedules movement
            # neither scan nor attack depend on internal logic of others
            try:
                func_timeout(RESPOND_TIMEOUT, r.respond)
                r._scan(other._pos for other in self.robots if other is not r)
                maybe_missile = r._launch_missile()
                if maybe_missile is not None:
                    self.missiles[self.cur_missile] = maybe_missile
                    self.cur_missile += 1
            except:
                # Timeout or exception from respond call
                # Either way, kill offending robot
                r._dmg = MAX_DMG
        # Clean up dead robots
        self.robots = [r for r in self.robots if r._dmg < MAX_DMG]

        self.missiles = {k: m for k, m in self.missiles.items() if m._dist > 0}
        for m in self.missiles.values():
            m._advance()

        for m in self.missiles.values():
            m._explode(self.robots)

        for i in range(len(self.robots)):
            # Only check for collisions against `_move`d robots
            self.robots[i]._move_and_check_crash(self.robots[:i])
        # Clean up dead robots
        self.robots = [r for r in self.robots if r._dmg < MAX_DMG]

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
