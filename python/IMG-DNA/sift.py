import cv2

import numpy as np
import img_dna_model


class SIFT(img_dna_model.ImgDnaModel):
    def __init__(self):
        super().__init__()

        self.sift = cv2.SIFT_create()

    def extract_dna(self, data):
        _, dna = self.sift.detectAndCompute(data, None)
        return np.array(dna)
