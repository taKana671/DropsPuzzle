import random
from collections import deque
from typing import NamedTuple

from direct.interval.IntervalGlobal import ProjectileInterval, Parallel, Sequence, Func
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


class Smiley(NodePath):

    def __init__(self, tag, model, scale=1.5):

        super().__init__(BulletRigidBodyNode(f'drop_{tag}'))
        # super().__init__(PandaNode('smiley'))
        self.set_scale(scale)
        self.node().set_tag('stage', tag)

        self.model = model.copy_to(self)
        end, tip = self.model.get_tight_bounds()
        self.node().set_linear_factor(Vec3(1, 0, 1))

        size = tip - end
        shape = BulletSphereShape(size.z / 2)
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1) | BitMask32.bit(2))
        self.node().set_mass(1)
        # # self.node().deactivation_enabled = True
        self.node().set_restitution(0.3)

    def make_movable(self):
        self.node().set_linear_factor(Vec3(1, 1, 1))
        self.node().set_kinematic(True)


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
        # 1: other drops and game board, 2: click raycast, 3: gameover raycast
        self.set_collide_mask(BitMask32.bit(1) | BitMask32.bit(2) | BitMask32.bit(3))
        self.node().set_mass(1)
        self.node().deactivation_enabled = False
        self.node().set_restitution(0.3)  # 0.7
        # self.set_transparency(TransparencyAttrib.MAlpha)
        self.rad = self.get_bounds().get_radius()


class Drop(NamedTuple):

    model: Convex
    merge_into: Convex
    vfx: VFXSetting
    appendable: bool
    last: bool = False
    score: int = 0


