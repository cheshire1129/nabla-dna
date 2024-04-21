import numpy as np
import os
from abc import ABC, abstractmethod
from keras.preprocessing import image


import logger
from lineEnumerator import LineEnumerator

image_fpath: str = ""
n_units = 64
epochs = 2
verbose = False


class DlDnaModel(ABC):
    @abstractmethod
    def train(self, fpath: str):
        pass

    @abstractmethod
    def extract_dna(self, data):
        pass

    def extract(self, fpath_extract: str):
        np.set_printoptions(precision=3)

        img_names = LineEnumerator(fpath_extract)
        for img_name in img_names:
            imgdata = load_img_data(img_name)
            res = self.extract_dna(np.array([imgdata]))
            print(f"{img_name}: {res}")

    # noinspection PyMethodMayBeStatic
    def save(self, path_save: str):
        print("saving model is not supported")
        exit(1)

    # noinspection PyMethodMayBeStatic
    def load(self, path_load: str):
        print("loading model is not supported")
        exit(1)


def _load_img_data_with_ext(name):
    img_path = os.path.join(image_fpath, name) if image_fpath else name
    if os.path.exists(img_path):
        img = image.load_img(img_path, target_size=(224, 224))
        if img is not None:
            return image.img_to_array(img)
    return None


def load_img_data(name):
    for ext in ['bmp', 'jpg', 'png']:
        img = _load_img_data_with_ext(name + '.' + ext)
        if img is not None:
            return img
    logger.error("cannot load image data: not found: " + name)
    exit(1)
