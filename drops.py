import random
from collections import deque

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletConvexHullShape, BulletSphereShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32, CardMaker, ColorBlendAttrib

from panda3d.core import Shader, TransparencyAttrib, Texture, FrameBufferProperties, OrthographicLens, TextureStage
from direct.filter.FilterManager import FilterManager
from panda3d.core import TransparencyAttrib
from direct.filter.CommonFilters import CommonFilters

from direct.interval.IntervalGlobal import Sequence

from create_geomnode import Sphere, Polyhedron, TextureAtlasNode
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

    def __init__(self, name, geomnode, scale):
        super().__init__(BulletRigidBodyNode(name))
        self.set_scale(scale)
        self.node().set_tag('drops_type', name)
        # self.set_pos(pos)
        self.convex = geomnode.copy_to(self)
        # self.convex = self.attach_new_node(geomnode)

        # import pdb; pdb.set_trace()
        self.node().set_linear_factor(Vec3(1, 0, 1))

        shape = BulletConvexHullShape()
        shape.add_geom(geomnode.node().get_geom(0))
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1) | BitMask32.bit(2))
        self.node().set_mass(1)
        # self.node().deactivation_enabled = True
        self.node().set_restitution(0.7)
        self.set_transparency(TransparencyAttrib.MAlpha)

        self.rad = self.get_bounds().get_radius()
        # self.set_shader_auto()
        # self.set_color(1, 1, 1, 1)


