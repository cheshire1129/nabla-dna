import numpy as np
import random
from abc import ABC, abstractmethod
from scipy import spatial

import img_load

from lineEnumerator import LineEnumerator

verbose = ""
threshold = None
similarity_type = None


class ImgDnaModel(ABC):
    @abstractmethod
    def extract_dna(self, data):
        pass

    def _get_dna(self, img_name):
        imgdata = img_load.load_img_data(img_name)
        return self.extract_dna(np.array(imgdata))

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