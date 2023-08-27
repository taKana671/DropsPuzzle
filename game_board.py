# from typing import NamedTuple

from direct.gui.DirectGui import OnscreenText
from panda3d.bullet import BulletRigidBodyNode, BulletGhostNode
from panda3d.bullet import BulletTriangleMeshShape, BulletTriangleMesh, BulletConvexHullShape, BulletBoxShape
from panda3d.core import NodePath, PandaNode, CardMaker
from panda3d.core import Vec3, Point3, BitMask32, LColor
from panda3d.core import TextNode
from panda3d.core import TransformState

from create_geomnode import Cube, RightTriangularPrism


class Cabinet(NodePath):

    def __init__(self, pos, restitution=0.0):
        super().__init__(BulletRigidBodyNode('cabibet'))
        self.set_collide_mask(BitMask32.bit(1))
        self.set_pos(pos)
        self.node().set_restitution(restitution)
        self.assemble()

        self.from_pos = Point3(-6.5, 0, 13.5)
        self.to_pos = Point3(6.5, 0, 13.5)

    def assemble(self):
        color = LColor(0, 0.5, 0, 1)

        li = {
            Cube(w=13, d=2, h=10): [((0, 0, -6), (0, 0, 0))],
            Cube(w=0.5, d=2, h=24): [(Point3(6.75, 0, 1), Vec3(0, 0, 0)), (Point3(-6.75, 0, 1), Vec3(0, 0, 0))],
            RightTriangularPrism(w=1.5, h=2): [(Point3(5.75, 0, -0.5), Vec3(180, 90, 0)), (Point3(-5.75, 0, -0.5), Vec3(0, 90, 0))]
        }

        for i, (np, pos_hpr) in enumerate(li.items()):
            for j, (pos, hpr) in enumerate(pos_hpr):
                name = f'cabinet_{i}{j}'
                self.make_convex_shape(name, np, pos, hpr, color)

        li = [
            [Point3(-6.5, 0, 16), Vec3(-90, 0, 0)],
            [Point3(6.5, 0, 16), Vec3(90, 0, 0)]
        ]

        cm = CardMaker('card')
        cm.set_frame(-1, 1, -3, 3)
        geomnode = cm.generate()
        np = NodePath(geomnode)

        for i, (pos, hpr) in enumerate(li):
            name = f'fence_{i}'
            self.make_mesh_shape(name, np, pos, hpr)

    def make_convex_shape(self, name, np, pos, hpr, color):
        model = np.copy_to(self)
        shape = BulletConvexHullShape()
        shape.add_geom(model.node().get_geom(0))
        self.node().add_shape(shape, TransformState.make_pos_hpr(pos, hpr))
        model.set_name(name)
        model.set_pos(pos)
        model.set_hpr(hpr)
        model.set_color(color)

    def make_mesh_shape(self, name, np, pos, hpr):
        model = np.copy_to(self)
        model.set_name(name)
        model.set_pos_hpr(pos, hpr)

        geom = model.node().get_geom(0)
        mesh = BulletTriangleMesh()
        mesh.add_geom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.node().add_shape(shape, TransformState.make_pos_hpr(pos, hpr))

    def is_outside(self, x, z):
        if -6.5 < x < 6.5 and 13.0 < z < 16.0:
            return True
        
        # if -6.5 < x < 6.5 and z < 13.5:
        #     return True

    # def show_gameover_line(self):


class GameOverZone(NodePath):

    def __init__(self, pos, size, bit):
        super().__init__(BulletGhostNode('sensor'))
        shape = BulletBoxShape(size)
        self.node().add_shape(shape)
        self.set_pos(pos)
        self.set_collide_mask(BitMask32.bit(bit))

    def detect(self):
        for nd in self.node().get_overlapping_nodes():
            yield nd


class GameBoard(NodePath):

    def __init__(self, world):
        super().__init__(PandaNode('game_board'))
        self.world = world

        self.cabinet = Cabinet(Point3(0, 0, 0), 1.0)
        self.cabinet.reparent_to(self)
        self.world.attach(self.cabinet.node())

        self.score_display = NumberDisplay('score_display', (0.05, -0.2), text='0')
        self.merge_display = NumberDisplay('num_display', (2.5, -0.2))

        # self.gameover_zone = GameOverZone(Point3(0, 0, 15), Vec3(6.5, 0.5, 1), 3)
        # self.gameover_zone.reparent_to(self)
        # self.world.attach(self.gameover_zone.node())

    # def display_score(self, num):
    #     self.score_display.add(num)

    # def display_count(self, num):
    #     self.merge_display.add(num)

    def is_outside_cabinet(self, np):
        return self.cabinet.is_outside(np.get_x(), np.get_z())
        # if self.cabinet.is_inside(np.get_x(), np.get_z()):
        #     return False
        # return True

    def detect(self):
        result = self.world.ray_test_closest(
            self.cabinet.from_pos,
            self.cabinet.to_pos,
            BitMask32.bit(3)
        )
        if result.has_hit():
            # print(result.get_node().set_angular_velocity((0, 0, 0)))
            if result.get_node().linear_velocity.length() == 0:
                return True

    # def detect(self):
    #     return [nd for nd in self.gameover_zone.detect() if nd.linear_velocity.length() == 0]


class NumberDisplay(OnscreenText):

    def __init__(self, name, pos, scale=0.1, fg=(1, 1, 1, 1), text=''):
        font = base.loader.loadFont('font/SegUIVar.ttf')
        super().__init__(
            text=text,
            parent=base.a2dTopLeft,
            align=TextNode.ALeft,
            pos=pos,
            scale=scale,
            font=font,
            fg=fg,
            mayChange=True
        )
        self.set_name(name)

    def add(self, num):
        if not (t := self.getText()):
            t = '0'
        added = int(t) + num
        self.setText(str(added))

    @property
    def score(self):
        if not (score := self.getText()):
            score = 0
        return int(score)