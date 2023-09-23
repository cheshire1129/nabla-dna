#!/usr/bin/python3

import sys
import os
import getopt
import logger
from bmp import Bitmap

DNA_SIZE_DEFAULT = 4

path_input: str = ""
path_output: str = ""
dna_size = DNA_SIZE_DEFAULT
gray_depth = 256
norm_gray = False
rotation = False


def _usage_mkdna():
    print("""\
Usage: mkdna.py [<options>] <image path>
   <options>
   -h: help(this message)
   -s <size>: dna size (default: 4)
   -g <depth>: gray depth(default: 256)
   -n: normalize gray(default: false)
   -r: get rotational dna
   -o <output>: save dna as an image or text
""")


def _mkdna(path):
    global path_output, dna_size, gray_depth, rotation, norm_gray

    bmp = Bitmap(dna_size, gray_depth, rotation)
    bmp.build_dna_bitmap(path, norm_gray)
    if path_output:
        res = os.path.splitext(path_output)
        if res[1] == '.pis':
            bmp.save_dna_text(path_output)
        elif res[1] == '.pix':
            bmp.save_dna_text(path_output, True)
        else:
            bmp.save_dna_bitmap(path_output)


def _parse_args():
    global path_input, path_output, dna_size, gray_depth, norm_gray, rotation

    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:s:g:nrh")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_mkdna()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_mkdna()
            exit(0)
        elif o == '-o':
            path_output = a
        elif o == '-s':
            dna_size = int(a)
        elif o == '-g':
            gray_depth = int(a)
        elif o == '-n':
            norm_gray = True
        elif o == '-r':
            rotation = True

    if len(args) < 1:
        logger.error("input image required")
        _usage_mkdna()
        exit(1)
    path_input = args[0]


if __name__ == "__main__":
    logger.init("mkdna")

    _parse_args()
    _mkdna(path_input)
