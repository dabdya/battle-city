__version__ = "1.1"
__email__ = "iamdabdya@gmail.com"

from enum import Enum
from copy import deepcopy
import argparse
import datetime
import sys

GAME_MODULE_ERROR = -1
REQUIREMENTS_ERROR = -2

try:
    from application.game import Game, GameStatus
    from application.level import Level

    from domain.infrastructure.geometry import Direction, Point
    from domain.infrastructure.move_obj import IMoveObject

    from domain.obstacle import Wall, WallType
    from domain.bonus import Bonus, BonusType
    from domain.boom import Boom, BoomType
    from domain.bullet import BulletType
    from domain.enemy import EnemyType
    from domain.player import Player
    from domain.terrain import Grass
    from domain.flag import Flag

except ModuleNotFoundError as err:
    sys.stdout.write(str(err))
    sys.exit(GAME_MODULE_ERROR)

try:
    from PyQt5.QtWidgets import (
        QApplication, QVBoxLayout,
        QMainWindow, QShortcut, QDialog,
        QLabel, QWidget, QStackedWidget)

    from PyQt5.QtGui import (
        QKeySequence, QPainter,
        QPalette, QPixmap,
        QImage, QBrush,
        QFont)

    from PyQt5.QtCore import (
        QBasicTimer, QPoint,
        QRect, QSize, Qt)

    from PyQt5.QtMultimedia import QSound

except ModuleNotFoundError as err:
    sys.stdout.write(str(err))
    sys.exit(REQUIREMENTS_ERROR)


SAVE = None


