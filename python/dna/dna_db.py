import time
import os
import numpy as np

from dna import dna_model
from lib import vdb
from lib.lineEnumerator import LineEnumerator


class DnaDb:
    def __init__(self, _vdb: vdb.Vdb = None):
        self.threshold = None
        if _vdb is None:
            _vdb = vdb.Vdb()
        self.vdb = _vdb

    def load(self, path: str):
        self.vdb.load(path)

    def create(self, path: str):
        self.vdb.create(path)

    def _add_dna_from_file(self, model: dna_model.DnaModel, path: str):
        list_dna = []
        lines = LineEnumerator(path)
        start = time.perf_counter()
        for img_name in lines:
            list_dna.append(model.get_dna(img_name))
        elapsed = time.perf_counter() - start
        print(f"dna extraction time: {elapsed:.6f} sec")

        start = time.perf_counter()
        self.vdb.insert_multi(list_dna)
        elapsed = time.perf_counter() - start
        print(f"vdb insert time: {elapsed:.6f} sec")

    def add(self, model: dna_model.DnaModel, path_or_name):
        if os.path.isfile(path_or_name):
            self._add_dna_from_file(model, path_or_name)
        else:
            self.vdb.insert(model.get_dna(path_or_name))
        self.vdb.save()

    def _search_dna_from_file(self, model: dna_model.DnaModel, path: str):
        list_dna = []
        lines = LineEnumerator(path)
        start = time.perf_counter()
        for img_name in lines:
            list_dna.append(model.get_dna(img_name))
        elapsed = time.perf_counter() - start
        print(f"dna extraction time: {elapsed:.6f} sec")

        start = time.perf_counter()
        dists, ids = self.vdb.search_multi(list_dna)
        elapsed = time.perf_counter() - start
        print(f"vdb search time: {elapsed:.6f} sec")
        if self.threshold:
            indices = np.where(dists <= self.threshold)
            ratio = len(indices[0]) / len(list_dna) * 100
            print(f"matched ratio: {ratio:.2f}")
            print("matched id:")
            no = 0
            for idr in ids[indices[0]]:
                matched = indices[0][no]
                print(f"{matched}: {idr[0]}")
                no += 1
        else:
            print(dists, ids)

    def search(self, model: dna_model.DnaModel, path_or_name):
        if os.path.isfile(path_or_name):
            self._search_dna_from_file(model, path_or_name)
        else:
            self.vdb.search(model.get_dna(path_or_name))
