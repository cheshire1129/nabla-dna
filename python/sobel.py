import numpy as np


def _get_sobel_sum(bmp: np.ndarray, pos_w:int, pos_h:int):
    filter_w = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    filter_h = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

    sum_w = 0
    sum_h = 0
    for i in range(3):
        for j in range(3):
            gray = bmp[pos_h - 1 + j][pos_w - 1 + i]
            sum_w += gray * filter_w[j][i]
            sum_h += gray * filter_h[j][i]
    return abs(sum_w) + abs(sum_h)


def filter_sobel(bmp, width, height, sobel_threshold: float):
    if width <= 2 or height <= 2:
        raise Exception('bitmap should be larger than 2')

    bmp_sobel = np.ndarray((height - 2, width - 2))
    max_value = 0
    min_value = 255
    for h in range(1, height - 1):
        for w in range(1, width - 1):
            sobel = _get_sobel_sum(bmp, w, h)
            bmp_sobel[h - 1][w - 1] = sobel
            if max_value < sobel: max_value = sobel
            if min_value > sobel: min_value = sobel

    drop_off = int(min_value + (max_value - min_value) * sobel_threshold)

    for h in range(height - 2):
        for w in range(width - 2):
            if bmp_sobel[h][w] <= drop_off:
                bmp_sobel[h][w] = 0
            else:
                bmp_sobel[h][w] = int((bmp_sobel[h][w] - drop_off) / (max_value - drop_off) * 255)
                if bmp_sobel[h][w] == 0: bmp_sobel[h][w] = 1

    return bmp_sobel


def get_contour_bound(bmp, width, height, sobel_threshold: float):
    bmp_sobel = filter_sobel(bmp, width, height, sobel_threshold)
    found_h_start = False
    w_start = width - 2
    h_start = w_end = h_end = 0
    for h in range(0, height - 2):
        found_w_start = False
        for w in range(0, width - 2):
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
