from domain.enemy import Enemy
from .infrastructure.geometry import Point


class Map:
    def __init__(self, size):
        self.size = size
        self._map = {
            Point(x, y): set()
            for x in range(size)
            for y in range(size)
        }

    def __getitem__(self, key):
        return self._map[key]

    def __iter__(self):
        return iter(self._map)

    def get_enemies(self):
        enemies = list()
        for location in self._map.values():
            for obj in location:
                if isinstance(obj, Enemy):
                    enemies.append(obj)
        return enemies

    def cell_types(self, location):
        _types = {
            type(x)
            for x in self._map[location]
        }
        return _types

    def swap(self, obj, location):
        if obj in self._map[obj.location]:
            self._map[obj.location].remove(obj)
        self._map[location].add(obj)

    def check_coords(self, coords):
        try:
            self._map[coords]
        except KeyError:
            return False
        return True
