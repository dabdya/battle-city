from domain.tank import Tank


class Player(Tank):
    def __init__(self, location, direction, health):
        super().__init__(location, direction, health)
        self.cheat = 0
