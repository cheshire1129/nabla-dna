import cv2

import numpy as np
import img_dna_model


def logistic(x):
  return 1 / (1 + np.exp(-x))


class ORB(img_dna_model.ImgDnaModel):
    def __init__(self):
        super().__init__()

        self.orb = cv2.ORB_create()
        self.verbose_level = 1 if img_dna_model.verbose else 0

    def extract_dna(self, data):
        _, dna = self.orb.detectAndCompute(data, None)
        return np.array(dna)

    def _get_similarity(self, img_name1, img_name2):
        dna1 = self._get_dna(img_name1)
        dna2 = self._get_dna(img_name2)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(dna1, dna2)

        # matching ratio is not used
        matching_ratio = len(matches) / min(len(dna1), len(dna2))
        if img_dna_model.similarity_type == 'distance':
            matches = sorted(matches, key=lambda x: x.distance)

            if len(matches) > 0:
                avg_distance = np.mean([m.distance for m in matches])
            else:
                avg_distance = float('inf')  # 매칭이 없을 경우

            max_distance = 200
            distance_similarity = max(1 - (avg_distance / max_distance), 0)
        else:
            matching_ratio = len(matches) / min(len(dna1), len(dna2))
            scale = 40 if matching_ratio < 0.1 else 5
            return 2 * logistic((matching_ratio - 0.1) * scale) - 1
        return distance_similarity
