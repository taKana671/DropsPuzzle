import random

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletConvexHullShape, BulletSphereShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32, CardMaker

from panda3d.core import Shader, TransparencyAttrib

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

        shape = BulletConvexHullShape()
        shape.add_geom(geomnode.node().get_geom(0))
        self.node().add_shape(shape)
        self.set_collide_mask(BitMask32.bit(1) | BitMask32.bit(2))
        self.node().set_mass(1)
        # self.node().deactivation_enabled = True
        self.node().set_restitution(0.7)


class Drops(NodePath):

    def __init__(self, world, game_board):
        super().__init__(PandaNode('drops'))
        self.world = world
        self.game_board = game_board
        self.contact_nodes = []
        self.setup()

        self.drops = {'drops1'}

        self.drops_tbl = {
            'drops1': Convex('drops1', Sphere(), Vec3(0.5)),
            'drops2': Convex('drops2', Polyhedron('icosidodecahedron'), Vec3(0.6)),
            'drops3': Convex('drops3', Polyhedron('truncated_octahedron'), Vec3(0.7)),
        }

        self.merge_tbl = {
            'drops1': 'drops2',
            'drops2': 'drops3',
        }

        self.proportion_tbl = {
            'drops1': 1,
            'drops2': 0.3,
            'drops3': 0.15,
            'drops4': 0.05
        }
        # self.create_bubbles()

    def setup(self):
        end, tip = self.game_board.pipe.get_tight_bounds()
        pipe_size = tip - end
        pipe_pos = self.game_board.pipe.get_pos()

        self.end_x = pipe_size.x / 2
        self.end_y = pipe_size.y / 2
        self.start_z = int(pipe_pos.z - pipe_size.z / 2)
        self.end_z = int(pipe_pos.z + pipe_size.z / 2)

    def get_start_pos(self, pt, r):
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

        return self.get_start_pos(pt, r)

    def fall(self, cnt):
        for name in self.drops:
            model = self.drops_tbl[name]
            end, tip = model.get_tight_bounds()
            r = self.end_x - (tip - end).x / 2

            if (prop := self.proportion_tbl[name]) == 1:
                prop -= sum(self.proportion_tbl[key] for key in self.drops if key != name)

            for i in range(int(cnt * prop)):
                pos = self.get_start_pos(Point3(0), r)
                drop = model.copy_to(self)
                drop.set_pos(pos)
                drop.set_name(f'{name}_{i}')
                self.world.attach(drop.node())

        # for obj in self.drops:
        #     # obj = self.drops[0]
        #     end, tip = obj.get_tight_bounds()
        #     r = self.end_x - (tip - end).x / 2
        #     name = obj.get_name()

        #     for i in range(cnt):
        #         pos = self.get_pos(Point3(0, 0, 0), r)
        #         s = obj.copy_to(self)
        #         s.set_pos(pos)
        #         s.set_name(f'{name}_{i}')
        #         self.world.attach(s.node())


        # for obj in self.drops:
        #     # obj = self.drops[0]
        #     end, tip = obj.get_tight_bounds()
        #     r = self.end_x - (tip - end).x / 2
        #     name = obj.get_name()

        #     for i in range(cnt):
        #         pos = self.get_pos(Point3(0, 0, 0), r)
        #         s = obj.copy_to(self)
        #         s.set_pos(pos)
        #         s.set_name(f'{name}_{i}')
        #         self.world.attach(s.node())

    def _find(self, node, tag, contact_nodes):
        contact_nodes.append(node)

        for con in self.world.contact_test(node, use_filter=True).get_contacts():
            if (contact_node := con.get_node1()) != self.game_board.body.node():
                if contact_node not in contact_nodes \
                        and contact_node.get_tag('drops_type') == tag:
                    self._find(contact_node, tag, contact_nodes)

    def find_contact_drops(self, node):
        self.contact_nodes = []
        tag = node.get_tag('drops_type')
        self._find(node, tag, self.contact_nodes)
        print(len(self.contact_nodes), [n.get_name() for n in self.contact_nodes])

        if len(self.contact_nodes):
            return True

    def merge_contact_drops(self):
        if contact_cnt := len(self.contact_nodes):
            org_nd = self.contact_nodes.pop()
            org_np = NodePath(org_nd)

            if contact_cnt == 1:
                tag = org_nd.get_tag('drops_type')

                if name := self.merge_tbl.get(tag):
                    merged = self.drops_tbl[name]
                    model = merged.copy_to(self)
                    model.set_pos(org_np.get_pos())
                    model.set_name('new')
                    self.world.attach(model.node())

                    if name in self.proportion_tbl:
                        self.drops.add(name)

                    return True

                print('self.next_drops has no next one')

            self.world.remove(org_nd)
            org_np.remove_node()
            return False



    
    
    
    
    
    # def create_bubbles(self):
    #     cm = CardMaker('bubbles')
    #     cm.set_frame(-128, 128, -128, 128)
    #     self.bubble_plane = NodePath(cm.generate())
    #     self.bubble_plane.look_at(0, 1, 0)
    #     self.bubble_plane.set_transparency(TransparencyAttrib.MAlpha)
    #     self.bubble_plane.set_color((1, 1, 1, 0))
    #     self.bubble_plane.set_pos(Point3(0, -10, 0))
    #     self.bubble_plane.flatten_strong()

    #     self.bubble_plane.set_shader(
    #         Shader.load(Shader.SL_GLSL, 'shaders/bubbles_v.glsl', 'shaders/bubbles_f.glsl'))

    #     props = base.win.get_properties()
    #     self.bubble_plane.set_shader_input('u_resolution', props.get_size())

    #     self.bubble_buffer = base.win.make_texture_buffer('bubbles', 512, 512)
    #     self.bubble_buffer.set_clear_color(base.win.get_clear_color())
    #     self.bubble_buffer.set_sort(-1)

    #     self.bubble_camera = base.make_camera(self.bubble_buffer)
    #     self.bubble_camera.node().set_lens(base.camLens)
    #     self.bubble_camera.node().set_camera_mask(BitMask32.bit(1))

    #     # self.bubble_plane.set_shader_input('uv', (0.5, 0.5))
    #     self.bubble_plane.reparent_to(base.render)
    #     self.bubble_camera.reparent_to(base.render)
    


