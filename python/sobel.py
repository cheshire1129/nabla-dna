import numpy as np


def _get_sobel_sum(bmp: np.ndarray, pos_w:int, pos_h:int, ksize:int):
    filter_w = [[-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2], [-4, -2, 0, 2, 4], [-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2]]
    filter_h = [[-2, -2, -4, -2, -2], [-1, -1, -2, -1, -1], [0, 0, 0, 0, 0], [1, 1, 2, 1, 1], [2, 2, 4, 2, 2]]

    base_idx = 0 if ksize == 5 else 1
    sum_w = 0
    sum_h = 0
    for i in range(ksize):
        for j in range(ksize):
            gray = bmp[pos_h - 1 + j][pos_w - 1 + i]
            sum_w += gray * filter_w[base_idx + j][base_idx + i]
            sum_h += gray * filter_h[base_idx + j][base_idx + i]
    return abs(sum_w) + abs(sum_h)


def filter_sobel(bmp, width, height, sobel_threshold: float, ksize: int = 3):
    if width < ksize or height < ksize:
        raise Exception(f'bitmap should be larger than {ksize}')

    bmp_sobel = np.ndarray((height - (ksize - 1), width - (ksize - 1)))
    max_value = 0
    min_value = 255
    for h in range(int(ksize / 2), height - int(ksize / 2)):
        for w in range(int(ksize / 2), width - int(ksize / 2)):
            sobel = _get_sobel_sum(bmp, w, h, 3)
            bmp_sobel[h - int(ksize / 2)][w - int(ksize / 2)] = sobel
            if max_value < sobel: max_value = sobel
            if min_value > sobel: min_value = sobel

    drop_off = int(min_value + (max_value - min_value) * sobel_threshold)

    for h in range(height - (ksize - 1)):
        for w in range(width - (ksize - 1)):
            if bmp_sobel[h][w] <= drop_off:
                bmp_sobel[h][w] = 0
            else:
                bmp_sobel[h][w] = int((bmp_sobel[h][w] - drop_off) / (max_value - drop_off) * 255)
                if bmp_sobel[h][w] == 0: bmp_sobel[h][w] = 1

    return bmp_sobel


def get_contour_bound(bmp, width, height, sobel_threshold: float, ksize: float = 3):
    bmp_sobel = filter_sobel(bmp, width, height, sobel_threshold, ksize)
    found_h_start = False
    w_start = width - (ksize - 1)
    h_start = w_end = h_end = 0
    for h in range(0, height - (ksize - 1)):
        found_w_start = False
        for w in range(0, width - (ksize - 1)):
            if bmp_sobel[h][w] != 0:
                if not found_w_start:
                    found_w_start = True
                    if w < w_start:
                        w_start = w
                if not found_h_start:
                    found_h_start = True
                    h_start = h
                w_end = w
                h_end = h
    return w_start, h_start, w_end, h_end
