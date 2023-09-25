#!/usr/bin/python3

import sys
import getopt
from enum import Enum
import logger
from bmp import Bitmap

DNA_SIZE_DEFAULT = 4


class Mode(Enum):
    ModeBitmap = 0
    ModeAverage = 1
    ModeRotated = 2


path_input: str = ""
dna_size: int = DNA_SIZE_DEFAULT
mode: Mode = Mode.ModeBitmap

def _usage_showbmp():
    print("""\
Usage: showbmp.py <image path>
   <options>
   -h: help(this message)
   -s <dna size>: dna size (default: 4)
   -a: show averaged bitmap
   -r: show rotated bitmap
""")


def _showbmp():
    global path_input, dna_size, mode

    bmp = Bitmap(dna_size)
    if (mode == Mode.ModeRotated):
        bmp.show_bitmap_rotated(path_input)
    else:
        bmp.show_bitmap(path_input, mode == Mode.ModeAverage)


def _parse_args():
    global path_input, dna_size, mode

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:ar")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_showbmp()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_showbmp()
            exit(0)
        elif o == '-s':
            dna_size = int(a)
        elif o == '-a':
            mode = Mode.ModeAverage
        elif o == '-r':
            mode = Mode.ModeRotated

    if len(args) < 1:
        logger.error("input image required")
        _usage_showbmp()
        exit(1)
    path_input = args[0]


if __name__ == "__main__":
    logger.init("showbmp")

    _parse_args()
    _showbmp()
