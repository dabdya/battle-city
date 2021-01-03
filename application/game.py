from domain.infrastructure.geometry import Point, Direction
from domain.enemy import Enemy, EnemyType
from application.cell_state import CellState
from application.ai import EnemyAI
from domain.obstacle import Wall, WallType
from domain.terrain import Grass
from domain.player import Player
from domain.bullet import Bullet
from domain.map import Map
from domain.flag import Flag
from domain.boom import Boom

from enum import Enum


class GameStatus(Enum):
    End = 1
    NextLevel = 2
    Process = 3
    Win = 4


class Game:
    def __init__(self, size=13):
        self.size = size
        self.map = None
        self.player = None
        self.status = None
        self.score = 0
        self.ai = EnemyAI(self)
        self.level_num = 1

    def start(self, level):
        self.map = Map(self.size)
        for y, line in enumerate(level):
            for x in range(len(line)):
                self._load_obj(line, x, y)
        if self.player:
            self.status = GameStatus.Process
            return self

    def _load_obj(self, line, x, y):
        location = Point(x, y)
        if line[x] == CellState.BrickWall:
            self.map[location].add(
                Wall(location, WallType.Brick))

        elif line[x] == CellState.ConcreteWall:
            self.map[location].add(
                Wall(location, WallType.Concrete))

        elif line[x] == CellState.Player:
            self.player = Player(
                location, Direction.Up, 1, 100, 1)
            self.map[location].add(self.player)

        elif line[x] == CellState.Terrain:
            self.map[location].add(Grass(location))

        elif line[x] == CellState.PatrollingEnemy:
            self.map[location].add(
                Enemy(EnemyType.Patrolling,
                      location, Direction.Up, 1, 100, 1))

        elif line[x] == CellState.HauntingEnemy:
            self.map[location].add(
                Enemy(EnemyType.Haunting,
                      location, Direction.Up, 1, 100, 1))

        elif line[x] == CellState.PlayerFlag:
            self.map[location].add(Flag(location))

    def move_player(self, direction):
        new_location = self.player.get_new_location(direction)
        if self.map.check_coords(new_location):
            # Можно переписать can_move
            for obj in self.map[new_location]:
                if type(obj) in [Wall, Flag, Enemy]:
                    self.player.rotate(direction)
                    self.player.velocity = Point(0, 0)
                    return
            bullet = self.get_obj_by_location_and_type(new_location, Bullet)
            if bullet:
                if isinstance(bullet.parent, Enemy):
                    bullet.parent.bullets.remove(bullet)
                    self.map[bullet.location].remove(bullet)
                    self.map[self.player.location].clear()
                    self.map[new_location].add(Boom(new_location))
                    self.status = GameStatus.End
                elif isinstance(bullet.parent, Player):
                    self.map.swap(self.player, new_location)
                    self.player.move(direction)
            else:
                self.map.swap(self.player, new_location)
                self.player.move(direction)
        else:
            self.player.rotate(direction)
            self.player.velocity = Point(0, 0)

    def move_bullets(self):
        for bullet in self.player.bullets.copy():
            self._move_bullet(bullet, self.player)

        for enemy in self.map.get_enemies():
            for bullet in enemy.bullets.copy():
                self._move_bullet(bullet, enemy)

    def _move_bullet(self, bullet, parent):
        new_location = bullet.get_new_location(bullet.direction)
        if self.map.check_coords(new_location):

            cell_types = {type(x) for x in self.map[new_location]}

            if bullet.can_move(self.map[new_location]):
                self.map.swap(bullet, new_location)
                bullet.move(bullet.direction)

            elif Wall in cell_types:
                wall = self.get_obj_by_location_and_type(new_location, Wall)
                if not wall.destruct(bullet.bullet_type):
                    parent.bullets.remove(bullet)
                    self.map[bullet.location].remove(bullet)
                    return
                if isinstance(parent, Player):
                    self.score += 0.5
                parent.bullets.remove(bullet)
                self.map[new_location].clear()
                self.map[bullet.location].remove(bullet)

            elif Enemy in cell_types:
                if isinstance(parent, Enemy):
                    parent.bullets.remove(bullet)
                    self.map[bullet.location].remove(bullet)
                    return
                if isinstance(parent, Player):
                    self.score += 1
                parent.bullets.remove(bullet)
                enemy = self.get_obj_by_location_and_type(new_location, Enemy)
                self.map[new_location].remove(enemy)
                unused_bullet = self.get_obj_by_location_and_type(new_location, Bullet)
                if unused_bullet:
                    self.map[new_location].remove(unused_bullet)
                self.map[bullet.location].remove(bullet)
                self.map[new_location].add(Boom(new_location))

            elif Player in cell_types:
                parent.bullets.remove(bullet)
                self.map[new_location].remove(self.player)
                self.map[bullet.location].remove(bullet)
                self.map[new_location].add(Boom(new_location))
                self.status = GameStatus.End

            elif Flag in cell_types:
                parent.bullets.remove(bullet)
                if isinstance(parent, Player):
                    return
                self.map[new_location].clear()
                self.map[bullet.location].remove(bullet)
                self.status = GameStatus.End

            elif Bullet in cell_types:
                parent.bullets.remove(bullet)
                vs = self.get_obj_by_location_and_type(new_location, Bullet)
                if vs in vs.parent.bullets:
                    vs.parent.bullets.remove(vs)
                self.map[new_location].remove(vs)
                self.map[bullet.location].remove(bullet)
        else:
            parent.bullets.remove(bullet)
            self.map[bullet.location].remove(bullet)

    def move_enemies(self):
        enemies = self.map.get_enemies()
        for enemy in enemies:
            direction = self.ai.calculate_direction(enemy)
            if not direction:
                enemy.velocity = Point(0, 0)
                continue
            new_location = enemy.get_new_location(direction)
            bullet = self.get_obj_by_location_and_type(new_location, Bullet)
            if bullet:
                if isinstance(bullet.parent, Enemy):
                    bullet.parent.bullets.remove(bullet)
                    self.map[bullet.location].remove(bullet)
                    enemy.directions.insert(0, direction)
                elif isinstance(bullet.parent, Player):
                    bullet.parent.bullets.remove(bullet)
                    self.map[bullet.location].remove(bullet)
                    self.map[enemy.location].remove(enemy)
                    self.map[new_location].add(Boom(new_location))
            else:
                self.map.swap(enemy, new_location)
                enemy.move(direction)

    def shoot(self):
        bullet = self.player.shoot()
        if bullet:
            self.map[bullet.location].add(bullet)

    def get_obj_by_location_and_type(self, location, _type):
        for obj in self.map[location]:
            if type(obj) == _type:
                return obj

