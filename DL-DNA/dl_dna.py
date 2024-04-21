#!/usr/bin/python3

import sys
import os
import getopt

import logger
import dl_dna_model
import triplet_model
import mobilenet

model_type = 'triplet_loss'
fpath_train: str = ""
fpath_extract: str = ""
path_save: str = ""
path_load: str = ""


def _usage_dl_dna():
    print("""\
Usage: DL-DNA.py [<options>]
   <options>
   -h: help(this message)
   -m <model>: triplet_loss(default), mobilenet
   -t <training file>: training mode with file path
       triplet_loss: image list with triple fields
       mobilenet: image list with single field
   -e <extraction file>: extract DL-DNA with file path
       file should be image list with single field
   -s <path for save>: path for saving model
   -l <path for load>: path for loading model
   -u <units>: unit count for embedding vector (N_UNITS: env variable)
   -f <image folder> (IMAGE_FOLDER)
   -E <epochs> (EPOCHS)
   -v: enable keras output
""")


def _setup_envs():
    if 'N_UNITS' in os.environ:
        dl_dna_model.n_units = int(os.environ['N_UNITS'])
    if 'IMAGE_FOLDER' in os.environ:
        dl_dna_model.image_fpath = os.environ['IMAGE_FOLDER']
    if 'EPOCHS' in os.environ:
        dl_dna_model.epochs = os.environ['EPOCHS']


def _parse_args():
    global model_type, fpath_train, fpath_extract, path_save, path_load

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:t:e:f:s:l:u:E:v")
    except getopt.GetoptError:
        logger.error("invalid option")
        _usage_dl_dna()
        exit(1)
    for o, a in opts:
        if o == '-h':
            _usage_dl_dna()
            exit(0)
        if o == '-m':
            model_type = a
        if o == '-t':
            fpath_train = a
        if o == '-e':
            fpath_extract = a
        elif o == '-f':
            dl_dna_model.image_fpath = a
        elif o == '-s':
            path_save = a
        elif o == '-l':
            path_load = a
        elif o == '-u':
            dl_dna_model.n_units = int(a)
        elif o == '-E':
            dl_dna_model.epochs = int(a)
        elif o == '-v':
            dl_dna_model.verbose = True


def get_dl_dna_model():
    if model_type == 'triplet_loss':
        return triplet_model.ModelTriplet()
    return mobilenet.ModelMobileNet()


if __name__ == "__main__":
    logger.init("DL-DNA")

    _setup_envs()
    _parse_args()
    model = get_dl_dna_model()
    if path_load:
        model.load(path_load)
    if fpath_train:
        model.train(fpath_train)
    if path_save:
        model.save(path_save)
    if fpath_extract:
        model.extract(fpath_extract)
