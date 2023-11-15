import logger


class Pairs:
    def __init__(self, fpath: str):
        self.pairs = []
        self._current = 0
        self.open(fpath)

    def open(self, fpath: str):
        try:
            f = open(fpath, 'r')
        except FileNotFoundError:
            logger.error("cannot open pairs file")
            exit(1)

        for line in f:
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            pairs = line.split()
            if len(pairs) == 0:
                continue
            if len(pairs) != 2:
                logger.error("weird format")
                exit(1)
            self.pairs.append(pairs)
        f.close()

    def convert_singles(self):
        singles = []
        for pair in self.pairs:
            for i in range(2):
                if pair[i] not in singles:
                    singles.append(pair[i])
        self.pairs = singles

    def __iter__(self):
        return self

    def __next__(self):
        if self._current < len(self.pairs):
            pair = self.pairs[self._current]
            self._current += 1
            return pair
        else:
            raise StopIteration
