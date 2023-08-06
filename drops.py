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

    def __init__(self, num, geomnode, scale):
        super().__init__(BulletRigidBodyNode(f'drop_{num}'))
        self.set_scale(scale)
        self.node().set_tag('num', num)
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


@dataclass
class Drop:

    model: Convex
    vfx: str
    scale: float
    proportion: float = None
    merge: int = None
    cnt: int = 0


class Drops(NodePath):

    def __init__(self, world, game_board, parent):
        super().__init__(PandaNode('drops'))
        self.world = world
        self.game_board = game_board
        # self.setup()

        self.merge_into = None
        self.parent_np = parent
        self.drops_q = deque()
        self.serial = 0
        self.vfx = VisualEffects()

        self.drops = {1}

        self.drops_tbl = {
            1: Drop(
                model=Convex('1', Sphere(), Vec3(0.5)),
                vfx='textures/boom_fire.png',
                scale=2,
                proportion=1.0,
                merge=2),
            2: Drop(
                model=Convex('2', Polyhedron('icosidodecahedron'), Vec3(0.75)),
                vfx='textures/m_blast.png',
                scale=2.5,
                proportion=0.3,
                merge=3),
            3: Drop(
                model=Convex('3', Polyhedron('truncated_octahedron'), Vec3(1.0)),
                vfx='textures/m_blast.png',
                scale=3,
                proportion=0.15,
                merge=4),
        }

        # self.drops_tbl = {
        #     1: Convex('drops1', Sphere(), Vec3(0.5)),
        #     2: Convex('drops2', Polyhedron('icosidodecahedron'), Vec3(0.75)),
        #     # 'drops3': Convex('drops3', Polyhedron('truncated_octahedron'), Vec3(1.0), 4),
        # }

        # self.merge_tbl = {
        #     1: 2,
        #     2: 3,
        # }

        # self.proportion_tbl = {
        #     1: 1,
        #     2: 0.3,
        #     # 'drops3': 0.15,
        #     # 'drops4': 0.05
        # }

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

    # def place(self, drop, round):
    #     if round > 5:
    #         print('end', round)
    #         return False

    #     x = random.randint(-6, 6)
    #     z = random.randint(16, 19)
    #     pos = Point3(x, 0, z)
    #     drop.set_pos(pos)

    #     if not self.world.contact_test(drop.node(), use_filter=True).get_num_contacts():
    #         print('again', round)
    #         return True

    #     return self.place(drop, round + 1)

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
            num = self.drops_q[0]
            drop = self.drops_tbl[num].model

            if pos := self.get_start_pos(drop.rad):
                _ = self.drops_q.popleft()
                new_drop = drop.copy_to(self)
                new_drop.set_name(f'drop_{self.serial}')
                self.serial += 1
                new_drop.set_pos(pos)
                self.world.attach(new_drop.node())

    def _find(self, node, tag, neighbours):
        neighbours.append(node)

        for con in self.world.contact_test(node, use_filter=True).get_contacts():
            if (con_node := con.get_node1()) != self.game_board.body.node():
                if con_node not in neighbours \
                        and con_node.get_tag('num') == tag:
                    self._find(con_node, tag, neighbours)

    def find_neighbours(self, node):
        self.neighbours = []
        tag = node.get_tag('num')
        self._find(node, tag, self.neighbours)
        # print(len(self.contact_nodes), [n.get_name() for n in self.neighbours])

        if len(self.neighbours) >= 2:
            drop = self.drops_tbl[int(tag)]
            if drop.merge:
                self.merge_into = node
                self.neighbours = self.neighbours[1:]

            self.vfx.start_disappear(drop.vfx, drop.scale, *self.neighbours)
            return True

    def add(self, cnt):
        props = {}

        for num in self.drops:
            num = int(num)
            if (prop := self.drops_tbl[num].proportion) == 1:
                prop -= sum(self.drops_tbl[n].proportion for n in self.drops if n != num)
            props[num] = int(cnt * prop)

        self.drops_q.extend(
            random.sample([num for num, c in props.items() for _ in range(c)], cnt)
        )


        # for key in self.drops:
        #     if (prop := self.proportion_tbl[key]) == 1:
        #         prop -= sum(self.proportion_tbl[id_] for id_ in self.drops if id_ != key)
        #     props[key] = int(cnt * prop)

        # self.drops_q.extend(
        #     random.sample([drop_id for drop_id, n in props.items() for _ in range(n)], cnt)
        # )

    def delete(self, node):
        self.world.remove(node)
        np = NodePath(node)
        return np.remove_node()

    def merge(self):
        if not self.vfx.is_playing:
            for node in self.neighbours:
                self.delete(node)

            if self.merge_into:
                tag = self.merge_into.get_tag('num')
                drop = self.drops_tbl[int(tag)]
                new_drop = self.drops_tbl[drop.merge]
                model = new_drop.model.copy_to(self)
                model.set_pos(NodePath(self.merge_into).get_pos())
                model.set_name(f'drop_{self.serial}')
                self.serial += 1
                self.world.attach(model.node())
                self.merge_into = self.delete(self.merge_into)
                self.add(20)
                self.drops.add(drop.merge)

            return True

                

            


            

            # if len(self.neighbours) == 1:
            #     drop = self.neighbours.pop()
            #     drop = NodePath(drop)

            #     merged = self.drops_tbl[2]
            #     model = merged.copy_to(self)
            #     model.set_pos(drop.get_pos())
            #     model.set_name('new')
            #     self.world.attach(model.node())
            #     self.world.remove(drop.node())
            #     drop.remove_node()
            #     self.add(20)

            # if len(self.neighbours) > 1:
            #     drop = self.neighbours.pop()
            #     drop = NodePath(drop)
            #     pos = drop.get_pos()
            #     self.world.remove(drop.node())
            #     drop.remove_node()




    def disappear(self):
        self.clicked_node = self.neighbours[0]
        tag = self.clicked_node.get_tag('num')
        drop = self.drops_tbl[tag]
        if drop.merge:
            self.drop_into = self.clicked_node
            self.neighbours = self.neighbours[1:]

        self.vfx.start_disappear('textures/vfx3.png', 2, *self.neighbours)

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
