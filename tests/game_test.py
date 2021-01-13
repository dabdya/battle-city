import unittest
import datetime
from application.game import Game, GameStatus
from application.level import Level
from application.level import CellState as cs
from domain.infrastructure.geometry import Point, Direction
from domain.bullet import Bullet, BulletType
from domain.bonus import Bonus, BonusType
from domain.enemy import Enemy

from unittest.mock import Mock


class GameTests(unittest.TestCase):
    def test_player_movement_on_empty_map_with_terrain(self):
        game = Game(size=3).start([
                [cs.Empty, cs.Empty, cs.Empty],
                [cs.Empty, cs.Player, cs.Empty],
                [cs.Empty, cs.Terrain, cs.Empty]
            ])

        game.move_player(Direction.Up)
        self.assertEqual(Point(1, 0), game.player.location)
        self.assertTrue(len(game.map[Point(1, 1)]) == 0)
        self.assertTrue(len(game.map[Point(1, 0)]) == 1)

        game.player.rotate(Direction.Left)
        game.move_player(Direction.Left)
        self.assertEqual(Point(0, 0), game.player.location)

        game.player.rotate(Direction.Down)
        game.move_player(Direction.Down)
        self.assertEqual(Point(0, 1), game.player.location)

        game.player.rotate(Direction.Right)
        game.move_player(Direction.Right)
        self.assertEqual(Point(1, 1), game.player.location)

    def test_player_not_move_if_wall_next(self):
        game = Game(size=3).start([
            [cs.Empty, cs.BrickWall, cs.Empty],
            [cs.Empty, cs.Player, cs.Empty],
            [cs.Empty, cs.ConcreteWall, cs.Empty]
        ])

        game.move_player(Direction.Up)
        self.assertNotEqual(Point(1, 0), game.player.location)
        self.assertEqual(Point(1, 1), game.player.location)

        game.move_player(Direction.Down)
        self.assertNotEqual(Point(1, 2), game.player.location)
        self.assertEqual(Point(1, 1), game.player.location)

    def test_enemy_not_spawn_if_maximum_reached(self):
        game = Game()
        level = Level(game.size, 10) \
            .with_brick_walls(game.size * 2) \
            .with_concrete_walls(game.size) \
            .with_terrains(game.size // 2) \
            .with_patrolling_enemies(1) \
            .with_haunting_enemies(2)
        game.start(level)

        self.assertEqual(len(game.map.get_enemies()), 3)
        game.spawn_enemy()
        self.assertEqual(len(game.map.get_enemies()), 3)

    def test_enemy_spawn_if_possible(self):
        game = Game()
        level = Level(game.size, 10) \
            .with_brick_walls(game.size * 2) \
            .with_concrete_walls(game.size) \
            .with_terrains(game.size // 2) \
            .with_patrolling_enemies(1) \
            .with_haunting_enemies(1)
        game.start(level)

        self.assertEqual(len(game.map.get_enemies()), 2)
        game.spawn_enemy()
        self.assertEqual(len(game.map.get_enemies()), 3)

    def test_kill_enemies(self):
        game = Game(size=3).start([
            [cs.Empty, cs.PatrollingEnemy, cs.Empty],
            [cs.HauntingEnemy, cs.Player, cs.Empty],
            [cs.Empty, cs.PatrollingEnemy, cs.Empty]
        ])

        game.player.shoot_delay = datetime.timedelta(milliseconds=-1)
        game.player.direction = Direction.Up
        self.assertTrue(len(game.map.get_enemies()) == 3)
        self.assertTrue(game.shoot())
        game.move_player_bullets()
        self.assertTrue(len(game.map.get_enemies()) == 2)

        game.player.direction = Direction.Down
        self.assertTrue(game.shoot())
        game.move_player_bullets()
        self.assertTrue(len(game.map.get_enemies()) == 1)

        game.player.direction = Direction.Left
        self.assertTrue(game.shoot())
        self.assertTrue(game.shoot())
        game.move_player_bullets()
        self.assertTrue(len(game.map.get_enemies()) == 0)

    def test_move_enemies(self):
        game = Game(size=3).start([
            [cs.Empty, cs.PatrollingEnemy, cs.Empty],
            [cs.HauntingEnemy, cs.Player, cs.Empty],
            [cs.Empty, cs.Empty, cs.Empty]
        ])

        haunting_enemy = game.map.get_obj_by_type(Point(0, 1), Enemy)
        haunting_direction = game.ai.calculate_direction(haunting_enemy)

        patrolling_enemy = game.map.get_obj_by_type(Point(1, 0), Enemy)
        patrolling_direction = game.ai.calculate_direction(patrolling_enemy)

        game.move_enemies()

        if haunting_direction:
            self.assertNotEqual(Point(0, 1), haunting_enemy.location)
        if patrolling_direction:
            self.assertNotEqual(Point(1, 0), patrolling_enemy.location)

    def test_enemies_kill_player_if_exists_tunnel(self):
        mock = Mock()
        mock.get_player_base = Mock(return_value=[(2, 1)])
        mock.__iter__ = Mock(return_value=iter([
            [cs.Empty, cs.Empty, cs.Empty],
            [cs.HauntingEnemy, cs.Empty, cs.Player],
            [cs.Empty, cs.Empty, cs.Empty]]))

        game = Game(size=3).start(mock)

        haunting_enemy = game.map.get_obj_by_type(Point(0, 1), Enemy)
        haunting_enemy.direction = Direction.Right

        for i in range(2, 0, -1):
            game.move_enemies()
            game.move_enemy_bullets()
            game.move_enemy_bullets()
            self.assertTrue(game.player.health == i)
            haunting_enemy.shoot_delay = datetime.timedelta(milliseconds=-1)
            haunting_enemy.shoot_count = 0

        game.move_enemies()
        game.move_enemy_bullets()
        game.move_enemy_bullets()
        self.assertTrue(game.player.health == 3)
        self.assertTrue(game.status != GameStatus.End)

    def test_player_invulnerability_for_self_bullets(self):
        game = Game(size=3).start([
            [cs.Empty, cs.PatrollingEnemy, cs.Empty],
            [cs.Bullet, cs.Player, cs.Empty],
            [cs.Empty, cs.Empty, cs.Empty]
        ])

        bullet = Bullet(Point(0, 1), Direction.Right,
                        game.player, BulletType.Normal)
        game.map[bullet.location].add(bullet)

        game.player.bullets.add(bullet)
        game.move_player_bullets()
        self.assertTrue(game.player.health == 3)
        self.assertTrue(bullet not in game.map[bullet.location])

    def test_enemy_invulnerability_for_self_bullets(self):
        game = Game(size=3).start([
            [cs.Empty, cs.Empty, cs.Player],
            [cs.Bullet, cs.HauntingEnemy, cs.Empty],
            [cs.Empty, cs.Empty, cs.Empty]
        ])

        enemy = game.map.get_obj_by_type(Point(1, 1), Enemy)
        bullet = Bullet(Point(0, 1), Direction.Right,
                        enemy, BulletType.Normal)
        game.map[bullet.location].add(bullet)

        enemy.bullets.add(bullet)
        game.move_enemy_bullets()
        self.assertTrue(enemy.health == 2)
        self.assertTrue(bullet not in game.map[bullet.location])

    def test_player_apply_bonus(self):
        game = Game(size=3).start([
            [cs.Empty, cs.Bonus, cs.Player],
            [cs.Empty, cs.Empty, cs.Empty],
            [cs.Empty, cs.Empty, cs.Empty]
        ])

        bonus = Bonus(Point(1, 0), BonusType.Invulnerability)
        game.map[bonus.location].add(bonus)
        game.player.rotate(Direction.Left)
        game.move_player(Direction.Left)
        self.assertTrue(game.player.invulnerability)

    def test_player_respawn_when_not_health(self):
        mock = Mock()
        mock.get_player_base = Mock(return_value=[(2, 2)])
        mock.__iter__ = Mock(return_value=iter([
            [cs.Empty, cs.Empty, cs.Empty],
            [cs.HauntingEnemy, cs.Bullet, cs.Player],
            [cs.Empty, cs.Empty, cs.Empty]]))

        game = Game(size=3).start(mock)
        enemy = game.map.get_obj_by_type(Point(0, 1), Enemy)
        bullet = Bullet(Point(1, 1), Direction.Right,
                        enemy, BulletType.Normal)
        enemy.bullets.add(bullet)
        game.map[bullet.location].add(bullet)
        game.player.health = 1
        game.move_enemy_bullets()
        self.assertTrue(game.player.health == 3)
        self.assertTrue(game.player.location == Point(2, 2))

    def test_game_end_if_and_only_if_when_flag_not_exists(self):
        mock = Mock()
        mock.get_player_base = Mock(return_value=[(0, 0)])
        mock.__iter__ = Mock(return_value=iter([
            [cs.Empty, cs.Empty, cs.Player],
            [cs.Empty, cs.Empty, cs.HauntingEnemy],
            [cs.HauntingEnemy, cs.Empty, cs.PlayerFlag]]))

        game = Game(size=3).start(mock)

        h_enemy = game.map.get_obj_by_type(Point(0, 2), Enemy)
        bullet = Bullet(Point(0, 2), Direction.Right,
                        h_enemy, BulletType.Normal)
        game.map[bullet.location].add(bullet)
        h_enemy.bullets.add(bullet)

        game.player.health = 1
        p_enemy = game.map.get_obj_by_type(Point(2, 1), Enemy)
        p_enemy.rotate(Direction.Up)
        game.move_enemies()
        game.move_enemy_bullets()
        self.assertTrue(game.player.health == 3)
        self.assertTrue(game.status == GameStatus.Process)
        game.move_enemy_bullets()
        self.assertTrue(game.status == GameStatus.End)
