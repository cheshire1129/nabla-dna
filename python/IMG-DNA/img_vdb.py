import faiss
import numpy as np
import json

from lib import vdb


class ImgVdb(vdb.Vdb):
    def __init__(self):
        super().__init__()
        self.vec_infos = []

    def load(self, path):
        self.path = path
        self.index = faiss.read_index(path + ".index")
        with open(path + ".infos", 'r') as f:
            self.vec_infos = json.load(f)

    def _get_dna_id(self):
        return self.vec_infos[-1] + 1 if self.vec_infos else 0

    def insert(self, dna):
        if self.index is None:
            self._create_index(len(dna[0]))
        vec_id = self._get_dna_id()
        for feat in dna:
            self.vec_infos.append(vec_id)
        self.index.add(dna)

    def insert_multi(self, list_dna):
        for dna in list_dna:
            self.insert(dna)

    def search(self, dna):
        dna_refs = {}
        _, searched = self.index.search(dna, 1)
        for s in searched:
            dna_id = self.vec_infos[s[0]]
            if dna_id in dna_refs:
                dna_refs[dna_id] += 1
            else:
                dna_refs[dna_id] = 1
        max_dna_id = max(dna_refs, key=dna_refs.get)
        ratio = 1 - dna_refs[max_dna_id] / len(searched)
        return [ratio], [max_dna_id]

    def search_multi(self, list_dna):
        res = []
        for dna in list_dna:
            res.append(self.search(dna))
        ratios, ids = zip(*res)
        return np.array(list(ratios)), np.array(list(ids))

    def save(self):
        if self.index and self.path:
            faiss.write_index(self.index, self.path + ".index")
            with open(self.path + ".infos", 'w') as f:
                json.dump(self.vec_infos, f)
