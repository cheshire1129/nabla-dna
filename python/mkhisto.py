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
Usage: mkhisto.py [<options>] <image or PIS path/folder>
   <options>
   -h: help(this message)
   -x <resolution>: DNA resolution (default: 4)
   -d <depth>: DNA depth bit(default and max: 8)
   -N: skip normalization
   -s: do nabla sum
   -o <output>: save histogram as text
""")

def _make_histogram(grays, path_out):
    h = histo.Histo(grays)
    if path_output:
        h.save(path_out)
    else:
        h.show()

def _make_histogram_by_bmp(path: str, path_out):
    global dna_resolution, dna_depth, do_nabla_sum, skip_normalization

    bmp = NablaBitmap(dna_resolution, dna_depth, not do_nabla_sum)
    bmp.build_dna_bitmap(path, skip_normalization)
    _make_histogram(bmp.bmp_dna, path_out)

def _mkhisto(path, path_out):
    global dna_resolution, dna_depth, do_nabla_sum, skip_normalization

    if pis.PIS.is_allowed_ext(path):
        p = pis.PIS(path)
        _make_histogram(p.dna, path_out)
    else:
        _make_histogram_by_bmp(path, path_out)


def _mkhisto_folder(path):
    global path_output

    out_ext = os.path.splitext(os.path.basename(path_output))[1]
    out_dir = os.path.dirname(path_output)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    dir_list = os.listdir(path)
    for item in dir_list:
        if not os.path.isfile(os.path.join(path, item)):
            continue
        name, ext = os.path.splitext(item)
        path_out = os.path.join(out_dir, name + out_ext)
        _mkhisto(os.path.join(path, item), path_out)


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
    if os.path.isfile(path_input):
        _mkhisto(path_input, path_output)
    else:
        if not path_output:
            logger.error("output path required")
            exit(1)
        _mkhisto_folder(path_input)
