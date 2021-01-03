from domain.infrastructure.geometry import Direction, Point
from domain.player import Player
from domain.obstacle import Wall
from domain.enemy import Enemy, EnemyType
from domain.flag import Flag
from random import randint


class EnemyAI:
    def __init__(self, game):
        self.game = game

    @staticmethod
    def _rotate_dx(enemy, dx):
        if dx < 0:
            enemy.rotate(Direction.Right)
        elif dx > 0:
            enemy.rotate(Direction.Left)

    @staticmethod
    def _rotate_dy(enemy, dy):
        if dy < 0:
            enemy.rotate(Direction.Down)
        elif dy > 0:
            enemy.rotate(Direction.Up)

    @staticmethod
    def _generate_direction(direction):
        directions = [
            Direction.Up,
            Direction.Down,
            Direction.Left,
            Direction.Right
        ]
        directions.remove(direction)
        index = randint(0, 2)
        return directions[index]

    @staticmethod
    def can_move(next_objs):
        for next_obj in next_objs:
            if type(next_obj) in [Wall, Player, Enemy, Flag]:
                return False
        return True

    def dfs(self, enemy, start, directions, visited):
        if Player in self.game.map.cell_types(start):
            directions.pop()
            return directions

        visited.add(start)
        for nxt in start.neighbors():
            location = nxt[0]
            direction = nxt[1]

            if location in visited or \
                    not self.game.map.check_coords(location):
                continue
            if Wall in self.game.map.cell_types(location):
                continue
                # wall = self.game.get_obj_by_location_and_type(location, Wall)
                # bullet_type = enemy.get_bullet_type()
                # if not wall.destruct(bullet_type):
                #     continue
                # else:
                #     pass

            directions.append(direction)
            res = self.dfs(enemy, location, directions, visited)
            if res:
                return directions
            else:
                if len(directions) != 0:
                    directions.pop()

    def _shoot_if_detect(self, enemy):
        enemy.shoot_count += 1
        if enemy.shoot_count < 5:
            bullet = enemy.shoot()
            if bullet:
                self.game.map[bullet.location].add(bullet)
                enemy.velocity = Point(0, 0)
            return True

    def _next_direction(self, enemy):
        for nxt in enemy.directions:
            enemy.directions.remove(nxt)
            new_location = enemy.get_new_location(nxt)
            if self.game.map.check_coords(new_location) and \
                    self.can_move(self.game.map[new_location]):
                enemy.shoot_count = 0
                return nxt
            else:
                enemy.rotate(nxt)
                return

    def _flag_enemy(self, enemy):
        pass

    def _haunting_enemy(self, enemy):
        dx = enemy.location.x - self.game.player.location.x
        dy = enemy.location.y - self.game.player.location.y

        was_shoot = False
        if dx == 0:
            EnemyAI._rotate_dy(enemy, dy)
            was_shoot = self._shoot_if_detect(enemy)
        elif dy == 0:
            EnemyAI._rotate_dx(enemy, dx)
            was_shoot = self._shoot_if_detect(enemy)
        if was_shoot:
            return

        if len(enemy.directions) != 0:
            nxt = self._next_direction(enemy)
            if nxt:
                return nxt
            else:
                self._shoot_if_detect(enemy)
        else:
            enemy.directions = list()

        directions = self.dfs(enemy, enemy.location, [], set())
        if directions:
            enemy.directions = directions
            nxt = self._next_direction(enemy)
            if nxt:
                return nxt
            else:
                self._shoot_if_detect(enemy)

    def _patrolling_enemy(self, enemy):
        enemy.shoot_count += 1
        if enemy.shoot_count % 6 == 0:
            enemy.shoot_count = 0
            if randint(0, 1):
                new_direction = self._generate_direction(enemy.direction)
                enemy.rotate(new_direction)
                bullet = enemy.shoot()
                if bullet:
                    self.game.map[bullet.location].add(bullet)
                    enemy.velocity = Point(0, 0)
                return

        new_location = enemy.get_new_location(enemy.direction)
        if self.game.map.check_coords(new_location) and \
                self.can_move(self.game.map[new_location]):
            return enemy.direction
        else:
            direction = self._generate_direction(enemy.direction)
            new_location = enemy.get_new_location(direction)
            if self.game.map.check_coords(new_location) and \
                    self.can_move(self.game.map[new_location]):
                enemy.rotate(direction)
                return direction

    def calculate_direction(self, enemy):
        direction = None
        if enemy.type == EnemyType.Patrolling:
            direction = self._patrolling_enemy(enemy)
        elif enemy.type == EnemyType.Haunting:
            direction = self._haunting_enemy(enemy)
        return direction
