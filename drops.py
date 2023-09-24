import random
from collections import deque

from direct.interval.IntervalGlobal import ProjectileInterval, Parallel, Sequence, Func, Wait
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletConvexHullShape, BulletSphereShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32
from panda3d.core import TransparencyAttrib
from panda3d.core import TransformState

from colors import theme_colors
from create_geomnode import Sphere, Polyhedron
from visual_effects import DisappearEffect, VFX, TextureAtlas, VFXSetting


class Models(NodePath):

    def __init__(self, tag, model, scale):
        super().__init__(BulletRigidBodyNode(f'drop_{tag}'))
        model.reparent_to(self)
        self.set_scale(scale)
        self.node().set_tag('stage', tag)
        self.node().set_linear_factor(Vec3(1, 0, 1))
        self.node().set_restitution(0.3)

    def make_movable(self, nd):
        nd.set_linear_factor(Vec3(1, 1, 1))
        nd.set_kinematic(True)


class Smiley(Models):

    def __init__(self, tag, model, scale=1.5):
        super().__init__(tag, model, scale)

        end, tip = model.get_tight_bounds()
        size = tip - end
        shape = BulletSphereShape(size.z / 2)
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1) | BitMask32.bit(2))
        self.node().set_mass(1)


class Convex(Models):

    def __init__(self, tag, model, scale):
        super().__init__(tag, model, scale)

        shape = BulletConvexHullShape()
        shape.add_geom(model.node().get_geom(0))
        self.node().add_shape(shape)
        # 1: other drops and game board, 2: click raycast, 3: gameover judge
        self.set_collide_mask(BitMask32.bit(1) | BitMask32.bit(2) | BitMask32.bit(3))
        self.node().set_mass(0.5)
        self.set_transparency(TransparencyAttrib.MAlpha)
        self.rad = self.get_bounds().get_radius()
        self.node().set_ccd_motion_threshold(1e-7)
        self.node().set_ccd_swept_sphere_radius(self.rad)


class Drop:

    def __init__(self, stage, vfx_setting, appendable,
                 merge_into=None, model=None, scale=Vec3(1), last=False, score=0):
        self.stage = stage
        self.merge_into = merge_into
        self.vfx = vfx_setting
        self.appendable = appendable
        self.scale = scale
        self.last = last
        self.score = score
        self.model = model

    def set_model(self, geomnode):
        self.model = Convex(self.stage, geomnode, self.scale)