class GameWindow(QWidget):
    def __init__(self, parent, load_save=False):
        super().__init__(parent)
        self._parent = parent
        self.scale = 50
        self.init_ui()

        self.pressed_keys = set()
        self.timer = QBasicTimer()
        self.timer.start(10, self)
        self.pause = False
        self.nxt_level = False

        self.count = 0
        self.game_speed = 16
        self._player_speed = 16
        self.enemy_bullet_speed = 8
        self._player_bullet_speed = 8

        self.game = Game(size=13)
        seeds = list(map(int, sys.argv[1:]))
        self.levels = self.init_levels(seeds)
        self.levels_count = len(self.levels)
        if load_save:
            self.game = deepcopy(SAVE)
        else:
            if (len(self.levels) == 0 or
                    not self.game.start(
                        self.levels[self.game.level_num - 1])):
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

        self.save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save.activated.connect(self.save_game)

    @property
    def player_speed(self):
        if self.game.player.speed_runner:
            return self._player_speed / 2 - 1
        return self._player_speed

    @property
    def player_bullet_speed(self):
        if self.game.player.fast_shooting:
            return self._player_bullet_speed / 2
        return self._player_bullet_speed

    def activate_cheat(self):
        self.game.player.cheat = 1

    def activate_imba(self):
        self.game.player.cheat = 2

    def activate_default(self):
        self.game.player.cheat = 0

    def save_game(self):
        global SAVE
        SAVE = deepcopy(self.game)

    def init_levels(self, seeds):
        levels = list()
        while len(seeds) != 0:
            level = (Level(self.game.size, seeds.pop())
                     .with_brick_walls(self.game.size * 2)
                     .with_concrete_walls(self.game.size)
                     .with_terrains(self.game.size // 2)
                     .with_patrolling_enemies(1)
                     .with_haunting_enemies(1))
            levels.append(level)
        return levels

    def check_status(self):
        if self.game.status == GameStatus.End:
            self.timer.stop()
            state = Window.States[Windows.GameOver]
            window = Window(self._parent, state)
            self._parent.addWidget(window)
            self._parent.setCurrentIndex(self._parent.currentIndex() + 1)
            self._parent.removeWidget(self)
            self.sounds["end"].play()
            return False
        elif self.game.status == GameStatus.NextLevel:
            self.game.start(self.levels[self.game.level_num - 1])
            self.pause = True
            self.nxt_level = True
            self.sounds["start"].play()
        elif self.game.status == GameStatus.Win:
            self.timer.stop()
            state = Window.States[Windows.GameSuccess]
            window = Window(self._parent, state)
            self._parent.addWidget(window)
            self._parent.setCurrentIndex(self._parent.currentIndex() + 1)
            self._parent.removeWidget(self)
            self.sounds["win"].play()
            return False
        return True

    def timerEvent(self, event):

        if Qt.Key_P in self.pressed_keys:
            self.pause = not self.pause
            self.nxt_level = False
            self.pressed_keys.remove(Qt.Key_P)

        if self.pause or not self.check_status():
            self.update()
            return

        self.count += 1
        if self.count % self.game_speed == 0:
            self.update_enemies()
            self.update_bonuses()
            self.update_booms()

        if self.count % self.player_speed == 0:
            if self.game.player.health:
                self.update_player()

        if self.count % self.player_bullet_speed == 0:
            self.update_player_bullets()

        if self.count % self.enemy_bullet_speed == 0:
            self.update_enemy_bullets()

        self.shoot_player()
        self.count %= self.game_speed
        self.update()

    def init_ui(self):
        image = QImage(r"application/images/background.jpg")
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(image))
        self.setPalette(palette)
        self._parent.setPalette(palette)

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        self.draw_player(painter)
        self.draw_bullets(painter)
        self.draw_enemy(painter)
        self.draw_locality(painter)
        self.draw_level_info(painter)
        if self.pause and self.nxt_level:
            self.draw_next_level(painter)
        elif self.pause:
            self.draw_pause(painter)
        painter.end()

    # region(Drawing)
    def draw_pause(self, painter):
        painter.setPen(Qt.darkRed)
        painter.setFont(QFont('Decorative', 20))
        painter.drawText(50, 40, "PAUSE")

    def draw_next_level(self, painter):
        painter.setPen(Qt.darkRed)
        painter.setFont(QFont('Decorative', 20))
        text = "NEW LEVEL LOADED. THE GAME IS PAUSED"
        painter.drawText(50, 40, text)

    def draw_level_info(self, painter):
        painter.setPen(Qt.darkRed)
        painter.setFont(QFont('Decorative', 14))
        painter.drawText(720, 690, f"SCORES: {self.game.score}")

        painter.drawText(
            720, 540,
            f"LEVEL: {self.game.level_num}/{self.levels_count}")

        bonus_images = {
            BonusType.Armor: "application/images/armor.png",
            BonusType.Invulnerability: "application/images/infinity.png",
        }

        image = None
        if self.game.player.invulnerability:
            image = bonus_images[BonusType.Invulnerability]
        elif self.game.player.armor:
            image = bonus_images[BonusType.Armor]
        if image:
            painter.drawImage(QRect(750, 450, 50, 50),
                              QImage(image))

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

        images = {

            Wall: {
                WallType.Brick: "application/images/brick_wall.png",
                WallType.Concrete: "application/images/concrete_wall.png"
            },

            Grass: "application/images/terrain.png",

            Flag: "application/images/flag.png",

            Boom: {
                BoomType.Wall: "application/images/boom_wall.png",
                BoomType.Small: "application/images/boom_1.png",
                BoomType.Big: "application/images/boom_2.png"
            },

            Bonus: {
                BonusType.Invulnerability: "application/images/infinity.png",
                BonusType.Armor: "application/images/armor.png",
                BonusType.Heart: "application/images/heart_bonus.png",
                BonusType.FastShooting: "application/images/bullet_bonus.png",
                BonusType.SpeedRunner: "application/images/speed_bonus.png"
            }
        }

        for location in self.game.map:
            for obj in self.game.map[location]:

                if isinstance(obj, Wall):
                    image = images[Wall][obj.wall_type]

                elif isinstance(obj, Grass):
                    image = images[Grass]

                elif isinstance(obj, Flag):
                    image = images[Flag]

                elif isinstance(obj, Boom):
                    image = images[Boom][obj.type]

                elif isinstance(obj, Bonus):
                    image = images[Bonus][obj.type]
                else:
                    continue

                painter.drawImage(QRect(
                    obj.location.x * self.scale + 50,
                    obj.location.y * self.scale + 50,
                    self.scale, self.scale),
                    QImage(image))

    def draw_player(self, painter):

        if not self.game.player.health:
            return

        dx = (-self.game.player.velocity.x +
              (self.count % self.player_speed) *
              self.game.player.velocity.x / self.player_speed)

        dy = (-self.game.player.velocity.y +
              (self.count % self.player_speed) *
              self.game.player.velocity.y / self.player_speed)

        images = {
            Direction.Up: [
                r"application/images/tank_up.png",
                r"application/images/cheat_tank_up.png",
                r"application/images/imba_tank_up.png"],

            Direction.Down: [
                r"application/images/tank_down.png",
                r"application/images/cheat_tank_down.png",
                r"application/images/imba_tank_down.png"],

            Direction.Left: [
                r"application/images/tank_left.png",
                r"application/images/cheat_tank_left.png",
                r"application/images/imba_tank_left.png"],

            Direction.Right: [
                r"application/images/tank_right.png",
                r"application/images/cheat_tank_right.png",
                r"application/images/imba_tank_right.png"],
        }

        rect = QRect(
            int((self.game.player.location.x + dx) * self.scale) + 50,
            int((self.game.player.location.y + dy) * self.scale) + 50,
            self.scale, self.scale)

        image = QImage(
            images[self.game.player.direction][self.game.player.cheat])

        painter.drawImage(rect, image)

    def draw_enemy(self, painter):

        images = {
            EnemyType.Patrolling: {
                Direction.Up: r"application/images/enemy_up.png",
                Direction.Down: r"application/images/enemy_down.png",
                Direction.Left: r"application/images/enemy_left.png",
                Direction.Right: r"application/images/enemy_right.png"
            },

            EnemyType.Haunting: {
                Direction.Up: r"application/images/enemy1_up.png",
                Direction.Down: r"application/images/enemy1_down.png",
                Direction.Left: r"application/images/enemy1_left.png",
                Direction.Right: r"application/images/enemy1_right.png"
            },

            EnemyType.SpawnPatrolling: {
                Direction.Down: r"application/images/spawn_1.png"
            },

            EnemyType.SpawnHaunting: {
                Direction.Down: r"application/images/spawn_1.png"
            }
        }

        for enemy in self.game.map.get_enemies():
            dx = (-enemy.velocity.x + self.count *
                  enemy.velocity.x / self.game_speed)
            dy = (-enemy.velocity.y + self.count *
                  enemy.velocity.y / self.game_speed)

            image = images[enemy.type][enemy.direction]
            rect = QRect(
                int((enemy.location.x + dx) * self.scale) + 50,
                int((enemy.location.y + dy) * self.scale) + 50,
                self.scale, self.scale)

            painter.drawImage(rect, QImage(image))

    def _draw_bullet(self, painter, image, bullet):
        bullet_size = 10

        speed = self.player_bullet_speed \
            if isinstance(bullet.parent, Player) \
            else self.enemy_bullet_speed

        dx_velocity = (-bullet.velocity.x +
                       (self.count % speed)
                       * bullet.velocity.x / speed)

        dy_velocity = (-bullet.velocity.y +
                       (self.count % speed)
                       * bullet.velocity.y / speed)

        dx_gun = {
            Direction.Up: self.scale / 2 - bullet_size / 2,
            Direction.Down: self.scale / 2 - bullet_size / 2,
            Direction.Left: -bullet_size,
            Direction.Right: self.scale
        }

        dy_gun = {
            Direction.Up: -bullet_size,
            Direction.Down: self.scale,
            Direction.Left: self.scale / 2 - bullet_size / 2,
            Direction.Right: self.scale / 2 - bullet_size / 2
        }

        rect = QRect(
            (int((bullet.location.x + dx_velocity) * self.scale)
             + int(dx_gun[bullet.direction]) + 50),
            (int((bullet.location.y + dy_velocity) * self.scale)
             + int(dy_gun[bullet.direction]) + 50),
            bullet_size, bullet_size)

        painter.drawImage(rect, QImage(image))

    def draw_bullets(self, painter):

        images = {
            BulletType.Normal: {
                Direction.Up: r"application/images/bullet_up.png",
                Direction.Down: r"application/images/bullet_down.png",
                Direction.Left: r"application/images/bullet_left.png",
                Direction.Right: r"application/images/bullet_right.png"
            },

            BulletType.Concrete: {
                Direction.Up: r"application/images/ubullet_up.png",
                Direction.Down: r"application/images/ubullet_down.png",
                Direction.Left: r"application/images/ubullet_left.png",
                Direction.Right: r"application/images/ubullet_right.png"
            }
        }

        if self.game.player.health != 0:
            for bullet in self.game.player.bullets:
                image = images[bullet.bullet_type][bullet.direction]
                self._draw_bullet(painter, image, bullet)

        for enemy in self.game.map.get_enemies():
            for bullet in enemy.bullets:
                image = images[bullet.bullet_type][bullet.direction]
                self._draw_bullet(painter, image, bullet)

    # endregion

    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.pressed_keys:
            self.pressed_keys.remove(event.key())

    def update_booms(self):
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

    def update_player_bullets(self):
        self.game.move_player_bullets()

    def update_enemy_bullets(self):
        self.game.move_enemy_bullets()

    def update_enemies(self):
        if not self.game.map.get_enemies():
            self.game.level_num += 1
            if len(self.levels) == self.game.level_num - 1:
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

    def update_bonuses(self):
        if self.game.player.invulnerability:
            delta = datetime.datetime.now() - \
                    self.game.player.invulnerability
            if delta > datetime.timedelta(milliseconds=10000):
                self.game.player.invulnerability = None

        if self.game.player.speed_runner:
            delta = (datetime.datetime.now()
                     - self.game.player.speed_runner)
            if delta > datetime.timedelta(milliseconds=10000):
                self.game.player.speed_runner = None

        if self.game.player.fast_shooting:
            delta = datetime.datetime.now() - \
                    self.game.player.fast_shooting
            if delta > datetime.timedelta(milliseconds=10000):
                self.game.player.fast_shooting = None

        for bonus in self.game.map.get_bonuses():
            if bonus.exists == 0:
                self.game.map[bonus.location].remove(bonus)
            else:
                bonus.exists -= 1

        if self.game.score not in [0, self.game.bonus_count] \
                and self.game.score % 3 == 0:
            self.game.bonus_count = self.game.score
            self.game.add_bonus()
            self.sounds["bonus"].play()

    def shoot_player(self):
        if Qt.Key_Space in self.pressed_keys:
            shoot = self.game.shoot()
            if shoot:
                self.sounds["fire"].play()


