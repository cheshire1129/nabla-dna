import os
from keras.preprocessing import image

import logger


image_fpath: str = ""


def _load_img_with_ext(name):
    img_path = os.path.join(image_fpath, name) if image_fpath else name
    if os.path.exists(img_path):
        return image.load_img(img_path, target_size=(224, 224))
    return None


def load_img(name):
    for ext in ['bmp', 'jpg', 'png']:
        img = _load_img_with_ext(name + '.' + ext)
        if img is not None:
            return img
    logger.error("cannot load image: not found: " + name)
    exit(1)


def load_img_data(name):
    img = load_img(name)
    return image.img_to_array(img)
