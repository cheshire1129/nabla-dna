from PIL import Image
import numpy as np

import abmp


class NablaBitmap(abmp.AveragedBitmap):
    def __init__(self, size_dna=0, gray_depth=256, rotation=False):
        super().__init__(size_dna, gray_depth)
        self.rotation = rotation

    def build_dna_bitmap(self, path, norm_gray=False):
        self.build_averaged_bitmap(path)

        if self.rotation:
            self._merge_rotation()
        else:
            self._vectorize()
        if norm_gray:
            self._normalize_gray()

        for i in range(len(self.bmp_dna)):
            self.bmp_dna[i] = round(self.bmp_dna[i] / 255 * (self.gray_depth - 1))

    def _normalize_gray(self):
        v_max = v_min = self.bmp_dna[0]
        for i in range(len(self.bmp_dna)):
            if self.bmp_dna[i] < v_min:
                v_min = self.bmp_dna[i]
            if self.bmp_dna[i] > v_max:
                v_max = self.bmp_dna[i]
        if v_min == v_max:
            for i in range(len(self.bmp_dna)):
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

    def _vectorize(self):
        bmp_vec = []
        for h in range(self.size_dna):
            for w in range(self.size_dna):
                bmp_vec.append(self.bmp_dna[h][w])
        self.bmp_dna = bmp_vec

    def _save_nabla_bitmap(self, im):
        im.putalpha(0)
        i = 0
        for h in range(int((self.size_dna + 1) / 2)):
            for w in range(h, self.size_dna - h):
                if (w >= self.size_dna - h - 1 and
                        (w != h or w != (self.size_dna + 1) / 2 - 1 or self.size_dna % 1 != 0)):
                    break
                im.putpixel((w, h), (int(self.bmp_dna[i] * 256 / self.gray_depth), 255))
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
            if is_hex:
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
