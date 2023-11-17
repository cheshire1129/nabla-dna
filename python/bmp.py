from PIL import Image
import numpy as np

from sobel import filter_sobel, get_contour_bound


class Bitmap:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.as_contour = False
        self.bmp_dna = None

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

    def reduce_bound(self, threshold: float, ksize: int = 3):
        w_start, h_start, w_end, h_end = get_contour_bound(self.bmp_dna, self.width, self.height, threshold, ksize)

        bmp_reduced = np.ndarray((h_end - h_start + 1, w_end - w_start + 1))
        for h in range(h_end - h_start + 1):
            for w in range(w_end - w_start + 1):
                bmp_reduced[h][w] = self.bmp_dna[h_start + h][w_start + w]
        self.bmp_dna = bmp_reduced
        self.width = w_end - w_start + 1
        self.height = h_end - h_start + 1

    def do_sobel(self, sobel_threshold: float):
        if sobel_threshold > 1:
            self.as_contour = True
            sobel_threshold -= 1

        self.bmp_dna = filter_sobel(self.bmp_dna, self.width, self.height, sobel_threshold)
        self.width -= 2
        self.height -= 2
