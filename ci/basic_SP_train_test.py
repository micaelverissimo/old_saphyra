from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
from tensorflow import keras
from saphyra import sp
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt


def test():
    print(tf.__version__)
    x_train = np.array([
        [1, 3, 5],
        [7, 8, 9],
        [2, 4, 6],
    ])
    y_train = np.array([
        1, 0, 1
    ])
    x_valid = np.array([
        [1, 2, 3],
        [2, 3, 1],
        [9, 8, 7]
    ])
    y_valid = np.array([
        1, 1, 0
    ])
    model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(3,)),
    tf.keras.layers.Dense(2, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(1)
    ])
    sp_values = []
    model.compile('adam', loss='mse', metrics=['accuracy'])
    sp_obj = sp(patience=25, verbose=True, save_the_best=True, sp_values=sp_values)
    sp_obj.set_validation_data ( (x_valid, y_valid) )
    model.fit (
        x_train, y_train,
        epochs = 5000,
        batch_size = 256,
        verbose = True,
        validation_data = (x_valid, y_valid),
        callbacks = [sp_obj],
        shuffle = True
    )