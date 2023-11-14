#!/usr/bin/python3

import sys
from PIL import Image
import math
import getopt
from enum import Enum
import logger
from nbmp import NablaBitmap

DNA_RESOLUTION_DEFAULT = 4


class Mode(Enum):
    ModeBitmap = 0
    ModeAverage = 1
    ModeRotated = 2
    ModeNabla = 3
    ModeSobel = 4


path_input: str = ""
dna_resolution: int = DNA_RESOLUTION_DEFAULT
mode: Mode = Mode.ModeBitmap
as_raw: bool = False
scaled: int = 1
apply_sobel: bool = False

def _usage_showbmp():
    print("""\
Usage: showbmp.py <image path>
   <options>
   -h: help(this message)
   -x <resolution>: DNA resolution (default: 4)
   -m <mode>: bitmap, averaged, rotated, nabla
   -r: show as raw texts
   -s <scale factor>: image scaling if it is too small
   -c: apply sobel filter(contour)
""")


def _show_bitmap_matrix_as_raw(bmp: NablaBitmap):
    for h in range(bmp.height):
        for w in range(bmp.width):
            print("%.2f " % float(bmp.bmp_dna[h][w]), end='')
        print()


def _show_bitmap_matrix_window(bmp: NablaBitmap):
    global scaled

    im = Image.new('L', (bmp.width * scaled, bmp.height * scaled))
    for h in range(bmp.height):
        for w in range(bmp.width):
            for i in range(scaled):
                for j in range(scaled):
                    im.putpixel((w * scaled + i, h * scaled + j), int(bmp.bmp_dna[h][w]))
    im.show('Bitmap Matrix')


def _show_bitmap_vector_as_raw(bmp: NablaBitmap):
    for f in bmp.bmp_dna:
        print("%.2f " % f, end='')
    print()


def _show_bitmap_vector_window(bmp: NablaBitmap):
    global scaled

    im = Image.new('LA', (bmp.width * scaled, bmp.height * scaled))
    im.putalpha(0)
    c = 0
    for h in range(int((bmp.dna_resolution + 1) / 2)):
        for w in range(h, bmp.dna_resolution - h):
            if (w >= bmp.dna_resolution - h - 1 and
                    (w != h or w != (bmp.dna_resolution + 1) / 2 - 1 or bmp.dna_resolution % 1 != 0)):
                break
            for i in range(scaled):
                for j in range(scaled):
                    im.putpixel((w * scaled + i, h * scaled + j), (int(bmp.bmp_dna[c]), 255))
            c += 1
    im.show('Bitmap Nabla')


def _show_bitmap_matrix(bmp: NablaBitmap):
    global as_raw

    if as_raw:
        _show_bitmap_matrix_as_raw(bmp)
    else:
        _show_bitmap_matrix_window(bmp)


def _show_bitmap_vector(bmp: NablaBitmap):
    global as_raw

    if as_raw:
        _show_bitmap_vector_as_raw(bmp)
    else:
        _show_bitmap_vector_window(bmp)


def _showbmp():
    global path_input, dna_resolution, mode, apply_sobel

    resolution = dna_resolution + 2 if apply_sobel else dna_resolution
    bmp = NablaBitmap(resolution)
    bmp.load_grayscale_bmp(path_input)
    if mode == Mode.ModeBitmap:
        _show_bitmap_matrix(bmp)
        return
    bmp.convert_averaged_bmp()
    if apply_sobel: bmp.do_sobel()

    if mode == Mode.ModeAverage:
        _show_bitmap_matrix(bmp)
        return
    bmp.do_nabla_sum()
    if mode == Mode.ModeNabla:
        bmp.normalize_intensity()

    _show_bitmap_vector(bmp)


def _setup_mode(mode_str: str):
    global mode

    mode_maps = {
        'bitmap': Mode.ModeBitmap,
        'averaged': Mode.ModeAverage,
        'rotated': Mode.ModeRotated,
        'nabla': Mode.ModeNabla
    }

    if mode_str not in mode_maps:
        logger.error(f"{mode_str}: unsupported mode")
        exit(1)
    mode = mode_maps[mode_str]


def _parse_args():
    global path_input, dna_resolution, as_raw, scaled, apply_sobel

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hx:m:rs:c")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_showbmp()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_showbmp()
            exit(0)
        elif o == '-x':
            dna_resolution = int(a)
        elif o == '-m':
            _setup_mode(a)
        elif o == '-r':
            as_raw = True
        elif o == '-s':
            scaled = int(a)
        elif o == '-c':
            apply_sobel = True

    if len(args) < 1:
        logger.error("input image required")
        _usage_showbmp()
        exit(1)
    path_input = args[0]


if __name__ == "__main__":
    logger.init("showbmp")

    _parse_args()
    _showbmp()
