from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape, BulletPlaneShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32
from panda3d.core import TransparencyAttrib

from create_geomnode import Cube


class Plate(NodePath):

    def __init__(self, name, geomnode, scale, hpr, pos):
        super().__init__(BulletRigidBodyNode(name))
        self.set_scale(scale)
        self.set_pos(pos)
        self.set_hpr(hpr)
        self.set_color((0, 0.5, 0, 1))
        self.plate = geomnode.copy_to(self)
        end, tip = self.plate.get_tight_bounds()
        shape = BulletBoxShape((tip - end) / 2)
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1))


class Wall(NodePath):

    def __init__(self, name, normal, pos):
        super().__init__(BulletRigidBodyNode(name))
        self.set_collide_mask(BitMask32.bit(1))
        shape = BulletPlaneShape(normal, 0)
        self.node().add_shape(shape)
        self.set_pos(pos)


class GameBoard(NodePath):

    def __init__(self, pos, world):
        super().__init__(PandaNode('game_board'))
        self.world = world
        self.set_pos(pos)
        self.create_board()
#         plate = Plate('test', Cube(), Vec3(0.5), Vec3(0, 0, 0), Point3(0, 0, 2))
#         plate.node().set_mass(1)
#         plate.reparent_to(self)
#         self.world.attach(plate.node())

    def create_board(self):
        plates = NodePath('plates')
        plates.reparent_to(self)
        self.create_plates(plates)

        walls = NodePath('walls')
        walls.reparent_to(self)
        self.create_walls(walls)

        self.flatten_strong()

    def create_plates(self, parent):
        geomnode = Cube()

        plates = [
            [Vec3(6, 6, 10), Vec3(0, 0, 10), Point3(-3, 0, -6)],
            [Vec3(6, 6, 10), Vec3(0, 0, -10), Point3(3, 0, -6)],
            [Vec3(10, 6, 1), Vec3(0, 0, 0), Point3(0, 0, 10)]
        ]

        for i, (scale, hpr, pos) in enumerate(plates):
            plate = Plate(f'plate_{i}', geomnode, scale, hpr, pos)
            # plate.set_transparency(TransparencyAttrib.MAlpha)
            # plate.set_texture(base.loader.load_texture('test.png'))
            plate.reparent_to(parent)
            self.world.attach(plate.node())

    def create_walls(self, parent):
        walls = [
            [Vec3.back(), Point3(0, 0.5, 0)],
            [Vec3.forward(), Point3(0, -0.5, 0)],
            [Vec3.right(), Point3(-9, 0, 0)],
            [Vec3.left(), Point3(9, 0, 0)]
        ]

        for i, (normal, pos) in enumerate(walls):
            wall = Wall(f'wall_{i}', normal, pos)
            wall.reparent_to(parent)
            self.world.attach(wall.node())



# class Plate(NodePath):

#     def __init__(self, name, geomnode, scale, hpr, pos):
#         super().__init__(BulletRigidBodyNode(name))
#         self.set_scale(scale)
#         self.set_pos(pos)
#         self.set_hpr(hpr)
#         # self.set_color((0, 0.5, 0, 1))
#         self.plate = geomnode.copy_to(self)
#         end, tip = self.plate.get_tight_bounds()
#         shape = BulletBoxShape((tip - end) / 2)
#         self.node().add_shape(shape)
#         self.set_collide_mask(BitMask32.bit(1))


# class Wall(NodePath):

#     def __init__(self, name, normal, pos):
#         super().__init__(BulletRigidBodyNode(name))
#         self.set_collide_mask(BitMask32.bit(1))
#         shape = BulletPlaneShape(normal, 0)
#         self.node().add_shape(shape)
#         self.set_pos(pos)


# class GameBoard(NodePath):

#     def __init__(self, pos, world):
#         super().__init__(PandaNode('game_board'))
#         self.world = world
#         self.set_pos(pos)
#         self.create_board()
# #         plate = Plate('test', Cube(), Vec3(0.5), Vec3(0, 0, 0), Point3(0, 0, 2))
# #         plate.node().set_mass(1)
# #         plate.reparent_to(self)
# #         self.world.attach(plate.node())

#     def create_board(self):
#         plates = NodePath('plates')
#         plates.reparent_to(self)
#         self.create_plates(plates)

#         walls = NodePath('walls')
#         walls.reparent_to(self)
#         self.create_walls(walls)

#         self.flatten_strong()

#     def create_plates(self, parent):
#         geomnode = Cube()

#         plates = [
#             [Vec3(10, 1, 10), Vec3(0, 0, 10), Point3(-4.9, 0, -7)],
#             [Vec3(10, 1, 10), Vec3(0, 0, -10), Point3(4.9, 0, -7)],
#             [Vec3(18, 1, 3), Vec3(0, 0, 0), Point3(0, 0, 13)]
#         ]

#         for i, (scale, hpr, pos) in enumerate(plates):
#             plate = Plate(f'plate_{i}', geomnode, scale, hpr, pos)
#             plate.set_transparency(TransparencyAttrib.MAlpha)
#             plate.set_texture(base.loader.load_texture('test.png'))
#             plate.reparent_to(parent)
#             self.world.attach(plate.node())

#     def create_walls(self, parent):
#         walls = [
#             [Vec3.back(), Point3(0, 0.5, 0)],
#             [Vec3.forward(), Point3(0, -0.5, 0)],
#             [Vec3.right(), Point3(-9, 0, 0)],
#             [Vec3.left(), Point3(9, 0, 0)]
#         ]

#         for i, (normal, pos) in enumerate(walls):
#             wall = Wall(f'wall_{i}', normal, pos)
#             wall.reparent_to(parent)
#             self.world.attach(wall.node())