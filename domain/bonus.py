from enum import Enum


class BonusType(Enum):
    Heart = 1
    Armor = 2
    Invulnerability = 3
    FastShooting = 4
    SpeedRunner = 5


class Bonus:
    def __init__(self, location, _type, exists=20):
        self.location = location
        self.type = _type
        self.exists = exists
