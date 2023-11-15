#!/usr/bin/python3

import sys
import os
import getopt
import glob

import logger
from pis import PIS
from hst import HST
import dist
import dist_histo
from pairs import Pairs

path_in: str = ''
path_comp: str = ''
dist_type: str = 'similarity'
dna_depth: int = 0
min_similarity: float = -100
pairs: Pairs = None

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
      similarity_histo: similarity with histogram check
   -P <pairs file>: only show matched pairs
""")


def _getdist_histo(path_cur, path_compared):
    hst1 = HST(path_cur)
    hst2 = HST(path_compared)

    return dist_histo.get(hst1.hst, hst2.hst)


def _getdist(_dist_type, path_cur, path_compared) -> float:
    global dna_depth

    if _dist_type == 'histogram':
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

    return dist.get(_dist_type, dna1, dna2, dna_depth)


def _showdist(_dist_type, item, item_compared, path_cur, path_compared):
    global min_similarity

    similarity = _getdist(dist_type, path_cur, path_compared)
    if similarity >= min_similarity:
        print(f"{similarity:.4f}", f"{item} {item_compared}")


def _getdist_one(path_compared: str):
    global dist_type, path_in

    print(_getdist(dist_type, path_in, path_compared))


def _getdist_folder(path_comp_dir):
    global dist_type, path_in, min_similarity

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
        similarity = _getdist(dist_type, path_in, path_compared)
        if similarity >= min_similarity:
            print(item, similarity)


def _getdist_folder_all():
    global dist_type, path_in

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
            _showdist(dist_type, item, item_compared, path_cur, path_compared)


def _getdist_folder_pairs():
    global pairs
    global dist_type, path_in, min_similarity

    for pair in pairs:
        path_cur = glob.glob(os.path.join(path_in, pair[0]) + '.*')[0]
        path_compared = glob.glob(os.path.join(path_in, pair[1]) + '.*')[0]

        _showdist(dist_type, pair[0], pair[1], path_cur, path_compared)


def _getdist_folder_all_similarity_histo():
    global path_in, min_similarity

    checked_items = []

    path_in_dir = os.path.dirname(path_in)
    for item in sorted(os.listdir(path_in)):
        path_cur = os.path.join(path_in_dir, item)
        if not os.path.isfile(path_cur):
            continue
        if not PIS().is_allowed_ext(path_cur):
            continue

        checked_items.append(item)

        for item_compared in os.listdir(path_in):
            if item_compared in checked_items:
                continue
            path_compared = os.path.join(path_in_dir, item_compared)
            if not PIS().is_allowed_ext(path_compared):
                continue

            similarity = _getdist('similarity', path_cur, path_compared)
            if similarity < min_similarity:
                continue

            path_hst = os.path.join(path_in_dir, PIS.get_basename(path_cur) + ".hst")
            path_hst_compared = os.path.join(path_in_dir, PIS.get_basename(path_compared) + ".hst")
            similarity_hst = _getdist('histogram', path_hst, path_hst_compared)
            if similarity_hst < min_similarity:
                continue

            print(f"{similarity:.4f} {similarity_hst:.4f} {item} {item_compared}")


def _parse_args():
    global path_in, path_comp, dist_type, dna_depth, min_similarity, pairs

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:d:t:P:")
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
        elif o == '-P':
            pairs = Pairs(a)

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
    elif dist_type == 'similarity_histo':
        _getdist_folder_all_similarity_histo()
    else:
        if pairs:
            _getdist_folder_pairs()
        else:
            _getdist_folder_all()
