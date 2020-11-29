from .infrastructure.move_obj import IMoveObject


class Bullet(IMoveObject):
    def __init__(self, location, direction, speed):
        super().__init__(location, direction, speed)
