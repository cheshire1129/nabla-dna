import faiss
import numpy as np


class Vdb:
    def __init__(self):
        self.path = None
        self.index = None

    def load(self, path):
        self.path = path
        self.index = faiss.read_index(path)

    def create(self, path: str):
        self.path = path

    def _create_index(self, vec_size):
        self.index = faiss.IndexFlatL2(vec_size)

    def insert(self, dna):
        if self.index is None:
            self._create_index(len(dna))
        self.index.add(dna[None, :])

    def insert_multi(self, list_dna):
        if self.index is None:
            self._create_index(len(list_dna[0]))
        self.index.add(np.array(list_dna))

    def search(self, dna):
        dist, searched = self.index.search(dna[None, :], 1)
        return dist, searched

    def search_multi(self, list_dna):
        dist, searched = self.index.search(np.array(list_dna), 1)
        return dist, searched

    def save(self):
        if self.index and self.path:
            faiss.write_index(self.index, self.path)
