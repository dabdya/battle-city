from enum import Enum
import argparse
import sys

GAME_MODULE_ERROR = -1
REQUIREMENTS_ERROR = -2

try:
    from domain.infrastructure.geometry import Direction, Point
    from domain.infrastructure.move_obj import IMoveObject
    from application.game import Game, GameStatus
    from application.level_generator import Level
    from domain.obstacle import Wall, WallType
    from domain.bullet import BulletType
    from domain.terrain import Grass
    from domain.flag import Flag
    from domain.boom import Boom, BoomType
    from domain.enemy import EnemyType
except ModuleNotFoundError as err:
    sys.stdout.write(str(err))
    sys.exit(GAME_MODULE_ERROR)

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QLabel,
        QWidget, QVBoxLayout, QShortcut)
    from PyQt5.QtGui import (
        QPainter, QImage, QPixmap, QPalette,
        QBrush, QFont, QKeySequence)
    from PyQt5.QtCore import (
        Qt, QRect, QBasicTimer, QSize, QPoint)
    from PyQt5.QtMultimedia import QSound
except ModuleNotFoundError as err:
    sys.stdout.write(str(err))
    sys.exit(REQUIREMENTS_ERROR)


class MainMenuState(Enum):
    StartGame = 1
    Help = 2
    Exit = 3


class GameOverState(Enum):
    MainMenu = 1
    NewGame = 2
    Exit = 3


class MainMenuWindow(QMainWindow):
    def __init__(self, size, parent=None):
        self._size = size
        self._parent = parent
        super().__init__(parent)
        self.init_ui(size)

        self.state = MainMenuState.StartGame
        self.pressed_keys = set()
        self.timer = QBasicTimer()
        self.timer.start(1000, self)

    def init_ui(self, size):
        if self._parent:
            self.setGeometry(self._parent.geometry())
        else:
            self.setFixedSize(size, size)
        self.setWindowTitle("Battle City")
        self.set_image(QImage(
            r"application/images/main_menu_1.jpeg"))

    def timerEvent(self, e):
        self.update_cursor()
        self.update()

    def paintEvent(self, e):
        if self.state == MainMenuState.StartGame:
            self.set_image(QImage(
                r"application/images/main_menu_1.jpeg"))
        elif self.state == MainMenuState.Help:
            self.set_image(QImage(
                r"application/images/main_menu_2.jpeg"))
        elif self.state == MainMenuState.Exit:
            self.set_image(QImage(
                r"application/images/main_menu_3.jpeg"))

    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())
        self.update_cursor()

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
        self.update_cursor()

    def set_image(self, image):
        _image = image.scaled(QSize(self._size, self._size))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(_image))
        self.setPalette(palette)

    def update_cursor(self):
        if Qt.Key_Down in self.pressed_keys:
            if self.state == MainMenuState.StartGame:
                self.state = MainMenuState.Help
            elif self.state == MainMenuState.Help:
                self.state = MainMenuState.Exit

        elif Qt.Key_Up in self.pressed_keys:
            if self.state == MainMenuState.Exit:
                self.state = MainMenuState.Help
            elif self.state == MainMenuState.Help:
                self.state = MainMenuState.StartGame

        elif Qt.Key_Return in self.pressed_keys \
                or Qt.Key_Enter in self.pressed_keys:
            if self.state == MainMenuState.StartGame:
                self.timer.stop()
                window = MainWindow(self._size, self)
                window.show()
                window.sounds["start"].play()
                self.hide()
            elif self.state == MainMenuState.Help:
                self.timer.stop()
                window = HelpWindow(self._size, self)
                window.show()
                self.hide()
            elif self.state == MainMenuState.Exit:
                self.close()


