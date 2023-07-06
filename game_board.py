from itertools import product

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletTriangleMeshShape, BulletTriangleMesh
from panda3d.core import NodePath, PandaNode, CardMaker
from panda3d.core import Vec3, Vec4, Point3, BitMask32, LColor
from panda3d.core import TransparencyAttrib

from create_geomnode import Cube


class Block(NodePath):

    def __init__(self, name, geomnode, scale, hpr, pos):
        super().__init__(BulletRigidBodyNode(name))
        self.set_scale(scale)
        self.set_pos(pos)
        self.set_hpr(hpr)
        self.block = geomnode.copy_to(self)

        end, tip = self.block.get_tight_bounds()
        shape = BulletBoxShape((tip - end) / 2)
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1))


class Card(NodePath):

    def __init__(self, name, geomnode, hpr, pos):
        super().__init__(BulletRigidBodyNode(name))
        self.set_pos(pos)
        self.set_hpr(hpr)
        self.card = geomnode.copy_to(self)

        geom = geomnode.node().get_geom(0)
        mesh = BulletTriangleMesh()
        mesh.add_geom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1))


class GameBoard(NodePath):

    def __init__(self, pos, world):
        super().__init__(PandaNode('game_board'))
        self.world = world
        self.set_pos(pos)
        self.create_board()

    def create_board(self):
        geomnode = Cube()
        board_color = LColor(0, 0.5, 0, 1)
        tex = base.loader.load_texture('textures/panel.png')

        self.create_body(geomnode, board_color)
        self.create_frames(geomnode, board_color)
        self.create_panels(tex)
        self.flatten_strong()

    def create_body(self, geomnode, color):
        body_np = NodePath('body')
        body_np.reparent_to(self)
        body_np.set_color(color)
        hpr = Vec3(0, 0, 0)

        plates = [
            [Vec3(10, 10, 10), Point3(0, 0, -6)],  # top
            [Vec3(10, 10, 1), Point3(0, 0, 10)],   # base
        ]

        for i, (scale, pos) in enumerate(plates):
            plate = Block(f'body_{i}', geomnode, scale, hpr, pos)
            plate.reparent_to(body_np)
            self.world.attach(plate.node())

    def create_frames(self, geomnode, color):
        frames_np = NodePath('frames')
        frames_np.reparent_to(self)
        frames_np.set_color(color)

        scale = Vec3(0.25, 0.25, 11)
        hpr = Vec3(0, 0, 0)

        for i, (x, y) in enumerate(product((4.875, -4.875), (4.875, -4.875))):
            pos = Point3(x, y, 4)
            plate = Block(f'frame_{i}', geomnode, scale, hpr, pos)
            plate.reparent_to(frames_np)
            self.world.attach(plate.node())

    def create_panels(self, tex):
        panels_np = NodePath('panels')
        panels_np.reparent_to(self)
        panels_np.set_transparency(TransparencyAttrib.MAlpha)
        panels_np.set_texture(tex)

        size = Vec4(5, -5, -5.5, 5.5)
        x, y, z = 4.99, 4.99, 4.0

        panels = [
            [Vec3(180, 0, 0), Point3(0, -y, z)],
            [Vec3(0, 0, 0), Point3(0, y, z)],
            [Vec3(90, 0, 0), Point3(-x, 0, z)],
            [Vec3(-90, 0, 0), Point3(x, 0, z)]
        ]

        for i, (hpr, pos) in enumerate(panels):
            card = CardMaker('card')
            card.set_frame(size)
            geomnode = NodePath(card.generate())

            panel = Card(f'panel_{i}', geomnode, hpr, pos)
            panel.reparent_to(panels_np)
            self.world.attach(panel.node())