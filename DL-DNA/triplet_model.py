import tensorflow as tf
# noinspection PyUnresolvedReferences
from tensorflow.keras.applications import MobileNet
# noinspection PyUnresolvedReferences
from tensorflow.keras.layers import Dense
# noinspection PyUnresolvedReferences
from tensorflow.keras.models import Model, load_model

import numpy as np

import dl_dna_model
from lineEnumerator import LineEnumerator


def _triplet_loss(_y_true, y_pred, alpha=0.4):
    anchor = y_pred[0]
    positive = y_pred[1]
    negative = y_pred[2]

    # 거리 계산
    pos_dist = tf.reduce_sum(tf.square(anchor - positive))
    neg_dist = tf.reduce_sum(tf.square(anchor - negative))

    # Triplet Loss
    basic_loss = pos_dist - neg_dist + alpha
    loss = tf.maximum(basic_loss, 0.0)

    return loss


class ModelTriplet(dl_dna_model.DlDnaModel):
    def __init__(self):
        super().__init__()

        tf.config.run_functions_eagerly(True)
        mobilenet = MobileNet(weights='imagenet', include_top=False, pooling='avg')

        embedding_layer = Dense(dl_dna_model.n_units, activation='relu')(mobilenet.output)
        self.dl_model = Model(inputs=mobilenet.input, outputs=embedding_layer)
        self.dl_model.compile(optimizer='adam', loss=_triplet_loss, metrics=['accuracy'])
        self.verbose_level = 1 if dl_dna_model.verbose else 0

    @staticmethod
    def _load_triplets(triples):
        images = []
        for triplet in triples:
            for name in triplet:
                images.append(dl_dna_model.load_img_data(name))
        return np.array(images)

    def _train_triplet_model(self, triples):
        images = self._load_triplets(triples)
        dummy_y = np.ones((images.shape[0],))
        self.dl_model.fit(x=images, y=dummy_y, batch_size=3, epochs=dl_dna_model.epochs, verbose=self.verbose_level)

    def train(self, fpath_train: str):
        triples = LineEnumerator(fpath_train, True)
        self._train_triplet_model(triples)

    def extract_dna(self, data):
        return self.dl_model.predict(data, verbose=self.verbose_level)[0]

    def save(self, path_save: str):
        self.dl_model.save(path_save)

    def load(self, path_load: str):
        self.dl_model = load_model(path_load, custom_objects={'_triplet_loss': _triplet_loss})
