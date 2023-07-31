import array
import random
from enum import Enum

from panda3d.core import Vec3, Point3, LColor
from panda3d.core import NodePath
from panda3d.core import Geom, GeomNode, GeomTriangles
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexArrayFormat


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
        # super().__init__('geomnode')
        # self.attach_new_node(geomnode)
        # self.set_two_sided(True)
        # self.find('**/+GeomNode').node()
        # import pdb; pdb.set_trace()
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


class RightTriangularPrism(GeomRoot):
    """Create a geom node of right triangular prism.
        Arges:
            w (float): width; dimension along the x-axis; cannot be negative;
            d (float): depth; dimension along the y-axis; cannot be negative;
            h (float): height; dimension along the z-axis; cannot be negative;
            segs_h (int) the number of subdivisions in height
    """

    def __init__(self, w=1.0, d=1.0, h=1.0, segs_h=2):
        self.w = w
        self.d = d
        self.h = h
        self.segs_h = segs_h
        self.color = (1, 1, 1, 1)
        super().__init__()

    def create_caps(self, points, index_offset, vdata_values, prim_indices):
        vertex_count = 0
        normal = (0, 0, 1) if all(pt.z > 0 for pt in points) else (0, 0, -1)

        for i, pt in enumerate(points):
            # u = i / (len(points) - 1)
            uv = (i, 0) if i < (len(points) - 1) else (0, 1)
            vdata_values.extend(pt)
            vdata_values.extend(self.color)
            vdata_values.extend(normal)
            vdata_values.extend(uv)
            vertex_count += 1

        prim_indices.extend((index_offset, index_offset + 2, index_offset + 1))

        return vertex_count

    def create_sides(self, sides, index_offset, vdata_values, prim_indices):
        vertex_count = 0
        vertex = Point3()
        segs_u = len(sides)

        for a, pts in enumerate(sides):
            pts_cnt = len(pts)

            if pts[0].y < 0 and pts[1].y > 0:
                normal = Vec3(1, 1, 0).normalized()
            elif pts[0].x < 0 and pts[1].x < 0:
                normal = Vec3(-1, 0, 0)
            elif pts[0].y < 0 and pts[1].y < 0:
                normal = Vec3(0, -1, 0)

            for i in range(self.segs_h + 1):
                v = i / self.segs_h
                vertex.z = -self.h / 2 + i / self.segs_h * self.h

                for j in range(pts_cnt):
                    pt = pts[j]
                    vertex.x, vertex.y = pt.x, pt.y
                    u = (a + j) / segs_u

                    vdata_values.extend(vertex)
                    vdata_values.extend(self.color)
                    vdata_values.extend(normal)
                    vdata_values.extend((u, v))
                    vertex_count += 1

                if i > 0:
                    idx = index_offset + i * 2
                    prim_indices.extend((idx, idx - 2, idx - 1))
                    prim_indices.extend((idx, idx - 1, idx + 1))

            index_offset += pts_cnt * (self.segs_h + 1)

        return vertex_count

    def create_vertices(self, vdata_values, prim_indices):
        half_w = self.w / 2
        half_d = self.d / 2
        half_h = self.h / 2

        top = [
            Point3(-half_w, half_d, half_h),
            Point3(-half_w, -half_d, half_h),
            Point3(half_w, -half_d, half_h)
        ]
        bottom = [
            Point3(-half_w, half_d, -half_h),
            Point3(-half_w, -half_d, -half_h),
            Point3(half_w, -half_d, -half_h)
        ]

        sides = [
            (bottom[0], bottom[1]),
            (bottom[1], bottom[2]),
            (bottom[2], bottom[0]),
        ]

        vertex_count = 0
        vertex_count += self.create_caps(top, vertex_count, vdata_values, prim_indices)
        vertex_count += self.create_sides(sides, vertex_count, vdata_values, prim_indices)
        vertex_count += self.create_caps(bottom, vertex_count, vdata_values, prim_indices)

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

    def create_vertices(self, vdata_values, prim_indices):
        vertices = self.data['vertices']
        faces = self.data['faces']
        colors = Colors.select(2)

        start = 0

        for face in faces:
            face_verts = [Vec3(vertices[n]) for n in face]
            for subdiv_face in self.subdivide(face_verts):
                i = 0 if any(pt.z == 0 for pt in subdiv_face) else 1
                color = colors[i]

                for vert in subdiv_face:
                    normal = vert.normalized()
                    vdata_values.extend(normal)
                    vdata_values.extend(color)
                    vdata_values.extend(normal)

                indices = (start, start + 1, start + 2)
                prim_indices.extend(indices)
                start += 3

        return 4 ** self.divnum * 20 * 3


