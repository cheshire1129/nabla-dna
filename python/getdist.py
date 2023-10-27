#!/usr/bin/python3

import sys
import os
import getopt
import logger
from pis import PIS
from hst import HST
import dist
import dist_histo

path_in: str = ''
path_comp: str = ''
dist_type: str = 'similarity'
dna_depth: int = 0
min_similarity: float = -100


def _usage_getdist():
    print("""\
Usage: getdist.py [<options>] <image path> <pis path or dir> or
                              <image path>: get similarity of all pis pairs
   <options>
   -h: help(this message)
   -s <minimum similarity value>: only shows pairs with larger value
   -d <DNA depth>: DNA depth. If not given and not guessed, depth 8 will be assumed
   -t <type>: distance type
      similarity(default): cosine similarity
      c-similarity(default): center weighted cosine similarity
      cosine: cosine distance
      euclidean: euclidean distance
      histogram: histogram similarity
""")


def _getdist_histo(path_cur, path_compared):
    hst1 = HST(path_cur)
    hst2 = HST(path_compared)

    return dist_histo.get(hst1.hst, hst2.hst)


def _getdist(path_cur, path_compared) -> float:
    global dna_depth

    if HST().is_allowed_ext(path_cur):
        return _getdist_histo(path_cur, path_compared)

    pis1 = PIS(path_cur)
    pis2 = PIS(path_compared)
    dna1 = pis1.get_dna()
    dna2 = pis2.get_dna()

    if pis1.dna_resolution > 0 and pis2.dna_resolution > 0:
        if pis1.dna_resolution != pis2.dna_resolution:
            raise Exception("DNA resolution mismatch")
    if pis1.dna_depth > 0 and pis2.dna_depth > 0:
        if pis1.dna_depth != pis2.dna_depth:
            raise Exception("DNA depth mismatch")
    if dna_depth == 0:
        dna_depth = pis1.dna_depth
        if dna_depth == 0:
            dna_depth = pis2.dna_depth
    if dna_depth == 0:
        dna_depth = 8

    return dist.get(dist_type, dna1, dna2, dna_depth)


def _getdist_one(path_compared: str):
    global path_in, min_similarity

    print(_getdist(path_in, path_compared))


def _getdist_folder(path_comp_dir):
    global path_in, min_similarity

    path_in_ext = os.path.splitext(os.path.basename(path_in))[1]
    path_compared_dir = os.path.dirname(path_comp_dir)
    dir_list = os.listdir(path_comp_dir)
    for item in dir_list:
        path_compared = os.path.join(path_compared_dir, item)
        if not os.path.isfile(path_compared):
            continue
        name, ext = os.path.splitext(item)
        if ext != path_in_ext:
            continue
        similarity = _getdist(path_in, path_compared)
        if similarity >= min_similarity:
            print(item, similarity)


def _getdist_folder_all():
    global path_in, min_similarity

    checked_items = []

    path_in_dir = os.path.dirname(path_in)
    for item in sorted(os.listdir(path_in)):
        path_cur = os.path.join(path_in_dir, item)
        if not os.path.isfile(path_cur):
            continue

        checked_items.append(item)

        for item_compared in os.listdir(path_in):
            if item_compared in checked_items:
                continue
            path_compared = os.path.join(path_in_dir, item_compared)
            similarity = _getdist(path_cur, path_compared)
            if similarity >= min_similarity:
                print(f"{similarity:.4f}", f"{item} {item_compared}")


def _parse_args():
    global path_in, path_comp, dist_type, dna_depth, min_similarity

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:d:t:")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_getdist()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_getdist()
            exit(0)
        elif o == '-d':
            dna_depth = int(a)
        elif o == '-t':
            dist_type = a
        elif o == '-s':
            min_similarity = float(a)

    if len(args) < 1 or (not os.path.isdir(args[0]) and len(args) < 2):
        logger.error("input images required")
        _usage_getdist()
        exit(1)
    if len(args) > 1:
        path_comp = args[1]
    path_in = args[0]


if __name__ == "__main__":
    logger.init("getdist")

    _parse_args()

    if os.path.isfile(path_comp):
        _getdist_one(path_comp)
    elif os.path.isfile(path_in):
        _getdist_folder(path_comp)
    else:
        _getdist_folder_all()
