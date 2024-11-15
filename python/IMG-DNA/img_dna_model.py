import cv2
import numpy as np
from abc import ABC

from dna import dna_model

threshold = 0.75
similarity_type = None


def logistic(x):
    return 1 / (1 + np.exp(-x))


class ImgDnaModel(dna_model.DnaModel, ABC):
    def __init__(self):
        super().__init__()

    def _get_similarity(self, img_name1, img_name2):
        dna1 = self.get_dna(img_name1)
        dna2 = self.get_dna(img_name2)
        bf = cv2.BFMatcher(cv2.NORM_L2)
        matches = bf.knnMatch(dna1, dna2, k=2)
        good_matches = []
        for m, n in matches:
            if m.distance < threshold * n.distance:
                good_matches.append(m)
        if similarity_type == 'distance':
            if len(good_matches) > 0:
                avg_distance = np.mean([m.distance for m in good_matches])
            else:
                avg_distance = float('inf')  # 매칭이 없을 경우
            max_distance = 300  # 임계값: 최대 허용 거리
            distance_similarity = max(1 - (avg_distance / max_distance), 0)
            return 2 * (distance_similarity - 0.5)
        else:
            matching_ratio = len(good_matches) / min(len(dna1), len(dna2))
            scale = 40 if matching_ratio < 0.1 else 5
            return 2 * logistic((matching_ratio - 0.1) * scale) - 1
