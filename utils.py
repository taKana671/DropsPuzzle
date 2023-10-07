import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

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


def round(val, digit=2):
    p = 10 ** digit
    return (val * p * 2 + 1) // 2 / p


def round_float(f, digit='0.01'):
    rounded = Decimal(str(f)).quantize(Decimal(digit), rounding=ROUND_HALF_UP)
    return float(rounded)


def set_logger():
    logger = logging.getLogger('log')
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s %(message)s')

    import sys
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    file_name = f'merge_ball_{datetime.now().strftime("%Y%m%d%H%M%S")}.log'
    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    # logger.info('setting log')