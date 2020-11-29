import unittest
from application.game import Game
from domain.infrastructure.geometry import Point, Direction


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(5).start()

    def test_movement_player(self):
        old_location = self.game.player.location
        self.game.player.move(Direction.Up)
        self.assertNotEqual(old_location, self.game.player.location)