class Drops(NodePath):

    def __init__(self, world):
        super().__init__(PandaNode('drops'))
        self.world = world

        self.smiley_q = deque()
        self.drops_q = deque()
        self.vfx_q = deque()
        self.disappear_vfx = DisappearEffect(self.vfx_q)
        self.smiley = Smiley('d8', base.loader.loadModel('smiley'))
        self.setup_drops()

        self.colors = theme_colors[:]
        random.shuffle(self.colors)
        self.color_idx = 0

    def setup_drops(self):
        vfx_1 = VFXSetting(TextureAtlas('boom_fire.png'), scale=2.0, tgt_remove_row=2)
        vfx_2 = VFXSetting(TextureAtlas('blast2.png'), scale=2.2, vfx_end_row=5, tgt_remove_row=2)
        vfx_3 = VFXSetting(TextureAtlas('rotating_fire.png'), scale=3.0, vfx_end_row=6, tgt_remove_row=3)
        vfx_4 = VFXSetting(TextureAtlas('m_blast.png'), scale=4.0, tgt_remove_row=3)
        vfx_5 = VFXSetting(TextureAtlas('spark2.png'), scale=2.0, vfx_end_row=5, tgt_remove_row=3)
        vfx_6 = VFXSetting(TextureAtlas('spark3.png'), scale=6.0, tgt_remove_row=4)
        vfx_7 = VFXSetting(TextureAtlas('spark1.png'), scale=6.5, offset=Vec3(1.0, 0, 0), vfx_end_row=4, tgt_remove_row=2)
        vfx_8 = VFXSetting(TextureAtlas('spark2.png'), scale=2.0, offset=Vec3(1, 0, 1), tgt_remove_row=3)

        self.drops = dict(
            d1=Drop('d1', merge_into='d2', vfx_setting=vfx_1, appendable=True, scale=Vec3(0.4)),
            d2=Drop('d2', merge_into='d3', vfx_setting=vfx_2, appendable=True, scale=Vec3(0.5)),
            d3=Drop('d3', merge_into='d4', vfx_setting=vfx_3, appendable=True, scale=Vec3(0.6), score=100),
            d4=Drop('d4', merge_into='d5', vfx_setting=vfx_4, appendable=True, scale=Vec3(0.8), score=200),
            d5=Drop('d5', merge_into='d6', vfx_setting=vfx_5, appendable=False, scale=Vec3(1.0), score=400),
            d6=Drop('d6', merge_into='d7', vfx_setting=vfx_6, appendable=False, scale=Vec3(1.2), score=500),
            d7=Drop('d7', merge_into='d8', vfx_setting=vfx_7, appendable=False, scale=Vec3(1.5), score=600),
            d8=Drop('d8', model=self.smiley, vfx_setting=vfx_8, appendable=False, score=1000, last=True)
        )

    def change_drop_color(self):
        colors = self.colors[self.color_idx]

        self.color_idx += 1
        if self.color_idx == len(self.colors):
            self.color_idx = 0

        geom_nodes = dict(
            d1=Sphere(colors),
            d2=Sphere(colors, pattern=1),
            d3=Sphere(colors, pattern=2),
            d4=Polyhedron(colors, 'd4.obj'),   # icosidodecahedron
            d5=Polyhedron(colors, 'd5.obj'),   # Parabiaugmented truncated dodecahedron
            d6=Polyhedron(colors, 'd6.obj'),   # Truncated icosidodecahedron
            d7=Polyhedron(colors, 'd7.obj')    # Truncated icosahedron
        )

        for key, geom_node in geom_nodes.items():
            drop = self.drops[key]
            drop.set_model(geom_node)

    def delete(self, np):
        self.world.remove(np.node())
        np.remove_node()

    def cleanup(self):
        for np in self.get_children():
            self.delete(np)

        self.smiley_q.clear()
        self.drops_q.clear()
        self.vfx_q.clear()

    def initialize(self):
        self.cleanup()
        self.change_drop_color()
        self.serial = 0
        self.complete_score = 0
        self.drops_add = []

    def get_start_pos(self, drop):
        for _ in range(3):
            x = random.uniform(-6, 6)
            from_pt = Point3(x, 0, 19)
            to_pt = Point3(x, 0, 16)

            from_ts = TransformState.make_pos(from_pt)
            to_ts = TransformState.make_pos(to_pt)
            result = self.world.sweepTestClosest(
                drop.node().get_shape(0), from_ts, to_ts, BitMask32.bit(1), 0.0)

            if not result.has_hit():
                return to_pt

    def copy_drop(self, drop, pos):
        np = drop.copy_to(self)
        np.set_name(f'drop_{self.serial}')

        if drop == self.smiley:
            self.smiley_q.append(np)

        self.serial += 1
        np.set_pos(pos)
        self.world.attach(np.node())

    def fall(self):
        if len(self.drops_q):
            key = self.drops_q[0]
            drop = self.drops[key].model

            if pos := self.get_start_pos(drop):
                _ = self.drops_q.popleft()
                self.copy_drop(drop, pos)

    def find_all_neighbours(self, nd, neighbours):
        """Find all of the balls contacting with each other recursivelly.
            Args:
                nd: BulletRigidBodyNode
                neighbours: set
        """
        for con in self.world.contact_test(nd, use_filter=True).get_contacts():
            con_nd = con.get_node1()
            if con_nd not in neighbours and con_nd.get_tag('stage'):
                neighbours.add(con_nd)
                self.find_all_neighbours(con_nd, neighbours)

    def _neighbours(self, node, tag, neighbours):
        neighbours.append(node)

        for con in self.world.contact_test(node, use_filter=True).get_contacts():
            con_nd = con.get_node1()
            if con_nd not in neighbours and con_nd.get_tag('stage') == tag \
                    and not con_nd.has_tag('effecting'):
                self._neighbours(con_nd, tag, neighbours)

    def find_neighbours(self, clicked_nd):
        neighbours = []
        now_stage = clicked_nd.get_tag('stage')
        self._neighbours(clicked_nd, now_stage, neighbours)

        if len(neighbours) >= 2:
            drop = self.drops[now_stage]
            next_stage = drop.merge_into
            clicked_nd.set_tag('merge', next_stage)
            self.disappear_vfx.start(drop.vfx, *neighbours)

    def set_drop_numbers(self, total):
        for key in self.drops_add[:-1]:
            start = 7 if key == 'd1' else 0
            prop = random.randint(start, 10) / 10
            cnt = int(prop * total)
            total -= cnt
            yield key, cnt

        last_key = self.drops_add[-1]
        yield last_key, total

    def add(self):
        match len(self.drops_add):
            case 0:
                self.drops_add.append('d1')
                total = random.randint(30, 40)
            case 2:
                total = random.randint(20, 30)
            case _:
                total = random.randint(10, 20)

        li = [k for k, v in self.set_drop_numbers(total) for _ in range(v)]
        random.shuffle(li)
        self.drops_q.extend(li)

    def merge(self):
        score = 0
        try:
            np = self.vfx_q.pop()

            if next_stage := np.get_tag('merge'):
                pos = np.get_pos()
                next_drop = self.drops[next_stage]
                score += next_drop.score
                self.copy_drop(next_drop.model, pos)

                if next_drop.appendable and next_stage not in self.drops_add:
                    self.drops_add.append(next_stage)

                if not next_drop.last:
                    self.add()

            self.delete(np)
            score += 1
        except IndexError:
            pass

        return score

    def update_complete_score(self):
        self.complete_score += 1

    def jump(self, delay=0.15):
        try:
            np = self.smiley_q.popleft()
            drop = self.drops[np.get_tag('stage')]

            vfx_func = Func(self.disappear_vfx.start, drop.vfx, np)
            if not self.complete_score:
                vfx_func = Func(VFX(drop.vfx, np).start)

            Sequence(
                Wait(delay),
                Func(self.smiley.make_movable, np.node()),
                SmileyRollingJumpInterval(np),
                Func(self.add),
                vfx_func,
                Func(self.update_complete_score)
            ).start()

        except IndexError:
            pass


class SmileyRollingJumpInterval(Parallel):

    def __init__(self, np):
        super().__init__()
        self.halfway = Point3(0, -10, 0)
        self.dest = Point3(9, 0, 13.5)
        self.make_rolling_jump_interval(np)

    def make_rolling_jump_interval(self, np):
        start = np.get_pos()

        self.append(Sequence(
            ProjectileInterval(np, duration=1.0, startPos=start, endPos=self.halfway, gravityMult=1.0),
            ProjectileInterval(np, duration=1.0, startPos=self.halfway, endPos=self.dest, gravityMult=1.0),
        ))
        self.append(np.hprInterval(2.0, (360, 720, 360)))