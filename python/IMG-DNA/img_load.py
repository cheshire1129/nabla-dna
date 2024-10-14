import os

import logger
import cv2

image_fpath: str = ""
grayscaled = False
resized = 0

def _load_img_path(img_path):
    if os.path.exists(img_path):
        if grayscaled:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        else:
            img = cv2.imread(img_path)
        if resized > 0:
            return cv2.resize(img, (resized, resized))
        return img
    return None


def _load_img_with_ext(name):
    img_path = os.path.join(image_fpath, name) if image_fpath else name
    return _load_img_path(img_path)


def load_img(name):
    if os.path.isfile(name):
        return _load_img_path(name)
    for ext in ['bmp', 'jpg', 'png']:
        img = _load_img_with_ext(name + '.' + ext)
        if img is not None:
            return img
    logger.error("cannot load image: not found: " + name)
    exit(1)


def load_img_data(name):
    return load_img(name)
