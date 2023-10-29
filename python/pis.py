import numpy as np
import os
import re


class PIS:
    def __init__(self, path = None):
        self.dna = []
        self.is_pix = False
        self.dna_depth = 0
        self.dna_resolution = 0

        if path:
            self.open(path)

    def open(self, path):
        if not self.is_allowed_ext(path):
            return False

        self.is_pix = self._is_pix_ext(path)
        self._guess_dna(path)
        f = open(path, 'r')
        for line in f:
            for x in line.split():
                val = int(x, 16) if self.is_pix else int(x)
                self.dna.append(val)
        f.close()

        return True

    def get_dna(self):
        return np.array(self.dna)

    def _guess_dna(self, path):
        res = os.path.splitext(path)

        pat = re.compile('\.x(\d\d)d(\d)')
        matched = pat.match(os.path.splitext(res[0])[1])
        if matched:
            self.dna_resolution = int(matched.group(1))
            self.dna_depth = int(matched.group(2))

    @staticmethod
    def get_basename(path):
        res = os.path.splitext(path)

        pat = re.compile('\.x\d\dd\d')
        res2 = os.path.splitext(res[0])
        matched = pat.match(res2[1])
        if matched:
            return os.path.basename(res2[0])
        else:
            return os.path.basename(res[0])

    @staticmethod
    def is_allowed_ext(path):
        res = os.path.splitext(path)
        return True if res[1] == '.pis' or res[1] == '.pix' else False

    @staticmethod
    def _is_pix_ext(path):
        res = os.path.splitext(path)
        return True if res[1] == '.pix' else False
