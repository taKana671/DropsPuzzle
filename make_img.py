import glob
import os

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


def crop_img(path, save_dir, cols, rows):
    img = Image.open(path)
    w, h = img.size
    w_crop = w / cols
    h_crop = h / rows

    for i in range(rows):
        upper = i * h_crop
        lower = upper + h_crop

        for j in range(cols):
            left = j * w_crop
            right = left + w_crop
            img_crop = img.crop((left, upper, right, lower))
            img_crop.save(f'{save_dir}/{i * cols + j}.png', quality=95)


def paste_img(file_name, w, h, rows, cols):
    dest = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    width = int(w / cols)
    height = int(h / rows)

    li = glob.glob('work/*.png')
    li.sort(key=lambda x: int(os.path.basename(x).split('.')[0]))
    limit = rows * cols

    r, c = 0, 0

    for i, f in enumerate(li[:limit]):
        img = Image.open(f)
        resized = img.resize((width, height))

        if i % cols == 0:
            r += 1
            c = 0

        dest.paste(resized, (c * width, r * height))
        c += 1

    dest.save(f'{file_name}.png', quality=95)


def delete_files(dir):
    for f in glob.glob(f'{dir}/*.png'):
        os.remove(f)


if __name__ == '__main__':
    delete_files('work')
    crop_img('pngegg.png', 'work', 8, 7)
    paste_img('paste9', 1024, 1024, 8, 8)