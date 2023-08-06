import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


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


def make_star_mask(size, peak_cnt, peak_r, ratio, file_path):
    """
        size (tuple) : containing (width, height) in pixels.
    """
    mask = Image.new('RGB', size, 0)
    draw = ImageDraw.Draw(mask)
    center_x = size[0] / 2
    center_y = size[1] / 2
    vally_r = peak_r * ratio

    step = int(360 / peak_cnt)
    delta = 360 / (peak_cnt * 2)
    points = []

    for i in range(0, 360, step):
        peak_angle = i / 360 * np.pi * 2
        peak_x = int(center_x + peak_r * np.sin(peak_angle))
        peak_y = int(center_y - peak_r * np.cos(peak_angle))
        points.append((peak_x, peak_y))

        vally_angle = (delta + i) / 360 * np.pi * 2
        vally_x = int(center_x + vally_r * np.sin(vally_angle))
        vally_y = int(center_y - vally_r * np.cos(vally_angle))
        points.append((vally_x, vally_y))

    draw.polygon(points, fill=(255, 255, 255))
    mask.save(file_path)


def blur(file_path, save_path, ksize):
    # mask = cv2.GaussianBlur(mask, (51, 51), 0)
    # mask = mask.filter(ImageFilter.GaussianBlur(4))
    mask = cv2.imread(file_path)
    mask_blur = cv2.GaussianBlur(mask, (25, 25), 0)
    cv2.imwrite(save_path, mask_blur)


def transparent(file_path, save_path):
    img = Image.open(file_path)
    img.putalpha(0)
    arr = np.array(img)
    arr[:, :, 3] = arr[:, :, 0]
    new = Image.fromarray(arr)
    new.save(save_path)


def make_circke_mask(size, file_path):
    mask = np.zeros(size)
    cv2.circle(mask, (150, 150), 20, (255, 255, 255), thickness=-1)
    cv2.imwrite(file_path, mask)



if __name__ == '__main__':
    size = (300, 300)
    # make_star_mask(size, 6, 100, 0.1, 'star.png')
    # blur('star.png', 'star_mask.png', (25, 25))
    # transparent('star_mask.png', 'dest.png')

    # make_circke_mask(size, ('circle.png'))
    # blur('circle.png', 'circle_blur.png', (135, 135))
    transparent('mask.png', 'circle_mask_2.png')


    # make_img(300, 300, (0, 0, 0, 0), (255, 255, 255, 255), (False, False, False, False), 'test.png')
    # make_img(300, 300, (255, 255, 255, 100), (0, 0, 0, 0), (False, False, False, False), 'test.png')
    # make_img(300, 300, (220, 220, 220, 100), (0, 0, 0, 0), (False, False, False, False), 'test.png')