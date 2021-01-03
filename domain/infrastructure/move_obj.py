from domain.infrastructure.geometry import Direction, Point
import abc


class IMoveObject(abc.ABC):
    def __init__(self, location, direction, speed):
        self.location = location
        self.direction = direction
        self.speed = speed
        self.velocity = Point(0, 0)

    def move(self, direction):
        if self.direction != direction:
            self.rotate(direction)
        new_location = self.get_new_location(direction)
        old_location = self.location
        self.location = new_location
        self.velocity = self.get_velocity(old_location)

    def rotate(self, direction: Direction):
        self.direction = direction

    def get_new_location(self, direction):
        dx_moves = {
            Direction.Left: -self.speed,
            Direction.Right: self.speed
        }

        dy_moves = {
            Direction.Up: -self.speed,
            Direction.Down: self.speed
        }

        x = self.location.x + dx_moves.get(direction, 0)
        y = self.location.y + dy_moves.get(direction, 0)
        return Point(x, y)

    def get_velocity(self, old_location):
        x = self.location.x - old_location.x
        y = self.location.y - old_location.y
        return Point(x, y)
