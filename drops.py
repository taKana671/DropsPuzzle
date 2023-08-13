import random
from collections import deque
from typing import NamedTuple

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletConvexHullShape, BulletSphereShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32

from panda3d.core import TransparencyAttrib
# from direct.filter.FilterManager import FilterManager
# from panda3d.core import TransparencyAttrib
# from direct.filter.CommonFilters import CommonFilters


from create_geomnode import Sphere, Polyhedron
from visual_effects import VFXManager, TextureAtlas, VFXSetting


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


class Drop(NamedTuple):

    model: Convex
    merge_into: Convex
    vfx: VFXSetting
    appendable: bool


class Drops(NodePath):

    def __init__(self, world, game_board, parent):
        super().__init__(PandaNode('drops'))
        self.world = world
        self.game_board = game_board
        # self.setup()

        self.drops_q = deque()
        self.serial = 0
        self.vfx = VFXManager()

        self.appendable_drops = []

        d1 = Convex('d1', Sphere(), Vec3(0.4))
        d2 = Convex('d2', Sphere(pattern=1), Vec3(0.5))
        d3 = Convex('d3', Sphere(pattern=2), Vec3(0.6))
        d4 = Convex('d4', Polyhedron('d4.obj'), Vec3(0.8))   # icosidodecahedron
        d5 = Convex('d5', Polyhedron('d5.obj'), Vec3(1.0))  # Parabiaugmented truncated dodecahedron
        d6 = Convex('d6', Polyhedron('d6.obj'), Vec3(1.2))  # Truncated icosidodecahedron
        d7 = Convex('d7', Polyhedron('d7.obj'), Vec3(1.4))  # Parabigyrate diminished rhombicosidodecahedron
        # d8 = Convex('d8', Polyhedron('truncated_icosidodecahedron.obj'), Vec3(1.2))

        d1_tex = TextureAtlas('boom_fire.png')
        d2_tex = TextureAtlas('m_blast.png')

        self.drops = {
            'd1': Drop(model=d1, merge_into=d2, vfx=VFXSetting(texture=d1_tex, scale=2), appendable=True),
            'd2': Drop(model=d2, merge_into=d3, vfx=VFXSetting(texture=d2_tex, scale=2.5), appendable=True),   # 2.5 TextureAtlas('m_blast.png', 2.5)
            'd3': Drop(model=d3, merge_into=d4, vfx=VFXSetting(texture=d2_tex, scale=3.0), appendable=True),
            'd4': Drop(model=d4, merge_into=d5, vfx=VFXSetting(texture=d2_tex, scale=3.5), appendable=True),
            'd5': Drop(model=d5, merge_into=d6, vfx=VFXSetting(texture=d2_tex, scale=4.0), appendable=False),
            'd6': Drop(model=d6, merge_into=d7, vfx=VFXSetting(texture=d2_tex, scale=4.5), appendable=False),
            'd7': Drop(model=d7, merge_into=None, vfx=VFXSetting(texture=d2_tex, scale=5.0), appendable=False),
            # 'd8': Drop(model=d8, merge_into=None, vfx=VFXSetting(texture=d2_tex, scale=5.5), appendable=False),
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
            drop = self.drops[key].model

            if pos := self.get_start_pos(drop.rad):
                _ = self.drops_q.popleft()
                self.create_new_drop(drop, pos)

    def _find(self, node, tag, neighbours):
        neighbours.append(node)

        for con in self.world.contact_test(node, use_filter=True).get_contacts():
            if (con_nd := con.get_node1()) != self.game_board.body.node():
                if con_nd not in neighbours \
                        and not con_nd.has_tag('effecting') and con_nd.get_tag('stage') == tag:
                    self._find(con_nd, tag, neighbours)

    def find_neighbours(self, clicked_nd):
        self.neighbours = []
        tag = clicked_nd.get_tag('stage')
        self._find(clicked_nd, tag, self.neighbours)

        if len(self.neighbours) >= 2:
            drop = self.drops[tag]
            if drop.merge_into:
                clicked_nd.set_tag('merge', '')

            self.vfx.start_disappear(drop.vfx, *self.neighbours)
            return True

    def set_drop_numbers(self, total):
        for key in self.appendable_drops[:-1]:
            start = 7 if key == 'd1' else 0
            prop = random.randint(start, 10) / 10
            cnt = int(prop * total)
            total -= cnt
            yield key, cnt

        last_key = self.appendable_drops[-1]
        yield last_key, total

    def add(self):
        match len(self.appendable_drops):
            case 0:
                self.appendable_drops.append('d1')
                total = random.randint(30, 40)
            case 2:
                total = random.randint(20, 30)
            case _:
                total = random.randint(10, 20)

        li = [k for k, v in self.set_drop_numbers(total) for _ in range(v)]
        random.shuffle(li)
        self.drops_q.extend(li)

    def merge(self):
        try:
            np = self.vfx.drops_q.pop()

            if np.has_tag('merge'):
                pos = np.get_pos()
                drop = self.drops[np.get_tag('stage')]
                new_drop = drop.merge_into
                self.create_new_drop(new_drop, pos)

                key = new_drop.get_tag('stage')
                if self.drops[key].appendable and key not in self.appendable_drops:
                    self.appendable_drops.append(key)

                self.add()

            self.world.remove(np.node())
            np.remove_node()
        except IndexError:
            pass



# self.drops_tbl = {
    #     'd1': Drop(
    #         model=d1,
    #         merge_into=d2,
    #         vfx='textures/boom_fire.png',
    #         scale=2,
    #         proportion=0.7),
    #     'd2': Drop(
    #         model=d2,
    #         merge_into=d3,
    #         vfx='textures/m_blast.png',
    #         scale=2.5,
    #         proportion=0.3),
    #     'd3': Drop(
    #         model=d3,
    #         merge_into=d4,
    #         vfx='textures/m_blast.png',
    #         scale=3,
    #         proportion=0.2),
    #     'd4': Drop(
    #         model=d4,
    #         merge_into=d5,
    #         vfx='textures/m_blast.png',
    #         scale=3.5,
    #         proportion=0.15),
    #     'd5': Drop(
    #         model=d5,
    #         merge_into=d6,
    #         vfx='textures/m_blast.png',
    #         scale=4.0,
    #         proportion=None),
    #     'd6': Drop(
    #         model=d6,
    #         merge_into=d7,
    #         vfx='textures/m_blast.png',
    #         scale=4.5,
    #         proportion=None),
    #     'd7': Drop(
    #         model=d7,
    #         merge_into=None,
    #         vfx='textures/m_blast.png',
    #         scale=5.0,
    #         proportion=None),
    #     # 'd8': Drop(
    #     #     model=d8,
    #     #     merge_into=None,
    #     #     vfx='textures/m_blast.png',
    #     #     scale=5.5,
    #     #     proportion=None),
    # }