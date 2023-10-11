import sys
import typing


class Histo:
    def __init__(self, grays: typing.List[int]):
        self.max_gray = 0
        self._counts = {}
        self._build(grays)

    def _build(self, grays: typing.List[int]):
        for gray in grays:
            if gray > self.max_gray:
                self.max_gray = gray
            if gray in self._counts:
                self._counts[gray] += 1
            else:
                self._counts[gray] = 1

    def get(self):
        counts = []
        for i in range(self.max_gray + 1):
            if i in self._counts:
                counts.append(self._counts[i])
            else:
                counts.append(0)
        return counts

    def _write_histo(self, f):
        for i in range(self.max_gray + 1):
            if i in self._counts:
                count = self._counts[i]
            else:
                count = 0
            if i != 0:
                f.write(' ')
            f.write(f"{count}")
        f.write('\n')

    def save(self, path):
        f = open(path, 'w')
        self._write_histo(f)
        f.close()

    def show(self):
        self._write_histo(sys.stdout)