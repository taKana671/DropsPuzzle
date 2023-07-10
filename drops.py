import random

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletConvexHullShape, BulletSphereShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32

from create_geomnode import Sphere, Polyhedron


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

    def __init__(self, name, geomnode, scale):  # , pos):
        super().__init__(BulletRigidBodyNode(name))
        self.set_scale(scale)
        # self.set_pos(pos)
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


class Convex(NodePath):

    def __init__(self, name, geomnode, scale):
        super().__init__(BulletRigidBodyNode(name))
        self.set_scale(scale)
        # self.set_pos(pos)
        self.convex = geomnode.copy_to(self)

        shape = BulletConvexHullShape()
        shape.add_geom(geomnode.node().get_geom(0))
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1))
        self.node().set_mass(1)
        self.node().deactivation_enabled = True
        self.node().set_restitution(0.7)


class Drops(NodePath):

    def __init__(self, world, pipe):
        super().__init__(PandaNode('drops'))
        self.world = world
        self.setup(pipe)

        self.drops = dict(
            drops1=Ball('drops1', Sphere(), Vec3(0.5)),
            drops2=Convex('drops2', Polyhedron('icosidodecahedron'), Vec3(0.6))
        )

    def setup(self, pipe):
        end, tip = pipe.get_tight_bounds()
        pipe_size = tip - end
        pipe_pos = pipe.get_pos()

        self.end_x = pipe_size.x / 2
        self.end_y = pipe_size.y / 2
        self.start_z = int(pipe_pos.z - pipe_size.z / 2)
        self.end_z = int(pipe_pos.z + pipe_size.z / 2)

    def get_pos(self, pt, r):
        # x = random.uniform(-2, 2)
        # y = random.uniform(-2, 2)
        # z = random.randint(13, 15)

        x = random.uniform(-self.end_x, self.end_x)
        y = random.uniform(-self.end_y, self.end_y)
        z = random.randint(self.start_z, self.end_z)
    

        # pos = Point3(x, y, z)
        # dist = ((x - center.x) ** 2 + (y - center.y) ** 2 + (z - center.z) ** 2) ** 0.5
        if ((x - pt.x) ** 2 + (y - pt.y) ** 2) ** 0.5 <= r:
            print('return')
            return Point3(x, y, z)

        return self.get_pos(pt, r)

    def fall(self, cnt):
        obj = self.drops['drops2']
        end, tip = obj.get_tight_bounds()
        r = self.end_x - (tip - end).x / 2

        for i in range(cnt):
            pos = self.get_pos(Point3(0, 0, 0), r)
            s = obj.copy_to(self)
            s.set_pos(pos)
            s.set_name(f'drop_{i}')
            self.world.attach(s.node())

