#!/usr/bin/python3

import sys
import getopt
import logger
from bmp import Bitmap
from pis import PIS
import dist

DNA_SIZE_DEFAULT = 4

path_inputs = []
dist_type = 'similarity'
is_pis = False


def _usage_getdist():
    print("""\
Usage: getdist.py [<options>] <image path> <image path>
   <options>
   -h: help(this message)
   -t <type>: distance type
      similarity(default): cosine similarity
      c-similarity(default): center weighted cosine similarity
      cosine: cosine distance
      euclidean: euclidean distance
""")



def _getdist(path):
    global path_inputs, is_pis

    if is_pis:
        pis1 = PIS()
        pis2 = PIS()
        pis1.open(path_inputs[0])
        pis2.open(path_inputs[1])
        dna1 = pis1.get_dna()
        dna2 = pis2.get_dna()
    else:
        bmp1 = Bitmap()
        bmp2 = Bitmap()
        bmp1.load_dna_bitmap(path_inputs[0])
        bmp2.load_dna_bitmap(path_inputs[1])
        dna1 = bmp1.get_dna()
        dna2 = bmp2.get_dna()
    print(dist.get(dist_type, dna1, dna2))


def _parse_args():
    global  path_inputs, dist_type, is_pis

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
    if PIS.is_pis_ext(args[0]) and PIS.is_pis_ext(args[1]):
        is_pis = True
    elif PIS.is_pis_ext(args[0]) or PIS.is_pis_ext(args[1]):
        logger.error("Both files should be PIS or not")
        exit(2)
    path_inputs.append(args[0])
    path_inputs.append(args[1])


if __name__ == "__main__":
    logger.init("getdist")

    _parse_args()
    _getdist(path_inputs)
