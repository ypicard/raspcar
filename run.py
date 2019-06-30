import os
import numpy as np
from math import atan2, sqrt, cos, sin
import random
from collections import deque
import arcade
import tensorflow as tf
from tensorflow import keras
from pathlib import Path

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Drive.ai"
checkpoint_path = "saves/cp.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)
cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path,
                                                 save_weights_only=True,
                                                 verbose=1, period=1000)


class Radar():
    RADAR_SIZE = 100

    def __init__(self, car, radians_offset=0):
        self.car = car
        self.radians_offset = radians_offset
        self.radians = self.car.radians + self.radians_offset
        self.color = arcade.color.RED
        self.start_x = self.car.center_x
        self.start_y = self.car.center_y
        self.end_x = self.car.center_x + cos(self.radians) * self.RADAR_SIZE
        self.end_y = self.car.center_y + sin(self.radians) * self.RADAR_SIZE

    def update(self):
        self.radians = self.car.radians + self.radians_offset
        self.start_x = self.car.center_x
        self.start_y = self.car.center_y
        self.end_x = self.car.center_x + cos(self.radians) * self.RADAR_SIZE
        self.end_y = self.car.center_y + sin(self.radians) * self.RADAR_SIZE

    def _get_points(self):
        return [(self.start_x, self.start_y), (self.end_x, self.end_y)]

    def bip(self, objects):
        detects = False
        for o in objects:
            if arcade.are_polygons_intersecting(self._get_points(), o):
                detects = True
                break
        return detects

    def draw(self):
        arcade.draw_line(self.start_x, self.start_y,
                         self.end_x, self.end_y, self.color)


class Car(arcade.Sprite):
    CAR_WIDTH = 50
    CAR_LENGTH = 100
    MAX_SPEED = 8
    MAX_ACC = 5
    HORSE_POWER = 0.5
    STEER = 0.1

    def __init__(self):
        super().__init__('images/car.png', scale=0.25, center_x=20, center_y=100)
        self.acc = 0
        self.speed = 0
        self.distance = 0
        self.radars = [Radar(self), Radar(self, 0.523), Radar(self, -0.523), Radar(self, 0.25), Radar(self, -0.25)]
        self.bips = [0] * len(self.radars)
        self.collides = False

    def _compute_speed(self):
        return sqrt(self.change_x * self.change_x + self.change_y * self.change_y)

    def throttle(self, val):
        """
        Increase or decrease car speed
        val = 1 : speed up
        val = 0 : constant
        val = -1 : slow down
        """
        self.acc = val * self.HORSE_POWER
        # max acceleration
        if self.acc > self.MAX_ACC:
            self.acc = self.MAX_ACC
        # No negative acceleration if no speed
        if self.acc < 0 and self.speed <= 0:
            self.acc = 0

        speed = self._compute_speed()
        self.change_x = (speed + self.acc) * cos(self.radians)
        self.change_y = (speed + self.acc) * sin(self.radians)

        # max speed
        if speed > self.MAX_SPEED:
            self.change_x = self.MAX_SPEED * \
                cos(atan2(self.change_y, self.change_x))
            self.change_y = self.MAX_SPEED * \
                sin(atan2(self.change_y, self.change_x))
        # No negative speed
        if self.change_x * cos(self.radians) + self.change_y * sin(self.radians) < 0:
            self.change_x = 0
            self.change_y = 0
        self.speed = self._compute_speed()

    def turn(self, val):
        """
        Turn car left or right
        val = 1 : right
        val = 0 : straight
        val = -1 : left
        """
        self.radians -= val * self.STEER

    def update(self):
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
        self.distance += self.speed

        for radar in self.radars:
            radar.update()

    def draw(self):
        """ Override Sprite draw method """
        super(Car, self).draw()
        for radar in self.radars:
            radar.draw()

    def check_collides(self, objects):
        self.collides = False
        for o in objects:
            if arcade.are_polygons_intersecting(self.get_points(), o):
                self.collides = True
                break

    def run_radars(self, objects):
        self.bips = [0] * len(self.radars)
        for idx, radar in enumerate(self.radars):
            if radar.bip(objects):
                self.bips[idx] = 1

    def get_state(self):
        return {'speed': self.speed,
                'speed_x': self.change_x,
                'speed_y': self.change_y,
                'distance': self.distance,
                'x': self.center_x,
                'y': self.center_y,
                'acc': self.acc,
                'radians': self.radians,
                'collides': self.collides,
                'bips': self.bips}


