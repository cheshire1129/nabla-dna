#!/usr/bin/python3

import sys
import os
import getopt

import logger
import img_load
import dl_dna_model
import dl_dna_model_get

import dl_db_op

model_type = 'autoencoder'
add_mode = False
fpath_train: str = ""
path_model: str = ""
args = None

def _usage_dl_db():
    print("""\
Usage: dl_db.py [<options>]  <image name>: add or search image DNA
                             <image list file>: add or search image DNA's in the list file
   <options>
   -h: help(this message)
   -A: add vector mode
   -m <model>: triplet_loss(default), mobilenet, vgg, autoencoder
   -l <model path>: model path
   -d <db path>: dna DB path(if existing)
   -D <db path>: create a new DB
   -f <image folder> (IMAGE_FOLDER)
   -u <units>: unit count for embedding vector
   -v <options>: enable verbose output
      k: keras output
      t: triple loss output
      T: simple triple loss output
""")


def _setup_envs():
    if 'IMAGE_FOLDER' in os.environ:
        img_load.image_fpath = os.environ['IMAGE_FOLDER']


def _parse_args():
    global model_type, fpath_train, args, path_model, add_mode

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hAm:t:l:d:D:u:v:")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_dl_db()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_dl_db()
            exit(0)
        if o == '-A':
            add_mode = True
        elif o == '-m':
            model_type = a
        elif o == '-l':
            path_model = a
        elif o == '-d':
            dl_db_op.load_vdb(a)
        elif o == '-D':
            dl_db_op.create_vdb(a)
        elif o == '-u':
            dl_dna_model.n_units = int(a)
        elif o == '-v':
            dl_dna_model.verbose = a

if __name__ == "__main__":
    logger.init("dl_db")

    _setup_envs()
    _parse_args()
    model = dl_dna_model_get.get_dl_dna_model(model_type)
    if path_model:
        model.load(path_model)

    if len(args) == 0:
        _usage_dl_db()
        exit(1)
    if add_mode:
        dl_db_op.add_dna(model, args[0])
    else:
        dl_db_op.search_dna(model, args[0])