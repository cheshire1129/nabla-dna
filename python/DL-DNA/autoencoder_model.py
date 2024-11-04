import tensorflow as tf
# noinspection PyUnresolvedReferences
from tensorflow.keras.layers import Input, Dense, Conv2D, Conv2DTranspose, Flatten, Reshape, LeakyReLU, BatchNormalization
# noinspection PyUnresolvedReferences
from tensorflow.keras.models import Model, load_model
# noinspection PyUnresolvedReferences
from tensorflow.keras.optimizers import Adam
# noinspection PyUnresolvedReferences
from tensorflow.keras.callbacks import EarlyStopping
# noinspection PyUnresolvedReferences
from tensorflow.keras import backend as K

from scipy import spatial

import numpy as np

import img_load
import dl_dna_model
from lineEnumerator import LineEnumerator

full_batch = False
path_decoded_image = None

# from https://pyimagesearch.com/2020/02/17/autoencoders-with-keras-tensorflow-and-deep-learning/

class AutoEncoder(dl_dna_model.DlDnaModel):
    def __init__(self):
        super().__init__()

        filters = (64, 32)

        tf.config.run_functions_eagerly(True)

        x = input_layer = Input(shape=(224, 224, 3))

        for f in filters:
            x = Conv2D(f, (3, 3), strides=2, padding="same")(x)
            x = LeakyReLU(alpha=0.2)(x)
            x = BatchNormalization()(x)

        volume_size = K.int_shape(x)
        x = Flatten()(x)

        encoded = Dense(dl_dna_model.n_units, name='encoded')(x)

        x = Dense(np.prod(volume_size[1:]))(encoded)
        x = Reshape((volume_size[1], volume_size[2], volume_size[3]))(x)

        for f in filters[::-1]:
            x = Conv2DTranspose(f, (3, 3), strides=2, padding="same")(x)
            x = LeakyReLU(alpha=0.2)(x)
            x = BatchNormalization()(x)

        decoded = Conv2DTranspose(3, (3, 3), activation='sigmoid', padding="same")(x)

        self.dl_model = Model(input_layer, decoded)
        optimizer = Adam(learning_rate=0.001)
        self.dl_model.compile(optimizer=optimizer, loss='mean_squared_error', metrics=['accuracy'])

        self.encoder = Model(input_layer, encoded)

        self.verbose_level = 1 if 'k' in dl_dna_model.verbose else 0

    @staticmethod
    def _load_images(lines):
        images = []
        for img_name in lines:
            images.append(img_load.load_img_data(img_name))
        return np.array(images)

    def train(self, fpath_train: str):
        lines = LineEnumerator(fpath_train)
        images = self._load_images(lines)

        images = images / 255.

        batch_size = dl_dna_model.batch_size if dl_dna_model.batch_size != 0 else len(images)
        self.dl_model.fit(images, images, epochs=dl_dna_model.epochs, batch_size=batch_size,
                          verbose=self.verbose_level)

    def extract_dna(self, data):
        global path_decoded_image

        data = data / 255.
        if path_decoded_image:
            img_load.save_img(path_decoded_image, self.dl_model.predict(data)[0] * 255.)
        return self.encoder.predict(data, verbose=self.verbose_level)[0]

    def _get_distance(self, dna1, dna2):
        return spatial.distance.cosine(dna1, dna2)

    def save(self, path_save: str):
        self.dl_model.save(path_save)

    def load(self, path_load: str):
        self.dl_model = load_model(path_load)

        self.encoder = Model(self.dl_model.input, self.dl_model.get_layer('encoded').output)