class MyGame(arcade.Window):

    def __init__(self, width, height, title, agent=None):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.games = 0
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.car = None
        self.terrains = []
        self.agent = agent
        self.draw = True

    def setup(self):
        print(" ----- GAME" , self.games)
        self.steps = 0
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.car = Car()
        self.terrains = []
        self.terrains.append([(400, 400), (500, 400), (500, 500), (400, 500)])
        self.terrains.append([(200, 200), (300, 200), (300, 300), (200, 300)])
        self.terrains.append([(500, 100), (550, 100), (550, 300), (500, 300)])
        self.terrains.append([(100, 700), (400, 700), (400, 600), (100, 600)])
        self.terrains.append([(700, 700), (750, 700), (750, 750), (700, 750)])
        # self.terrains.append([(0, 0), (50, 0), (50, 50), (0, 50)])
        self.terrains.append([(70, 300), (70, 500), (80, 500), (80, 300)])
        self.terrains.append([(700, 400), (750, 400), (750, 600), (700, 600)])
        self.terrains.append([(200, 100), (200, 50), (400, 50), (400, 100)])

    def on_draw(self):
        """ Render the screen. """
        # return
        arcade.start_render()  # Clear screen
        if not self.draw:
            return
        
        self.car.draw()
        for o in self.terrains:
            arcade.draw_polygon_filled(o, arcade.color.BLUE)

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """


        # Run dqn here
        self.car.run_radars(self.terrains)
        self.car.check_collides(self.terrains)
        # get current state
        car_state = self.car.get_state()
        agent_state = [car_state['distance'], car_state['speed'],
                       car_state['acc']] + car_state['bips']
        agent_state = np.reshape(agent_state, [1, 8])

        # get action to do
        action = self.agent.act(agent_state)

        self.do_action(action)

        # execute action
        # throttle
        throttle = 0
        if self.up_pressed:
            throttle = 1
        elif self.down_pressed:
            throttle = -1
        # turn
        turn = 0
        if self.right_pressed:
            turn = 1
        elif self.left_pressed:
            turn = -1

        self.car.turn(turn)
        self.car.throttle(throttle)
        self.car.update()

        # get next state
        self.car.run_radars(self.terrains)
        self.car.check_collides(self.terrains)

        next_car_state = self.car.get_state()
        next_agent_state = [next_car_state['distance'], next_car_state['speed'],
                            next_car_state['acc']] + next_car_state['bips']
        done = next_car_state['collides']
        reward = self.compute_reward(next_agent_state, done)
        next_agent_state = np.reshape(next_agent_state, [1, 8])
        print("--- STEP" , self.steps, ' -- radars : ' , self.car.bips, ' -- reward :', reward)
        # remember
        self.agent.remember(agent_state, action, reward,
                            next_agent_state, done)

        if done:
            # restart game
            print("--- RESTART --------------------------------")
            self.games += 1
            self.setup()
        if self.steps > 20 and self.steps % 5 == 0:
            self.agent.replay(20)
        self.steps += 1

    def compute_reward(self, agent_state, done):
        if done:
            return -10000
        else:
            return agent_state[1] * 5 # distance and speed

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.D:
            self.draw = not self.draw
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def do_action(self, action):
        self.up_pressed = action == 0
        self.right_pressed = action == 1
        self.down_pressed = action == 2
        self.left_pressed = action == 3


class DQNAgent():
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=3000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1  # exploration rate
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = keras.Sequential()
        model.add(keras.layers.Dense(10, input_dim=self.state_size, activation='relu'))
        model.add(keras.layers.Dense(10, activation='relu'))
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
        print(self.epsilon)
        if np.random.rand() <= self.epsilon:
            print("explore")
            return random.randrange(self.action_size)
        print("not explore")
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * \
                    np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1,
                           verbose=0, callbacks=[cp_callback])
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


if __name__ == "__main__":
    agent = DQNAgent(8, 4)
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, agent=agent)
    game.setup()
    arcade.run()