class GameOverWindow(QMainWindow):
    def __init__(self, size, parent):
        self._parent = parent
        self._size = size
        super().__init__(parent)
        self.init_ui(size)

        self.state = GameOverState.MainMenu
        self.pressed_keys = set()
        self.timer = QBasicTimer()
        self.timer.start(2000, self)

    def init_ui(self, size):
        self.setGeometry(self._parent.geometry())
        self.setWindowTitle("Battle City")
        self.set_image(QImage(
            r"application/images/game_over_1.jpeg"))

    def timerEvent(self, e):
        self.update_cursor()
        self.update()

    def paintEvent(self, e):
        if self.state == GameOverState.MainMenu:
            self.set_image(QImage(
                r"application/images/game_over_1.jpeg"))
        elif self.state == GameOverState.NewGame:
            self.set_image(QImage(
                r"application/images/game_over_2.jpeg"))
        elif self.state == GameOverState.Exit:
            self.set_image(QImage(
                r"application/images/game_over_3.jpeg"))

    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())
        self.update_cursor()

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
        self.update_cursor()

    def set_image(self, image):
        _image = image.scaled(QSize(self._size, self._size))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(_image))
        self.setPalette(palette)

    def update_cursor(self):
        if Qt.Key_Down in self.pressed_keys:
            if self.state == GameOverState.MainMenu:
                self.state = GameOverState.NewGame
            elif self.state == GameOverState.NewGame:
                self.state = GameOverState.Exit
        elif Qt.Key_Up in self.pressed_keys:
            if self.state == GameOverState.Exit:
                self.state = GameOverState.NewGame
            elif self.state == GameOverState.NewGame:
                self.state = GameOverState.MainMenu
        elif Qt.Key_Return in self.pressed_keys \
                or Qt.Key_Enter in self.pressed_keys:
            if self.state == GameOverState.NewGame:
                self.timer.stop()
                window = MainWindow(self._size, self)
                window.show()
                self.hide()
            elif self.state == GameOverState.MainMenu:
                self.timer.stop()
                window = MainMenuWindow(self._size, parent=self)
                window.show()
                self.hide()
            elif self.state == GameOverState.Exit:
                self.close()


class HelpWindow(QMainWindow):
    def __init__(self, size, parent):
        self._parent = parent
        self._size = size
        super().__init__(parent)
        self.init_ui(size)

        self.pressed_keys = set()
        self.timer = QBasicTimer()
        self.timer.start(2000, self)

    def init_ui(self, size):
        self.setGeometry(self._parent.geometry())
        self.setWindowTitle("Battle City")
        self.set_image(QImage(
            r"application/images/help_1.jpeg"))

    def timerEvent(self, e):
        self.update_cursor()
        self.update()

    def paintEvent(self, e):
        pass

    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())
        self.update_cursor()

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
        self.update_cursor()

    def set_image(self, image):
        _image = image.scaled(QSize(self._size, self._size))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(_image))
        self.setPalette(palette)

    def update_cursor(self):
        if Qt.Key_Return in self.pressed_keys \
                or Qt.Key_Enter in self.pressed_keys:
            self.timer.stop()
            window = MainMenuWindow(self._size, parent=self)
            window.show()
            self.hide()


class NextLevelState(Enum):
    NextLevel = 1
    MainMenu = 2


class NextLevelWindow(QMainWindow):
    def __init__(self, size, parent):
        self._parent = parent
        self._size = size
        super().__init__(parent)
        self.init_ui(size)

        self.state = NextLevelState.NextLevel
        self.pressed_keys = set()
        self.timer = QBasicTimer()
        self.timer.start(2000, self)

    def init_ui(self, size):
        self.setFixedSize(size, size)
        self.setWindowTitle("Battle City")
        self.set_image(QImage(
            r"application/images/next_level_1.jpeg"))

    def timerEvent(self, e):
        self.update_cursor()
        self.update()

    def paintEvent(self, e):
        if self.state == NextLevelState.MainMenu:
            self.set_image(QImage(
                r"application/images/next_level_2.jpeg"))
        elif self.state == NextLevelState.NextLevel:
            self.set_image(QImage(
                r"application/images/next_level_1.jpeg"))

    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())
        self.update_cursor()

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
        self.update_cursor()

    def set_image(self, image):
        _image = image.scaled(QSize(self._size, self._size))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(_image))
        self.setPalette(palette)

    def update_cursor(self):
        if Qt.Key_Down in self.pressed_keys:
            if self.state == NextLevelState.NextLevel:
                self.state = NextLevelState.MainMenu
        elif Qt.Key_Up in self.pressed_keys:
            if self.state == NextLevelState.MainMenu:
                self.state = NextLevelState.NextLevel
        elif Qt.Key_Return in self.pressed_keys \
                or Qt.Key_Enter in self.pressed_keys:
            if self.state == NextLevelState.NextLevel:
                self.timer.stop()
                self._parent.show()
                self.hide()
            elif self.state == NextLevelState.MainMenu:
                pass


