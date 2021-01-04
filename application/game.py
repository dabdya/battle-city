from domain.infrastructure.geometry import Point, Direction
from application.level_generator import CellState
from domain.enemy import Enemy, EnemyType
from application.ai import EnemyAI
from domain.obstacle import Wall, WallType
from domain.terrain import Grass
from domain.player import Player
from domain.bullet import Bullet
from domain.map import Map
from domain.flag import Flag
from domain.boom import Boom, BoomType

from enum import Enum
import random


class GameStatus(Enum):
    End = 1
    NextLevel = 2
    Process = 3
    Win = 4


class Game:
    def __init__(self, size=13):
        self.size = size
        self.map = None
        self.level = None
        self.player = None
        self.status = None
        self.score = 0
        self.ai = EnemyAI(self)
        self.level_num = 1
        self.spawn_count_haunting = 0
        self.spawn_count_patrolling = 0

    def start(self, level):
        self.level = level
        self.map = Map(self.size)
        for y, line in enumerate(level):
            for x in range(len(line)):
                self._load_obj(line, x, y)
        self.spawn_count_haunting = 10 - len(self.map.get_enemies()) * 2
        self.spawn_count_patrolling = self.spawn_count_haunting // 2
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
                location, Direction.Up, 3)
            self.map[location].add(self.player)

        elif line[x] == CellState.Terrain:
            self.map[location].add(Grass(location))

        elif line[x] == CellState.PatrollingEnemy:
            self.map[location].add(
                Enemy(EnemyType.Patrolling,
                      location, Direction.Up, 1))

        elif line[x] == CellState.HauntingEnemy:
            self.map[location].add(
                Enemy(EnemyType.Haunting,
                      location, Direction.Up, 2))

        elif line[x] == CellState.PlayerFlag:
            self.map[location].add(Flag(location))

    def move_player(self, direction):
        new_location = self.player.get_new_location(direction)
        if self.map.check_coords(new_location):
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
                    if self.player.health > 1:
                        self.player.health -= 1
                        self.player.velocity = Point(0, 0)
                        return
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
                parent.bullets.remove(bullet)
                self.map[new_location].remove(wall)
                self.map[bullet.location].remove(bullet)
                self.map[new_location].add(
                    Boom(new_location, _type=BoomType.Wall))

            elif Enemy in cell_types:
                if isinstance(parent, Enemy):
                    parent.bullets.remove(bullet)
                    self.map[bullet.location].remove(bullet)
                    return
                enemy = self.get_obj_by_location_and_type(new_location, Enemy)
                parent.bullets.remove(bullet)

                unused_bullet = self.get_obj_by_location_and_type(new_location, Bullet)
                if unused_bullet:
                    self.map[new_location].remove(unused_bullet)

                self.map[bullet.location].remove(bullet)
                if enemy.health > 1:
                    enemy.health -= 1
                    return
                if isinstance(parent, Player):
                    self.score += 1
                self.map[new_location].remove(enemy)
                self.map[new_location].add(Boom(new_location))

            elif Player in cell_types:
                parent.bullets.remove(bullet)
                self.map[bullet.location].remove(bullet)
                if self.player.health > 1:
                    self.player.health -= 1
                    return
                self.map[new_location].remove(self.player)
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
                    # if bullet in bullet.parent.bullets:
                    bullet.parent.bullets.remove(bullet)
                    self.map[bullet.location].remove(bullet)
                    if enemy.health > 1:
                        enemy.health -= 1
                        enemy.velocity = Point(0, 0)
                        return
                    if isinstance(bullet.parent, Player):
                        self.score += 1
                    self.map[enemy.location].remove(enemy)
                    self.map[new_location].add(Boom(new_location))
            else:
                self.map.swap(enemy, new_location)
                enemy.move(direction)

    def spawn_enemy(self):
        for enemy in self.map.get_enemies():
            if enemy.type == EnemyType.SpawnPatrolling:
                enemy.type = EnemyType.Patrolling
            elif enemy.type == EnemyType.SpawnHaunting:
                enemy.type = EnemyType.Haunting

        available_locations = [
            Point(*reversed(x))
            for x in self.level.get_enemies_base()
            if len(self.map[Point(*reversed(x))]) == 0
        ]

        exist_count = len(self.map.get_enemies())

        if not available_locations or exist_count >= 3:
            return

        location = random.choice(available_locations)
        if random.randint(0, 1):
            if self.spawn_count_haunting > 0:
                self.spawn_count_haunting -= 1
                self.map[location].add(Enemy(
                    EnemyType.SpawnHaunting, location,
                    Direction.Down, 2))
        else:
            if self.spawn_count_patrolling > 0:
                self.spawn_count_patrolling -= 1
                self.map[location].add(Enemy(
                    EnemyType.SpawnPatrolling, location,
                    Direction.Down, 1))

    def shoot(self):
        if self.player.cheat == 0:
            bullet = self.player.shoot()
            if bullet:
                self.map[bullet.location].add(bullet)
                return True
        elif self.player.cheat == 1:
            bullets = self.player.cheat_shoot()
            if not bullets:
                return
            b1, b2 = bullets
            if b1 and b2:
                self.map[b1.location].add(b1)
                self.map[b2.location].add(b2)
                return True
        else:
            bullets = self.player.imba_shoot()
            if not bullets:
                return
            b1, b2, b3, b4 = bullets
            if b1 and b2 and b3 and b4:
                self.map[b1.location].add(b1)
                self.map[b2.location].add(b2)
                self.map[b3.location].add(b3)
                self.map[b4.location].add(b4)
                return True

    def get_obj_by_location_and_type(self, location, _type):
        for obj in self.map[location]:
            if type(obj) == _type:
                return obj

