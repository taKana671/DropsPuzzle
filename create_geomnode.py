import array
import functools

from panda3d.core import Vec3, Point3
from panda3d.core import NodePath
from panda3d.core import Geom, GeomNode, GeomTriangles
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexArrayFormat

from utils import load_obj


OBJ_DIR = 'objs'


class GeomRoot(NodePath):

    def __init__(self, name, tex=True):
        geomnode = self.create_geomnode(name, tex)
        super().__init__(geomnode)
        self.set_two_sided(True)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if 'create_vertices' not in cls.__dict__:
            raise NotImplementedError('Subclasses should implement create_vertices.')

    def create_format(self, tex):
        arr_format = GeomVertexArrayFormat()
        arr_format.add_column('vertex', 3, Geom.NTFloat32, Geom.CPoint)
        arr_format.add_column('color', 4, Geom.NTFloat32, Geom.CColor)
        arr_format.add_column('normal', 3, Geom.NTFloat32, Geom.CColor)

        if tex:
            arr_format.add_column('texcoord', 2, Geom.NTFloat32, Geom.CTexcoord)

        fmt = GeomVertexFormat.register_format(arr_format)
        return fmt

    def create_geomnode(self, name, tex):
        fmt = self.create_format(tex)
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])

        vertex_count = self.create_vertices(vdata_values, prim_indices)

        vdata = GeomVertexData(name, fmt, Geom.UHStatic)
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
        super().__init__('cube')

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
        super().__init__('right_triangular_prism')

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


class TextureAtlasNode(GeomRoot):

    def __init__(self, max_u, start_v):
        self.max_u = max_u
        self.start_v = start_v
        self.color = (1, 1, 1, 1)
        super().__init__('texture_atlas')

    def create_vertices(self, vdata_values, prim_indices):
        vertices = [
            (-0.5, 0, 0.5),
            (-0.5, 0, -0.5),
            (0.5, 0, 0.5),
            (0.5, 0, -0.5),
        ]
        # order is important
        uvs = [
            (0, 1),
            (0, self.start_v),
            (self.max_u, 1),
            (self.max_u, self.start_v),
        ]

        for i, (vertex, uv) in enumerate(zip(vertices, uvs)):
            vdata_values.extend(vertex)
            vdata_values.extend(self.color)
            vdata_values.extend(Vec3(vertex).normalized())
            vdata_values.extend(uv)

        idx = 2
        prim_indices.extend((idx, idx - 2, idx - 1))
        prim_indices.extend((idx, idx - 1, idx + 1))

        return len(vertices)


class Sphere(GeomRoot):
    """Create a geom node of sphere.
        Arges:
            divnum (int): the number of divisions of a triangle; cannot be negative;
            pattern (int): the pattern of a sphere
                0: one color
                1: dot; two color
                2: one line; two color
    """

    def __init__(self, colors, divnum=3, pattern=0):
        self.obj_file = f'{OBJ_DIR}/icosahedron.obj'
        self.divnum = divnum
        self.pattern = pattern
        self.colors = colors
        super().__init__('sphere', False)

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

    def get_vertex_color(self, indexer, colors, pts):
        idx = indexer(pts)
        return colors[idx]

    def create_vertices(self, vdata_values, prim_indices):
        vertices, faces = load_obj(self.obj_file)

        match self.pattern:
            case 0:
                get_vertex_color = functools.partial(
                    self.get_vertex_color,
                    lambda vertices: 0,
                    self.colors.select(1)
                )
            case 1:
                get_vertex_color = functools.partial(
                    self.get_vertex_color,
                    lambda vertices: 0 if any(not (v.z or v.x) or not (v.z or v.y) or not (v.x or v.y) for v in vertices) else 1,
                    self.colors.select(2)
                )
            case 2:
                get_vertex_color = functools.partial(
                    self.get_vertex_color,
                    lambda vertices: 0 if any(v.z == 0 for v in vertices) else 1,
                    self.colors.select(2)
                )

        start = 0
        for face in faces:
            face_verts = [Vec3(vertices[n]) for n in face]
            for subdiv_face in self.subdivide(face_verts):
                color = get_vertex_color(subdiv_face)
                for vert in subdiv_face:
                    normal = vert.normalized()
                    vdata_values.extend(normal)
                    vdata_values.extend(color)
                    vdata_values.extend(normal)

                indices = (start, start + 1, start + 2)
                prim_indices.extend(indices)
                start += 3

        return 4 ** self.divnum * 20 * 3


class Polyhedron(GeomRoot):

    def __init__(self, colors, file_name):
        self.obj_file = f'{OBJ_DIR}/{file_name}'
        self.colors = colors
        super().__init__('polyhedron', False)

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
        vertices, faces = load_obj(self.obj_file)
        nums = set(len(face) for face in faces)
        colors = self.colors.select(len(nums))
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