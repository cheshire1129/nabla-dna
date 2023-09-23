from PIL import Image
import numpy as np
import math


def _get_intensity_sum(bmp, fws: float, fwe: float, fhs: float, fhe: float) -> float:
    intensity_sum = 0

    ws: int = int(math.floor(fws))
    we: int = int(math.ceil(fwe))
    hs: int = int(math.floor(fhs))
    he: int = int(math.ceil(fhe))

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
            intensity_sum += bmp[h][w] * weight_cur
    return intensity_sum


class Bitmap:
    def __init__(self, size_dna=0, gray_depth=256, rotation=False):
        self.size_dna = size_dna
        self.gray_depth = gray_depth
        self.rotation = rotation
        self.bmp_dna = None
        if self.size_dna > 0:
            self.bmp_dna = np.ndarray((size_dna, size_dna))

    def build_dna_bitmap(self, path, norm_gray=False):
        img = Image.open(path)
        arr_img = np.array(img)
        if arr_img.shape[2] == 3:
            r, g, b = np.split(arr_img, 3, axis=2)
        else:
            r, g, b, t = np.split(arr_img, 4, axis=2)

        r = r.reshape(r.shape[:2])
        g = g.reshape(g.shape[:2])
        b = b.reshape(b.shape[:2])

        bmp = list(map(lambda x: 0.299 * x[0] + 0.587 * x[1] + 0.114 * x[2], zip(r, g, b)))
        bmp_unit_w = arr_img.shape[1] / (self.size_dna + 1)
        bmp_unit_h = arr_img.shape[0] / (self.size_dna + 1)

        for j in range(self.size_dna):
            for i in range(self.size_dna):
                self.bmp_dna[j][i] = _get_intensity_sum(bmp, bmp_unit_w * i, bmp_unit_w * (i + 1), bmp_unit_h * j,
                                                        bmp_unit_h * (j + 1)) / (bmp_unit_w * bmp_unit_h)
        if self.rotation:
            self._merge_rotation()
        if norm_gray:
            self._normalize_gray()

        for j in range(self.size_dna):
            for i in range(self.size_dna):
                self.bmp_dna[j][i] = round(round((float(self.bmp_dna[j][i] / 255)) * (self.gray_depth - 1)) * 255 /
                                           (self.gray_depth - 1))
        self.bmp_dna = self.bmp_dna.astype(np.uint8)

    def _need_exclude_norm(self, i, j):
        if not self.rotation:
            return False
        size_half = int(self.size_dna / 2)
        is_odd_size = True if self.size_dna % 2 else False
        if j > size_half:
            return True
        if j == size_half:
            return False if is_odd_size and i == size_half else True
        if i < j:
            return True
        if i >= self.size_dna - 1 - j:
            return True
        return False

    def _normalize_gray(self):
        v_min = self.bmp_dna[0][0]
        v_max = self.bmp_dna[0][0]
        for j in range(self.size_dna):
            for i in range(self.size_dna):
                if self._need_exclude_norm(i, j):
                    continue
                if self.bmp_dna[j][i] < v_min:
                    v_min = self.bmp_dna[j][i]
                if self.bmp_dna[j][i] > v_max:
                    v_max = self.bmp_dna[j][i]
        if v_min == v_max:
            for j in range(self.size_dna):
                for i in range(self.size_dna):
                    self.bmp_dna[j][i] = 0
            return
        for j in range(self.size_dna):
            for i in range(self.size_dna):
                if self._need_exclude_norm(i, j):
                    continue
                self.bmp_dna[j][i] = (self.bmp_dna[j][i] - v_min) * 255 / (v_max - v_min)

    def _merge_rotation(self):
        c = 1
        for j in range(int(self.size_dna / 2)):
            for i in range(j, self.size_dna - c):
                self.bmp_dna[j][i] += self.bmp_dna[self.size_dna - 1 - i][j]                        # 90 degree
                self.bmp_dna[j][i] += self.bmp_dna[self.size_dna - 1 - j][self.size_dna - 1 - i]    # 180
                self.bmp_dna[j][i] += self.bmp_dna[i][self.size_dna - 1 - j]                        # -90
                self.bmp_dna[j][i] /= 4
            c += 1

    def load_dna_bitmap(self, path):
        img = Image.open(path)
        self.bmp_dna = np.array(img)
        self.size_dna = self.bmp_dna.shape[0]

    @staticmethod
    def _mark_pixel_shown(im, i, j):
        pixel = im.getpixel((i, j))
        pixel = (pixel[0], 255)
        im.putpixel((i, j), pixel)

    def _set_alpha_rotation(self, im):
        im.convert("LA")
        im.putalpha(0)
        size_half = int(self.size_dna / 2)
        c = 1
        for j in range(size_half):
            for i in range(j, self.size_dna - c):
                self._mark_pixel_shown(im, i, j)
            c += 1
        if self.size_dna % 2 == 1:
            self._mark_pixel_shown(im, size_half, size_half)

    def save_dna_bitmap(self, path):
        im = Image.fromarray(self.bmp_dna, "L")
        if self.rotation:
            self._set_alpha_rotation(im)
        im.save(path)

    def _write_rotated_text(self, f, is_hex=False):
        size_half = int(self.size_dna / 2)
        c = 1
        for j in range(size_half):
            for i in range(j, self.size_dna - c):
                f.write(("%02x " if is_hex else "%d ") % self.bmp_dna[j][i])
            c += 1
            f.write('\n')
        if self.size_dna % 2 == 1:
            f.write(("%02x\n" if is_hex else "%d\n") % self.bmp_dna[size_half][size_half])

    def save_dna_text(self, path, is_hex=False):
        f = open(path, 'w')
        if self.rotation:
            self._write_rotated_text(f, is_hex)
        else:
            if hex:
                np.savetxt(f, self.bmp_dna, '%02x')
            else:
                np.savetxt(f, self.bmp_dna, '%3d')
        f.close()

    def show_dna_text(self):
        size_half = int(self.size_dna / 2)
        c = 1
        for j in range(size_half):
            for i in range(j, self.size_dna - c):
                print("%d " % int(self.bmp_dna[j][i]), end='')
            c += 1
            print()
        if self.size_dna % 2 == 1:
            print("%d\n" % int(self.bmp_dna[size_half][size_half]), end='')


    def get_dna(self):
        return self.bmp_dna.reshape(-1)
