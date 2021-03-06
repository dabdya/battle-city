from .infrastructure.move_obj import IMoveObject
from domain.terrain import Grass
from domain.bonus import Bonus
from enum import Enum


class BulletType(Enum):
    Normal = 1,
    Concrete = 2


class Bullet(IMoveObject):
    def __init__(self, location, direction, parent, bullet_type):
        super().__init__(location, direction)
        self.bullet_type = bullet_type
        self.parent = parent

    def can_move(self, cell):
        if len(cell) == 0:
            return True
        elif len(cell) > 1:
            return False
        obj = cell.pop()
        cell.add(obj)
        return type(obj) in [Grass, Bonus]
