import array
import math

from panda3d.core import Vec3, Point3, LColor
from panda3d.core import NodePath
from panda3d.core import Geom, GeomNode, GeomTriangles
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexArrayFormat

# ************************************
import sys
from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from panda3d.bullet import BulletWorld, BulletDebugNode, BulletConvexHullShape
from panda3d.bullet import BulletRigidBodyNode

from panda3d.core import Vec3, BitMask32, Point3
# ************************************


class GeomRoot(NodePath):

    def __init__(self):
        geomnode = self.create_geomnode()
        super().__init__(geomnode)
        self.set_two_sided(True)

    def create_format(self):
        arr_format = GeomVertexArrayFormat()
        arr_format.add_column('vertex', 3, Geom.NTFloat32, Geom.CPoint)
        arr_format.add_column('color', 4, Geom.NTFloat32, Geom.CColor)
        arr_format.add_column('normal', 3, Geom.NTFloat32, Geom.CColor)
        arr_format.add_column('texcoord', 2, Geom.NTFloat32, Geom.CTexcoord)
        fmt = GeomVertexFormat.register_format(arr_format)
        return fmt

    def create_geomnode(self):
        fmt = self.create_format()
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])

        vertex_count = self.create_vertices(vdata_values, prim_indices)

        vdata = GeomVertexData('tube', fmt, Geom.UHStatic)
        vdata.unclean_set_num_rows(vertex_count)
        vdata_mem = memoryview(vdata.modify_array(0)).cast('B').cast('f')
        vdata_mem[:] = vdata_values

        prim = GeomTriangles(Geom.UHStatic)
        prim_array = prim.modify_vertices()
        prim_array.unclean_set_num_rows(len(prim_indices))
        prim_mem = memoryview(prim_array).cast('B').cast('H')
        prim_mem[:] = prim_indices

        node = GeomNode('geomnode')
        geom = Geom(vdata)
        geom.add_primitive(prim)
        node.add_geom(geom)
        return node


class RingShape(GeomRoot):
    """Create a geom node of torus, spiral, half ring and so on.
       Args:
            segs_rcnt (int): the number of segments
            segs_r (int): the number of segments of the ring
            segs_s (int): the number of segments of the cross-sections
            ring_radius (float): the radius of the ring; cannot be negative;
            section_radius (float): the radius of the cross-sections perpendicular to the ring; cannot be negative;
            slope (float): the increase of the cross-sections hight
    """

    def __init__(self, segs_rcnt=24, segs_r=24, segs_s=12, ring_radius=1.2, section_radius=0.5, slope=0):
        self.segs_rcnt = segs_rcnt
        self.segs_r = segs_r
        self.segs_s = segs_s
        self.ring_radius = ring_radius
        self.section_radius = section_radius
        self.slope = slope
        super().__init__()

    def create_vertices(self, vdata_values, prim_indices):
        delta_angle_h = 2.0 * math.pi / self.segs_r
        delta_angle_v = 2.0 * math.pi / self.segs_s

        for i in range(self.segs_rcnt + 1):
            angle_h = delta_angle_h * i
            u = i / self.segs_rcnt

            for j in range(self.segs_s + 1):
                angle_v = delta_angle_v * j
                r = self.ring_radius - self.section_radius * math.cos(angle_v)
                c = math.cos(angle_h)
                s = math.sin(angle_h)

                x = r * c
                y = r * s
                z = self.section_radius * math.sin(angle_v) + self.slope * i

                nx = x - self.ring_radius * c
                ny = y - self.ring_radius * s
                normal_vec = Vec3(nx, ny, z).normalized()
                v = 1.0 - j / self.segs_s
                vdata_values.extend((x, y, z))
                vdata_values.extend((1, 1, 1, 1))
                vdata_values.extend(normal_vec)
                vdata_values.extend((u, v))

        for i in range(self.segs_rcnt):
            for j in range(0, self.segs_s):
                idx = j + i * (self.segs_s + 1)
                prim_indices.extend([idx, idx + 1, idx + self.segs_s + 1])
                prim_indices.extend([idx + self.segs_s + 1, idx + 1, idx + 1 + self.segs_s + 1])

        return (self.segs_rcnt + 1) * (self.segs_s + 1)


