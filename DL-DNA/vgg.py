import numpy as np
from keras.applications import VGG16

import dl_dna_model


class VGG(dl_dna_model.DlDnaModel):
    def __init__(self):
        super().__init__()

        self.dl_model = VGG16(weights='imagenet', include_top=True)
        self.verbose_level = 1 if dl_dna_model.verbose else 0

    def train(self, fpath_train: str):
        print("training for VGG is not supported")
        exit(1)

    def extract_dna(self, data):
        res = self.dl_model.predict(data, verbose=self.verbose_level)
        # 1000 is the number of VGG classes
        # ASSUME: n_units is divisor of 1000
        cnt_avg = int(1000 / dl_dna_model.n_units)
        dna = []
        start = 0
        for i in range(dl_dna_model.n_units):
            dna.append(np.mean(res[0, start: start + cnt_avg]) * cnt_avg)
            start += cnt_avg
        return np.array(dna)
