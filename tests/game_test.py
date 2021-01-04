import unittest
from application.game import Game
from application.level_generator import Level
from application.level_generator import CellState as cs
from domain.infrastructure.geometry import Point, Direction


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(size=3)

    def test_player_movement_on_empty_map(self):
        self.game = self.game.start([
                [cs.Empty, cs.Empty, cs.Empty],
                [cs.Empty, cs.Player, cs.Empty],
                [cs.Empty, cs.Empty, cs.Empty]
            ])

        self.game.move_player(Direction.Up)
        self.assertEqual(Point(1, 0), self.game.player.location)
        self.assertTrue(len(self.game.map[Point(1, 1)]) == 0)
        self.assertTrue(len(self.game.map[Point(1, 0)]) == 1)

        self.game.move_player(Direction.Left)
        self.assertEqual(Point(0, 0), self.game.player.location)

        self.game.move_player(Direction.Down)
        self.assertEqual(Point(0, 1), self.game.player.location)

        self.game.move_player(Direction.Right)
        self.assertEqual(Point(1, 1), self.game.player.location)

    def test_player_not_move_if_wall_next(self):
        self.game = self.game.start([
            [cs.Empty, cs.BrickWall, cs.Empty],
            [cs.Empty, cs.Player, cs.Empty],
            [cs.Empty, cs.ConcreteWall, cs.Empty]
        ])

        self.game.move_player(Direction.Up)
        self.assertNotEqual(Point(1, 0), self.game.player.location)
        self.assertEqual(Point(1, 1), self.game.player.location)

        self.game.move_player(Direction.Down)
        self.assertNotEqual(Point(1, 2), self.game.player.location)
        self.assertEqual(Point(1, 1), self.game.player.location)

    def test_player_not_move_if_flag_next(self):
        pass

    def test_terrain_is_available_next_cell(self):
        self.game = self.game.start([
            [cs.Empty, cs.Terrain, cs.Empty],
            [cs.Empty, cs.Player, cs.Empty],
            [cs.Empty, cs.Empty, cs.Empty]
        ])

        self.game.move_player(Direction.Up)
        self.assertEqual(Point(1, 0), self.game.player.location)
        self.assertTrue(len(self.game.map[Point(1, 0)]) == 2)
        self.assertTrue(len(self.game.map[Point(1, 1)]) == 0)

    def test_enemy_not_spawn_if_maximum_reached(self):
        self.game = Game()
        level = Level(self.game.size, 10) \
            .with_brick_walls(self.game.size * 2) \
            .with_concrete_walls(self.game.size) \
            .with_terrains(self.game.size // 2) \
            .with_patrolling_enemies(1) \
            .with_haunting_enemies(2)
        self.game = self.game.start(level)

        self.assertEqual(len(self.game.map.get_enemies()), 3)
        self.game.spawn_enemy()
        self.assertEqual(len(self.game.map.get_enemies()), 3)

    def test_enemy_spawn_if_possible(self):
        self.game = Game()
        level = Level(self.game.size, 10) \
            .with_brick_walls(self.game.size * 2) \
            .with_concrete_walls(self.game.size) \
            .with_terrains(self.game.size // 2) \
            .with_patrolling_enemies(1) \
            .with_haunting_enemies(1)
        self.game = self.game.start(level)

        self.assertEqual(len(self.game.map.get_enemies()), 2)
        self.game.spawn_enemy()
        self.assertEqual(len(self.game.map.get_enemies()), 3)
