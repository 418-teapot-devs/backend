import importlib
import inspect
from typing import List

from app.game import *
from app.game.board import Board


class Executor:
    def __init__(self, robot_ids: List):
        self.games_execd = 0
        self.robot_classes = []

        self.won_games = {}
        self.survived_games = {}

        for r_id in robot_ids:
            module = importlib.import_module(f".{r_id}", ROBOT_MODULE)
            classes = inspect.getmembers(module, inspect.isclass)
            classes = list(filter(lambda c: c[0] != "Robot", classes))
            assert len(classes) == 1
            robotName = classes[0][0]
            r = getattr(module, robotName)
            self.robot_classes.append((r_id, r))

            self.won_games[r_id] = 0
            self.survived_games[r_id] = 0

    def simulate(self, rounds: int) -> List:
        b = Board(self.robot_classes)
        g = [b.to_round_schema()]
        for _ in range(rounds):
            b.next_round()
            g.append(b.to_round_schema())
            if len(b.robots) == 0 and len(b.missiles) == 0:
                break
        return g

    def execute_game(self, rounds: int):
        self.games_execd += 1
        b = Board(self.robot_classes)

        for _ in range(rounds):
            b.next_round()

            if len(b.robots) <= 1:
                break

        survivors = list(map(lambda x: x._id, b.robots))

        for r in survivors:
            self.survived_games[r] += 1
        if len(survivors) == 1:
            self.won_games[survivors[0]] += 1

    def generate_stats(self):
        positions = sorted(
            self.won_games, key=lambda r: self.won_games[r], reverse=True
        )

        # Offset all death counts by number of games played
        # We didn't know the offset before the games were executed
        death_counts = {
            k: self.games_execd - v for (k, v) in self.survived_games.items()
        }
        return (positions, death_counts)
