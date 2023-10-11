#!/usr/bin/python3

import sys
import os
import getopt
import logger
from nbmp import NablaBitmap

DNA_RESOLUTION_DEFAULT = 4
DNA_DEPTH_DEFAULT = 8

path_input: str = ""
path_output: str = ""
dna_resolution = DNA_RESOLUTION_DEFAULT
dna_depth: int = 8
skip_normalization = False
skip_nabla_sum = False


def _usage_mkdna():
    print("""\
Usage: mkdna.py [<options>] <image path or folder>
   <options>
   -h: help(this message)
   -x <resolution>: DNA resolution (default: 4)
   -d <depth>: DNA depth bit(default and max: 8)
   -N: skip normalization
   -S: skip nabla sum
   -o <output>: save dna as an image or text
""")


def _mkdna(path, path_out):
    global dna_resolution, dna_depth, skip_nabla_sum, skip_normalization

    bmp = NablaBitmap(dna_resolution, dna_depth, skip_nabla_sum)
    bmp.build_dna_bitmap(path, skip_normalization)
    if path_out:
        res = os.path.splitext(path_out)
        if res[1] == '.pis':
            bmp.save_dna_text(path_out)
        elif res[1] == '.pix':
            bmp.save_dna_text(path_out, True)
        else:
            bmp.save_dna_bitmap(path_out)
    else:
        bmp.show_dna_text()


def _mkdna_folder(path):
    global path_output

    out_ext = os.path.splitext(os.path.basename(path_output))[1]
    out_dir = os.path.dirname(path_output)
    dir_list = os.listdir(path)
    for item in dir_list:
        if not os.path.isfile(os.path.join(path, item)):
            continue
        name, ext = os.path.splitext(item)
        path_out = os.path.join(out_dir, name + out_ext)
        _mkdna(os.path.join(path, item), path_out)


def _parse_args():
    global path_input, path_output, dna_resolution, dna_depth, skip_nabla_sum, skip_normalization

    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:x:d:NSh")
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
        elif o == '-x':
            dna_resolution = int(a)
        elif o == '-d':
            dna_depth = int(a)
            if dna_depth < 1 or dna_depth > 8:
                logger.error("DNA depth should be between 1 and 8")
                exit(1)
        elif o == '-N':
            skip_normalization = True
        elif o == '-S':
            skip_nabla_sum = True

    if len(args) < 1:
        logger.error("input image required")
        _usage_mkdna()
        exit(1)
    path_input = args[0]


if __name__ == "__main__":
    logger.init("mkdna")

    _parse_args()
    if os.path.isfile(path_input):
        _mkdna(path_input, path_output)
    else:
        _mkdna_folder(path_input)
