#!/usr/bin/python3

import sys
import os
import getopt
import glob

import logger
from nbmp import NablaBitmap
from pairs import Pairs

DNA_RESOLUTION_DEFAULT = 4
DNA_DEPTH_DEFAULT = 8

path_input: str = ""
path_output: str = ""
dna_resolution = DNA_RESOLUTION_DEFAULT
dna_depth: int = 8
skip_normalization = False
skip_nabla_sum = False
sobel_threshold: float = -1
crop_threshold: float = -1
pairs: Pairs = None

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
   -c <threshold>: apply sobel filter(contour) with threshold(drop ratio)
                   if threshold > 1, pixels over threshold - 1 will be 255 gray depth.
   -C <threshold>: crop area outside contour
   -P <pairs file>: only make DNA's for matched pairs
""")


def _mkdna(path, path_out):
    global dna_resolution, dna_depth, skip_nabla_sum, skip_normalization, sobel_threshold, crop_threshold

    resolution = dna_resolution + 2 if sobel_threshold >= 0 else dna_resolution

    bmp = NablaBitmap(resolution, dna_depth, skip_nabla_sum)
    bmp.build_dna_bitmap(path, skip_normalization, sobel_threshold, crop_threshold)
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


def _mkdna_folder_pairs(path):
    global pairs, path_output

    out_ext = os.path.splitext(os.path.basename(path_output))[1]
    out_dir = os.path.dirname(path_output)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    for single in pairs:
        path_in = glob.glob(os.path.join(path, single) + '.*')[0]
        path_out = os.path.join(out_dir, single + out_ext)
        _mkdna(path_in, path_out)


def _parse_args():
    global path_input, path_output, dna_resolution, dna_depth, skip_nabla_sum, skip_normalization,\
        sobel_threshold, crop_threshold, pairs

    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:x:d:NSc:C:P:h")
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
        elif o == '-c':
            sobel_threshold = float(a)
        elif o == '-C':
            crop_threshold = float(a)
        elif o == '-P':
            pairs = Pairs(a)
            pairs.convert_singles()

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
        if pairs:
            _mkdna_folder_pairs(path_input)
        else:
            _mkdna_folder(path_input)
