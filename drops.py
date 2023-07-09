import random

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletConvexHullShape, BulletSphereShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32

from create_geomnode import Sphere


class FallingBlock(NodePath):

    def __init__(self, name, geomnode, scale, hpr, pos):
        super().__init__(BulletRigidBodyNode(name))
        self.set_scale(scale)
        self.set_pos(pos)
        self.set_hpr(hpr)
        self.set_color((0, 0, 1, 1))
        self.block = geomnode.copy_to(self)

        geom = self.block.node().get_geom(0)
        shape = BulletConvexHullShape()
        shape.add_geom(geom)
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1))
        self.node().set_mass(1)


class Ball(NodePath):

    def __init__(self, name, geomnode, scale, pos):
        super().__init__(BulletRigidBodyNode(name))
        self.set_scale(scale)
        self.set_pos(pos)
        # self.set_color((0, 0, 1, 1))
        self.sphere = geomnode.copy_to(self)
        end, tip = self.sphere.get_tight_bounds()
        size = tip - end
        shape = BulletSphereShape(size.z / 2)
        # shape = BulletSphereShape(0.5)
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1))
        self.node().set_mass(1)
        self.node().deactivation_enabled = True
        self.node().set_restitution(0.7)


class Drops(NodePath):

    def __init__(self, start_z, world):
        super().__init__(PandaNode('drops'))
        self.world = world
        self.start_z = start_z
        self.sphere = Sphere()
        # sphere_maker = SphereGeomMaker()
        # self.sphere = NodePath(sphere_maker.make_geomnode())
        # self.sphere.set_two_sided(True)

    def get_pos(self, pt, r):
        x = random.uniform(-2, 2)
        y = random.uniform(-2, 2)
        z = random.randint(13, 15)
        # print(x, y, z)

        # pos = Point3(x, y, z)
        # dist = ((x - center.x) ** 2 + (y - center.y) ** 2 + (z - center.z) ** 2) ** 0.5
        if ((x - pt.x) ** 2 + (y - pt.y) ** 2) ** 0.5 <= r:
            print('return')
            return Point3(x, y, z)

        return self.get_pos(pt, r)


    def fall(self, idx):
    # def fall(self):
        # start_z = 13

        # for i in range(4):
        #     z = start_z + i
        #     for j, (x, y) in enumerate([(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]):
        #         pos = Point3(x, y, z)
        #         s = Sphere(f'drop_{i}{j}', self.sphere, Vec3(0.5), pos)
        #         s.reparent_to(self)
        #         self.world.attach(s.node())

        pos = self.get_pos(Point3(0, 0, 0), 1.5)

        s = Ball(f'drop_{idx}', self.sphere, Vec3(0.5), pos)
        s.reparent_to(self)
        self.world.attach(s.node())


