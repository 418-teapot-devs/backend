from app.game.robot import Robot


class LoopBot(Robot):
    def initialize(self):
        self.var = 0
        return

    def respond(self):
        self.var += 90
        self.drive(self.var, 100)
        return