class Drops(NodePath):
# class Drops:

    def __init__(self, world, game_board):
        super().__init__(PandaNode('drops'))
        self.world = world
        self.game_board = game_board
        # self.setup()

        self.smiley = None
        self.smiley_q = deque()
        self.drops_q = deque()
        self.serial = -1
        self.vfx = VFXManager()

        self.appendable_drops = []
        # self.smiley = base.loader.loadModel('smiley')    


        d1 = Convex('d1', Sphere(), Vec3(0.4))
        d2 = Convex('d2', Sphere(pattern=1), Vec3(0.5))
        d3 = Convex('d3', Sphere(pattern=2), Vec3(0.6))
        d4 = Convex('d4', Polyhedron('d4.obj'), Vec3(0.8))   # icosidodecahedron
        d5 = Convex('d5', Polyhedron('d5.obj'), Vec3(1.0))   # Parabiaugmented truncated dodecahedron
        d6 = Convex('d6', Polyhedron('d6.obj'), Vec3(1.2))   # Truncated icosidodecahedron
        # d7 = Convex('d7', Polyhedron('d7.obj'), Vec3(1.4))   # Parabigyrate diminished rhombicosidodecahedron
        d7 = Convex('d7', Polyhedron('s06.obj'), Vec3(1.5))
        self.d8 = base.loader.loadModel('smiley')

        d1_tex = TextureAtlas('boom_fire.png', tgt_remove_row=2)
        d2_tex = TextureAtlas('blast2.png', vfx_end_row=6, tgt_remove_row=2)
        # d2_tex = TextureAtlas('blast2.png', vfx_end_row=7)
        d3_tex = TextureAtlas('spark1.png', vfx_end_row=5, tgt_remove_row=2)
        d4_tex = TextureAtlas('spark2.png', vfx_end_row=5, tgt_remove_row=3)
        d5_tex = TextureAtlas('vortex.png', vfx_end_row=5, tgt_remove_row=3)
        d6_tex = TextureAtlas('m_blast.png', tgt_remove_row=3)
        d7_tex = TextureAtlas('rotating_fire.png', vfx_end_row=6, tgt_remove_row=3)

        self.drops = {
            'd1': Drop(model=d1, merge_into='d2', vfx=VFXSetting(texture=d1_tex, scale=2.3), appendable=True),
            'd2': Drop(model=d2, merge_into='d3', vfx=VFXSetting(texture=d2_tex, scale=2.2, offset=Vec3(0.3, 0, 0)), appendable=True),
            'd3': Drop(model=d3, merge_into='d4', vfx=VFXSetting(texture=d3_tex, scale=3.1), appendable=True, score=100),
            'd4': Drop(model=d4, merge_into='d5', vfx=VFXSetting(texture=d4_tex, scale=4.0), appendable=True, score=200),
            'd5': Drop(model=d5, merge_into='d6', vfx=VFXSetting(texture=d5_tex, scale=4.5), appendable=False, score=400),
            'd6': Drop(model=d6, merge_into='d7', vfx=VFXSetting(texture=d6_tex, scale=5.5), appendable=False, score=500),
            'd7': Drop(model=d7, merge_into='d8', vfx=VFXSetting(texture=d7_tex, scale=6.5), appendable=False, score=600),
            # 'd8': Drop(model=d8, merge_into=None, vfx=VFXSetting(texture=d2_tex, scale=5.5), appendable=False),
            'd8': Drop(model=self.d8, merge_into=None, vfx=VFXSetting(texture=d4_tex, scale=2, offset=Vec3(1, 0, 1)), appendable=False, last=True, score=1000),
        }

        # self.set_transparency(TransparencyAttrib.MAlpha)
        # filters = CommonFilters(base.win, base.cam)
        # filters.setBloom(size="large", blend=(1, 0, 0, 1), desat=0.0)
        # filters.setBloom(size="large", blend=(1, 0, 0, 0))

    # def setup(self):
    #     end, tip = self.game_board.pipe.get_tight_bounds()
    #     pipe_size = tip - end
    #     pipe_pos = self.game_board.pipe.get_pos()

    #     self.end_x = pipe_size.x / 2
    #     self.end_y = pipe_size.y / 2
    #     self.start_z = int(pipe_pos.z - pipe_size.z / 2)
    #     self.end_z = int(pipe_pos.z + pipe_size.z / 2)

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

    def copy_drop(self, drop, pos):
        if drop == self.d8:
            np = Smiley('d8', drop)
            self.smiley_q.append(np)
            np.reparent_to(self)
        else:
            np = drop.copy_to(self)

        # np = drop.copy_to(self)
        self.serial += 1
        np.set_name(f'drop_{self.serial}')
        np.set_pos(pos)
        self.world.attach(np.node())

        # if drop == self.smiley:
        #     self.smiley_q.append(np)

    def fall(self):
        if len(self.drops_q):
            key = self.drops_q[0]
            drop = self.drops[key].model

            if pos := self.get_start_pos(drop.rad):
                _ = self.drops_q.popleft()
                self.copy_drop(drop, pos)

    def _find(self, node, tag, neighbours):
        neighbours.append(node)

        for con in self.world.contact_test(node, use_filter=True).get_contacts():
            if (con_nd := con.get_node1()) != self.game_board.cabinet.node():
                if con_nd not in neighbours \
                        and not con_nd.has_tag('effecting') and con_nd.get_tag('stage') == tag:
                    self._find(con_nd, tag, neighbours)

    def find_neighbours(self, clicked_nd):
        self.neighbours = []
        now_stage = clicked_nd.get_tag('stage')
        self._find(clicked_nd, now_stage, self.neighbours)

        if len(self.neighbours) >= 2:
            drop = self.drops[now_stage]
            next_stage = drop.merge_into
            clicked_nd.set_tag('merge', next_stage)

            self.vfx.disappear(drop.vfx, *self.neighbours)
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
                self.appendable_drops.append('d7')
                total = random.randint(5, 5)
                # self.appendable_drops.append('d1')
                # total = random.randint(30, 40)
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
            score = 0

            if next_stage := np.get_tag('merge'):
                pos = np.get_pos()
                next_drop = self.drops[next_stage]
                score += next_drop.score
                self.copy_drop(next_drop.model, pos)

                if next_drop.appendable and next_stage not in self.appendable_drops:
                    self.appendable_drops.append(next_stage)

                if not next_drop.last:
                    self.add()

            self.world.remove(np.node())
            np.remove_node()

            score += 1
            self.game_board.score_display.add(score)
        except IndexError:
            pass

    def start_jump(self, np, task):
        start = np.get_pos()
        dest_1 = Point3(0, -10, 0)
        dest_2 = Point3(9.6, 0, 12)
        drop = self.drops[np.get_tag('stage')]
        vfx = self.vfx.disappear

        if not self.smiley:
            self.smiley = drop
            vfx = self.vfx.short

        Sequence(
            Func(np.make_movable),
            Parallel(
                Sequence(
                    ProjectileInterval(np, duration=1.0, startPos=start, endPos=dest_1, gravityMult=1.0),
                    Func(self.add),
                    ProjectileInterval(np, duration=1.0, startPos=dest_1, endPos=dest_2, gravityMult=1.0),
                ),
                np.hprInterval(2.0, (360, 720, 360))
            ),
            Func(vfx, drop.vfx, np),
            Func(lambda: self.game_board.num_display.add(1))
            # Func(self.add)
        ).start()

        return task.done

    def jump(self, delay=0.15):
        try:
            np = self.smiley_q.popleft()

            base.taskMgr.do_method_later(
                delay,
                self.start_jump,
                'jump',
                extraArgs=[np],
                appendTask=True
            )
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