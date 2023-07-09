import sys

from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from panda3d.core import MouseButton
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import load_prc_file_data
from panda3d.core import NodePath
from panda3d.core import Vec3, BitMask32, Point3, LColor

from game_board import GameBoard
from drops import Drops
from lights import BasicAmbientLight, BasicDayLight


# load_prc_file_data("", """
#     window-title Panda3D drops puzzle
#     fullscreen false
#     win-size 800 650
#     win-fixed-size 1""")


class Game(ShowBase):

    def __init__(self):
        super().__init__()
        self.set_background_color(LColor(0.57, 0.43, 0.85, 1.0))
        self.disable_mouse()

        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))
        self.debug = self.render.attach_new_node(BulletDebugNode('debug'))
        self.world.set_debug_node(self.debug.node())

        self.game_np = NodePath('game_np')
        self.game_np.reparent_to(self.render)

        self.camera_np = NodePath('camera_np')
        self.camera_np.reparent_to(self.game_np)
        self.camera.set_pos(Point3(0, -35, 5))  # Point3(0, -39, 1)
        self.camera.set_hpr(Vec3(0, -1.6, 0))   # Vec3(0, -2.1, 0)
        # self.camera.look_at(Point3(0, 0, 0))
        self.camera.reparent_to(self.camera_np)

        self.ambient_light = BasicAmbientLight()
        self.ambient_light.reparent_to(self.game_np)
        self.day_light = BasicDayLight()
        self.day_light.reparent_to(self.camera_np)

        self.game_board = GameBoard(self.world)
        self.game_board.reparent_to(self.game_np)

        self.drops = Drops(7, self.world)
        self.drops.reparent_to(self.game_board)

        self.clicked = False
        self.dragging = False
        self.before_mouse_x = None

        self.drops_cnt = 0

        self.accept('escape', sys.exit)
        self.accept('d', self.toggle_debug)
        self.accept('mouse1', self.mouse_click)
        self.accept('mouse1-up', self.mouse_release)

        self.taskMgr.add(self.update, 'update')

        self.accept('x', self.test_move_camera, ['x', 'up'])
        self.accept('shift-x', self.test_move_camera, ['x', 'down'])
        self.accept('y', self.test_move_camera, ['y', 'up'])
        self.accept('shift-y', self.test_move_camera, ['y', 'down'])
        self.accept('z', self.test_move_camera, ['z', 'up'])
        self.accept('shift-z', self.test_move_camera, ['z', 'down'])

        self.accept('h', self.test_move_camera, ['h', 'up'])
        self.accept('shift-h', self.test_move_camera, ['h', 'down'])
        self.accept('p', self.test_move_camera, ['p', 'up'])
        self.accept('shift-p', self.test_move_camera, ['p', 'down'])
        self.accept('r', self.test_move_camera, ['r', 'up'])
        self.accept('shift-r', self.test_move_camera, ['r', 'down'])

    def toggle_debug(self):
        if self.debug.is_hidden():
            self.debug.show()
            self.day_light.node().show_frustum()
        else:
            self.debug.hide()
            self.day_light.node().hide_frustum()

    def mouse_click(self):
        self.dragging = True
        self.dragging_start_time = globalClock.get_frame_time()

    def mouse_release(self):
        if globalClock.get_frame_time() - self.dragging_start_time < 0.2:
            self.clicked = True
        self.dragging = False
        self.before_mouse_x = None

    def rotate_camera(self, mouse_x, dt):
        if self.before_mouse_x is None:
            self.before_mouse_x = mouse_x

        angle = 0

        if (diff := mouse_x - self.before_mouse_x) < 0:
            angle += 90
        elif diff > 0:
            angle -= 90

        angle *= dt
        self.camera_np.set_h(self.camera_np.get_h() + angle)
        self.before_mouse_x = mouse_x
        # print('camera_pos', self.camera.get_pos(), 'camera_hpr', self.camera.get_hpr())
        # print('camera_navi', self.camera_np.get_pos(), 'camera_navi', self.camera_np.get_hpr())
        # print('basic_light', self.day_light.get_pos(), 'basic_light', self.day_light.get_hpr())
        # print('game_np', self.game_np.get_pos(), 'basic_light', self.game_np.get_hpr())
        # print('--------------------------------')

    def update(self, task):
        dt = globalClock.get_dt()

        if self.mouseWatcherNode.has_mouse():
            # mouse_pos = self.mouseWatcherNode.get_mouse()
            mouse_x = self.mouseWatcherNode.get_mouse_x()

            if self.clicked:
                print('clicked')
                # self.drops.fall()
                self.drops_cnt = 40
                self.clicked = False

            if self.dragging:
                if globalClock.get_frame_time() - self.dragging_start_time >= 0.2:
                    print('dragging')
                    self.rotate_camera(mouse_x, dt)

        if self.drops_cnt:
            self.drops.fall(self.drops_cnt)
            if self.drops_cnt > 0:
                self.drops_cnt -= 1


        self.world.do_physics(dt)
        return task.cont

    def test_move_camera(self, direction, move):
        if direction == 'x':
            x = self.camera.get_x()
            if move == 'up':
                self.camera.set_x(x + 2)
            else:
                self.camera.set_x(x - 2)

        if direction == 'y':
            y = self.camera.get_y()
            if move == 'up':
                self.camera.set_y(y + 2)
            else:
                self.camera.set_y(y - 2)

        if direction == 'z':
            z = self.camera.get_z()
            if move == 'up':
                self.camera.set_z(z + 2)
            else:
                self.camera.set_z(z - 2)

        if direction == 'h':
            h = self.camera.get_h()
            if move == 'up':
                self.camera.set_h(h + 2)
            else:
                self.camera.set_h(h - 2)

        if direction == 'p':
            p = self.camera.get_p()
            if move == 'up':
                self.camera.set_p(p + 2)
            else:
                self.camera.set_p(p - 2)

        if direction == 'r':
            r = self.camera.get_r()
            if move == 'up':
                self.camera.set_r(r + 2)
            else:
                self.camera.set_r(r - 2)

        print(f'pos: {self.camera.get_pos()}, hpr: {self.camera.get_hpr()}')
        
        









if __name__ == '__main__':
    game = Game()
    game.run()