# region(Window)
class Windows(Enum):
    MainMenu = 0
    GameOver = 1
    GameSuccess = 2
    Help = 3
    Save = 4


class Window(QDialog):
    def __init__(self, parent, states):
        super().__init__()
        self._parent = parent
        self.title = "Battle City"
        self.state_id = 0
        self.states = states
        self.states_count = len(states)
        self.init_ui(parent)

        self.pressed_keys = set()
        self.timer = QBasicTimer()
        self.timer.start(100, self)

    States = {

        Windows.MainMenu: {
            0: ("application/images/main_menu_1.jpeg", GameWindow),
            1: ("application/images/main_menu_2.jpeg", Windows.Help),
            2: ("application/images/main_menu_3.jpeg", None)},

        Windows.GameOver: {
            0: ("application/images/game_over_1.jpeg", Windows.Save),
            1: ("application/images/game_over_2.jpeg", Windows.MainMenu),
            2: ("application/images/game_over_3.jpeg", GameWindow),
            3: ("application/images/game_over_4.jpeg", None)},

        Windows.GameSuccess: {
            0: ("application/images/you_win_1.jpeg", Windows.MainMenu),
            1: ("application/images/you_win_2.jpeg", GameWindow),
            2: ("application/images/you_win_3.jpeg", None)},

        Windows.Help: {
            0: ("application/images/help_1.jpeg", Windows.MainMenu)}

    }

    def init_ui(self, parent):
        self.setWindowTitle(self.title)
        if parent:
            self.setGeometry(parent.geometry())

        image = QImage(self.states[self.state_id][0])
        self.set_image(parent, image)

    def set_image(self, parent, image):
        size = QSize(self.width(), self.height())
        _image = QImage(image).scaled(size)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(_image))
        self.setPalette(palette)
        parent.setPalette(palette)

    def timerEvent(self, e):
        self.update_cursor()
        self.update()

    def paintEvent(self, e):
        image = self.states[self.state_id][0]
        self.set_image(self._parent, image)

    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def update_cursor(self):
        if Qt.Key_Down in self.pressed_keys:
            self.state_id = (self.state_id + 1) % self.states_count

        elif Qt.Key_Up in self.pressed_keys:
            if self.state_id == 0:
                self.state_id = self.states_count
            self.state_id = (self.state_id - 1) % self.states_count

        elif Qt.Key_Return in self.pressed_keys:
            window = self.states[self.state_id][1]
            if not window:
                self._parent.close()
            elif window is GameWindow:
                self.timer.stop()
                window = GameWindow(self._parent)
                self._parent.addWidget(window)
                window.sounds["start"].play()
            elif window == Windows.Save and SAVE:
                self.timer.stop()
                window = GameWindow(self._parent, load_save=True)
                window.pause = True
                self._parent.addWidget(window)
            elif window != Windows.Save:
                self.timer.stop()
                w = Window(self._parent, Window.States[window])
                self._parent.addWidget(w)
            else:
                return

            self._parent.setCurrentIndex(self._parent.currentIndex() + 1)
            self._parent.removeWidget(self)
# endregion


class ScreenSwitcher(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battle City")
        self.setFixedSize(850, 750)

    def keyPressEvent(self, event):
        if self.currentWidget():
            self.currentWidget().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.currentWidget():
            self.currentWidget().keyReleaseEvent(event)


def main():
    create_parser().parse_args()
    app = QApplication(sys.argv)
    widget = ScreenSwitcher()
    widget.addWidget(Window(widget, Window.States[Windows.MainMenu]))
    widget.show()
    sys.exit(app.exec_())


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "levels", type=list, nargs="+",
        help="Seeds for level generation")
    return parser


if __name__ == "__main__":
    main()