class Drops(NodePath):

    def __init__(self, world, game_board, parent):
        super().__init__(PandaNode('drops'))
        self.world = world
        self.game_board = game_board
        self.neighbours = []  # deque is better?
        # self.setup()

        self.parent_np = parent
        self.drops_q = deque()
        self.drop_num = 0
        self.vfx = VisualEffects()

        self.drops = {1}

        self.drops_tbl = {
            1: Convex('drops1', Sphere(), Vec3(0.5)),
            2: Convex('drops2', Polyhedron('icosidodecahedron'), Vec3(0.8)),
            # 'drops3': Convex('drops3', Polyhedron('truncated_octahedron'), Vec3(0.7), 4),
        }

        self.merge_tbl = {
            1: 2,
            2: 3,
        }

        self.proportion_tbl = {
            1: 1,
            2: 0.3,
            # 'drops3': 0.15,
            # 'drops4': 0.05
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

    def place(self, drop, round):
        if round > 5:
            print('end', round)
            return False

        x = random.randint(-6, 6)
        z = random.randint(16, 19)
        pos = Point3(x, 0, z)
        drop.set_pos(pos)

        if not self.world.contact_test(drop.node(), use_filter=True).get_num_contacts():
            print('again', round)
            return True

        return self.place(drop, round + 1)

    def _check(self, drop, pos, rad):
        d_pos, d_rad = drop
        dist = ((d_pos.x - pos.x) ** 2 + (d_pos.y - pos.y) ** 2 + (d_pos.z - pos.z) ** 2) ** 0.5

        if dist > rad + d_rad:
            return True
        return False

    def get_start_pos(self, rad):
        existing_drops = [
            (np.get_pos(), np.get_bounds().get_radius()) for np in self.get_children() if np.get_z() >= 16
        ]

        for _ in range(3):
            y = 0
            x = random.uniform(-6, 6)
            z = random.uniform(16, 19)
            pos = Point3(x, y, z)

            if all(self._check(drop, pos, rad) for drop in existing_drops):
                return pos

        return None

    def fall(self):
        if len(self.drops_q):
            drop_id = self.drops_q[0]
            obj = self.drops_tbl[drop_id]

            if pos := self.get_start_pos(obj.rad):
                _ = self.drops_q.popleft()
                drop = obj.copy_to(self)
                drop.set_name(f'drop_{self.drop_num}')
                self.drop_num += 1
                drop.set_pos(pos)
                self.world.attach(drop.node())

    def _find(self, node, tag, neighbours):
        print(node, tag)
        neighbours.append(node)

        for con in self.world.contact_test(node, use_filter=True).get_contacts():
            if (contact_node := con.get_node1()) != self.game_board.body.node():
                if contact_node not in neighbours \
                        and contact_node.get_tag('drops_type') == tag:
                    self._find(contact_node, tag, neighbours)

    def find_neighbours(self, node):
        self.neighbours = []
        tag = node.get_tag('drops_type')
        self._find(node, tag, self.neighbours)
        # print(len(self.contact_nodes), [n.get_name() for n in self.neighbours])

        if len(self.neighbours) >= 2:
            return True

    def add(self, cnt):
        props = {}

        for drop_id in self.drops:
            if (prop := self.proportion_tbl[drop_id]) == 1:
                prop -= sum(self.proportion_tbl[id_] for id_ in self.drops if id_ != drop_id)
            props[drop_id] = int(cnt * prop)

        self.drops_q.extend(
            random.sample([drop_id for drop_id, n in props.items() for _ in range(n)], cnt)
        )

    def merge(self):
        if not self.vfx.is_playing:
            if len(self.neighbours) == 1:
                drop = self.neighbours.pop()
                drop = NodePath(drop)
            
                merged = self.drops_tbl[2]
                model = merged.copy_to(self)
                model.set_pos(drop.get_pos())
                model.set_name('new')
                self.world.attach(model.node())
                self.world.remove(drop.node())
                drop.remove_node()
                self.add(20)

            if len(self.neighbours) > 1:
                drop = self.neighbours.pop()
                drop = NodePath(drop)
                pos = drop.get_pos()
                self.world.remove(drop.node())
                drop.remove_node()

    def disappear(self):
        self.vfx.start_disappear('textures/m_blast.png', 2, *self.neighbours)


        # if contact_cnt := len(self.contact_nodes):
        #     org_nd = self.contact_nodes.pop()
        #     org_np = NodePath(org_nd)

        #     if contact_cnt == 1:
        #         tag = org_nd.get_tag('drops_type')

        #         if name := self.merge_tbl.get(tag):
        #             merged = self.drops_tbl[name]
        #             model = merged.copy_to(self)
        #             model.set_pos(org_np.get_pos())
        #             model.set_name('new')
        #             self.world.attach(model.node())

        #             if name in self.proportion_tbl:
        #                 self.drops.add(name)

        #             return True

        #         print('self.next_drops has no next one')

        #     self.pos = org_np.get_pos(base.render)
        #     # self.pos.y -= 0.8

        #     # self.world.remove(org_nd)
        #     # org_np.remove_node()

        #     # self.effect.set_pos(self.pos)
        #     # self.effect.set_scale(3.0)
        #     # self.effect.setTexOffset(TextureStage.getDefault(), self.vfxU, self.vfxV)
        #     self.effect.reparent_to(base.render)
        #     self.vfxU = -0.125
        #     self.vfxV = 0
        #     self.start()
            
        #     self.world.remove(org_nd)
        #     org_np.remove_node()
            
            
        #     # self.bubble_plane.scaleInterval(0.5, 0.05).start()
        #     # self.bubble_plane.set_pos(pos)
        #     # self.bubble_plane.set_scale(0.5)
        #     # self.bubble_plane.reparent_to(base.render)
        #     # self.bubble_plane.scaleInterval(0.5, 0.05).start()

        #     return False

    # def create_bubbles(self):
    #     # cm = CardMaker('bubbles')
    #     # cm.set_frame(-1, 1, -1, 1)
    #     # self.effect = NodePath(cm.generate())
        
    #     tex_atlas = TextureAtlasNode(0.125, 0.875)
    #     self.effect = NodePath(tex_atlas)
    #     # self.effect.look_at(0, -1, 0)
    #     # self.effect.set_texture(base.loader.load_texture('circle_mask_2.png'))
    #     self.effect.setAttrib(ColorBlendAttrib.make(
    #         ColorBlendAttrib.M_add,
    #         ColorBlendAttrib.O_incoming_alpha,
    #         ColorBlendAttrib.O_one
    #     ))
 
    #     tex = base.loader.load_texture('textures/blast2.png')
    #     # tex.set_magfilter(Texture.FTLinearMipmapLinear)
    #     # tex.set_minfilter(Texture.FTLinearMipmapLinear)


    #     self.effect.set_texture(TextureStage.get_default(), tex, 1)
    #     # self.effect.reparent_to(base.render)
    #     self.effect.set_bin('fixed', 40)
    #     self.effect.set_depth_write(False)
    #     self.effect.set_depth_test(False)
    #     self.effect.set_light_off()
    #     self.effect.set_scale(2)
    #     self.effect.flatten_light()
    #     print(self.effect)
    #     self.Z = 0.0
    #     self.vfxU = -0.125
    #     self.vfxV = 0


    # def start(self, speed=0.05):
    #     taskMgr.doMethodLater(speed, self.run, 'vfx')
        
    # def run(self, task): 
    #     # self.effect.setPos(self.getPos(base.render))
    #     try:
    #         self.effect.setPos(self.pos)
    #     except Exception:
    #         self.effect.reparent_to(base.render)    
        
    #     self.effect.setZ(self.effect.getZ()+self.Z)
    #     self.vfxU=self.vfxU+0.125   
    #     if self.vfxU>=1.0:
    #         self.vfxU=0
    #         self.vfxV=self.vfxV-0.125
    #     if self.vfxV <=-1:
    #         # self.effect.removeNode()
    #         self.effect.detachNode()
    #         return task.done          
    #     self.effect.lookAt(base.camera)
    #     self.effect.setTexOffset(TextureStage.getDefault(), self.vfxU, self.vfxV)
    #     return task.again
