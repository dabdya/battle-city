from domain.obstacle import Wall
from domain.enemy import Enemy
from domain.player import Player
from random import randint


class EnemyAI:
    def __init__(self, game):
        self.game = game

    def calculate_direction(self, target_obj, enemy):
        if enemy.last_move:
            enemy.last_move = None

        adj = list(self.game.map.get_neighbors(enemy.location))
        for way in range(len(adj)):
            index = randint(0, len(adj) - 1)
            if self.can_move(adj[index][1]):
                enemy.last_move = adj[index][0]
                return enemy.last_move

    def can_move(self, next_obj):
        if not next_obj:
            return True
        return self.game.map.check_coords(next_obj.location) \
               and not isinstance(next_obj, Wall) \
               and not isinstance(next_obj, Player) \
               and not isinstance(next_obj, Enemy)
