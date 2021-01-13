from domain.infrastructure.geometry import Point, Direction
from application.level import CellState
from domain.enemy import Enemy, EnemyType
from application.ai import EnemyAI
from domain.obstacle import Wall, WallType
from domain.terrain import Grass
from domain.player import Player
from domain.bullet import Bullet
from domain.map import Map
from domain.flag import Flag
from domain.boom import Boom, BoomType
from domain.bonus import Bonus, BonusType

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
        self.bonus_count = 0
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
        if (not self.map.check_coords(new_location)
                or self.player.direction != direction):
            self.player.rotate(direction)
            self.player.velocity = Point(0, 0)
            return

        for obj in self.map[new_location]:
            if type(obj) in [Wall, Flag, Enemy]:
                self.player.rotate(direction)
                self.player.velocity = Point(0, 0)
                return

        bullet = self.map.get_obj_by_type(new_location, Bullet)
        bonus = self.map.get_obj_by_type(new_location, Bonus)
        if bullet:
            if isinstance(bullet.parent, Enemy):
                bullet.parent.bullets.remove(bullet)
                self.map[bullet.location].remove(bullet)
                if self.player.health > 1:
                    self.player.health -= 1
                    self.player.velocity = Point(0, 0)
                    return
                self.map[new_location].add(Boom(new_location))
                self.spawn_player()

            elif isinstance(bullet.parent, Player):
                self.map.swap(self.player, new_location)
                self.player.move(direction)
        elif bonus:
            self.player.apply_bonus(bonus)
            self.map[new_location].remove(bonus)
            self.map.swap(self.player, new_location)
            self.player.move(direction)
        else:
            self.map.swap(self.player, new_location)
            self.player.move(direction)

    def spawn_player(self):

        available_locations = [
            Point(*reversed(x))
            for x in self.level.get_player_base()
            if len(self.map[Point(*reversed(x))]) == 0
        ]

        if not available_locations:
            return

        location = random.choice(available_locations)
        self.map.swap(self.player, location)
        self.player.recover(location)

    def move_player_bullets(self):
        for bullet in self.player.bullets.copy():
            self._move_bullet(bullet, self.player)

    def move_enemy_bullets(self):
        for enemy in self.map.get_enemies():
            for bullet in enemy.bullets.copy():
                self._move_bullet(bullet, enemy)

    def _move_bullet(self, bullet, parent):
        location = bullet.get_new_location(bullet.direction)

        if not self.map.check_coords(location):
            if bullet in self.map[bullet.location]:
                self.map[bullet.location].remove(bullet)
            if bullet in parent.bullets:
                parent.bullets.remove(bullet)
            return

        if bullet.can_move(self.map[location]):
            self.map.swap(bullet, location)
            bullet.move(bullet.direction)
            return

        if bullet in self.map[bullet.location]:
            self.map[bullet.location].remove(bullet)
        if bullet in parent.bullets:
            parent.bullets.remove(bullet)

        for obj in self.map[location].copy():

            if isinstance(obj, Wall):
                if obj.destruct(bullet.bullet_type):
                    self._bullet_with_wall(obj, location)

            if isinstance(obj, Enemy):
                if not isinstance(parent, Enemy):
                    self._bullet_with_enemy(obj, location)

            if isinstance(obj, Player):
                if not isinstance(parent, Player):
                    self._bullet_with_player(self.player, location)

            if isinstance(obj, Flag):
                if not isinstance(parent, Player):
                    self._bullet_with_flag(obj, location)

            if isinstance(obj, Bullet) and obj != bullet:
                self._bullet_with_bullet(obj, location)

    def _bullet_with_wall(self, wall, location):
        boom = Boom(location, _type=BoomType.Wall)
        self.map[location].remove(wall)
        self.map[location].add(boom)

    def _bullet_with_enemy(self, enemy, location):
        if enemy.health > 1:
            enemy.health -= 1
        else:
            self.score += 1
            boom = Boom(location)
            if enemy in self.map[location]:
                self.map[location].remove(enemy)
            self.map[location].add(boom)

    def _bullet_with_player(self, player, location):
        if not player.invulnerability:
            if not player.armor:
                player.health -= 1
                if player.health == 0:
                    self.map[location].add(Boom(location))
                    self.spawn_player()
            else:
                player.armor = False

    def _bullet_with_flag(self, flag, location):
        boom = Boom(location, _type=BoomType.Wall)
        self.status = GameStatus.End
        self.map[location].remove(flag)
        self.map[location].add(boom)

    def _bullet_with_bullet(self, bullet, location):
        if bullet in bullet.parent.bullets:
            bullet.parent.bullets.remove(bullet)
        if bullet in self.map[location]:
            self.map[location].remove(bullet)

    def move_enemies(self):
        enemies = self.map.get_enemies()
        for enemy in enemies:
            direction = self.ai.calculate_direction(enemy)
            if not direction:
                enemy.velocity = Point(0, 0)
                continue
            new_location = enemy.get_new_location(direction)
            bullet = self.map.get_obj_by_type(new_location, Bullet)
            if bullet:
                if isinstance(bullet.parent, Enemy):
                    bullet.parent.bullets.remove(bullet)
                    self.map[bullet.location].remove(bullet)
                    enemy.directions.insert(0, direction)
                elif isinstance(bullet.parent, Player):
                    if bullet in bullet.parent.bullets:
                        bullet.parent.bullets.remove(bullet)
                    self.map[bullet.location].remove(bullet)
                    if enemy.health > 1:
                        enemy.health -= 1
                        return
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

    def add_bonus(self):
        available_cells = [
            location
            for location in self.map
            if len(self.map[location]) == 0
        ]

        location = random.choice(available_cells)
        _type = random.choice(list(BonusType))
        bonus = Bonus(location, _type)
        self.map[location].add(bonus)
