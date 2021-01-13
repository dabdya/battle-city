from domain.tank import Tank
from domain.bonus import BonusType
from domain.infrastructure.geometry import Direction
import datetime


class Player(Tank):
    def __init__(self, location, direction, health):
        super().__init__(location, direction, health)
        self.cheat = 0
        self.invulnerability = None
        self.speed_runner = None
        self.fast_shooting = None
        self.armor = False

    def apply_bonus(self, bonus):
        if bonus.type == BonusType.Heart:
            if self.health < 3:
                self.health += 1
        elif bonus.type == BonusType.Invulnerability:
            if not self.armor:
                self.invulnerability = datetime.datetime.now()
        elif bonus.type == BonusType.Armor:
            if not self.invulnerability:
                self.armor = True
        elif bonus.type == BonusType.SpeedRunner:
            self.speed_runner = datetime.datetime.now()
        elif bonus.type == BonusType.FastShooting:
            self.fast_shooting = datetime.datetime.now()

    def recover(self, location):
        self.health = 3
        self.location = location
        self.direction = Direction.Up
