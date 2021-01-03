from enum import Enum


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
    SpawnPlace = 9
