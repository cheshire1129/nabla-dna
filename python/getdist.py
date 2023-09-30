#!/usr/bin/python3

import sys
import os
import getopt
import logger
from bmp import Bitmap
from pis import PIS
import dist

DNA_SIZE_DEFAULT = 4

path_in: str = ''
path_comp: str = ''
dist_type: str = 'similarity'
is_pis: bool = False


def _usage_getdist():
    print("""\
Usage: getdist.py [<options>] <image path> <image path or dir>
   <options>
   -h: help(this message)
   -t <type>: distance type
      similarity(default): cosine similarity
      c-similarity(default): center weighted cosine similarity
      cosine: cosine distance
      euclidean: euclidean distance
""")


def _getdist(path_compared) -> float:
    global path_in, is_pis

    if is_pis:
        pis1 = PIS()
        pis2 = PIS()
        pis1.open(path_in)
        pis2.open(path_compared)
        dna1 = pis1.get_dna()
        dna2 = pis2.get_dna()
    else:
        bmp1 = Bitmap()
        bmp2 = Bitmap()
        bmp1.load_dna_bitmap(path_in)
        bmp2.load_dna_bitmap(path_compared)
        dna1 = bmp1.get_dna()
        dna2 = bmp2.get_dna()
    return dist.get(dist_type, dna1, dna2)


def _getdist_one(path_compared: str):
    print(_getdist(path_compared))


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
        print(item, _getdist(path_compared))


def _parse_args():
    global path_in, path_comp, dist_type, is_pis

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_getdist()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_getdist()
            exit(0)
        elif o == '-t':
            dist_type = a

    if len(args) < 2:
        logger.error("input images required")
        _usage_getdist()
        exit(1)
    if PIS.is_pis_ext(args[0]) and (os.path.isdir(args[1]) or PIS.is_pis_ext(args[1])):
        is_pis = True
    elif ((PIS.is_pis_ext(args[0]) and os.path.isfile(args[1])) or
          (os.path.isfile(args[1]) and PIS.is_pis_ext(args[1]))):
        logger.error("Both files should be PIS or not")
        exit(2)
    path_in = args[0]
    path_comp = args[1]


if __name__ == "__main__":
    logger.init("getdist")

    _parse_args()
    if os.path.isfile(path_comp):
        _getdist_one(path_comp)
    else:
        _getdist_folder(path_comp)
