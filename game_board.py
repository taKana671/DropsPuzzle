from typing import NamedTuple

from direct.gui.DirectGui import OnscreenText
from panda3d.bullet import BulletRigidBodyNode, BulletGhostNode
from panda3d.bullet import BulletTriangleMeshShape, BulletTriangleMesh
from panda3d.bullet import BulletConvexHullShape, BulletBoxShape, BulletPlaneShape
from panda3d.core import NodePath, PandaNode, CardMaker
from panda3d.core import Vec3, Point3, BitMask32, LColor
from panda3d.core import TextNode
from panda3d.core import TransformState

from create_geomnode import Cube, RightTriangularPrism


class Dimensions(NamedTuple):

    center: Vec3
    width: float
    height: float

    @property
    def left(self):
        return -self.width / 2

    @property
    def right(self):
        return self.width / 2

    @property
    def top(self):
        return self.height / 2 + 1


class Cabinet(NodePath):

    def __init__(self, pos, restitution=0.0):
        super().__init__(BulletRigidBodyNode('cabibet'))
        self.set_collide_mask(BitMask32.bit(1))
        self.set_pos(pos)
        self.node().set_restitution(restitution)
        self.dims = Dimensions(Vec3(0, 0, 0), 13, 24)
        self.assemble()

    def assemble(self):
        color = LColor(0, 0.5, 0, 1)

        li = {
            Cube(w=13, d=2, h=10): [((0, 0, -5), (0, 0, 0))],
            Cube(w=0.5, d=2, h=24): [(Point3(6.75, 0, 0), Vec3(0, 0, 0)), (Point3(-6.75, 0, 0), Vec3(0, 0, 0))],
            RightTriangularPrism(w=1.5, h=2): [(Point3(5.75, 0, 0.5), Vec3(180, 90, 0)), (Point3(-5.75, 0, 0.5), Vec3(0, 90, 0))]
        }

        for i, (np, pos_hpr) in enumerate(li.items()):
            for j, (pos, hpr) in enumerate(pos_hpr):
                name = f'cabinet_{i}{j}'
                self.make_convex_shape(name, np, pos, hpr, color)

        li = [
            [Point3(-6.5, 0, 15), Vec3(-90, 0, 0)],
            [Point3(6.5, 0, 15), Vec3(90, 0, 0)]
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

    def is_inside(self, pos):
        if self.dims.left < pos.x < self.dims.right \
                and pos.z <= self.dims.top:
            return True


class Sensor(NodePath):

    def __init__(self):
        super().__init__(BulletRigidBodyNode('sensor'))
        cm = CardMaker('card')
        cm.set_frame(-5, 5, -1, 1)
        geomnode = cm.generate()
        geom = geomnode.get_geom(0)
        mesh = BulletTriangleMesh()
        mesh.add_geom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        # self.card = self.attach_new_node(geomnode)
        self.node().add_shape(shape)
        self.set_p(-90)
        self.set_collide_mask(BitMask32.bit(3))


class GameBoard(NodePath):

    def __init__(self, world):
        super().__init__(PandaNode('game_board'))
        self.world = world

        self.cabinet = Cabinet(Point3(0, 0, 0), 1.0)
        self.cabinet.reparent_to(self)
        self.world.attach(self.cabinet.node())

        # self.floor = Floor()
        # self.floor.reparent_to(self)
        # self.world.attach(self.floor.node())

        self.score_display = NumberDisplay('score_display', (0.05, -0.2), text='0')
        self.merge_display = NumberDisplay('num_display', (2.5, -0.2))

        self.sensor = Sensor()
        self.sensor.reparent_to(self)
        self.world.attach(self.sensor.node())

    def is_overflow(self, np):
        if np.get_z() > self.cabinet.dims.top:
            return True

    def is_in_gameover_zone(self, np):
        pos = np.get_pos()
        if self.cabinet.dims.left < pos.x < self.cabinet.dims.right \
                and pos.z > self.cabinet.dims.top:
            return True

    def initialize(self):
        self.score_display.setText('0')
        self.merge_display.setText('')

    def show_displays(self):
        self.score_display.show()
        self.merge_display.show()

    def hide_displays(self):
        self.score_display.hide()
        self.merge_display.hide()

    def sense_contact(self):
        for con in self.world.contact_test(self.sensor.node(), use_filter=True).get_contacts():
            nd = con.get_node0()
            yield nd


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

    def show_score(self, num, positive_only=False):
        if positive_only:
            if not num:
                self.setText('')
                return

        self.setText(str(num))