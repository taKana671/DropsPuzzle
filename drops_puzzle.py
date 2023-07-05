import sys

from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import load_prc_file_data
from panda3d.core import Vec3, BitMask32, Point3, LColor

from game_board import GameBoard
from falling_block import Blocks
from lights import BasicAmbientLight, BasicDayLight


load_prc_file_data("", """
    window-title Panda3D Tumu Tumu
    fullscreen false
    win-size 800 650
    win-fixed-size 1""")


class Game(ShowBase):

    def __init__(self):
        super().__init__()
        self.set_background_color(LColor(0.57, 0.43, 0.85, 1.0))
        self.disable_mouse()
        self.camera.set_pos(Point3(0, -35, 5))
        self.camera.look_at(Point3(0, 0, 0))

        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))
        self.debug = self.render.attach_new_node(BulletDebugNode('debug'))
        self.world.set_debug_node(self.debug.node())

        self.ambient_light = BasicAmbientLight()
        self.basic_light = BasicDayLight()

        self.board_pos = Point3(0, -5, -4)
        self.board = GameBoard(self.board_pos, self.world)
        self.board.reparent_to(self.render)

        self.blocks = Blocks(Point3(0, -5, 3), self.world)
        self.blocks.reparent_to(self.render)

        self.blocks.fall()

        self.accept('escape', sys.exit)
        self.accept('d', self.toggle_debug)
        self.taskMgr.add(self.update, 'update')



    def toggle_debug(self):
        if self.debug.is_hidden():
            self.debug.show()
        else:
            self.debug.hide()

    def update(self, task):
        dt = globalClock.get_dt()

        self.world.do_physics(dt)
        return task.cont


if __name__ == '__main__':
    game = Game()
    game.run()