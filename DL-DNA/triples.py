import logger


class Triples:
    def __init__(self, fpath: str):
        self.triples = []
        self._current = 0
        self.open(fpath)

    def open(self, fpath: str):
        try:
            f = open(fpath, 'r')
        except FileNotFoundError:
            logger.error("cannot open triples file")
            exit(1)

        for line in f:
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            pairs = line.split()
            if len(pairs) == 0:
                continue
            if len(pairs) != 3:
                logger.error("weird format")
                exit(1)
            self.triples.append(pairs)
        f.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self._current < len(self.triples):
            triple = self.triples[self._current]
            self._current += 1
            return triple
        else:
            raise StopIteration