class GameWinWindows(QMainWindow):
    def __init__(self, size, parent):
        self._parent = parent
        self._size = size
        super().__init__(parent)
        self.init_ui(size)

        self.state = GameOverState.MainMenu
        self.pressed_keys = set()
        self.timer = QBasicTimer()
        self.timer.start(2000, self)

    def init_ui(self, size):
        self.setGeometry(self._parent.geometry())
        self.setWindowTitle("Battle City")
        self.set_image(QImage(
            r"application/images/you_win_1.jpeg"))

    def timerEvent(self, e):
        self.update_cursor()
        self.update()

    def paintEvent(self, e):
        if self.state == GameOverState.MainMenu:
            self.set_image(QImage(
                r"application/images/you_win_1.jpeg"))
        elif self.state == GameOverState.NewGame:
            self.set_image(QImage(
                r"application/images/you_win_2.jpeg"))
        elif self.state == GameOverState.Exit:
            self.set_image(QImage(
                r"application/images/you_win_3.jpeg"))

    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())
        self.update_cursor()

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
        self.update_cursor()

    def set_image(self, image):
        _image = image.scaled(QSize(self._size, self._size))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(_image))
        self.setPalette(palette)

    def update_cursor(self):
        if Qt.Key_Down in self.pressed_keys:
            if self.state == GameOverState.MainMenu:
                self.state = GameOverState.NewGame
            elif self.state == GameOverState.NewGame:
                self.state = GameOverState.Exit
        elif Qt.Key_Up in self.pressed_keys:
            if self.state == GameOverState.Exit:
                self.state = GameOverState.NewGame
            elif self.state == GameOverState.NewGame:
                self.state = GameOverState.MainMenu
        elif Qt.Key_Return in self.pressed_keys \
                or Qt.Key_Enter in self.pressed_keys:
            if self.state == GameOverState.NewGame:
                self.timer.stop()
                window = MainWindow(self._size, self)
                window.show()
                self.hide()
            elif self.state == GameOverState.MainMenu:
                self.timer.stop()
                window = MainMenuWindow(self._size, parent=self)
                window.show()
                self.hide()
            elif self.state == GameOverState.Exit:
                self.close()


