import numpy as np
import os


class PIS:
    def __init__(self):
        self.dna = []

    def open(self, path):
        is_pix = self._is_pix_ext(path)
        f = open(path, 'r')
        for line in f:
            for x in line.split():
                val = int(x, 16) if is_pix else int(x)
                self.dna.append(val)
        f.close()

    def get_dna(self):
        return np.array(self.dna)

    @staticmethod
    def is_pis_ext(path):
        res = os.path.splitext(path)
        return True if res[1] == '.pis' or res[1] == '.pix' else False

    @staticmethod
    def _is_pix_ext(path):
        res = os.path.splitext(path)
        return True if res[1] == '.pix' else False
