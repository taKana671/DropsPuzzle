from panda3d.core import LineSegs
from panda3d.core import NodePath


def load_obj(file_path):
    vertices = []
    faces = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            li = [val for val in line.split(' ') if val]

            match li[0]:
                case 'v':
                    vertices.append(tuple(float(val) for val in li[1:]))

                case 'f':
                    faces.append(tuple(int(val) - 1 for val in li[1:]))

    return vertices, faces


def make_line(from_pt, to_pt, color):
    lines = LineSegs()
    lines.set_color(color)
    lines.move_to(from_pt)
    lines.draw_to(to_pt)
    lines.set_thickness(2.0)
    node = lines.create()

    return NodePath(node)