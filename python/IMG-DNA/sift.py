import cv2

import numpy as np
import img_dna_model


class SIFT(img_dna_model.ImgDnaModel):
    def __init__(self):
        super().__init__()

        self.sift = cv2.SIFT_create()
        self.verbose_level = 1 if img_dna_model.verbose else 0

    def extract_dna(self, data):
        _, dna = self.sift.detectAndCompute(data, None)
        return np.array(dna)

    def _get_similarity(self, img_name1, img_name2):
        dna1 = self._get_dna(img_name1)
        dna2 = self._get_dna(img_name2)
        bf = cv2.BFMatcher(cv2.NORM_L2)
        matches = bf.knnMatch(dna1, dna2, k=2)
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)
        # matching_ratio Not used
        matching_ratio = len(good_matches) / min(len(dna1), len(dna2))
        if len(good_matches) > 0:
            avg_distance = np.mean([m.distance for m in good_matches])
        else:
            avg_distance = float('inf')  # 매칭이 없을 경우

        max_distance = 300  # 임계값: 최대 허용 거리
        distance_similarity = max(1 - (avg_distance / max_distance), 0)
        return distance_similarity
