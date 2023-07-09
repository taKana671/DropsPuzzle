from itertools import product

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletTriangleMeshShape, BulletTriangleMesh
from panda3d.core import NodePath, PandaNode, CardMaker
from panda3d.core import Vec3, Vec4, Point3, BitMask32, LColor
from panda3d.core import TransparencyAttrib
from panda3d.core import TransformState

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


class Assemblies(NodePath):

    def __init__(self, name, pos, restitution=0.0):
        super().__init__(BulletRigidBodyNode(name))
        self.set_collide_mask(BitMask32.bit(1))
        self.set_pos(pos)
        self.node().set_restitution(restitution)

    def add_block(self, name, cube, scale, pos):
        block = cube.copy_to(self)
        block.set_name(name)
        block.set_scale(scale)
        block.set_pos(pos)
        end, tip = block.get_tight_bounds()
        shape = BulletBoxShape((tip - end) / 2)
        self.node().add_shape(shape, TransformState.make_pos(pos))

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


class GameBoard(NodePath):

    def __init__(self, world):
        super().__init__(PandaNode('game_board'))
        self.world = world
        self.create_game_board()

    def create_game_board(self):
        body_color = LColor(0, 0.5, 0, 1)
        cube = Cube()

        # top
        self.cover = Assemblies('cover', Point3(0, 0, 10))
        self.create_cover(cube, self.cover, body_color)
        self.cover.reparent_to(self)
        self.world.attach(self.cover.node())

        # body
        self.body = Assemblies('body', Point3(0, 0, 0), 1.0)
        self.create_body(cube, self.body, body_color)

        # transparent panels
        self.body.set_transparency(TransparencyAttrib.MAlpha)
        tex = base.loader.load_texture('textures/panel.png')
        self.create_panels(self.body, tex)

        self.body.reparent_to(self)
        self.world.attach(self.body.node())

        # feed pipe
        self.pipe = Assemblies('pipe', Point3(0, 0, 12.5))
        self.create_feed_pipe(self.pipe)
        self.pipe.reparent_to(self)
        self.world.attach(self.pipe.node())
        self.pipe.hide()

        self.flatten_strong()

    def create_cover(self, cube, cover, color):
        blocks = [
            [Vec3(3, 10, 1), (Point3(x, 0, 0) for x in (3.5, -3.5))],
            [Vec3(4, 3, 1), (Point3(0, y, 0) for y in (3.5, -3.5))],
        ]

        for i, (scale, pos_gen) in enumerate(blocks):
            for j, pos in enumerate(pos_gen):
                block = cover.add_block(f'cover_{i}{j}', cube, scale, pos)
                block.set_color(color)

    def create_body(self, cube, body, color):
        blocks = [
            [Vec3(10, 10, 10), [Point3(0, 0, -6)]],
            [Vec3(0.25, 0.25, 11), (Point3(x, y, 4) for x, y in product((4.875, -4.875), repeat=2))]
        ]

        for i, (scale, pos_gen) in enumerate(blocks):
            for j, pos in enumerate(pos_gen):
                block = body.add_block(f'body_{i}{j}', cube, scale, pos)
                block.set_color(color)

    def create_panels(self, body, tex):
        size = Vec4(-5, 5, -5.5, 5.5)
        x, y, z = 4.99, 4.99, 4.0

        panels = [
            [Vec3(0, 0, 0), Point3(0, -y, z)],
            [Vec3(180, 0, 0), Point3(0, y, z)],
            [Vec3(-90, 0, 0), Point3(-x, 0, z)],
            [Vec3(90, 0, 0), Point3(x, 0, z)]
        ]

        card = CardMaker('card')
        card.set_frame(size)
        rect = NodePath(card.generate())

        for i, (hpr, pos) in enumerate(panels):
            panel = body.add_card(f'panel_{i}', rect, hpr, pos)
            panel.set_texture(tex)

    def create_feed_pipe(self, pipe):
        size = Vec4(-2, 2, -3, 3)
        x, y, z = 2, 2, 0

        panels = [
            [Vec3(0, 0, 0), Point3(0, -y, z)],
            [Vec3(180, 0, 0), Point3(0, y, z)],
            [Vec3(-90, 0, 0), Point3(-x, 0, z)],
            [Vec3(90, 0, 0), Point3(x, 0, z)]
        ]

        card = CardMaker('card')
        card.set_frame(size)
        rect = NodePath(card.generate())

        for i, (hpr, pos) in enumerate(panels):
            pipe.add_card(f'pipe_{i}', rect, hpr, pos)