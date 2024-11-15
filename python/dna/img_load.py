import os
import cv2

from lib import logger

image_fpath: str = ""
gray_scaled = False
resized = 0


def _load_img_path(img_path):
    if os.path.exists(img_path):
        if gray_scaled:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        else:
            img = cv2.imread(img_path)
        if resized:
            img = cv2.resize(img, (resized, resized))
        return img
    return None


def _load_img_with_ext(name):
    img_path = os.path.join(image_fpath, name) if image_fpath else name
    return _load_img_path(img_path)


def load_img_data(name):
    img = _load_img_path(name)
    if img:
        return img
    for ext in ['bmp', 'jpg', 'png']:
        img = _load_img_with_ext(name + '.' + ext)
        if img is not None:
            return img
    logger.error("cannot load image: not found: " + name)
    exit(1)


def show_img(img_name):
    img = load_img_data(img_name)
    cv2.imshow(img_name, img)
    cv2.waitKey(0)


def save_img(path, img):
    cv2.imwrite(path, img)
