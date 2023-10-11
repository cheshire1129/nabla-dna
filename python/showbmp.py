#!/usr/bin/python3

import sys
import getopt
from enum import Enum
import logger
from nbmp import NablaBitmap

DNA_RESOLUTION_DEFAULT = 4


class Mode(Enum):
    ModeBitmap = 0
    ModeAverage = 1
    ModeNabla = 2


path_input: str = ""
dna_resolution: int = DNA_RESOLUTION_DEFAULT
mode: Mode = Mode.ModeBitmap

def _usage_showbmp():
    print("""\
Usage: showbmp.py <image path>
   <options>
   -h: help(this message)
   -x <resolution>: DNA resolution (default: 4)
   -a: show averaged bitmap
   -n: show nabla bitmap
""")

def _show_bitmap_matrix(bmp: NablaBitmap):
    for h in range(bmp.height):
        for w in range(bmp.width):
            print("%.2f " % float(bmp.bmp_dna[h][w]), end='')
        print()

def _show_bitmap_vector(bmp: NablaBitmap):
    for f in bmp.bmp_dna:
        print("%.2f " % f, end='')
    print()

def _showbmp():
    global path_input, dna_resolution, mode

    bmp = NablaBitmap(dna_resolution)
    bmp.load_grayscale_bmp(path_input)
    if mode == Mode.ModeBitmap:
        _show_bitmap_matrix(bmp)
        return
    bmp.convert_averaged_bmp()
    if mode == Mode.ModeAverage:
        _show_bitmap_matrix(bmp)
        return
    bmp.do_nabla_sum()
    _show_bitmap_vector(bmp)


def _parse_args():
    global path_input, dna_resolution, mode

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hx:an")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_showbmp()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_showbmp()
            exit(0)
        elif o == '-s':
            dna_resolution = int(a)
        elif o == '-a':
            mode = Mode.ModeAverage
        elif o == '-n':
            mode = Mode.ModeNabla

    if len(args) < 1:
        logger.error("input image required")
        _usage_showbmp()
        exit(1)
    path_input = args[0]


if __name__ == "__main__":
    logger.init("showbmp")

    _parse_args()
    _showbmp()
