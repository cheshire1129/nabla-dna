from PIL import Image
import numpy as np
import math


class AveragedBitmap:
    def __init__(self, dna_resolution=0):
        self.dna_resolution = dna_resolution
        self.bmp_dna = None
        self.width = 0
        self.height = 0
        self.as_contour = False
        if self.dna_resolution > 0:
            self.bmp_dna = np.ndarray((dna_resolution, dna_resolution))

    def load_grayscale_bmp(self, path):
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
        if we > self.width: we -= 1
        if he > self.height: he -= 1

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

    def convert_averaged_bmp(self):
        bmp_avg = np.ndarray([self.dna_resolution, self.dna_resolution])
        bmp_unit_w = self.width / self.dna_resolution
        bmp_unit_h = self.height / self.dna_resolution

        for h in range(self.dna_resolution):
            for w in range(self.dna_resolution):
                bmp_avg[h][w] = self._get_intensity_sum(bmp_unit_w * w, bmp_unit_w * (w + 1), bmp_unit_h * h,
                                                        bmp_unit_h * (h + 1)) / (bmp_unit_w * bmp_unit_h)
        self.bmp_dna = bmp_avg
        self.width = self.dna_resolution
        self.height = self.dna_resolution

    def build_averaged_bitmap(self, path):
        self.load_grayscale_bmp(path)
        self.convert_averaged_bmp()

    def do_sobel(self, sobel_threshold: float):
        if self.dna_resolution <= 3:
            raise Exception('DNA resolution should be larger than 3')

        filter_w = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        filter_h = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

        if sobel_threshold > 1:
            self.as_contour = True
            sobel_threshold -= 1

        bmp_sobeled = np.ndarray([self.dna_resolution - 2, self.dna_resolution - 2])
        max_value = 0
        min_value = 255
        for h in range(1, self.dna_resolution - 1):
            for w in range(1, self.dna_resolution - 1):
                sum_w = 0
                sum_h = 0
                for i in range(3):
                    for j in range(3):
                        gray = self.bmp_dna[h - 1 + j][w - 1 + i]
                        sum_w += gray * filter_w[j][i]
                        sum_h += gray * filter_h[j][i]
                sobel = abs(sum_w) + abs(sum_h)
                bmp_sobeled[h - 1][w - 1] = sobel
                if max_value < sobel:
                    max_value = sobel
                if min_value > sobel:
                    min_value = sobel
        drop_off = int(min_value + (max_value - min_value) * sobel_threshold)
        self.dna_resolution -= 2
        self.width -= 2
        self.height -= 2
        self.bmp_dna = bmp_sobeled

        for h in range(0, self.dna_resolution):
            for w in range(0, self.dna_resolution):
                if self.bmp_dna[h][w] <= drop_off:
                    self.bmp_dna[h][w] = 0
                else:
                    if self.as_contour:
                        self.bmp_dna[h][w] = 255
                    else:
                        self.bmp_dna[h][w] = int((self.bmp_dna[h][w] - drop_off) / (max_value - drop_off) * 255)
