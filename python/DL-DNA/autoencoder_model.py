import tensorflow as tf
# noinspection PyUnresolvedReferences
from tensorflow.keras.layers import Input, Dense, Conv2D, Flatten, Reshape, MaxPooling2D, UpSampling2D, BatchNormalization
# noinspection PyUnresolvedReferences
from tensorflow.keras.models import Model, load_model
# noinspection PyUnresolvedReferences
from tensorflow.keras.optimizers import Adam
# noinspection PyUnresolvedReferences
from tensorflow.keras.callbacks import EarlyStopping
from scipy import spatial

import numpy as np

import img_load
import dl_dna_model
from lineEnumerator import LineEnumerator

full_batch = False
path_decoded_image = None

class AutoEncoder(dl_dna_model.DlDnaModel):
    def __init__(self):
        super().__init__()

        tf.config.run_functions_eagerly(True)

        input_layer = Input(shape=(224, 224, 3))

        x = Conv2D(64, (3, 3), activation='relu', padding='same')(input_layer)
        x = MaxPooling2D((2, 2), padding='same')(x)

        x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
        x = MaxPooling2D((2, 2), padding='same')(x)

        x = Conv2D(16, (3, 3), activation='relu', padding='same')(x)
        x = MaxPooling2D((2, 2), padding='same')(x)

        volume_size = np.prod(x.shape[1:])
        x = Flatten()(x)
        encoded = Dense(dl_dna_model.n_units, activation='relu', name='encoded')(x)

        x = Dense(volume_size, activation='relu')(encoded)
        x = Reshape((28, 28, 16))(x)

        x = Conv2D(16, (3, 3), activation='relu', padding='same')(x)
        x = UpSampling2D((2, 2))(x)

        x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
        x = UpSampling2D((2, 2))(x)

        x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        x = UpSampling2D((2, 2))(x)

        decoded = Conv2D(3, (3, 3), activation='relu', padding='same')(x)

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

        batch_size = dl_dna_model.batch_size if dl_dna_model.batch_size != 0 else len(images)
        self.dl_model.fit(images, images, epochs=dl_dna_model.epochs, batch_size=batch_size,
                          verbose=self.verbose_level)

    def extract_dna(self, data):
        global path_decoded_image

        if path_decoded_image:
            img_load.save_img(path_decoded_image, self.dl_model.predict(data)[0])
        return self.encoder.predict(data, verbose=self.verbose_level)[0]

    def _get_distance(self, dna1, dna2):
        return 2 * spatial.distance.cosine(dna1, dna2)

    def save(self, path_save: str):
        self.dl_model.save(path_save)

    def load(self, path_load: str):
        self.dl_model = load_model(path_load)

        self.encoder = Model(self.dl_model.input, self.dl_model.get_layer('encoded').output)
