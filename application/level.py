from random import randint
from enum import Enum


class PointState(Enum):
    Player = 0,
    Obstacle = 1,
    Terrain = 2,
    Bullet = 3,
    Empty = 4,
    Enemy = 5,
    Flag = 6


class Level:
    def __init__(self, size):
        self.size = size
        self.level = list()
        for _ in range(size):
            line = [PointState.Empty] * size
            self.level.append(line)

    def with_obstacles(self, count):
        return self._with(count, PointState.Obstacle)

    def with_player(self):
        return self._with(1, PointState.Player)

    def with_enemies(self, count):
        return self._with(count, PointState.Enemy)

    def with_terrains(self, count):
        return self._with(count, PointState.Terrain)

    def with_flag(self):
        return self

    def _with(self, count, game_obj):
        for _ in range(count):
            x = randint(0, self.size - 1)
            y = randint(0, self.size - 1)
            self.level[x][y] = game_obj
        return self

    def __iter__(self):
        return iter(self.level)
