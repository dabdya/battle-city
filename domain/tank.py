from .infrastructure.geometry import Direction, Point
from .infrastructure.move_obj import IMoveObject
from .bullet import Bullet, BulletType
import datetime


class Tank(IMoveObject):
    def __init__(
            self, location, direction, speed, health, damage,
            shoot_delay=datetime.timedelta(milliseconds=600)):
        super().__init__(location, direction, speed)
        self.shoot_delay = shoot_delay
        self.last_shoot = None
        self.health = health
        self.damage = damage
        self.bullets = set()
        self.level = 1

    def get_bullet_type(self):
        if self.level == 1:
            return BulletType.Normal
        return BulletType.Concrete

    def up_level(self):
        self.level += 1

    def shoot(self):
        if not self.last_shoot or \
                datetime.datetime.now() - self.last_shoot > self.shoot_delay:
            location = Point(self.location.x, self.location.y)
            bullet_type = self.get_bullet_type()
            bullet = Bullet(location, self.direction, self.speed, self, bullet_type)
            self.bullets.add(bullet)
            self.last_shoot = datetime.datetime.now()
            return bullet
