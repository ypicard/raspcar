import os
import numpy as np
from math import atan2, sqrt, cos, sin
import random
from collections import deque
import arcade
import tensorflow as tf
from tensorflow import keras
from pathlib import Path
import matplotlib.pyplot as plt
import itertools

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
NETWORK_NAME = 'dueling_dqn'
checkpoint_path = f"saves/{NETWORK_NAME}/cp.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)
cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path,
                                                 save_weights_only=True,
                                                 verbose=1, period=1000)


class Radar():

    def __init__(self, car, radians_offset=0, length=80):
        self.car = car
        self._length = length
        self.radians_offset = radians_offset
        self.radians = self.car.radians + self.radians_offset
        self.detects = 0
        self.start_x = self.car.center_x
        self.start_y = self.car.center_y
        self.end_x = self.car.center_x + cos(self.radians) * self._length
        self.end_y = self.car.center_y + sin(self.radians) * self._length
        self.radians = random.random() * 3.14

    def update(self, terrain):
        self.radians = self.car.radians + self.radians_offset
        self.start_x = self.car.center_x
        self.start_y = self.car.center_y
        self.end_x = self.car.center_x + cos(self.radians) * self._length
        self.end_y = self.car.center_y + sin(self.radians) * self._length

        self._bip(terrain)

    def _get_points(self):
        return [(self.start_x, self.start_y), (self.end_x, self.end_y)]

    def _bip(self, objects):
        self.detects = 0
        for o in objects:
            if arcade.are_polygons_intersecting(self._get_points(), o):
                self.detects = 1
                break
        return self.detects

    def draw(self):
        color = arcade.color.RED if self.detects else arcade.color.BLUE
        arcade.draw_line(self.start_x, self.start_y,
                         self.end_x, self.end_y, color)


class Car(arcade.Sprite):
    CAR_WIDTH = 50
    CAR_LENGTH = 100
    _speed = 5
    _steer = 0.2

    def __init__(self, terrain):
        super().__init__('images/car.png', scale=0.25,
                         center_x=SCREEN_WIDTH/2, center_y=SCREEN_HEIGHT/2)
        self._distance = 0
        self.radars = [Radar(self, 0.7, length=40), Radar(self, 0.4, length=60), Radar(
            self), Radar(self, -0.4, length=60), Radar(self, -0.7, length=40)]
        self.bips = [0] * len(self.radars)
        self.collides = False
        self._terrain = terrain
        self.change_angle = 0
        self.radians = random.random() * 3.14  # random initial angle

    def turn(self, val):
        """
        Turn car left or right
        val = 1 : right
        val = 0 : straight
        val = -1 : left
        """
        self.change_angle = -val * self._steer

    def update(self):
        self.radians += self.change_angle
        self.change_x = self._speed * cos(self.radians)
        self.change_y = self._speed * sin(self.radians)
        self.center_x += self.change_x
        self.center_y += self.change_y

        # +- 100 to avoid problems when approaching screen sides and radars not detecting border on other side
        if self.center_x - 100 < 0:
            self.center_x = SCREEN_WIDTH - 100
        if self.center_x + 100 > SCREEN_WIDTH:
            self.center_x = 0 + 100
        if self.center_y < 0:
            self.center_y = SCREEN_HEIGHT
        if self.center_y > SCREEN_HEIGHT:
            self.center_y = 0
        # total distance
        self._distance += self._speed

        self._run_radars()
        self._check_collides()
        # print(f"car : distance={self._distance} - speed={self._speed} - collides={self.collides} - change_angle={self.change_angle} - bips={self.bips}")

    def draw(self):
        """ Override Sprite draw method """
        super(Car, self).draw()
        for radar in self.radars:
            radar.draw()

    def _check_collides(self):
        self.collides = False
        for o in self._terrain:
            if arcade.are_polygons_intersecting(self.get_points(), o):
                self.collides = True
                break

    def _run_radars(self):
        self.bips = [False] * len(self.radars)
        for idx, radar in enumerate(self.radars):
            radar.update(self._terrain)
            self.bips[idx] = radar.detects

    def get_state(self):
        # return [self.collides, self._distance, self._speed, self.change_angle] + self.bips
        return self.bips


