import logger


class LineEnumerator:
    def __init__(self, fpath: str):
        self.singles = []
        self._current = 0
        self.open(fpath)

    def open(self, fpath: str):
        try:
            f = open(fpath, 'r')
        except FileNotFoundError:
            logger.error("cannot open singles file")
            exit(1)

        for line in f:
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            self.singles.append(line.strip())
        f.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self._current < len(self.singles):
            single = self.singles[self._current]
            self._current += 1
            return single
        else:
            raise StopIteration
