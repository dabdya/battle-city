from .infrastructure.geometry import Direction, Point
from .infrastructure.move_obj import IMoveObject
from .bullet import Bullet
import datetime


class Tank(IMoveObject):
    def __init__(
            self, location, direction, speed, health, damage,
            shoot_delay=datetime.timedelta(milliseconds=500)):
        super().__init__(location, direction, speed)
        self.shoot_delay = shoot_delay
        self.last_shoot = None
        self.health = health
        self.damage = damage
        self.bullets = set()

    def shoot(self):
        if not self.last_shoot \
                or datetime.datetime.now() - self.last_shoot > self.shoot_delay:
            location = Point(self.location.x, self.location.y)
            bullet = Bullet(location, self.direction, self.speed)
            self.bullets.add(bullet)
            self.last_shoot = datetime.datetime.now()
