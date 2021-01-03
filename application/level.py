from application.cell_state import CellState
import random


class Level:
    def __init__(self, size, seed):
        self.size = size
        random.seed(seed)

        self.level = [
            [CellState.Empty] * size
            for _ in range(size)
        ]

        self._free_cells = [
            (x, y)
            for x in range(self.size)
            for y in range(self.size)
            if (x, y) != (size - 3, size // 2)
            if (x, y) != (size - 1, size // 2)
            if (x, y) != (size - 2, size // 2)
            if (x, y) != (size - 2, size // 2 - 1)
            if (x, y) != (size - 2, size // 2 + 1)
            if (x, y) != (size - 1, size // 2 + 1)
            if (x, y) != (size - 1, size // 2 - 1)
        ]

        self.level[size - 3][size // 2] = CellState.Player
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
            free_count = len(self._free_cells)
            if game_obj in [CellState.HauntingEnemy,
                            CellState.PatrollingEnemy]:
                point = random.choice(
                    self._free_cells[:free_count // 4])
            else:
                point = random.choice(self._free_cells)
            self.level[point[0]][point[1]] = game_obj
            self._free_cells.remove(point)
        return self

    def __iter__(self):
        return iter(self.level)
