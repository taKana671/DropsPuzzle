from itertools import product

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletTriangleMeshShape, BulletTriangleMesh, BulletConvexHullShape
from panda3d.core import NodePath, PandaNode, CardMaker
from panda3d.core import Vec3, Vec4, Point3, BitMask32, LColor
from panda3d.core import TransparencyAttrib
from panda3d.core import TransformState

from create_geomnode import Cube, RightTriangularPrism


class Assemblies(NodePath):

    def __init__(self, name, pos, restitution=0.0):
        super().__init__(BulletRigidBodyNode(name))
        self.set_collide_mask(BitMask32.bit(1))
        self.set_pos(pos)
        self.node().set_restitution(restitution)

    def add_block(self, name, obj, pos, hpr):
        block = obj.copy_to(self)
        shape = BulletConvexHullShape()
        shape.add_geom(block.node().get_geom(0))
        self.node().add_shape(shape, TransformState.make_pos_hpr(pos, hpr))

        block.set_name(name)
        block.set_pos(pos)
        block.set_hpr(hpr)

        return block

    def add_card(self, name, rect, hpr, pos):
        card = rect.copy_to(self)
        card.reparent_to(self)
        card.set_name(name)
        card.set_pos_hpr(pos, hpr)

        geom = card.node().get_geom(0)
        mesh = BulletTriangleMesh()
        mesh.add_geom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.node().add_shape(shape, TransformState.make_pos_hpr(pos, hpr))

        return card


# class Card(NodePath):

#     def __init__(self, name, rect, hpr, pos, bit):
#         super().__init__(BulletRigidBodyNode(name))
#         self.set_pos(pos)
#         self.set_hpr(hpr)
#         self.card = rect.copy_to(self)

#         geom = self.card.node().get_geom(0)
#         mesh = BulletTriangleMesh()
#         mesh.add_geom(geom)
#         shape = BulletTriangleMeshShape(mesh, dynamic=False)
#         self.node().add_shape(shape)
#         self.set_collide_mask(BitMask32.bit(bit))


class GameBoard(NodePath):

    def __init__(self, world):
        super().__init__(PandaNode('game_board'))
        self.world = world
        self.create_game_board()

        self.top_l = Point3(-6.5, 0, 13)
        self.top_r = Point3(6.5, 0, 13)

        # self.inseide_dim = (13, 2, 14)

    def create_game_board(self):
        body_color = LColor(0, 0.5, 0, 1)

        # body
        self.body = Assemblies('body', Point3(0, 0, 0), 1.0)
        self.create_body(self.body, body_color)

        # partitions
        self.create_partitions(self.body)

        self.body.reparent_to(self)
        self.world.attach(self.body.node())

    def create_body(self, body, color):
        blocks = [
            [Cube(w=13, d=2, h=10), [(Point3(0, 0, -6), Vec3(0, 0, 0))]],
            [Cube(w=0.5, d=2, h=24), [(Point3(6.75, 0, 1), Vec3(0, 0, 0)), (Point3(-6.75, 0, 1), Vec3(0, 0, 0))]],
            [RightTriangularPrism(w=1.5, h=2), [(Point3(5.75, 0, -0.5), Vec3(180, 90, 0)), (Point3(-5.75, 0, -0.5), Vec3(0, 90, 0))]]
        ]

        for i, (obj, details) in enumerate(blocks):
            for j, (pos, hpr) in enumerate(details):
                block = body.add_block(f'body_{i}{j}', obj, pos, hpr)
                block.set_color(color)

    def create_partitions(self, body):
        size = Vec4(-1, 1, -3, 3)
        # x, y, z = 4.99, 4.99, 4.0

        panels = [
            # [Vec3(0, 0, 0), Point3(0, -y, z)],
            # [Vec3(180, 0, 0), Point3(0, y, z)],
            [Vec3(-90, 0, 0), Point3(-6.5, 0, 16)],
            [Vec3(90, 0, 0), Point3(6.5, 0, 16)]
        ]

        card = CardMaker('card')
        card.set_frame(size)
        rect = NodePath(card.generate())

        for i, (hpr, pos) in enumerate(panels):
            _ = body.add_card(f'panel_{i}', rect, hpr, pos)