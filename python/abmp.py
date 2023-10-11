from PIL import Image
import numpy as np
import math


class AveragedBitmap:
    def __init__(self, size_dna=0, gray_depth=256):
        self.size_dna = size_dna
        self.gray_depth = gray_depth
        self.bmp_dna = None
        self.width = 0
        self.height = 0
        if self.size_dna > 0:
            self.bmp_dna = np.ndarray((size_dna, size_dna))

    def _load_grayscale_bmp(self, path):
        img = Image.open(path)
        arr_img = np.array(img)
        if arr_img.shape[2] == 3:
            r, g, b = np.split(arr_img, 3, axis=2)
        else:
            r, g, b, t = np.split(arr_img, 4, axis=2)

        r = r.reshape(r.shape[:2])
        g = g.reshape(g.shape[:2])
        b = b.reshape(b.shape[:2])

        self.width = arr_img.shape[1]
        self.height = arr_img.shape[0]
        self.bmp_dna = list(map(lambda x: 0.299 * x[0] + 0.587 * x[1] + 0.114 * x[2], zip(r, g, b)))

    def _get_intensity_sum(self, fws: float, fwe: float, fhs: float, fhe: float) -> float:
        intensity_sum = 0

        ws: int = int(math.floor(fws))
        we: int = int(math.ceil(fwe))
        hs: int = int(math.floor(fhs))
        he: int = int(math.ceil(fhe))

        # following cases can occur due to floating point error
        if we >= self.width:
            we -= 1
        if he >= self.height:
            he -= 1
        for h in range(hs, he):
            weight: float = 1
            if h == hs:
                weight *= (1 - (fhs - hs))
            elif h == he - 1:
                weight *= (fhe - (he - 1))

            for w in range(ws, we):
                weight_cur: float = weight

                if w == ws:
                    weight_cur = weight * (1 - (fws - ws))
                elif w == we - 1:
                    weight_cur = weight * (fwe - (we - 1))
                intensity_sum += self.bmp_dna[h][w] * weight_cur
        return intensity_sum

    def _convert_averaged_bmp(self):
        bmp_avg = np.ndarray([self.size_dna, self.size_dna])
        bmp_unit_w = self.width / self.size_dna
        bmp_unit_h = self.height / self.size_dna

        for h in range(self.size_dna):
            for w in range(self.size_dna):
                bmp_avg[h][w] = self._get_intensity_sum(bmp_unit_w * w, bmp_unit_w * (w + 1), bmp_unit_h * h,
                                                        bmp_unit_h * (h + 1)) / (bmp_unit_w * bmp_unit_h)
        self.bmp_dna = bmp_avg

    def build_averaged_bitmap(self, path):
        self._load_grayscale_bmp(path)
        self._convert_averaged_bmp()
