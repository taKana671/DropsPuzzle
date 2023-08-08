import random
from collections import deque
from dataclasses import dataclass

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletConvexHullShape, BulletSphereShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32

from panda3d.core import TransparencyAttrib
# from direct.filter.FilterManager import FilterManager
# from panda3d.core import TransparencyAttrib
# from direct.filter.CommonFilters import CommonFilters


from create_geomnode import Sphere, Polyhedron
from visual_effects import VisualEffects


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
        self.node().set_tag('type', name)
        # self.set_pos(pos)
        # self.set_color((0, 0, 1, 1))
        self.sphere = geomnode.copy_to(self)
        end, tip = self.sphere.get_tight_bounds()
        size = tip - end
        shape = BulletSphereShape(size.z / 2)
        # shape = BulletSphereShape(0.5)
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1) | BitMask32.bit(2))
        self.node().set_mass(1)
        # self.node().deactivation_enabled = True
        self.node().set_restitution(0.7)


class Convex(NodePath):

    def __init__(self, tag, geomnode, scale):
        super().__init__(BulletRigidBodyNode(f'drop_{tag}'))
        self.set_scale(scale)
        self.node().set_tag('stage', tag)
        geomnode.reparent_to(self)
        # make drop move only x axis
        self.node().set_linear_factor(Vec3(1, 0, 1))

        shape = BulletConvexHullShape()
        shape.add_geom(geomnode.node().get_geom(0))
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1) | BitMask32.bit(2) | BitMask32.bit(3))
        self.node().set_mass(1)
        self.node().deactivation_enabled = False
        self.node().set_restitution(0.3)  # 0.7
        self.set_transparency(TransparencyAttrib.MAlpha)
        self.rad = self.get_bounds().get_radius()


@dataclass
class Drop:

    model: Convex
    merge_into: Convex
    vfx: str
    scale: float
    proportion: float = None
    # cnt: int = 0


class Drops(NodePath):

    def __init__(self, world, game_board, parent):
        super().__init__(PandaNode('drops'))
        self.world = world
        self.game_board = game_board
        # self.setup()

        self.new_drop = None
        self.drops_q = deque()
        self.serial = 0
        self.vfx = VisualEffects()

        self.drops = {'d1'}

        d1 = Convex('d1', Sphere(), Vec3(0.5))
        d2 = Convex('d2', Polyhedron('icosidodecahedron'), Vec3(0.75))
        d3 = Convex('d3', Polyhedron('truncated_octahedron'), Vec3(1.0))

        self.drops_tbl = {
            'd1': Drop(
                model=d1,
                merge_into=d2,
                vfx='textures/boom_fire.png',
                scale=2,
                proportion=1.0),
            'd2': Drop(
                model=d2,
                merge_into=d3,
                vfx='textures/m_blast.png',
                scale=2.5,
                proportion=0.3),
            'd3': Drop(
                model=d3,
                merge_into=None,
                vfx='textures/m_blast.png',
                scale=3,
                proportion=0.15),
        }

        # self.set_transparency(TransparencyAttrib.MAlpha)
        # filters = CommonFilters(base.win, base.cam)
        # filters.setBloom(size="large", blend=(1, 0, 0, 1), desat=0.0)
        # filters.setBloom(size="large", blend=(1, 0, 0, 0))

    def setup(self):
        end, tip = self.game_board.pipe.get_tight_bounds()
        pipe_size = tip - end
        pipe_pos = self.game_board.pipe.get_pos()

        self.end_x = pipe_size.x / 2
        self.end_y = pipe_size.y / 2
        self.start_z = int(pipe_pos.z - pipe_size.z / 2)
        self.end_z = int(pipe_pos.z + pipe_size.z / 2)

    def _check(self, drop, pos, rad):
        d_pos, d_rad = drop
        dist = ((d_pos.x - pos.x) ** 2 + (d_pos.y - pos.y) ** 2 + (d_pos.z - pos.z) ** 2) ** 0.5

        if dist > rad + d_rad:
            return True
        return False

    def get_start_pos(self, rad):
        floating_np = [(np.get_pos(), np.get_bounds().get_radius()) for np in self.get_children() if np.get_z() >= 16]

        for _ in range(3):
            y = 0
            x = random.uniform(-6, 6)
            z = random.uniform(16, 19)
            pos = Point3(x, y, z)

            if all(self._check(np, pos, rad) for np in floating_np):
                return pos

        return None

    def create_new_drop(self, drop, pos):
        new_drop = drop.copy_to(self)
        new_drop.set_name(f'drop_{self.serial}')
        self.serial += 1
        new_drop.set_pos(pos)
        self.world.attach(new_drop.node())

    def fall(self):
        if len(self.drops_q):
            key = self.drops_q[0]
            drop = self.drops_tbl[key].model

            if pos := self.get_start_pos(drop.rad):
                _ = self.drops_q.popleft()
                self.create_new_drop(drop, pos)

    def _find(self, node, tag, neighbours):
        neighbours.append(node)

        for con in self.world.contact_test(node, use_filter=True).get_contacts():
            if (con_node := con.get_node1()) != self.game_board.body.node():
                if con_node not in neighbours \
                        and con_node.get_tag('stage') == tag:
                    self._find(con_node, tag, neighbours)

    def find_neighbours(self, node):
        self.neighbours = []
        tag = node.get_tag('stage')
        self._find(node, tag, self.neighbours)

        if len(self.neighbours) >= 2:
            drop = self.drops_tbl[tag]
            self.new_drop = drop.merge_into

            self.vfx.start_disappear(drop.vfx, drop.scale, *self.neighbours)
            return True

    def add(self, cnt):
        props = {}
        total = 0

        for key in self.drops:
            if key != 'd1':
                prop = self.drops_tbl[key].proportion
                if (num := int(cnt * prop)) > 0:
                    props[key] = num
                    total += num

        props['d1'] = cnt - total

        self.drops_q.extend(
            random.sample([num for num, c in props.items() for _ in range(c)], cnt)
        )

    def merge(self):
        if not self.vfx.is_playing:
            if self.new_drop:
                node = self.neighbours[0]
                pos = NodePath(node).get_pos()
                self.create_new_drop(self.new_drop, pos)
                self.drops.add(self.new_drop.get_tag('stage'))

            for node in self.neighbours:
                self.world.remove(node)
                np = NodePath(node)
                np.remove_node()

            return True