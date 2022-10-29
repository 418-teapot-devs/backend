import importlib
import inspect
from typing import List

from app.game.robot import MAX_DMG
import app.schemas.simulation as schemas
from app.game import ASSETS_MODULE


class Board:
    def __init__(self, robot_ids: List):
        self.robots = []
        self.missiles = []

        for i, r_id in enumerate(robot_ids):
            module = importlib.import_module(f".{r_id}", f"{ASSETS_MODULE}.robots")
            classes = inspect.getmembers(module, inspect.isclass)
            classes = list(filter(lambda c: c[0] != "Robot", classes))
            assert len(classes) == 1
            robotName = classes[0][0]
            # getattr returns a class, which we immediately initialize
            r = getattr(module, robotName)(r_id, (500, 500))
            r.initialize()
            self.robots.append(r)

    def nextRound(self):
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
            r._id: schemas.RobotInRound(
                x=r._pos[0],
                y=r._pos[1],
                dmg=r._dmg
            ) for r in self.robots}
        m_summary = []
        return schemas.Round(robots=r_summary, missiles=m_summary)
