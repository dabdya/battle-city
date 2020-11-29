from domain.enemy import Enemy
from .infrastructure.geometry import Point, Direction


class Map:
    def __init__(self, size=13):
        self.size = size
        self._map = dict()

    def __setitem__(self, key, value):
        self._map[key] = value

    def __getitem__(self, key):
        return self._map[key]

    def __delitem__(self, key):
        del self._map[key]

    def __iter__(self):
        return iter(self._map)

    def get_enemies(self):
        for location in self._map:
            if isinstance(self._map[location], Enemy):
                yield self._map[location]

    def swap(self, v1, v2):
        self._map[v1], self._map[v2] \
            = self._map[v2], self._map[v1]

    def get_neighbors(self, location):
        neighbor = Point(location.x, location.y - 1)
        if self.check_coords(neighbor):
            yield Direction.Up, self._map[neighbor]

        neighbor = Point(location.x, location.y + 1)
        if self.check_coords(neighbor):
            yield Direction.Down, self._map[neighbor]

        neighbor = Point(location.x - 1, location.y)
        if self.check_coords(neighbor):
            yield Direction.Left, self._map[neighbor]

        neighbor = Point(location.x + 1, location.y)
        if self.check_coords(neighbor):
            yield Direction.Right, self._map[neighbor]

    def check_coords(self, coords):
        try:
            self._map[coords]
        except KeyError:
            return False
        return True
