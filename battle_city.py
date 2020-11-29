import sys

GAME_MODULE_ERROR = -1
try:
    from domain.infrastructure.geometry import Direction
    from application.game import Game
    from domain.obstacle import Wall
    from domain.terrain import Grass
except ModuleNotFoundError as err:
    sys.stdout.write(str(err))
    sys.exit(GAME_MODULE_ERROR)

REQUIREMENTS_ERROR = -2
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt5.QtGui import QPainter, QImage, QPixmap
    from PyQt5.QtCore import Qt, QRect, QBasicTimer
except ModuleNotFoundError as err:
    sys.stdout.write(str(err))
    sys.exit(REQUIREMENTS_ERROR)


class MainMenu(QMainWindow):
    def __init__(self, size):
        super().__init__()
        self.init_ui(size)

    def init_ui(self, size):
        self.setGeometry(0, 0, size, size)
        self.setStyleSheet("background-color: black")
        self.setWindowTitle("Battle City")


class MainWindow(QMainWindow):
    def __init__(self, size):
        super().__init__()
        self.init_ui(size)
        self.scale = 50
        self.timer = QBasicTimer()
        self.timer.start(120, self)
        self.pressed_keys = set()
        self.game = Game()
        self.game.start()
        self.upd = False

    def timerEvent(self, event):
        self.update_player()
        self.update_bullets()
        if self.upd:
            self.update_enemies()
            self.upd = False
        else:
            self.upd = True
        self.update()

    def init_ui(self, size):
        self.setGeometry(0, 0, size, size)
        self.setStyleSheet("background-color: black")
        self.setWindowTitle("Battle City")

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        self.draw_player(painter)
        self.draw_enemy(painter)
        self.draw_locality(painter)
        self.draw_bullets(painter)
        painter.end()

    def draw_locality(self, painter):
        painter.setPen(Qt.green)

        for coord in self.game.map:
            if type(self.game.map[coord]) not in [Wall, Grass]:
                continue
            obj = self.game.map[coord]
            image = {
                Wall: "application/images/wall.png",
                Grass: "application/images/terrain.png"
            }

            painter.drawImage(QRect(
                obj.location.x * self.scale,
                obj.location.y * self.scale,
                self.scale, self.scale),
                QImage(image[type(obj)]))

    def draw_player(self, painter):
        painter.setPen(Qt.red)

        images = {
            Direction.Up: r"application/images/tank_up.png",
            Direction.Down: r"application/images/tank_down.png",
            Direction.Left: r"application/images/tank_left.png",
            Direction.Right: r"application/images/tank_right.png"
        }

        painter.drawImage(QRect(
            int(self.game.player.location.x * self.scale),
            int(self.game.player.location.y * self.scale),
            self.scale, self.scale),
            QImage(images[self.game.player.direction]))

    def draw_enemy(self, painter):
        painter.setPen(Qt.red)

        images = {
            Direction.Up: r"application/images/enemy_up.png",
            Direction.Down: r"application/images/enemy_down.png",
            Direction.Left: r"application/images/enemy_left.png",
            Direction.Right: r"application/images/enemy_right.png"
        }

        for enemy in self.game.map.get_enemies():
            painter.drawImage(QRect(
                int(enemy.location.x * self.scale),
                int(enemy.location.y * self.scale),
                self.scale, self.scale),
                QImage(images[enemy.direction]))

    def draw_bullets(self, painter):
        painter.setPen(Qt.red)
        images = {
            Direction.Up: r"application/images/bullet_up.png",
            Direction.Down: r"application/images/bullet_down.png",
            Direction.Left: r"application/images/bullet_left.png",
            Direction.Right: r"application/images/bullet_right.png"
        }

        dx = 0
        dy = 0
        bullet_size = 10
        if self.game.player.direction == Direction.Up:
            dx += 50 / 2 - bullet_size / 2
        if self.game.player.direction == Direction.Down:
            dx += 50 / 2 - bullet_size / 2
            dy += 50
        if self.game.player.direction == Direction.Left:
            dy += 50 / 2 - bullet_size / 2
        if self.game.player.direction == Direction.Right:
            dx += 50
            dy += 50 / 2 - bullet_size / 2

        for bullet in self.game.player.bullets:
            painter.drawImage(QRect(
                int(bullet.location.x * self.scale) + int(dx),
                int(bullet.location.y * self.scale) + int(dy),
                bullet_size, bullet_size),
                QImage(images[bullet.direction]))

    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())

    def keyReleaseEvent(self, event):
        self.pressed_keys.remove(event.key())

    def update_bullets(self):
        self.game.move_bullets()

    def update_enemies(self):
        self.game.move_enemies()

    def update_player(self):
        if Qt.Key_Up in self.pressed_keys:
            self.game.move_player(Direction.Up)
        elif Qt.Key_Down in self.pressed_keys:
            self.game.move_player(Direction.Down)
        elif Qt.Key_Left in self.pressed_keys:
            self.game.move_player(Direction.Left)
        elif Qt.Key_Right in self.pressed_keys:
            self.game.move_player(Direction.Right)
        elif Qt.Key_Space in self.pressed_keys:
            self.game.shoot()


def main():
    app = QApplication([])
    main_window = MainWindow(650)
    main_window.show()
    # main_w = MainMenu(650)
    # main_w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