class SphericalShape(GeomRoot):
    """Create a geom node of sphere.
       Args:
            radius (int): the radius of sphere;
            segments (int): the number of surface subdivisions;
    """

    def __init__(self, radius=1.5, segments=22):
        self.radius = radius
        self.segments = segments
        super().__init__()

    def create_bottom_pole(self, vdata_values, prim_indices):
        # the bottom pole vertices
        normal = (0.0, 0.0, -1.0)
        vertex = (0.0, 0.0, -self.radius)
        color = (1, 1, 1, 1)

        for i in range(self.segments):
            u = i / self.segments
            vdata_values.extend(vertex)
            vdata_values.extend(color)
            vdata_values.extend(normal)
            vdata_values.extend((u, 0.0))

            # the vertex order of the pole vertices
            prim_indices.extend((i, i + self.segments + 1, i + self.segments))

        return self.segments

    def create_quads(self, index_offset, vdata_values, prim_indices):
        delta_angle = 2 * math.pi / self.segments
        color = (1, 1, 1, 1)
        vertex_count = 0

        # the quad vertices
        for i in range((self.segments - 2) // 2):
            angle_v = delta_angle * (i + 1)
            radius_h = self.radius * math.sin(angle_v)
            z = self.radius * -math.cos(angle_v)
            v = 2.0 * (i + 1) / self.segments

            for j in range(self.segments + 1):
                angle = delta_angle * j
                c = math.cos(angle)
                s = math.sin(angle)
                x = radius_h * c
                y = radius_h * s
                normal = Vec3(x, y, z).normalized()
                u = j / self.segments

                vdata_values.extend((x, y, z))
                vdata_values.extend(color)
                vdata_values.extend(normal)
                vdata_values.extend((u, v))

                # the vertex order of the quad vertices
                if i > 0 and j <= self.segments:
                    px = i * (self.segments + 1) + j + index_offset
                    prim_indices.extend((px, px - self.segments - 1, px - self.segments))
                    prim_indices.extend((px, px - self.segments, px + 1))

            vertex_count += self.segments + 1

        return vertex_count

    def create_top_pole(self, index_offset, vdata_values, prim_indices):
        vertex = (0.0, 0.0, self.radius)
        normal = (0.0, 0.0, 1.0)
        color = (1, 1, 1, 1)

        # the top pole vertices
        for i in range(self.segments):
            u = i / self.segments
            vdata_values.extend(vertex)
            vdata_values.extend(color)
            vdata_values.extend(normal)
            vdata_values.extend((u, 1.0))

            # the vertex order of the top pole vertices
            x = i + index_offset
            prim_indices.extend((x, x + 1, x + self.segments + 1))

        return self.segments

    def create_vertices(self, vdata_values, prim_indices):
        vertex_count = 0

        # create vertices of the bottom pole, quads, and top pole
        vertex_count += self.create_bottom_pole(vdata_values, prim_indices)
        vertex_count += self.create_quads(vertex_count, vdata_values, prim_indices)
        vertex_count += self.create_top_pole(vertex_count - self.segments - 1, vdata_values, prim_indices)

        return vertex_count


class Cube(GeomRoot):
    """Create a geom node of cube.
        Arges:
            w (float): width; dimension along the x-axis; cannot be negative;
            d (float): depth; dimension along the y-axis; cannot be negative;
            h (float): height; dimension along the z-axis; cannot be negative;
            segs_w (int) the number of subdivisions in width;
            segs_d (int) the number of subdivisions in depth;
            segs_h (int) the number of subdivisions in height
    """

    def __init__(self, w=1.0, d=1.0, h=1.0, segs_w=2, segs_d=2, segs_h=2):
        self.w = w
        self.d = d
        self.h = h
        self.segs_w = segs_w
        self.segs_d = segs_d
        self.segs_h = segs_h
        self.color = (1, 1, 1, 1)
        super().__init__()

    def create_vertices(self, vdata_values, prim_indices):
        vertex_count = 0
        vertex = Point3()
        segs = (self.segs_w, self.segs_d, self.segs_h)
        dims = (self.w, self.d, self.h)
        segs_u = self.segs_w * 2 + self.segs_d * 2
        offset_u = 0

        # (fixed, outer loop, inner loop, normal, uv)
        side_idxes = [
            (2, 0, 1, 1, False),     # top
            (1, 0, 2, -1, False),    # front
            (0, 1, 2, 1, False),     # right
            (1, 0, 2, 1, True),      # back
            (0, 1, 2, -1, True),     # left
            (2, 0, 1, -1, False),    # bottom
        ]

        for a, (i0, i1, i2, n, reverse) in enumerate(side_idxes):
            segs1 = segs[i1]
            segs2 = segs[i2]
            dim1_start = dims[i1] * -0.5
            dim2_start = dims[i2] * -0.5

            normal = Vec3()
            normal[i0] = n
            vertex[i0] = dims[i0] * 0.5 * n

            for j in range(segs1 + 1):
                vertex[i1] = dim1_start + j / segs1 * dims[i1]

                if i0 == 2:
                    u = j / segs1
                else:
                    u = (segs1 - j + offset_u) / segs_u if reverse else (j + offset_u) / segs_u

                for k in range(segs2 + 1):
                    vertex[i2] = dim2_start + k / segs2 * dims[i2]
                    v = k / segs2
                    vdata_values.extend(vertex)
                    vdata_values.extend(self.color)
                    vdata_values.extend(normal)
                    vdata_values.extend((u, v))
                if j > 0:
                    for k in range(segs2):
                        idx = vertex_count + j * (segs2 + 1) + k
                        prim_indices.extend((idx, idx - segs2 - 1, idx - segs2))
                        prim_indices.extend((idx, idx - segs2, idx + 1))

            vertex_count += (segs1 + 1) * (segs2 + 1)
            offset_u += segs2

        return vertex_count


class Cylinder(GeomRoot):
    """Create a geom node of cylinder.
       Args:
            radius (float): the radius of the cylinder; cannot be negative;
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum is 3;
            height (int): length of the cylinder;
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1;
    """

    def __init__(self, radius=0.5, segs_c=20, height=1, segs_a=2):
        self.radius = radius
        self.segs_c = segs_c
        self.height = height
        self.segs_a = segs_a
        super().__init__()

    def cap_vertices(self, delta_angle, bottom=True):
        z = 0 if bottom else self.height

        # vertex and uv of the center
        yield ((0, 0, z), (0.5, 0.5))

        # vertex and uv of triangles
        for i in range(self.segs_c):
            angle = delta_angle * i
            c = math.cos(angle)
            s = math.sin(angle)
            x = self.radius * c
            y = self.radius * s
            u = 0.5 + c * 0.5
            v = 0.5 - s * 0.5
            yield ((x, y, z), (u, v))

    def create_bottom_cap(self, delta_angle, vdata_values, prim_indices):
        normal = (0, 0, -1)
        color = (1, 1, 1, 1)

        # bottom cap center and triangle vertices
        for vertex, uv in self.cap_vertices(delta_angle, bottom=True):
            vdata_values.extend(vertex)
            vdata_values.extend(color)
            vdata_values.extend(normal)
            vdata_values.extend(uv)

        # the vertex order of the bottom cap vertices
        for i in range(self.segs_c - 1):
            prim_indices.extend((0, i + 2, i + 1))
        prim_indices.extend((0, 1, self.segs_c))

        return self.segs_c + 1

    def create_mantle(self, index_offset, delta_angle, vdata_values, prim_indices):
        vertex_count = 0

        # mantle triangle vertices
        for i in range(self.segs_a + 1):
            z = self.height * i / self.segs_a
            v = i / self.segs_a

            for j in range(self.segs_c + 1):
                angle = delta_angle * j
                x = self.radius * math.cos(angle)
                y = self.radius * math.sin(angle)
                normal = Vec3(x, y, 0.0).normalized()
                u = j / self.segs_c
                vdata_values.extend((x, y, z))
                vdata_values.extend((1, 1, 1, 1))
                vdata_values.extend(normal)
                vdata_values.extend((u, v))

            vertex_count += self.segs_c + 1

            # the vertex order of the mantle vertices
            if i > 0:
                for j in range(self.segs_c):
                    px = index_offset + i * (self.segs_c + 1) + j
                    prim_indices.extend((px, px - self.segs_c - 1, px - self.segs_c))
                    prim_indices.extend((px, px - self.segs_c, px + 1))

        return vertex_count

    def create_top_cap(self, index_offset, delta_angle, vdata_values, prim_indices):
        normal = (0, 0, 1)
        color = (1, 1, 1, 1)

        # top cap center and triangle vertices
        for vertex, uv in self.cap_vertices(delta_angle, bottom=False):
            vdata_values.extend(vertex)
            vdata_values.extend(color)
            vdata_values.extend(normal)
            vdata_values.extend(uv)

        # the vertex order of top cap vertices
        for i in range(index_offset + 1, index_offset + self.segs_c):
            prim_indices.extend((index_offset + self.segs_c, i - 1, i))
        prim_indices.extend((index_offset + self.segs_c, index_offset, index_offset + self.segs_c - 1))

        return self.segs_c + 1

    def create_vertices(self, vdata_values, prim_indices):
        delta_angle = 2 * math.pi / self.segs_c
        vertex_count = 0

        # create vertices of the bottom cap, mantle and top cap.
        vertex_count += self.create_bottom_cap(delta_angle, vdata_values, prim_indices)
        vertex_count += self.create_mantle(vertex_count, delta_angle, vdata_values, prim_indices)
        vertex_count += self.create_top_cap(vertex_count, delta_angle, vdata_values, prim_indices)

        return vertex_count


class SphereGeomMaker:

    def __init__(self):
        self.data = POLYHEDRONS['icosahedron']
        self.divnum = 3
        self.make_format()

    def make_format(self):
        arr_format = GeomVertexArrayFormat()
        arr_format.add_column('vertex', 3, Geom.NTFloat32, Geom.CPoint)
        arr_format.add_column('color', 4, Geom.NTFloat32, Geom.CColor)
        arr_format.add_column('normal', 3, Geom.NTFloat32, Geom.CNormal)
        self.format_ = GeomVertexFormat.register_format(arr_format)

    def make_geomnode(self, colors=None):
        # self.colors = colors if colors else Colors.select(2)
        self.colors = [LColor(0, 1, 0, 1), LColor(0.54, 0.16, 0.88, 1)]
        
        node = self._make_geomnode()
        return node

    def num_rows(self):
        """One triangle is subdivided into 4.
           The number of subdivide repetition is self.divnum.
           An icosahedron has 20 faces and a face has 3 vertices.
        """
        return 4 ** self.divnum * 20 * 3

    def calc_midpoints(self, face):
        """face: A list of Vec3, having 3 elements.
        """
        # (i, j): [(0, 1), (1, 2), (2, 0)]
        for i, pt1 in enumerate(face):
            j = i + 1 if i < len(face) - 1 else 0
            pt2 = face[j]
            mid_pt = (pt1 + pt2) / 2

            yield mid_pt

    def subdivide(self, face, divnum=0):
        if divnum == self.divnum:
            yield face
        else:
            midpoints = [pt for pt in self.calc_midpoints(face)]

            for i, vertex in enumerate(face):
                j = len(face) - 1 if i == 0 else i - 1
                face = [vertex, midpoints[i], midpoints[j]]
                yield from self.subdivide(face, divnum + 1)
            yield from self.subdivide(midpoints, divnum + 1)

    def faces(self):
        vertices = self.data['vertices']
        faces = self.data['faces']

        for tup in faces:
            face = [Vec3(vertices[n]) for n in tup]
            for subdiv_face in self.subdivide(face):
                idx = 0 if any(pt.z == 0 for pt in subdiv_face) else 1
                yield (subdiv_face, self.colors[idx])

    def _make_geomnode(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array("H", [])
        start = 0

        for face, rgba in self.faces():
            for pt in face:
                n = pt.normalized()
                vdata_values.extend(n)
                vdata_values.extend(rgba)
                vdata_values.extend(n)

            indices = (start, start + 1, start + 2)
            prim_indices.extend(indices)
            start += 3

        vdata = GeomVertexData('sphere', self.format_, Geom.UHStatic)
        vdata.unclean_set_num_rows(self.num_rows())
        vdata_mem = memoryview(vdata.modify_array(0)).cast('B').cast('f')
        vdata_mem[:] = vdata_values

        prim = GeomTriangles(Geom.UHStatic)
        prim_array = prim.modify_vertices()
        prim_array.unclean_set_num_rows(len(prim_indices))
        prim_mem = memoryview(prim_array).cast('B').cast('H')
        prim_mem[:] = prim_indices

        node = GeomNode('geomnode')
        geom = Geom(vdata)
        geom.add_primitive(prim)
        node.add_geom(geom)

        return node


POLYHEDRONS = {
    'icosahedron': {
        'vertices': [
            (-0.52573111, -0.72360680, 0.44721360),
            (-0.85065081, 0.27639320, 0.44721360),
            (-0.00000000, 0.89442719, 0.44721360),
            (0.85065081, 0.27639320, 0.44721360),
            (0.52573111, -0.72360680, 0.44721360),
            (0.00000000, -0.89442719, -0.44721360),
            (-0.85065081, -0.27639320, -0.44721360),
            (-0.52573111, 0.72360680, -0.44721360),
            (0.52573111, 0.72360680, -0.44721360),
            (0.85065081, -0.27639320, -0.44721360),
            (0.00000000, 0.00000000, 1.00000000),
            (-0.00000000, 0.00000000, -1.00000000)
        ],
        'faces': [
            (0, 1, 6), (0, 6, 5), (0, 5, 4), (0, 4, 10),
            (0, 10, 1), (1, 2, 7), (1, 7, 6), (1, 10, 2),
            (2, 3, 8), (2, 8, 7), (2, 10, 3), (3, 4, 9),
            (3, 9, 8), (3, 10, 4), (4, 5, 9), (5, 6, 11),
            (5, 11, 9), (6, 7, 11), (7, 8, 11), (8, 9, 11)
        ]
    }
}




class TestShape(NodePath):

    def __init__(self):
        super().__init__(BulletRigidBodyNode('testShape'))
        self.reparentTo(base.render)
        # model = Cube(3, 1.5, 1, 7, 4, 5)
        # model = Cube(2, 5, 3, 1, 4, 5)
        # model = Cube(1, 1, 1, 1, 1, 1)
        # model = RightTriangularPrism2()

        # model = RingShape(segs_rcnt=8, ring_radius=1)
        model = Cylinder(radius=0.5, segs_c=5, height=1, segs_a=2)

        model.reparent_to(self)
        # obj.reparentTo(self) <= いらない
        shape = BulletConvexHullShape()
        shape.addGeom(model.node().getGeom(0))
        self.node().addShape(shape)
        self.setCollideMask(BitMask32(1))
        self.setScale(1, 1, 1)
        self.setColor((0, 0, 1, 1))
        # self.setH(90)
        # self.setX(10)

        # tex = base.loader.loadTexture('layingrock.jpg')
        # tex.setWrapU(1)
        # tex.setWrapV(1)
        # model.setTexture(tex)


class Test(ShowBase):

    def __init__(self):
        super().__init__()
        self.disableMouse()
        self.camera.setPos(10, 10, 10)  # 20, -20, 5
        self.camera.lookAt(0, 0, 0)
        self.world = BulletWorld()

        # *******************************************
        collide_debug = self.render.attachNewNode(BulletDebugNode('debug'))
        self.world.setDebugNode(collide_debug.node())
        collide_debug.show()
        # *******************************************

        shape = TestShape()
        self.world.attachRigidBody(shape.node())
        shape.hprInterval(10, (360, 720, 360)).loop()
        self.accept('escape', sys.exit)
        self.taskMgr.add(self.update, 'update')

    def update(self, task):
        dt = globalClock.getDt()
        self.world.doPhysics(dt)
        return task.cont



if __name__ == '__main__':
    test = Test()
    test.run()