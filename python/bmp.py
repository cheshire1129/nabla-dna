from PIL import Image
import numpy as np
import math


class Bitmap:
    def __init__(self, size_dna=0, gray_depth=256, rotation=False):
        self.size_dna = size_dna
        self.gray_depth = gray_depth
        self.rotation = rotation
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

    def build_dna_bitmap(self, path, norm_gray=False):
        self._load_grayscale_bmp(path)
        bmp_unit_w = self.width / (self.size_dna + 1)
        bmp_unit_h = self.height / (self.size_dna + 1)

        self._convert_averaged_bmp()

        if self.rotation:
            self._merge_rotation()
        if norm_gray:
            self._normalize_gray()

        for i in range(len(self.bmp_dna)):
            self.bmp_dna[i] = int(round(round((float(self.bmp_dna[i] / 255)) * (self.gray_depth - 1)) * 255 /
                                        (self.gray_depth - 1)))

    def _normalize_gray(self):
        v_max = v_min = self.bmp_dna[0]
        for i in range(self.size_dna):
            if self.bmp_dna[i] < v_min:
                v_min = self.bmp_dna[i]
            if self.bmp_dna[i] > v_max:
                v_max = self.bmp_dna[i]
        if v_min == v_max:
            self.bmp_dna[i] = 0
            return
        for i in range(len(self.bmp_dna)):
            self.bmp_dna[i] = (self.bmp_dna[i] - v_min) * 255 / (v_max - v_min)

    def _merge_rotation(self):
        bmp_rot = []
        for h in range(int((self.size_dna + 1) / 2)):
            for w in range(h, self.size_dna - h):
                if (w >= self.size_dna - h - 1 and
                        (w != h or w != (self.size_dna + 1) / 2 - 1 or self.size_dna % 1 != 0)):
                    break
                self.bmp_dna[h][w] += self.bmp_dna[self.size_dna - 1 - w][h]                        # 90 degree
                self.bmp_dna[h][w] += self.bmp_dna[self.size_dna - 1 - h][self.size_dna - 1 - w]    # 180
                self.bmp_dna[h][w] += self.bmp_dna[w][self.size_dna - 1 - h]                        # -90
                self.bmp_dna[h][w] /= 4
                bmp_rot.append(self.bmp_dna[h][w])
        self.bmp_dna = bmp_rot

    def load_dna_bitmap(self, path):
        img = Image.open(path)
        self.bmp_dna = np.array(img)
        self.size_dna = self.bmp_dna.shape[0]

    def _save_nabla_bitmap(self, im):
        im.putalpha(0)
        i = 0
        for h in range(int((self.size_dna + 1) / 2)):
            for w in range(h, self.size_dna - h):
                if (w >= self.size_dna - h - 1 and
                        (w != h or w != (self.size_dna + 1) / 2 - 1 or self.size_dna % 1 != 0)):
                    break
                im.putpixel((w, h), (self.bmp_dna[i], 255))
                i += 1

    def save_dna_bitmap(self, path):
        im = Image.new("LA", (self.size_dna, self.size_dna), 255)
        if self.rotation:
            self._save_nabla_bitmap(im)
        im.save(path)

    def _write_rotated_text(self, f, is_hex=False):
        for i in range(len(self.bmp_dna)):
            f.write(("%02x " if is_hex else "%d ") % self.bmp_dna[i])
        f.write('\n')

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

    def show_bitmap(self, path, averaged: bool):
        self._load_grayscale_bmp(path)
        if averaged:
            self._convert_averaged_bmp()
            height = width = self.size_dna
        else:
            width = self.width
            height = self.height

        for h in range(height):
            for w in range(width):
                print("%.2f " % float(self.bmp_dna[h][w]), end='')
            print()

    def show_bitmap_rotated(self, path):
        self._load_grayscale_bmp(path)
        self._convert_averaged_bmp()
        self._merge_rotation()
        for f in self.bmp_dna:
            print("%.2f " % f, end='')
        print()

    def show_dna_text(self):
        for i in range(len(self.bmp_dna)):
            print("%d " % int(self.bmp_dna[i]), end='')
        print()

    def get_dna(self):
        return self.bmp_dna.reshape(-1)
