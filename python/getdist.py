#!/usr/bin/python3

import sys
import os
import getopt
import logger
from bmp import Bitmap
from pis import PIS
import dist

path_in: str = ''
path_comp: str = ''
dist_type: str = 'similarity'
depth: int = 256
is_pis: bool = False
min_similarity: float = -100


def _usage_getdist():
    print("""\
Usage: getdist.py [<options>] <image path> <image path or dir> or
                              <image path>: get similarity of all pairs
   <options>
   -h: help(this message)
   -s <minimum similarity value>: only shows pairs with larger value
   -d <depth>: bitmap depth bit(default and max: 8)
   -t <type>: distance type
      similarity(default): cosine similarity
      c-similarity(default): center weighted cosine similarity
      cosine: cosine distance
      euclidean: euclidean distance
""")


def _getdist(path_cur, path_compared) -> float:
    global is_pis, depth

    if is_pis:
        pis1 = PIS()
        pis2 = PIS()
        pis1.open(path_cur)
        pis2.open(path_compared)
        dna1 = pis1.get_dna()
        dna2 = pis2.get_dna()
    else:
        bmp1 = Bitmap()
        bmp2 = Bitmap()
        bmp1.load_dna_bitmap(path_cur)
        bmp2.load_dna_bitmap(path_compared)
        dna1 = bmp1.get_dna()
        dna2 = bmp2.get_dna()
    return dist.get(dist_type, dna1, dna2, depth)


def _getdist_one(path_compared: str):
    global path_in, min_similarity

    print(_getdist(path_in, path_compared))


def _getdist_folder(path_comp_dir):
    global path_in

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
        if not os.path.isfile(path_cur) or os.path.splitext(item)[1] != '.pis':
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
    global path_in, path_comp, dist_type, depth, is_pis, min_similarity

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
            depth = 2 ** int(a)
        elif o == '-t':
            dist_type = a
        elif o == '-s':
            min_similarity = float(a)

    if len(args) < 1 or (not os.path.isdir(args[0]) and len(args) < 2):
        logger.error("input images required")
        _usage_getdist()
        exit(1)
    if len(args) == 1:
        is_pis = True
    else:
        if PIS.is_pis_ext(args[0]) and (os.path.isdir(args[1]) or PIS.is_pis_ext(args[1])):
            is_pis = True
        elif ((PIS.is_pis_ext(args[0]) and os.path.isfile(args[1])) or
              (os.path.isfile(args[1]) and PIS.is_pis_ext(args[1]))):
            logger.error("Both files should be PIS or not")
            exit(2)
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
