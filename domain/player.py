from domain.tank import Tank


class Player(Tank):
    def __init__(self, location, direction, speed, health, damage):
        super().__init__(location, direction, speed, health, damage)