class MyGame(arcade.Window):

    def __init__(self, width, height, agent=None):
        super().__init__(width, height, f"Drive.ai - {NETWORK_NAME}")

        arcade.set_background_color(arcade.color.AMAZON)

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.games = 0
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.car = None
        self.agent = agent
        self.draw = True
        self.graphs = False
        self.pause = False
        self.history = {'games': [], 'score': [],
                        'epsilons': [], 'rewards': []}
        self._world = []
        # map 1
        # self._world.append([(400, 400), (500, 400), (500, 500), (400, 500)])
        # self._world.append([(200, 200), (300, 200), (300, 300), (200, 300)])
        # self._world.append([(500, 100), (550, 100), (550, 300), (500, 300)])
        # self._world.append([(100, 700), (400, 700), (400, 600), (100, 600)])
        # self._world.append([(700, 700), (750, 700), (750, 750), (700, 750)])
        # # self._world.append([(0, 0), (50, 0), (50, 50), (0, 50)])
        # self._world.append([(70, 300), (70, 500), (80, 500), (80, 300)])
        # self._world.append([(700, 400), (750, 400), (750, 600), (700, 600)])
        # self._world.append([(200, 100), (200, 50), (400, 50), (400, 100)])

        # map 2
        # bottom
        # self._world.append([(0, 250), (SCREEN_WIDTH, 250), (SCREEN_WIDTH, 0), (0, 0)])
        # top
        # selfd._world.append([(0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - 330), (0, SCREEN_HEIGHT- 330)])
        # top left
        # self._world.append([(150, 350), (300, 350), (300, 600), (150, 600)])
        # # top right
        # self._world.append([(650, 600), (750, 600), (750, 350), (650, 350)])
        # # bottom
        # self._world.append([(200, 200), (600, 200), (600, 100), (200, 100)])

        # map 3
        # bottom
        self._world.append(
            [(0, 320), (SCREEN_WIDTH, 320), (SCREEN_WIDTH, 0), (0, 0)])
        # top
        self._world.append([(0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT),
                            (SCREEN_WIDTH, SCREEN_HEIGHT - 320), (0, SCREEN_HEIGHT - 320)])

    def setup(self):
        print(f"------------------\n\tGAME {self.games}\n------------------")
        self._steps = 0
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.car = Car(terrain=self._world)
        self.cum_reward = 0
        self.states = deque(maxlen=FRAMES_PER_STATE)
        # 4 initial state frames
        self.add_car_state(self.car.get_state())
        self.add_car_state(self.car.get_state())
        self.add_car_state(self.car.get_state())
        self.add_car_state(self.car.get_state())
        self.state, _, _ = self.observe()

    def on_draw(self):
        """ Render the screen. """
        # return
        arcade.start_render()  # Clear screen
        if not self.draw:
            return

        self.car.draw()
        for o in self._world:
            arcade.draw_polygon_filled(o, arcade.color.BLUE)
        arcade.draw_text(f'{NETWORK_NAME}', 10,
                         SCREEN_HEIGHT-25, arcade.color.WHITE)
        arcade.draw_text(f'game {self.games}', 10,
                         SCREEN_HEIGHT-50, arcade.color.WHITE)
        arcade.draw_text(f'step {self._steps}', 10,
                         SCREEN_HEIGHT-75, arcade.color.WHITE)
        arcade.draw_text(f'reward {self.cum_reward}',
                         10, SCREEN_HEIGHT-100, arcade.color.WHITE)

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        if self.pause:
            return

        if self.graphs:
            self.draw_graphs()

        # get agent action
        action = agent.act(self.state)
        self._do_action(action)

        # update car
        turn = 1 if self.right_pressed else -1 if self.left_pressed else 0
        self.car.turn(turn)
        self.car.update()
        self.add_car_state(self.car.get_state())

        next_state, reward, done = self.observe()

        self.agent.remember(self.state, action, reward, next_state, done)
        self.state = next_state
        self.cum_reward += reward

        print(
            f"step #{self._steps} : state={self.state}, reward={reward}, done={done}")
        # replay only when a lot of exploration has been done
        if len(self.agent.memory) > 30 and self._steps % 5 == 0:
            self.agent.replay(30)

        if done:
            print(
                f'#### game {self.games} : steps={self._steps}, score={self.cum_reward}')
            self.history['games'].append(self.games)
            self.history['score'].append(self._steps)
            self.history['epsilons'].append(self.agent.epsilon)
            self.history['rewards'].append(self.cum_reward)
            # restart game
            self.games += 1
            self.setup()
        self._steps += 1

    def observe(self):
        state = np.reshape(
            list(itertools.chain.from_iterable(self.states)), [1, STATE_SIZE])
        done = self.car.collides or self._steps == 500
        # reward
        reward = 1  # best so far
        # reward = len(state[0]) - sum(state[0]) + 1
        if self.car.collides:
            reward = -50

        return state, reward, done

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.D:
            self.draw = not self.draw
        if key == arcade.key.G:
            self.graphs = not self.graphs
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        if key == arcade.key.SPACE:
            self.pause = not self.pause

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def _do_action(self, action):
        if action == 0:
            self.left_pressed = False
            self.right_pressed = False
        elif action == 1:
            self.right_pressed = True
        elif action == 2:
            self.left_pressed = True

    def add_car_state(self, state):
        self.states.append(state)

    def draw_graphs(self):
        fig, ax = plt.subplots(nrows=2, ncols=2)
        ax[0, 0].plot(self.history['score'], label='score')
        ax[0, 0].legend(loc="upper right")

        ax[0, 1].plot(self.history['epsilons'], label='epsilons')
        ax[0, 1].legend(loc="upper right")

        ax[1, 0].plot(self.history['rewards'], label='rewards')
        ax[1, 0].legend(loc="upper right")

        ax[1, 1].plot(self.history['score'], '-', label='score')
        mva9 = np.convolve(self.history['score'], np.ones(9)/9)
        ax[1, 1].plot(mva9, label='mva 9')
        mva50 = np.convolve(self.history['score'], np.ones(50)/50)
        ax[1, 1].plot(mva50, label='mva 50')
        mva100 = np.convolve(self.history['score'], np.ones(100)/100)
        ax[1, 1].plot(mva100, label='mva 100')
        ax[1, 1].legend(loc="upper right")

        plt.legend()
        plt.show()
        self.graphs = False


