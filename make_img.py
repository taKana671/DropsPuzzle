import numpy as np
from PIL import Image


def gradient_2d(start, stop, width, height, is_horizontal):
    if is_horizontal:
        return np.tile(np.linspace(start, stop, width), (height, 1))
    else:
        return np.tile(np.linspace(start, stop, height), (width, 1)).T


def gradient_3d(width, height, start_arr, stop_arr, horizontal_arr):
    result = np.zeros((height, width, len(start_arr)), dtype=np.float64)

    for i, (start, stop, is_horizontal) in enumerate(zip(start_arr, stop_arr, horizontal_arr)):
        result[:, :, i] = gradient_2d(start, stop, width, height, is_horizontal)

    return result


def make_img(width, height, start_arr, stop_arr, horizontal_arr, path):
    array = gradient_3d(width, height, start_arr, stop_arr, horizontal_arr)
    Image.fromarray(np.uint8(array)).save(path, quality=95)


if __name__ == '__main__':
    # make_img(300, 300, (0, 0, 0, 0), (255, 255, 255, 255), (False, False, False, False), 'test.png')
    make_img(300, 300, (255, 255, 255, 100), (0, 0, 0, 0), (False, False, False, False), 'test.png')