import os


class HST:
    def __init__(self, path = None):
        self.hst = []

        if path:
            self.open(path)

    def open(self, path):
        if not self.is_allowed_ext(path):
            return False

        f = open(path, 'r')
        for line in f:
            for x in line.split():
                self.hst.append(int(x))
        f.close()

        return True


    @staticmethod
    def is_allowed_ext(path):
        res = os.path.splitext(path)
        return True if res[1] == '.hst' else False
