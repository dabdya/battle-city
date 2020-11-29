from domain.infrastructure.geometry import Point, Direction
from application.level import Level, PointState
from application.ai import EnemyAI
from domain.obstacle import Wall
from domain.terrain import Grass
from domain.player import Player
from domain.enemy import Enemy
from domain.map import Map


class Game:
    def __init__(self, size=13):
        self.size = size
        self.map = Map(size)
        self.player = None
        self.ai = EnemyAI(self)
        self.num_level = 1

    def start(self):
        level = Level(self.size) \
            .with_obstacles(self.size) \
            .with_terrains(self.size) \
            .with_enemies(1) \
            .with_player()
        self.load_level(level)
        return self

    def load_level(self, level):
        for y, line in enumerate(level):
            for x in range(len(line)):
                location = Point(x, y)
                if line[x] == PointState.Obstacle:
                    self.map[location] = Wall(location, 100)
                elif line[x] == PointState.Player:
                    self.player = Player(
                        location, Direction.Up, 1, 100, 1)
                    self.map[location] = self.player
                elif line[x] == PointState.Empty:
                    self.map[location] = None
                elif line[x] == PointState.Terrain:
                    self.map[location] = Grass(location)
                elif line[x] == PointState.Enemy:
                    enemy = Enemy(location, Direction.Up, 1, 100, 1)
                    self.map[location] = enemy

    def move_player(self, direction):
        new_location = self.player.get_new_location(direction)
        if self.map.check_coords(new_location) \
                and not isinstance(self.map[new_location], Wall):
            old_location = self.player.location
            self.player.move(direction)
            self.map.swap(new_location, old_location)

    def move_bullets(self):
        for bullet in self.player.bullets.copy():
            new_location = bullet.get_new_location(bullet.direction)
            if self.map.check_coords(new_location):
                if not self.map[new_location] \
                        or isinstance(self.map[new_location], Grass):
                    bullet.move(bullet.direction)
                elif isinstance(self.map[new_location], Wall):
                    del self.map[new_location]
                    self.player.bullets.remove(bullet)
                    self.map[new_location] = None
                elif isinstance(self.map[new_location], Enemy):
                    del self.map[new_location]
                    self.player.bullets.remove(bullet)
                    self.map[new_location] = None
            else:
                self.player.bullets.remove(bullet)

    def move_enemies(self):
        for enemy in self.map.get_enemies():
            direction = self.ai.calculate_direction(self.player, enemy)
            if not direction:
                return
            new_location = enemy.get_new_location(direction)
            old_location = enemy.location
            enemy.move(direction)
            self.map.swap(old_location, new_location)

    def shoot(self):
        self.player.shoot()
