import numpy as np
import random
from abc import ABC, abstractmethod

from dna import dna_model

n_units = 64
epochs = 2
batch_size = 32
threshold = None
seed = 0
verbose = ""

class DlDnaModel(dna_model.DnaModel):
    def __init__(self):
        global seed

        np.set_printoptions(precision=3)
        if seed != 0:
            random.seed(seed)
            np.random.seed(seed)
            import tensorflow
            tensorflow.random.set_seed(seed)

    @abstractmethod
    def train(self, fpath: str):
        pass

    # noinspection PyMethodMayBeStatic
    def save(self, path_save: str):
        print("saving model is not supported")
        exit(1)

    # noinspection PyMethodMayBeStatic
    def load(self, path_load: str):
        print("loading model is not supported")
        exit(1)