from keras.applications import MobileNet
from keras.layers import Dense
from keras.models import Model
import keras.backend as backend
import keras.saving
from keras.models import load_model

import numpy as np

import dl_dna_model
from lineEnumerator import LineEnumerator


@keras.saving.register_keras_serializable()
# Triplet Loss
def _triplet_loss(y_true, y_pred, alpha=0.4):
    anchor = y_pred[0]
    positive = y_pred[1]
    negative = y_pred[2]

    # 거리 계산
    pos_dist = backend.sum(backend.square(anchor - positive))
    neg_dist = backend.sum(backend.square(anchor - negative))

    # Triplet Loss
    basic_loss = pos_dist - neg_dist + alpha
    loss = backend.maximum(basic_loss, 0.0)

    return loss


class ModelTriplet(dl_dna_model.DlDnaModel):
    def __init__(self):
        self.dl_model = MobileNet(weights='imagenet', include_top=False, pooling='avg')

        embedding_layer = Dense(dl_dna_model.n_units, activation='relu')(self.dl_model.output)
        self.dl_model = Model(inputs=self.dl_model.input, outputs=embedding_layer)
        self.dl_model.compile(optimizer='adam', loss=_triplet_loss)
        self.verbose_level = 1 if dl_dna_model.verbose else 0

    @staticmethod
    def _load_triplet(triplet):
        images = []
        for name in triplet:
            images.append(dl_dna_model.load_img_data(name))
        return np.array(images)

    def _train_triplet_model(self, triples):
        dummy_y = np.array([1, 1, 1])
        verbose_level = 1 if dl_dna_model.verbose else 0

        for triple in triples:
            images = self._load_triplet(triple)
            self.dl_model.fit(x=images, y=dummy_y, epochs=dl_dna_model.epochs, verbose=verbose_level)

    def train(self, fpath_train: str):
        triples = LineEnumerator(fpath_train, True)
        self._train_triplet_model(triples)

    def extract_dna(self, data):
        return self.dl_model.predict(data, verbose=self.verbose_level)[0]

    def save(self, path_save: str):
        self.dl_model.save(path_save)

    def load(self, path_load: str):
        self.dl_model = load_model(path_load)
