import numpy as np
import tensorflow as tf
from tensorflow import keras
from pathlib import Path

STATE_SIZE = 5
ACTION_SIZE = 3
LEARNING_RATE = 0.001
def _action_str(action):
        return ['do nothing', 'go right', 'go left'][action]
def _build_model():
    # Neural Net for Deep-Q learning Model
    model = keras.Sequential()
    model.add(keras.layers.Dense(
        24, input_dim=STATE_SIZE, activation='relu'))
    model.add(keras.layers.Dense(24, activation='relu'))
    model.add(keras.layers.Dense(ACTION_SIZE, activation='linear'))
    model.compile(loss='mse',
                    optimizer=keras.optimizers.Adam(lr=LEARNING_RATE))

    print("LOAD")
    model.load_weights("saves/cp.ckpt")
    return model

model = _build_model()
state = [False, False, True,False,False]
state = np.reshape(state, [1, len(state)])
act_values = model.predict(state)
print(act_values)
act_idx = np.argmax(act_values[0])
print(act_idx)
print(_action_str(act_idx))