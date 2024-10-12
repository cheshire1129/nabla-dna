import logger


class LineEnumerator:
    def __init__(self, fpath: str, need_split=False):
        self.lines = []
        self._current = 0
        self.open(fpath)
        self.need_split = need_split

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
            self.lines.append(line.strip())
        f.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self._current < len(self.lines):
            line = self.lines[self._current]
            self._current += 1
            if self.need_split:
                return line.split()
            return line
        else:
            raise StopIteration
