from app.game.entities import Robot
import math
import random

def random_pos():
    return (random.uniform(0, 1000), random.uniform(0, 1000))

class RabbitBot(Robot):
    def initialize(self):
        self.goto = random_pos()
        return

    def respond(self):
        p = self.get_position()
        if math.dist(p, self.goto) < 50:
            if self.get_velocity() > 0:
                self.drive(0, 0)
                return
            self.goto = random_pos()

        self.drive(self.get_dir(self.goto), 25)
        return

    def get_dir(self, dest):
        p = self.get_position()
        x = dest[0] - p[0]
        y = dest[1] - p[1]
        if x == 0:
            if dest[1] > 0:
                return 90
            else:
                return 270
        else:
            if dest[0] > p[0]:
                return math.degrees(math.atan(y/x))
            else:
                return math.degrees(math.atan(y/x)) + 180
