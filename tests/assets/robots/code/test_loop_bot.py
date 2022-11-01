from app.game.entities import Robot


class LoopBot(Robot):
    def initialize(self):
        self.var = 0
        return

    def respond(self):
        self.var += 90
        self.drive(self.var, 50)
        return
