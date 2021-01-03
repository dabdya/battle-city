from domain.tank import Tank
from enum import Enum


class EnemyType(Enum):
    Haunting = 1
    Patrolling = 2


class Enemy(Tank):
    def __init__(self, _type, location, direction, speed, health, damage):
        super().__init__(location, direction, speed, health, damage)
        self.type = _type
        self.directions = list()
        self.shoot_count = 0
