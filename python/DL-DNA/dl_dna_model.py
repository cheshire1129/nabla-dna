import numpy as np
import random
from abc import ABC, abstractmethod
from scipy import spatial

import img_load

from lineEnumerator import LineEnumerator

n_units = 64
epochs = 2
batch_size = 32
threshold = None
seed = 0
verbose = ""


class DlDnaModel(ABC):
    def __init__(self):
        global seed

        np.set_printoptions(precision=3)
        if seed != 0:
            random.seed(seed)
            np.random.seed(seed)
            import tensorflow
            tensorflow.random.set_seed(seed)

    @abstractmethod
    def train(self, fpath: str):
        pass

    @abstractmethod
    def extract_dna(self, data):
        pass

    def get_dna(self, img_name):
        imgdata = img_load.load_img_data(img_name)
        return self.extract_dna(np.array([imgdata]))

    def _get_distance(self, dna1, dna2):
        return spatial.distance.cosine(dna1, dna2)

    def _get_similarity(self, img_name1, img_name2):
        dna1 = self.get_dna(img_name1)
        dna2 = self.get_dna(img_name2)
        return 1 - self._get_distance(dna1, dna2)

    def show_dna(self, img_name):
        dna = self.get_dna(img_name)
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