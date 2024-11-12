import faiss
import numpy as np


class Vdb:
    def __init__(self):
        self.path = None
        self.index = None

    def load(self, path):
        self.path = path
        self.index = faiss.read_index(path)
        print("Read")

    def create(self, path):
        self.path = path

    def insert(self, dna):
        if self.index is None:
            self.index = faiss.IndexFlatL2(len(dna))
        self.index.add(np.array([dna]))

    def insert_multi(self, list_dna):
        if self.index is None:
            self.index = faiss.IndexFlatL2(len(list_dna[0]))
        self.index.add(np.array(list_dna))

    def search(self, dna):
        dist, searched = self.index.search(dna[None, :], 1)
        print(dist, searched)

    def search_multi(self, list_dna):
        dist, searched = self.index.search(list_dna, 1)
        print(dist, searched)

    def save(self):
        if self.index and self.path:
            faiss.write_index(self.index, self.path)