from enum import Enum


class BoomType(Enum):
    Small = 1
    Big = 2
    Wall = 3


class Boom:
    def __init__(self, location, _type=BoomType.Small):
        self.location = location
        self.type = _type
