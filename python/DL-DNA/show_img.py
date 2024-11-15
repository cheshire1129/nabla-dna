#!/usr/bin/python3

import sys
import os
import getopt
from lib import logger
from dna import img_load


img_name: str = ""


def _usage_show_img():
    print("""\
Usage: show_img.py <image name>
   <options>
   -h: help(this message)
   -f <image folder> (IMAGE_FOLDER)
   -C <threshold>: crop area outside contour
""")


def _setup_envs():
    if 'IMAGE_FOLDER' in os.environ:
        img_load.image_fpath = os.environ['IMAGE_FOLDER']


def _show_img():
    img_load.show_img(img_name)


def _parse_args():
    global img_name

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_show_img()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_show_img()
            exit(0)
        elif o == '-f':
            img_load.image_fpath = a

    if len(args) < 1:
        logger.error("input image required")
        _usage_show_img()
        exit(1)
    img_name = args[0]


if __name__ == "__main__":
    logger.init("show_img")

    _setup_envs()
    _parse_args()
    _show_img()
