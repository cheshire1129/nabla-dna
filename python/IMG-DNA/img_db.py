#!/usr/bin/python3

import sys
import os
import getopt

from lib import logger
from dna import img_load
from dna import dna_db
import img_dna_model_get

import img_vdb

model_type = ''
add_mode = False
args = []


img_dna_db = dna_db.DnaDb(img_vdb.ImgVdb())


def _usage_img_db():
    print("""\
Usage: img_db.py [<options>]  <image name>: add or search image DNA
                             <image list file>: add or search image DNA's in the list file
   <options>
   -h: help(this message)
   -A: add vector mode
   -m <model>: sift, orb
   -d <db path>: dna DB path(if existing)
   -D <db path>: create a new DB
   -t <threshold>: threshold for multi search
   -f <image folder> (IMAGE_FOLDER)
""")


def _setup_envs():
    if 'IMAGE_FOLDER' in os.environ:
        img_load.image_fpath = os.environ['IMAGE_FOLDER']


def _parse_args():
    global model_type, args, add_mode

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hAm:d:t:D:")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_img_db()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_img_db()
            exit(0)
        if o == '-A':
            add_mode = True
        elif o == '-m':
            model_type = a
        elif o == '-d':
            img_dna_db.load(a)
        elif o == '-t':
            img_dna_db.threshold = float(a)
        elif o == '-D':
            img_dna_db.create(a)


if __name__ == "__main__":
    logger.init("img_db")

    _setup_envs()
    _parse_args()
    model = img_dna_model_get.get_img_dna_model(model_type)

    if len(args) == 0:
        _usage_img_db()
        exit(1)
    if add_mode:
        img_dna_db.add(model, args[0])
    else:
        img_dna_db.search(model, args[0])
