import sys
import random
from enum import Enum, auto

from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import load_prc_file_data
from panda3d.core import NodePath
from panda3d.core import LineSegs, Fog
from panda3d.core import Vec3, BitMask32, Point3, LColor, Point2

from game_board import GameBoard, NumberDisplay
from drops import Drops
from lights import BasicAmbientLight, BasicDayLight
from monitor import Monitor


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

    DISAPPEAR = auto()
    MERGE = auto()
    FALL = auto()


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

        self.drops = Drops(self.world)
        self.drops.reparent_to(self.scene)

        self.monitor = Monitor(self.game_board, self.drops)

        self.debug = self.render.attach_new_node(BulletDebugNode('debug'))
        self.world.set_debug_node(self.debug.node())
        # self.debug_line = self.make_debug_line(self.game_board.top_l, self.game_board.top_r, LColor(1, 0, 0, 1))
        # self.debug_line.reparent_to(self.debug)

        self.clicked = False
        self.play = True

        # self.taskMgr.do_method_later(0.2, self.drops.add, 'add')
        self.drops.add()


        self.accept('escape', sys.exit)
        self.accept('d', self.toggle_debug)
        self.accept('mouse1', self.mouse_click)
        self.accept('gameover', self.gameover)
        # self.accept('mouse1-up', self.mouse_release)

        self.taskMgr.add(self.update, 'update')

    def gameover(self):
        self.play = False
        print('gameover!!!!!!!!!')

        # for c in self.drops.get_children():
        #     c.node().set_linear_factor(Vec3(1, 1, 1))

        # self.game_board.cabinet.hprInterval(1.0, Vec3(0, 20, 0)).start()

    def make_debug_line(self, from_pt, to_pt, color):
        lines = LineSegs()
        lines.set_color(color)
        lines.move_to(from_pt)
        lines.draw_to(to_pt)
        lines.set_thickness(2.0)
        node = lines.create()
        return NodePath(node)

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
                print('hit_node', hit_node)
                return self.drops.find_neighbours(hit_node)

    def update(self, task):
        dt = globalClock.get_dt()

        if self.play:
            if self.mouseWatcherNode.has_mouse():
                mouse_pos = self.mouseWatcherNode.get_mouse()
                if self.clicked:
                    self.choose(mouse_pos)
                    self.clicked = False

        if self.monitor.update():
            self.play = False

        self.world.do_physics(dt)
        return task.cont


if __name__ == '__main__':
    game = Game()
    game.run()