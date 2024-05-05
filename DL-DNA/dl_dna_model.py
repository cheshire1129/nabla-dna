import numpy as np
import os
from abc import ABC, abstractmethod
from keras.preprocessing import image
from scipy import spatial


import logger
from lineEnumerator import LineEnumerator

image_fpath: str = ""
n_units = 64
epochs = 2
verbose = False


class DlDnaModel(ABC):
    def __int__(self):
        np.set_printoptions(precision=3)

    @abstractmethod
    def train(self, fpath: str):
        pass

    @abstractmethod
    def extract_dna(self, data):
        pass

    def _get_dna(self, img_name):
        imgdata = load_img_data(img_name)
        return self.extract_dna(np.array([imgdata]))

    def _get_similarity(self, img_name1, img_name2):
        dna1 = self._get_dna(img_name1)
        dna2 = self._get_dna(img_name2)
        return 1 - spatial.distance.cosine(dna1, dna2)

    def show_dna(self, img_name):
        dna = self._get_dna(img_name)
        print(f"{dna}")

    def show_similarity(self, img_name1, img_name2):
        similarity = self._get_similarity(img_name1, img_name2)
        print(f"{similarity:.4f}")

    def show_similarities(self, fpath_pairs: str):
        lines = LineEnumerator(fpath_pairs, True)
        for img_name1, img_name2 in lines:
            similarity = self._get_similarity(img_name1, img_name2)
            print(f"{img_name1} {img_name2}: {similarity:.4f}")

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
