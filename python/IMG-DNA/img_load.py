import os

import logger
import cv2

image_fpath: str = ""


def _load_img_with_ext(name):
    img_path = os.path.join(image_fpath, name) if image_fpath else name
    if os.path.exists(img_path):
        return cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    return None


def load_img(name):
    for ext in ['bmp', 'jpg', 'png']:
        img = _load_img_with_ext(name + '.' + ext)
        if img is not None:
            return img
    logger.error("cannot load image: not found: " + name)
    exit(1)


def load_img_data(name):
    return load_img(name)
