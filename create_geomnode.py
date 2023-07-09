import array
import math
import random
from enum import Enum

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


class Colors(Enum):

    RED = LColor(1, 0, 0, 1)
    BLUE = LColor(0, 0, 1, 1)
    YELLOW = LColor(1, 1, 0, 1)
    GREEN = LColor(0, 0.5, 0, 1)
    ORANGE = LColor(1, 0.549, 0, 1)
    MAGENTA = LColor(1, 0, 1, 1)
    PURPLE = LColor(0.501, 0, 0.501, 1)
    SKY = LColor(0, 0.74, 1, 1)
    LIME = LColor(0, 1, 0, 1)
    VIOLET = LColor(0.54, 0.16, 0.88, 1)

    @classmethod
    def select(cls, n):
        return random.sample([m.value for m in cls], n)


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


class DropsGeomRoot(GeomRoot):

    def create_format(self):
        arr_format = GeomVertexArrayFormat()
        arr_format.add_column('vertex', 3, Geom.NTFloat32, Geom.CPoint)
        arr_format.add_column('color', 4, Geom.NTFloat32, Geom.CColor)
        arr_format.add_column('normal', 3, Geom.NTFloat32, Geom.CNormal)
        fmt = GeomVertexFormat.register_format(arr_format)

        return fmt


class Sphere(DropsGeomRoot):

    def __init__(self):
        self.data = POLYHEDRONS['icosahedron']
        self.divnum = 3
        self.colors = Colors.select(2)
        super().__init__()

    def calc_midpoints(self, face):
        """face (list): list of Vec3; having 3 elements like below.
           [(0, 1), (1, 2), (2, 0)]
        """
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

    def create_vertices(self, vdata_values, prim_indices):
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

        return 4 ** self.divnum * 20 * 3


class Polyhedron(DropsGeomRoot):

    def __init__(self, key):
        self.data = POLYHEDRONS[key]
        super().__init__()

    def faces(self):
        vertices = self.data['vertices']
        faces = self.data['faces']
        color_pattern = set(len(elem) for elem in faces)
        self.colors = Colors.select(len(color_pattern))

        for face in faces:
            vert = (vertices[i] for i in face)
            normal = (Vec3(vertices[i]).normalized() for i in idxes)

            yield (vert, self.colors[n], normal, len(idxes))

    def num_rows(self):
        return sum(len(face) for face in self.data['faces'])

    def create_vertices(self, vdata_values, prim_indices):
        start = 0

        for verts, rgba, norms, num_verts in self.faces():
            for pt, norm in zip(verts, norms):
                vdata_values.extend(pt)
                vdata_values.extend(rgba)
                vdata_values.extend(norm)

            for indices in self.prim_indices(start, num_verts):
                prim_indices.extend(indices)
            start += num_verts

        vdata = GeomVertexData('polyhedron', self.format_, Geom.UHStatic)
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
        # obj.reparentTo(self) <= not needed
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