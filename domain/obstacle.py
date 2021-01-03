from domain.bullet import BulletType
from enum import Enum


class WallType(Enum):
    Brick = 1,
    Concrete = 2


class Wall:
    def __init__(self, location, wall_type):
        self.location = location
        self.wall_type = wall_type

    def destruct(self, bullet_type):
        if bullet_type == BulletType.Normal:
            return self.wall_type == WallType.Brick
        elif bullet_type == BulletType.Concrete:
            available = [WallType.Concrete, WallType.Brick]
            return self.wall_type in available
