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


class Compound(NodePath):

    def __init__(self, name, models, color):
        super().__init__(BulletRigidBodyNode(name))
        self.compound(models)
        self.set_collide_mask(BitMask32.bit(1))
        self.set_color(color)

    def compound(self, models):
        for model in models:
            scale = model.get_scale()
            pos = model.get_pos()
            shape = BulletBoxShape(scale / 2)
            self.node().add_shape(shape, TransformState.make_pos(pos))
            model.reparent_to(self)


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

    def __init__(self, world):
        super().__init__(PandaNode('game_board'))
        self.world = world
        self.create_game_board()

    def create_game_board(self):
        board_color = LColor(0, 0.5, 0, 1)

        models = [model for model in self.create_cover()]
        self.cover = Compound('cover', models, board_color)
        self.cover.set_z(10)
        self.cover.reparent_to(self)
        self.world.attach(self.cover.node())

        models = [model for model in self.create_body()]
        self.body = Compound('cover', models, board_color)
        self.body.set_z(0)
        self.body.reparent_to(self)
        self.world.attach(self.body.node())

        tex = base.loader.load_texture('textures/panel.png')
        self.panels = NodePath('panels')
        self.panels.reparent_to(self)
        self.panels.set_transparency(TransparencyAttrib.MAlpha)
        self.panels.set_texture(tex)

        for panel in self.create_panels():
            panel.reparent_to(self.panels)
            self.world.attach(panel.node())

    def create_cover(self):
        blocks = [
            [Vec3(3, 10, 1), Point3(-3.5, 0, 0)],
            [Vec3(3, 10, 1), Point3(3.5, 0, 0)],
            [Vec3(4, 3, 1), Point3(0, -3.5, 0)],
            [Vec3(4, 3, 1), Point3(0, 3.5, 0)],
        ]

        for i, (scale, pos) in enumerate(blocks):
            model = Cube()
            model.set_name(f'cover_{i}')
            model.set_scale(scale)
            model.set_pos(pos)

            yield model

    def create_body(self):
        blocks = [
            [Vec3(10, 10, 10), Point3(0, 0, -6)],  # bottom
            [Vec3(0.25, 0.25, 11), Point3(4.875, -4.875, 4)],
            [Vec3(0.25, 0.25, 11), Point3(4.875, 4.875, 4)],
            [Vec3(0.25, 0.25, 11), Point3(-4.875, -4.875, 4)],
            [Vec3(0.25, 0.25, 11), Point3(-4.875, 4.875, 4)],
        ]
        for i, (scale, pos) in enumerate(blocks):
            model = Cube()
            model.set_name(f'body_{i}')
            model.set_scale(scale)
            model.set_pos(pos)

            yield model

    def create_panels(self):
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

            yield panel