class MainWindow(QMainWindow):
    def __init__(self, size, parent):
        super().__init__(parent)
        self._parent = parent
        self._size = size
        self.scale = 50
        self.init_ui(size)

        self.pressed_keys = set()
        self.timer = QBasicTimer()
        self.timer.start(10, self)
        self.pause = False
        self.count = 0

        self.game = Game(size=size // self.scale)
        seeds = list(map(int, sys.argv[1:]))
        self.levels = self.init_levels(seeds)
        self.levels_count = len(self.levels)

        if len(self.levels) == 0 or \
                not self.game.start(self.levels.pop()):
            self.close()

        self.sounds = {
            "fire": QSound("application/sounds/fire.wav"),
            "start": QSound("application/sounds/start.wav"),
            "boom": QSound("application/sounds/boom.wav"),
            "end": QSound("application/sounds/end.wav"),
            "bonus": QSound("application/sounds/bonus.wav"),
            "brick": QSound("application/sounds/brick.wav"),
            "win": QSound("application/sounds/win.wav")
        }

        self.cheat = QShortcut(QKeySequence("Ctrl+K"), self)
        self.cheat.activated.connect(self.activate_cheat)
        self.imba = QShortcut(QKeySequence("Ctrl+L"), self)
        self.imba.activated.connect(self.activate_imba)
        self.default = QShortcut(QKeySequence("Ctrl+J"), self)
        self.default.activated.connect(self.activate_default)

    def activate_cheat(self):
        self.game.player.cheat = 1

    def activate_imba(self):
        self.game.player.cheat = 2

    def activate_default(self):
        self.game.player.cheat = 0

    def init_levels(self, seeds):
        levels = list()
        while len(seeds) != 0:
            level = Level(self.game.size, seeds.pop()) \
                .with_brick_walls(self.game.size * 2) \
                .with_concrete_walls(self.game.size) \
                .with_terrains(self.game.size // 2) \
                .with_patrolling_enemies(1) \
                .with_haunting_enemies(1)
            levels.append(level)
        return levels

    def check_status(self):
        if self.game.status == GameStatus.End:
            self.timer.stop()
            window = GameOverWindow(self._size, self._parent)
            window.show()
            self.hide()
            self.sounds["end"].play()
            return False
        elif self.game.status == GameStatus.NextLevel:
            # window = NextLevelWindow(self._size, self)
            # window.show()
            # self.hide()
            self.game.start(self.levels.pop())
            self.sounds["start"].play()
        elif self.game.status == GameStatus.Win:
            self.timer.stop()
            window = GameWinWindows(self._size, self._parent)
            window.show()
            self.hide()
            self.sounds["win"].play()
            return False
        return True

    def timerEvent(self, event):
        if Qt.Key_P in self.pressed_keys:
            self.pause = not self.pause
            self.pressed_keys.remove(Qt.Key_P)

        if self.pause:
            self.update()
            return

        if not self.check_status():
            return

        self.count += 1
        if self.count != 0 and self.count % 15 == 0:
            self.count = 0
            self.update_bullets()
            if not self.check_status():
                return
            self.update_player()
            self.update_enemies()

        if self.count != 0 and self.count % 8 == 0:
            self.update_bullets()

        self.shoot_player()
        self.update()

    def init_ui(self, size):
        self.setFixedSize(size + 200, size + 100)
        image = QImage(r"application/images/background.jpg")
        _image = image.scaled(QSize(size + 200, size + 100))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(_image))
        self.setPalette(palette)
        self.setWindowTitle("Battle City")

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        self.draw_player(painter)
        self.draw_bullets(painter)
        self.draw_enemy(painter)
        self.draw_locality(painter)
        if self.pause:
            self.draw_pause(painter)
        self.draw_level_info(painter)
        painter.end()

    def draw_pause(self, painter):
        painter.setPen(Qt.darkRed)
        painter.setFont(QFont('Decorative', 20))
        painter.drawText(50, 40, "PAUSE")

    def draw_level_info(self, painter):
        painter.setPen(Qt.darkRed)
        painter.setFont(QFont('Decorative', 14))
        painter.drawText(720, 690, f"SCORES: {self.game.score}")

        painter.drawText(
            720, 540,
            f"LEVEL: {self.game.level_num}/{self.levels_count}")

        painter.drawText(720, 600, f"HEALTH:")
        for i in range(self.game.player.health):
            image = r"application/images/heart.png"
            painter.drawImage(QRect(
                720 + i * 40, 620, 30, 30),
                QImage(image))

        painter.drawText(720, 70, f"SPAWNS:")
        for i in range(self.game.spawn_count_haunting):
            image = r"application/images/enemy1_up_spawn.png"
            painter.drawImage(QRect(
                720, 90 + i * 60, self.scale, self.scale),
                QImage(image))

        for i in range(self.game.spawn_count_patrolling):
            image = r"application/images/enemy_up_spawn.png"
            painter.drawImage(QRect(
                780, 90 + i * 60, self.scale, self.scale),
                QImage(image))

        painter.setFont(QFont('Decorative', 10))
        painter.drawText(50, 730, "Default: Ctrl+J")
        painter.drawText(200, 730, "Double-gun: Ctrl+K")
        painter.drawText(400, 730, "Quad-gun: Ctrl+L")

    def draw_locality(self, painter):
        painter.setPen(Qt.green)

        for location in self.game.map:
            for obj in self.game.map[location]:
                if type(obj) not in [Wall, Grass, Flag, Boom]:
                    continue
                image = {
                    Wall: "application/images/brick_wall.png",
                    Grass: "application/images/terrain.png",
                    Flag: "application/images/flag.png",
                    Boom: "application/images/boom_1.png"
                }

                if type(obj) is Wall and obj.wall_type == WallType.Concrete:
                    image[Wall] = "application/images/concrete_wall.png"

                if type(obj) is Boom and obj.type == BoomType.Big:
                    image[Boom] = "application/images/boom_2.png"

                if type(obj) is Boom and obj.type == BoomType.Wall:
                    image[Boom] = "application/images/boom_wall.png"

                painter.drawImage(QRect(
                    obj.location.x * self.scale + 50,
                    obj.location.y * self.scale + 50,
                    self.scale, self.scale),
                    QImage(image[type(obj)]))

    def draw_player(self, painter):
        if self.game.status == GameStatus.End:
            return
        painter.setPen(Qt.red)

        dx = -self.game.player.velocity.x
        dx += self.count * self.game.player.velocity.x / 14

        dy = -self.game.player.velocity.y
        dy += self.count * self.game.player.velocity.y / 14

        images = {
            Direction.Up: [r"application/images/tank_up.png",
                           r"application/images/cheat_tank_up.png",
                           r"application/images/imba_tank_up.png"],

            Direction.Down: [r"application/images/tank_down.png",
                             r"application/images/cheat_tank_down.png",
                             r"application/images/imba_tank_down.png"],

            Direction.Left: [r"application/images/tank_left.png",
                             r"application/images/cheat_tank_left.png",
                             r"application/images/imba_tank_left.png"],

            Direction.Right: [r"application/images/tank_right.png",
                              r"application/images/cheat_tank_right.png",
                              r"application/images/imba_tank_right.png"],
        }

        painter.drawImage(QRect(
            int((self.game.player.location.x + dx) * self.scale) + 50,
            int((self.game.player.location.y + dy) * self.scale) + 50,
            self.scale, self.scale),
            QImage(images[self.game.player.direction][self.game.player.cheat]))

    def draw_enemy(self, painter):
        painter.setPen(Qt.red)

        images = {
            Direction.Up: r"application/images/enemy_up.png",
            Direction.Down: r"application/images/enemy_down.png",
            Direction.Left: r"application/images/enemy_left.png",
            Direction.Right: r"application/images/enemy_right.png"
        }

        uimages = {
            Direction.Up: r"application/images/enemy1_up.png",
            Direction.Down: r"application/images/enemy1_down.png",
            Direction.Left: r"application/images/enemy1_left.png",
            Direction.Right: r"application/images/enemy1_right.png"
        }

        for enemy in self.game.map.get_enemies():

            dx = -enemy.velocity.x + self.count * enemy.velocity.x / 14
            dy = -enemy.velocity.y + self.count * enemy.velocity.y / 14

            if enemy.type == EnemyType.Haunting:
                image = uimages[enemy.direction]
            elif enemy.type == EnemyType.Patrolling:
                image = images[enemy.direction]
            else:
                image = r"application/images/spawn_1.png"

            painter.drawImage(QRect(
                int((enemy.location.x + dx) * self.scale) + 50,
                int((enemy.location.y + dy) * self.scale) + 50,
                self.scale, self.scale),
                QImage(image))

    def _draw_bullet(self, painter, image, bullet):
        dx_velocity = -bullet.velocity.x + \
                      (self.count % 8) * bullet.velocity.x / 7
        dy_velocity = -bullet.velocity.y + \
                      (self.count % 8) * bullet.velocity.y / 7

        dx = 0
        dy = 0
        bullet_size = 10
        if bullet.direction == Direction.Up:
            dx += self.scale / 2 - bullet_size / 2
            dy -= bullet_size
        if bullet.direction == Direction.Down:
            dx += self.scale / 2 - bullet_size / 2
            dy += self.scale
        if bullet.direction == Direction.Left:
            dx -= bullet_size
            dy += self.scale / 2 - bullet_size / 2
        if bullet.direction == Direction.Right:
            dx += self.scale
            dy += self.scale / 2 - bullet_size / 2

        painter.drawImage(QRect(
            int((bullet.location.x + dx_velocity) * self.scale) + int(dx) + 50,
            int((bullet.location.y + dy_velocity) * self.scale) + int(dy) + 50,
            bullet_size, bullet_size), QImage(image))

    def draw_bullets(self, painter):
        painter.setPen(Qt.red)
        images = {
            Direction.Up: r"application/images/bullet_up.png",
            Direction.Down: r"application/images/bullet_down.png",
            Direction.Left: r"application/images/bullet_left.png",
            Direction.Right: r"application/images/bullet_right.png"
        }

        uimages = {
            Direction.Up: r"application/images/ubullet_up.png",
            Direction.Down: r"application/images/ubullet_down.png",
            Direction.Left: r"application/images/ubullet_left.png",
            Direction.Right: r"application/images/ubullet_right.png"
        }

        for bullet in self.game.player.bullets:
            image = images[bullet.direction] \
                if bullet.bullet_type == BulletType.Normal \
                else uimages[bullet.direction]
            self._draw_bullet(painter, image, bullet)

        for enemy in self.game.map.get_enemies():
            for bullet in enemy.bullets:
                image = images[bullet.direction] \
                    if bullet.bullet_type == BulletType.Normal \
                    else uimages[bullet.direction]
                self._draw_bullet(painter, image, bullet)

    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.pressed_keys:
            self.pressed_keys.remove(event.key())

    def update_bullets(self):
        for location in self.game.map:
            for obj in self.game.map[location].copy():
                if type(obj) == Boom:
                    if obj.type == BoomType.Big:
                        self.game.map[obj.location].remove(obj)
                        self.sounds["boom"].play()
                    elif obj.type == BoomType.Wall:
                        self.game.map[obj.location].remove(obj)
                        self.sounds["brick"].play()
                    else:
                        obj.type = BoomType.Big
        self.game.move_bullets()

    def update_enemies(self):
        if not self.game.map.get_enemies():
            self.game.level_num += 1
            if len(self.levels) == 0:
                self.game.status = GameStatus.Win
            else:
                self.game.status = GameStatus.NextLevel
            return
        self.game.move_enemies()
        self.game.spawn_enemy()

    def update_player(self):
        if Qt.Key_Up in self.pressed_keys:
            self.game.move_player(Direction.Up)
        elif Qt.Key_Down in self.pressed_keys:
            self.game.move_player(Direction.Down)
        elif Qt.Key_Left in self.pressed_keys:
            self.game.move_player(Direction.Left)
        elif Qt.Key_Right in self.pressed_keys:
            self.game.move_player(Direction.Right)
        else:
            self.game.player.velocity = Point(0, 0)

        if self.game.score >= 5:
            self.game.player.up_level()

    def shoot_player(self):
        if Qt.Key_Space in self.pressed_keys:
            self.shoot = False
            shoot = self.game.shoot()
            if shoot:
                self.sounds["fire"].play()


def main():
    args = create_argparser().parse_args()
    app = QApplication(sys.argv)
    main_w = MainMenuWindow(650)
    main_w.show()
    sys.exit(app.exec_())


def create_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "levels", type=list, nargs="+",
        help="Seed for level generation")
    return argparser


if __name__ == "__main__":
    main()
