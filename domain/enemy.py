from domain.tank import Tank


class Enemy(Tank):
    def __init__(self, location, direction, speed, health, damage):
        super().__init__(location, direction, speed, health, damage)
        self.last_move = None
