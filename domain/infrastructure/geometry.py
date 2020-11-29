from enum import Enum


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __hash__(self):
        return self.x * 173 + self.y * 9397

    def __eq__(self, other):
        if not isinstance(other, Point):
            raise TypeError
        return self.x == other.x and self.y == other.y


class Direction(Enum):
    Up = 1,
    Down = 2,
    Left = 3,
    Right = 4
