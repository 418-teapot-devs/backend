from app.game.entities import Robot
import random

class LoopBot(Robot):
    def initialize(self):
        self.var = 0

        return

    def respond(self):
        dist = self.scanned()

        if dist < 9999:
            self.cannon(self.var + random.randrange(-5, 5), dist)
            self.point_scanner(self.var, 2.5)
        else:
            self.var += 5
            self.point_scanner(self.var, 3)

        return
