import random

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletConvexHullShape, BulletSphereShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32

from create_geomnode import Cylinder, SphericalShape, SphereGeomMaker


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


class Sphere(NodePath):

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
        self.node().set_mass(10)
        self.node().deactivation_enabled = True


class Drops(NodePath):

    def __init__(self, start_z, world):
        super().__init__(PandaNode('drops'))
        self.world = world
        self.start_z = start_z
        sphere_maker = SphereGeomMaker()
        self.sphere = NodePath(sphere_maker.make_geomnode())
        self.sphere.set_two_sided(True)

    def fall(self, idx):
        # for i in range(20):
        # x = random.uniform(-3, 3)
        # y = random.uniform(-3, 3)

        pos = Point3(0, 0, 13)
        s = Sphere(f'drop_{idx}', self.sphere, Vec3(0.5), pos)
        s.reparent_to(self)
        self.world.attach(s.node())


        # cylinder = Cylinder(segs_c=12, height=0.8)
        # b = FallingBlock('b', cylinder, Vec3(1.5, 1.5, 1), Vec3(0, 90, 0), self.start_pos)
        # b.reparent_to(self)
        # self.world.attach(b.node())



