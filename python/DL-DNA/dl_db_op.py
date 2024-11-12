import os
import numpy as np

import vdb
from lineEnumerator import LineEnumerator

_vdb: vdb.Vdb = vdb.Vdb()

def load_vdb(path):
    _vdb.load(path)

def create_vdb(path):
    _vdb.create(path)

def _add_dna_from_file(model, path):
    list_dna = []
    lines = LineEnumerator(path)
    for img_name in lines:
        list_dna.append(model.get_dna(img_name))
    _vdb.insert_multi(list_dna)

def add_dna(model, path_or_name):
    if os.path.isfile(path_or_name):
        _add_dna_from_file(model, path_or_name)
    else:
        _vdb.insert(model.get_dna(path_or_name))
    _vdb.save()

def _search_dna_from_file(model, path):
    list_dna = []
    lines = LineEnumerator(path)
    for img_name in lines:
        list_dna.append(model.get_dna(img_name))
    _vdb.search_multi(np.array(list_dna))

def search_dna(model, path_or_name):
    if os.path.isfile(path_or_name):
        _search_dna_from_file(model, path_or_name)
    else:
        _vdb.search(model.get_dna(path_or_name))