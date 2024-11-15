import tensorflow as tf
# noinspection PyUnresolvedReferences
from tensorflow.keras.applications import MobileNet
# noinspection PyUnresolvedReferences
from tensorflow.keras.layers import Dense
# noinspection PyUnresolvedReferences
from tensorflow.keras.models import Model, load_model
# noinspection PyUnresolvedReferences
from tensorflow.keras.optimizers import Adam
# noinspection PyUnresolvedReferences
from tensorflow.keras.callbacks import EarlyStopping

import numpy as np

from dna import img_load
from lib.lineEnumerator import LineEnumerator
import dl_dna_model


def _triplet_loss(_y_true, y_pred, alpha=0.4):
    losses = []
    n_triples = int(y_pred.shape[0] / 3)
    for idx in range(0, n_triples * 3, 3):
        anchor = y_pred[idx]
        positive = y_pred[idx + 1]
        negative = y_pred[idx + 2]
        pos_dist = tf.reduce_sum(tf.square(anchor - positive))
        neg_dist = tf.reduce_sum(tf.square(anchor - negative))
        basic_loss = pos_dist - neg_dist + alpha
        losses.append(tf.maximum(basic_loss, 0.0))
        if 't' in dl_dna_model.verbose:
            print(f"a: {anchor.numpy()} p: {positive.numpy()}, n: {negative.numpy()} pd: {pos_dist.numpy():.3f}, "
                  f"nd: {neg_dist.numpy():.3f}")
        elif 'T' in dl_dna_model.verbose:
            print(f"pd: {pos_dist.numpy():.3f}, nd: {neg_dist.numpy():.3f}")

    x = tf.reduce_mean(losses)
    return x


class ModelTriplet(dl_dna_model.DlDnaModel):
    def __init__(self):
        super().__init__()

        tf.config.run_functions_eagerly(True)
        mobilenet = MobileNet(weights='imagenet', include_top=True)
        mobilenet.trainable = False

        embedding_layer = Dense(dl_dna_model.n_units, activation='relu')(mobilenet.output)

        self.dl_model = Model(inputs=mobilenet.input, outputs=embedding_layer)
        optimizer = Adam(learning_rate=0.1)
        self.dl_model.compile(optimizer=optimizer, loss=_triplet_loss, metrics=['accuracy'])

        self.verbose_level = 1 if 'k' in dl_dna_model.verbose else 0

    @staticmethod
    def _load_triplets(triples):
        images = []
        for triplet in triples:
            for name in triplet:
                images.append(img_load.load_img_data(name))
        return np.array(images)

    def _train_triplet_model(self, triples):
        images = self._load_triplets(triples)
        dummy_y = np.ones((images.shape[0],))

        batch_size = 3 if dl_dna_model.batch_size != 0 else len(images)
        early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
        self.dl_model.fit(x=images, y=dummy_y, batch_size=batch_size, epochs=dl_dna_model.epochs,
                          shuffle=False, callbacks=[early_stopping], verbose=self.verbose_level)

    def train(self, fpath_train: str):
        triples = LineEnumerator(fpath_train, True)
        self._train_triplet_model(triples)

    def extract_dna(self, data):
        if data.ndim == 3:
            data = data[None, :]
        return self.dl_model.predict(data, verbose=self.verbose_level)[0]

    def save(self, path_save: str):
        self.dl_model.save(path_save)

    def load(self, path_load: str):
        self.dl_model = load_model(path_load, custom_objects={'_triplet_loss': _triplet_loss})
