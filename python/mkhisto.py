#!/usr/bin/python3

import sys
import os
import getopt
import logger
from nbmp import NablaBitmap
import pis
import histo

DNA_RESOLUTION_DEFAULT = 4
DNA_DEPTH_DEFAULT = 8

path_input: str = ""
path_output: str = ""
dna_resolution = DNA_RESOLUTION_DEFAULT
dna_depth: int = 8
skip_normalization = False
do_nabla_sum = False


def _usage_mkhisto():
    print("""\
Usage: mkhisto.py [<options>] <image or PIS path>
   <options>
   -h: help(this message)
   -x <resolution>: DNA resolution (default: 4)
   -d <depth>: DNA depth bit(default and max: 8)
   -N: skip normalization
   -s: do nabla sum
   -o <output>: save histogram as text
""")

def _make_histogram(grays):
    global path_output

    h = histo.Histo(grays)
    if path_output:
        h.save(path_output)
    else:
        h.show()

def _make_histogram_by_bmp(path: str):
    global dna_resolution, dna_depth, do_nabla_sum, skip_normalization

    bmp = NablaBitmap(dna_resolution, dna_depth, not do_nabla_sum)
    bmp.build_dna_bitmap(path, skip_normalization)
    _make_histogram(bmp.bmp_dna)

def _mkhisto(path, path_out):
    global dna_resolution, dna_depth, do_nabla_sum, skip_normalization

    if pis.PIS.is_pis_ext(path):
        p = pis.PIS(path)
        _make_histogram(p.dna)
    else:
        _make_histogram_by_bmp(path)


def _parse_args():
    global path_input, path_output, dna_resolution, dna_depth, do_nabla_sum, skip_normalization

    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:x:d:Nsh")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_mkhisto()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_mkhisto()
            exit(0)
        elif o == '-o':
            path_output = a
        elif o == '-x':
            dna_resolution = int(a)
        elif o == '-d':
            dna_depth = int(a)
            if dna_depth < 1 or dna_depth > 8:
                logger.error("DNA depth should be between 1 and 8")
                exit(1)
        elif o == '-N':
            skip_normalization = True
        elif o == '-s':
            do_nabla_sum = True

    if len(args) < 1:
        logger.error("input image or PIS required")
        _usage_mkhisto()
        exit(1)
    path_input = args[0]


if __name__ == "__main__":
    logger.init("mkhisto")

    _parse_args()
    _mkhisto(path_input, path_output)
