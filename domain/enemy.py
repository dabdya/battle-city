from domain.tank import Tank
from enum import Enum


class EnemyType(Enum):
    Haunting = 1
    Patrolling = 2
    SpawnHaunting = 3
    SpawnPatrolling = 4


class Enemy(Tank):
    def __init__(self, _type, location, direction, health):
        super().__init__(location, direction, health)
        self.type = _type
        self.directions = list()
        self.shoot_count = 0