class Polyhedron(DropsGeomRoot):

    def __init__(self, key):
        self.data = POLYHEDRONS[key]
        super().__init__()

    def triangle(self, start):
        return (start, start + 1, start + 2)

    def square(self, start):
        for x, y, z in [(2, 1, 0), (0, 3, 2)]:
            yield (start + x, start + y, start + z)

    def polygon(self, start, vertices_num):
        for i in range(2, vertices_num):
            if i == 2:
                yield (start, start + i - 1, start + i)
            else:
                yield (start + i - 1, start, start + i)

    def get_indices(self, start, num):
        match num:
            case 3:
                yield self.triangle(start)
            case 4:
                yield from self.square(start)
            case _:
                yield from self.polygon(start, num)

    def create_vertices(self, vdata_values, prim_indices):
        vertices = self.data['vertices']
        faces = self.data['faces']
        nums = set(len(face) for face in faces)
        colors = Colors.select(len(nums))
        face_color = {n: colors[i] for i, n in enumerate(nums)}

        start = 0

        for face in faces:
            cnt = len(face)
            color = face_color[len(face)]
            for idx in face:
                vertex = Vec3(vertices[idx])
                normal = vertex.normalized()

                vdata_values.extend(vertex)
                vdata_values.extend(color)
                vdata_values.extend(normal)

            for indices in self.get_indices(start, cnt):
                prim_indices.extend(indices)
            start += cnt

        return sum(len(face) for face in faces)


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
    },
    'icosidodecahedron': {
        'vertices': [
            (-0.30901699, -0.95105652, -0.00000000),
            (-0.80901699, -0.58778525, -0.00000000),
            (-1.00000000, 0.00000000, -0.00000000),
            (-0.80901699, 0.58778525, -0.00000000),
            (-0.30901700, 0.95105652, -0.00000000),
            (0.30901699, 0.95105652, -0.00000000),
            (0.80901699, 0.58778525, -0.00000000),
            (1.00000000, 0.00000000, -0.00000000),
            (0.80901699, -0.58778525, -0.00000000),
            (0.30901699, -0.95105652, -0.00000000),
            (0.00000000, -0.85065081, -0.52573111),
            (-0.80901699, -0.26286556, -0.52573111),
            (-0.50000000, 0.68819096, -0.52573111),
            (0.50000000, 0.68819096, -0.52573111),
            (0.80901699, -0.26286556, -0.52573111),
            (-0.30901699, -0.42532540, -0.85065081),
            (-0.50000000, 0.16245985, -0.85065081),
            (0.00000000, 0.52573111, -0.85065081),
            (0.50000000, 0.16245985, -0.85065081),
            (0.30901699, -0.42532540, -0.85065081),
            (-0.50000000, -0.68819096, 0.52573111),
            (0.50000000, -0.68819096, 0.52573111),
            (0.80901699, 0.26286556, 0.52573111),
            (-0.00000000, 0.85065081, 0.52573111),
            (-0.80901699, 0.26286556, 0.52573111),
            (0.00000000, -0.52573111, 0.85065081),
            (0.50000000, -0.16245985, 0.85065081),
            (0.30901699, 0.42532540, 0.85065081),
            (-0.30901699, 0.42532540, 0.85065081),
            (-0.50000000, -0.16245985, 0.85065081)
        ],
        'faces': [
            (0, 1, 11, 15, 10), (0, 10, 9), (0, 9, 21, 25, 20), (0, 20, 1),
            (1, 2, 11), (1, 20, 29, 24, 2), (2, 3, 12, 16, 11), (2, 24, 3),
            (3, 4, 12), (3, 24, 28, 23, 4), (4, 5, 13, 17, 12), (4, 23, 5),
            (5, 6, 13), (5, 23, 27, 22, 6), (6, 7, 14, 18, 13), (6, 22, 7),
            (7, 8, 14), (7, 22, 26, 21, 8), (8, 9, 10, 19, 14), (8, 21, 9),
            (10, 15, 19), (11, 16, 15), (12, 17, 16), (13, 18, 17),
            (14, 19, 18), (15, 16, 17, 18, 19), (20, 25, 29), (21, 26, 25),
            (22, 27, 26), (23, 28, 27), (24, 29, 28), (25, 26, 27, 28, 29)
        ],
    },
    'truncated_octahedron': {
        'vertices': [
            (-0.31622777, -0.54772256, 0.77459667),
            (-0.63245553, 0.00000000, 0.77459667),
            (-0.31622777, 0.54772256, 0.77459667),
            (0.31622777, 0.54772256, 0.77459667),
            (0.63245553, -0.00000000, 0.77459667),
            (0.31622777, -0.54772256, 0.77459667),
            (-0.31622777, -0.91287093, 0.25819889),
            (-0.94868330, 0.18257419, 0.25819889),
            (-0.63245553, 0.73029674, 0.25819889),
            (0.63245553, 0.73029674, 0.25819889),
            (0.94868330, 0.18257419, 0.25819889),
            (0.31622777, -0.91287093, 0.25819889),
            (-0.63245553, -0.73029674, -0.25819889),
            (-0.94868330, -0.18257419, -0.25819889),
            (-0.31622777, 0.91287093, -0.25819889),
            (0.31622777, 0.91287093, -0.25819889),
            (0.94868330, -0.18257419, -0.25819889),
            (0.63245553, -0.73029674, -0.25819889),
            (-0.31622777, -0.54772256, -0.77459667),
            (-0.63245553, 0.00000000, -0.77459667),
            (-0.31622777, 0.54772256, -0.77459667),
            (0.31622777, 0.54772256, -0.77459667),
            (0.63245553, -0.00000000, -0.77459667),
            (0.31622777, -0.54772256, -0.77459667)
        ],
        'faces': [
            (0, 6, 11, 5),
            (0, 5, 4, 3, 2, 1),
            (0, 1, 7, 13, 12, 6),
            (1, 2, 8, 7),
            (2, 3, 9, 15, 14, 8),
            (3, 4, 10, 9),
            (4, 5, 11, 17, 16, 10),
            (6, 12, 18, 23, 17, 11),
            (7, 8, 14, 20, 19, 13),
            (9, 10, 16, 22, 21, 15),
            (12, 13, 19, 18),
            (14, 15, 21, 20),
            (16, 17, 23, 22),
            (18, 19, 20, 21, 22, 23)
        ]
    },
}