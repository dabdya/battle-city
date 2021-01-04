from .infrastructure.geometry import Direction, Point
from .infrastructure.move_obj import IMoveObject
from .bullet import Bullet, BulletType
import datetime


class Tank(IMoveObject):
    def __init__(self, location, direction, health,
                 shoot_delay=datetime.timedelta(milliseconds=600)):
        super().__init__(location, direction)
        self.shoot_delay = shoot_delay
        self.last_shoot = None
        self.health = health
        self.bullets = set()
        self.level = 1

    def get_bullet_type(self):
        if self.level == 1:
            return BulletType.Normal
        return BulletType.Concrete

    def up_level(self):
        self.level += 1

    def _shoot(self, direction):
        location = Point(self.location.x, self.location.y)
        bullet_type = self.get_bullet_type()
        bullet = Bullet(location, direction, self, bullet_type)
        self.bullets.add(bullet)
        self.last_shoot = datetime.datetime.now()
        return bullet

    def shoot(self):
        if not self.last_shoot or \
                datetime.datetime.now() - self.last_shoot > self.shoot_delay:
            return self._shoot(self.direction)

    def cheat_shoot(self):
        if not self.last_shoot or \
                datetime.datetime.now() - self.last_shoot > self.shoot_delay:
            return self._shoot(self.direction), \
                   self._shoot(self.opposite_direction())

    def imba_shoot(self):
        if not self.last_shoot or \
                datetime.datetime.now() - self.last_shoot > self.shoot_delay:
            return self._shoot(Direction.Up), \
                   self._shoot(Direction.Down), \
                   self._shoot(Direction.Left), \
                   self._shoot(Direction.Right)
