import random
from collections import deque

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletConvexHullShape, BulletSphereShape
from panda3d.core import NodePath, PandaNode
from panda3d.core import Vec3, Point3, BitMask32, CardMaker, ColorBlendAttrib

from panda3d.core import Shader, TransparencyAttrib, Texture, FrameBufferProperties, OrthographicLens
from direct.filter.FilterManager import FilterManager
from panda3d.core import TransparencyAttrib
from direct.filter.CommonFilters import CommonFilters

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
        self.contact_nodes = []
        # self.setup()

        self.parent_np = parent
        self.drops_q = deque()
        self.drop_num = 0

        self.drops = {1, 2}

        self.drops_tbl = {
            1: Convex('drops1', Sphere(), Vec3(0.5)),
            2: Convex('drops2', Polyhedron('icosidodecahedron'), Vec3(1.2)),
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
        self.create_bubbles()
        # self.set_transparency(TransparencyAttrib.MAlpha)
        # filters = CommonFilters(base.win, base.cam)
        # filters.setBloom(size="large", blend=(1, 0, 0, 0), desat=0.0)

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

    def _find(self, node, tag, contact_nodes):
        print(node, tag)
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

        if len(self.contact_nodes) >= 2:
            cnt = 30
            self.add(cnt)
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

    def create_bubbles2(self):
        root = NodePath('buffer_root')
        root.reparent_to(base.render)
        root.set_pos(0, 10, 0)

        tex = Texture()
        tex.setWrapU(Texture.WMClamp)
        tex.setWrapU(Texture.WMClamp)
        tex.set_magfilter(Texture.FTLinearMipmapLinear)
        tex.set_minfilter(Texture.FTLinearMipmapLinear)
        props = FrameBufferProperties()
        props.set_rgba_bits(16, 16, 0, 0)
        props.set_srgb_color(False)
        props.set_float_color(True)
        buff = base.win.make_texture_buffer('buff', 256, 256, tex, fbp=props)
        cam = base.make_camera(win=buff)
        cam.reparent_to(root)
        cam.set_pos(128, 128, 0)
        cam.set_p(90)
        lens = OrthographicLens()
        lens.set_film_size(256, 256)
        cam.node().set_lens(lens)
        cm = CardMaker('plane')
        cm.set_frame(-128, 128, -128, 128)
        quad = root.attach_new_node(cm.generate())
        # quad.set_pos(Point3(0, 10, 0))
        quad.look_at(0, 1, 0)

        quad.set_shader(
            Shader.load(Shader.SL_GLSL, 'shaders/bubbles_v.glsl', 'shaders/bubbles_f.glsl'))
        # quad.set_shader_input('mask', base.loader.load_texture('shaders/circle_mask.png'))
        props = base.win.get_properties()
        quad.set_shader_input('u_resolution', props.get_size())


    def create_bubbles(self):
        cm = CardMaker('bubbles')
        # cm.set_frame(-2, 2, -2, 2)
        cm.set_frame(-1, 1, -1, 1)
        self.bubble_plane = NodePath(cm.generate())
        self.bubble_plane.look_at(0, 1, 0)
        self.bubble_plane.set_texture(base.loader.load_texture('shaders/star_mask.png'))
        self.bubble_plane.setAttrib(ColorBlendAttrib.make(
            ColorBlendAttrib.M_add,
            ColorBlendAttrib.O_incoming_alpha,
            ColorBlendAttrib.O_one
        ))


        # self.bubble_plane.set_transparency(TransparencyAttrib.MAlpha)
        self.bubble_plane.set_pos(Point3(0, 0, 0))
        # self.bubble_plane.set_scale(0.5)
        
        # self.bubble_plane.flatten_strong()

        self.bubble_plane.set_shader(
            Shader.load(Shader.SL_GLSL, 'shaders/bubbles_v.glsl', 'shaders/bubbles_f.glsl'))

        # self.game_board.body.set_shader(
        #     Shader.load(Shader.SL_GLSL, 'shaders/bubbles_v.glsl', 'shaders/bubbles_f.glsl'))


        props = base.win.get_properties()
        self.bubble_plane.set_shader_input('u_resolution', props.get_size())

        # self.bubble_plane.set_shader_input('mask', base.loader.load_texture('shaders/circle_mask.png'))

        # self.game_board.body.set_shader_input('u_resolution', props.get_size())

        # self.bubble_buffer = base.win.make_texture_buffer('bubbles', 512, 512)
        # self.bubble_buffer.set_clear_color(base.win.get_clear_color())
        # self.bubble_buffer.set_sort(-1)

        # self.bubble_camera = base.make_camera(self.bubble_buffer)
        # self.bubble_camera.node().set_lens(base.camLens)
        # self.bubble_camera.node().set_camera_mask(BitMask32.bit(3))

        # self.bubble_plane.set_shader_input('uv', (0.5, 0.5))
        # self.bubble_plane.reparent_to(self.parent_np)

        self.bubble_plane.reparent_to(base.render)
        # self.bubble_camera.reparent_to(base.render)
    


