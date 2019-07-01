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

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
checkpoint_path = "saves/cp.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)
cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path,
                                                 save_weights_only=True,
                                                 verbose=1, period=1000)


class Radar():

    def __init__(self, car, radians_offset=0, length=100, ):
        self.car = car
        self._length = length
        self.radians_offset = radians_offset
        self.radians = self.car.radians + self.radians_offset
        self.detects = False
        self.start_x = self.car.center_x
        self.start_y = self.car.center_y
        self.end_x = self.car.center_x + cos(self.radians) * self._length
        self.end_y = self.car.center_y + sin(self.radians) * self._length

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
        self.detects = False
        for o in objects:
            if arcade.are_polygons_intersecting(self._get_points(), o):
                self.detects = True
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
    STEER = 0.1

    def __init__(self, terrain):
        super().__init__('images/car.png', scale=0.25, center_x=SCREEN_WIDTH/2, center_y=SCREEN_HEIGHT/2)
        self._distance = 0
        self.radars = [Radar(self, 0.5), Radar(self, 0.25), Radar(
            self), Radar(self, -0.25), Radar(self, -0.5)]
        self.bips = [0] * len(self.radars)
        self.collides = False
        self._terrain = terrain

    def turn(self, val):
        """
        Turn car left or right
        val = 1 : right
        val = 0 : straight
        val = -1 : left
        """
        self.radians -= val * self.STEER

    def update(self):
        self.change_x = self._speed * cos(self.radians)
        self.change_y = self._speed * sin(self.radians)
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.center_x < 0:
            self.center_x = SCREEN_WIDTH
        if self.center_x > SCREEN_WIDTH:
            self.center_x = 0
        if self.center_y < 0:
            self.center_y = SCREEN_HEIGHT
        if self.center_y > SCREEN_HEIGHT:
            self.center_y = 0
        # total distance
        self._distance += self._speed

        self._run_radars()
        self._check_collides()
        print(
            f"car : distance={self._distance} - speed={self._speed} - collides={self.collides} - bips={self.bips}")

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
        return [self.collides, self._distance, self._speed] + self.bips


class MyGame(arcade.Window):

    def __init__(self, width, height, agent=None):
        super().__init__(width, height, "Drive.ai")

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
        self.history = {'games': [], 'steps': [], 'epsilons': [], 'rewards': []}
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
        self._world.append([(0, 250), (SCREEN_WIDTH, 250), (SCREEN_WIDTH, 0), (0, 0)]) 
        #top
        self._world.append([(0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - 330), (0, SCREEN_HEIGHT- 330)])
        # top left
        self._world.append([(150, 400), (380, 400), (380, 600), (150, 600)])
        # top right
        self._world.append([(650, 800), (750, 800), (750, 350), (650, 350)])
        # bottom
        self._world.append([(200, 300), (600, 300), (600, 200), (200, 200)])
        
        

    def setup(self):
        print(f"------------------\n\tGAME {self.games}\n------------------")
        self._steps = 0
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.car = Car(terrain=self._world)

    def on_draw(self):
        """ Render the screen. """
        # return
        arcade.start_render()  # Clear screen
        if not self.draw:
            return

        self.car.draw()
        for o in self._world:
            arcade.draw_polygon_filled(o, arcade.color.BLUE)

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        if self.pause:
            return

        if self.graphs:
            fig, ax = plt.subplots(nrows=2, ncols=2)
            ax[0, 0].plot(self.history['games'],
                          self.history['steps'], label='steps')

            ax[0, 1].plot(self.history['games'],
                          self.history['epsilons'], label='epsilons')

            ax[1, 0].plot(self.history['games'],
                          self.history['rewards'], label='rewards')
            plt.legend()
            plt.show()
            self.graphs = False

        print(f"- step #{self._steps}")

        # get current state
        cur_state, done = self._get_state()
        cur_state = np.reshape(cur_state, [1, 5])

        # get agent action
        action = agent.act(cur_state)
        print(f"action={self._action_str(action)}")
        self._do_action(action)

        # update car
        turn = 1 if self.right_pressed else -1 if self.left_pressed else 0
        self.car.turn(turn)
        self.car.update()

        next_state, done = self._get_state()
        reward = self._get_reward(next_state, done)
        print(f"reward={reward}")
        next_state = np.reshape(next_state, [1, 5])

        self.agent.remember(cur_state, action, reward, next_state, done)

        self._steps += 1
        # replay
        if self._steps % 35 == 0:
            self.agent.replay(32)

        if done:
            self.history['games'].append([self.games])
            self.history['steps'].append([self._steps])
            self.history['epsilons'].append([self.agent.epsilon])
            self.history['rewards'].append([reward])

            # restart game
            self.games += 1
            self.setup()

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

    def _action_str(self, action):
        return ['do nothing', 'go right', 'go left'][action]

    def _get_state(self):
        car_state = self.car.get_state()
        # [...bips]
        state = car_state[3:]
        # collides
        done = car_state[0]
        
        return state, done

    def _get_reward(self, state, done):
        if done:
            # collides
            return -20
        return len(state) - sum(state) # number of radars not detecting anything


class DQNAgent():
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=3000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 0.5  # exploration rate
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = keras.Sequential()
        model.add(keras.layers.Dense(
            6, input_dim=self.state_size, activation='relu'))
        model.add(keras.layers.Dense(6, activation='relu'))
        model.add(keras.layers.Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=keras.optimizers.Adam(lr=self.learning_rate))
        # load saved model
        if Path(checkpoint_dir).exists():
            latest = tf.train.latest_checkpoint(checkpoint_dir)
            model.load_weights(latest)
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            print(f"exploration (epsilon={self.epsilon})")
            return random.randrange(self.action_size)

        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * \
                    np.amax(self.model.predict(next_state)[0])
                print('target', target)
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1,
                           verbose=0, callbacks=[cp_callback])
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


if __name__ == "__main__":
    state_size = 5
    nb_actions = 3
    agent = DQNAgent(state_size, nb_actions)
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, agent=agent)
    game.setup()
    arcade.run()
