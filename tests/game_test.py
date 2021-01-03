import unittest
from application.game import Game
from application.cell_state import CellState as cs
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
