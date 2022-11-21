from app.game.entities import Robot
class AttackRobot(Robot):
    def initialize(self):
        self.var = 0
        return

    def respond(self):
        if self.get_position()[0] < 900:
            self.drive(0, 30)
        self.cannon(180, self.get_position()[0] - 500)

        return
