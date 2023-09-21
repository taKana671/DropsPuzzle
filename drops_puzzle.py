import sys
from enum import Enum, auto

from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from panda3d.bullet import BulletWorld, BulletDebugNode
# from panda3d.core import load_prc_file_data
from panda3d.core import NodePath
from panda3d.core import Vec3, BitMask32, Point3, LColor

from game_board import GameBoard
from drops import Drops
from lights import BasicAmbientLight, BasicDayLight
from monitor import Monitor
from screen import Screen, Button, Frame, Label
from utils import make_line


# load_prc_file_data("", """
#     window-title Panda3D drops puzzle
#     fullscreen false
#     win-size 800 650
#     win-fixed-size 1""")

# load_prc_file_data("", """
#     textures-power-2 none
#     gl-coordinate-system default
#     window-title Panda3D Drops Puzzl
#     filled-wireframe-apply-shader true
#     stm-max-views 8
#     stm-max-chunk-count 2048""")


class Status(Enum):

    PLAY = auto()
    PAUSE = auto()
    GAMEOVER = auto()
    RESTART = auto()
    WARNING = auto()


class Game(ShowBase):

    def __init__(self):
        super().__init__()
        # self.set_background_color(LColor(0.57, 0.43, 0.85, 1.0))
        self.disable_mouse()

        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))

        self.camera.set_pos(Point3(0, -35, 7))  # Point3(0, -39, 1)
        # self.camera.set_pos(Point3(0, -70, 7))
        self.camera.set_hpr(Vec3(0, -1.6, 0))   # Vec3(0, -2.1, 0)
        self.camera.reparent_to(self.render)

        self.scene = NodePath('scene')
        self.scene.reparent_to(self.render)

        self.ambient_light = BasicAmbientLight()
        self.ambient_light.reparent_to(self.scene)
        self.day_light = BasicDayLight()
        self.day_light.reparent_to(self.scene)

        self.game_board = GameBoard(self.world)
        self.game_board.reparent_to(self.scene)
        self.game_board.hide_displays()

        self.drops = Drops(self.world, self.game_board)
        self.drops.reparent_to(self.scene)

        self.monitor = Monitor(self.game_board, self.drops)

        self.debug = self.render.attach_new_node(BulletDebugNode('debug'))
        self.world.set_debug_node(self.debug.node())
        self.debug_line = make_line(
            self.game_board.cabinet.dims.top_left, self.game_board.cabinet.dims.top_right, LColor(1, 0, 0, 1))
        self.debug_line.reparent_to(self.debug)

        self.screen = self.create_gui()
        self.screen.show()
        self.state = None

        self.accept('escape', sys.exit)
        self.accept('d', self.toggle_debug)
        self.accept('mouse1', self.mouse_click)
        self.taskMgr.add(self.update, 'update')

    def create_gui(self):
        font = self.loader.loadFont('font/Candaral.ttf')

        self.start_frame = Frame(self.aspect2d)
        Label(self.start_frame, 'START', (0, 0, 0.3), font)
        start_btn = Button(self.start_frame, 'PLAY', (0, 0, 0), font, self.initialize, focus=True)
        quit_btn1 = Button(self.start_frame, 'QUIT', (0, 0, -0.2), font, lambda: sys.exit())
        self.start_frame.create_group(start_btn, quit_btn1)
        screen = Screen(self.start_frame)

        self.pause_frame = Frame(self.aspect2d, hide=True)
        Label(self.pause_frame, 'PAUSE', (0, 0, 0.3), font)
        continue_btn = Button(self.pause_frame, 'CONTINUE', (0, 0, 0), font, self.continue_game, focus=True)
        reset_btn = Button(self.pause_frame, 'RRSET', (0, 0, -0.2), font, self.restart_game)
        quit_btn2 = Button(self.pause_frame, 'QUIT', (0, 0, -0.4), font, lambda: sys.exit())
        self.pause_frame.create_group(continue_btn, reset_btn, quit_btn2)
        self.pause_frame.hide()

        return screen

    def start_game(self, is_add=False):
        print('start_game!!!!')
        self.accept('escape', self.pause)
        self.clicked = False
        self.game_board.show_displays()
        self.state = Status.PLAY
        if is_add:
            self.drops.add()

    def initialize(self):
        print('initialize')
        self.ignore('escape')
        self.drops.initialize()
        self.monitor.initialize()
        self.game_board.initialize()
        self.screen.fade_out(self.start_game, True)

    def pause(self):
        print('pause!!!!')
        self.ignore('escape')
        self.state = Status.PAUSE
        self.game_board.hide_displays()
        self.screen.gui = self.pause_frame
        self.screen.fade_in(self.accept, 'escape', sys.exit)

    def continue_game(self):
        print('continue!!!!')
        self.ignore('escape')
        self.screen.fade_out(self.start_game)

    def gameover(self):
        print('gameover!!!!')
        self.ignore('escape')
        self.state = Status.GAMEOVER
        self.game_board.hide_displays()
        self.screen.gui = self.start_frame
        self.screen.fade_in(self.accept, 'escape', sys.exit)

    def restart_game(self):
        self.state = Status.RESTART

    def toggle_debug(self):
        if self.debug.is_hidden():
            self.debug.show()
            self.day_light.node().show_frustum()
        else:
            self.debug.hide()
            self.day_light.node().hide_frustum()

    def mouse_click(self):
        self.clicked = True

    def choose(self, mouse_pos):
        near_pos = Point3()
        far_pos = Point3()
        self.camLens.extrude(mouse_pos, near_pos, far_pos)
        from_pos = self.render.get_relative_point(self.cam, near_pos)
        to_pos = self.render.get_relative_point(self.cam, far_pos)
        result = self.world.ray_test_closest(from_pos, to_pos, BitMask32.bit(2))

        if result.has_hit():
            hit_node = result.get_node()
            if not hit_node.has_tag('effecting'):
                self.drops.find_neighbours(hit_node)

    def update(self, task):
        dt = globalClock.get_dt()

        if self.state == Status.PLAY:
            if self.mouseWatcherNode.has_mouse():
                mouse_pos = self.mouseWatcherNode.get_mouse()
                if self.clicked:
                    self.choose(mouse_pos)
                    self.clicked = False

            if not self.monitor.update():
                self.monitor.warn_gameover(self.gameover)
                self.state = Status.WARNING

        if self.state == Status.RESTART:
            if self.monitor.restart_check():
                self.state = Status.PAUSE
                self.initialize()

        self.world.do_physics(dt)
        return task.cont


if __name__ == '__main__':
    game = Game()
    game.run()