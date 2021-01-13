from enum import Enum
import random


class CellState(Enum):
    Player = 0
    PlayerFlag = 1
    BrickWall = 2
    ConcreteWall = 3
    Terrain = 4
    Bullet = 5
    Empty = 6
    PatrollingEnemy = 7
    HauntingEnemy = 8
    Bonus = 9


class Level:
    def __init__(self, size, seed):
        self.size = size
        self.seed = seed
        random.seed(seed)

        self.level = [
            [CellState.Empty] * size
            for _ in range(size)
        ]

        self._set_player_base(size)
        self.enemies_base = self.get_enemies_base()

        left_tunnel = [
            (size - x, size // 2 - 3)
            for x in range(3, size)
        ]

        right_tunnel = [
            (size - x, size // 2 + 3)
            for x in range(3, size)
        ]

        self._free_cells = [
            (x, y)
            for x in range(self.size)
            for y in range(self.size)

            # Player base
            if (x, y) != (size - 3, size // 2)
            if (x, y) != (size - 3, size // 2 - 1)
            if (x, y) != (size - 3, size // 2 + 1)
            if (x, y) != (size - 3, size // 2 - 2)
            if (x, y) != (size - 3, size // 2 + 2)
            if (x, y) != (size - 1, size // 2)
            if (x, y) != (size - 2, size // 2)
            if (x, y) != (size - 2, size // 2 - 1)
            if (x, y) != (size - 2, size // 2 + 1)
            if (x, y) != (size - 1, size // 2 + 1)
            if (x, y) != (size - 1, size // 2 - 1)

            # Tunnels
            if (x, y) not in left_tunnel
            if (x, y) not in right_tunnel

            # Enemy base
            if (x, y) not in self.enemies_base
            if (x, y) != (2, size // 2 - 2)
            if (x, y) != (2, size // 2 - 1)
            if (x, y) != (2, size // 2 + 2)
            if (x, y) != (2, size // 2 + 1)
        ]

    def get_player_base(self):
        return [
            (self.size - 3, self.size // 2),
            (self.size - 3, self.size // 2 - 1),
            (self.size - 3, self.size // 2 + 1),
            (self.size - 3, self.size // 2 - 2),
            (self.size - 3, self.size // 2 + 2),
            (self.size - 1, self.size // 2),
            (self.size - 2, self.size // 2),
            (self.size - 2, self.size // 2 - 1),
            (self.size - 2, self.size // 2 + 1),
            (self.size - 1, self.size // 2 + 1),
            (self.size - 1, self.size // 2 - 1)
        ]

    def get_enemies_base(self):
        return [
            # Central
            (0, self.size // 2),
            (1, self.size // 2),
            (1, self.size // 2 - 1),
            (1, self.size // 2 + 1),
            (0, self.size // 2 + 1),
            (0, self.size // 2 - 1),

            # Left
            (0, self.size // 2 - 5),
            (0, self.size // 2 - 6),
            (1, self.size // 2 - 5),
            (1, self.size // 2 - 6),
            (2, self.size // 2 - 5),
            (2, self.size // 2 - 4),

            # Right
            (0, self.size // 2 + 5),
            (0, self.size // 2 + 6),
            (1, self.size // 2 + 5),
            (1, self.size // 2 + 6),
            (2, self.size // 2 + 5),
            (2, self.size // 2 + 4),
        ]

    def _set_player_base(self, size):
        self.level[size - 3][size // 2] = CellState.Player
        self.level[size - 3][size // 2 - 1] = CellState.Empty
        self.level[size - 3][size // 2 + 1] = CellState.Empty
        self.level[size - 3][size // 2 + 2] = CellState.Empty
        self.level[size - 3][size // 2 - 2] = CellState.Empty
        self.level[size - 1][size // 2] = CellState.PlayerFlag
        self.level[size - 2][size // 2] = CellState.BrickWall
        self.level[size - 2][size // 2 - 1] = CellState.BrickWall
        self.level[size - 2][size // 2 + 1] = CellState.BrickWall
        self.level[size - 1][size // 2 + 1] = CellState.BrickWall
        self.level[size - 1][size // 2 - 1] = CellState.BrickWall

    def with_brick_walls(self, count):
        return self._with(count, CellState.BrickWall)

    def with_concrete_walls(self, count):
        return self._with(count, CellState.ConcreteWall)

    def with_patrolling_enemies(self, count):
        return self._with(count, CellState.PatrollingEnemy)

    def with_haunting_enemies(self, count):
        return self._with(count, CellState.HauntingEnemy)

    def with_terrains(self, count):
        return self._with(count, CellState.Terrain)

    def _with(self, count, game_obj):
        for _ in range(count):
            if game_obj in [CellState.HauntingEnemy,
                            CellState.PatrollingEnemy]:
                point = random.choice(self.enemies_base)
                self.enemies_base.remove(point)
            else:
                point = random.choice(self._free_cells)
                self._free_cells.remove(point)
            self.level[point[0]][point[1]] = game_obj
        return self

    def __iter__(self):
        return iter(self.level)