class DQNAgent():
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.tau = 100
        self.gamma = 0.95  # discount rate
        self.epsilon = 1  # exploration rate
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
        self.trained = 0

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = keras.Sequential()
        model.add(keras.layers.Dense(
            24, input_dim=self.state_size, activation='relu'))
        model.add(keras.layers.Dense(24, activation='relu'))
        model.add(keras.layers.Dense(self.action_size + 1, activation='linear'))    
        model.add(keras.layers.Lambda(lambda a: keras.backend.expand_dims(a[:, 0], -1) + a[:, 1:] - keras.backend.mean(a[:, 1:], axis=1, keepdims=True), output_shape=(self.action_size,)))
        model.compile(loss='mse',
                      optimizer=keras.optimizers.Adam(lr=self.learning_rate))
        # load saved model
        # latest = tf.train.latest_checkpoint(checkpoint_dir)
        # model.load_weights(latest)
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)

        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # regturns action

    def replay(self, batch_size):
        self.trained += 1
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * \
                    np.amax(self.target_model.predict(next_state)[0])
            target_f = self.target_model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1,
                           verbose=0, callbacks=[cp_callback])
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        if self.trained % self.tau == 0:
            # update model weights with target_model weights every tau steps
            self.update_target_model()

    def update_target_model(self):
        ''' Assign weights from an other agent to self '''
        print("Updating weights...")
        self.target_model.set_weights(self.model.get_weights())


CAR_STATE_SIZE = 5
ACTION_SIZE = 3
FRAMES_PER_STATE = 2
STATE_SIZE = FRAMES_PER_STATE * CAR_STATE_SIZE
if __name__ == "__main__":
    agent = DQNAgent(STATE_SIZE, ACTION_SIZE)
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, agent=agent)
    game.setup()
    arcade.run()
