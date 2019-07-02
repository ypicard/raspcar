import gym
from collections import deque
import numpy as np
import tensorflow as tf
from tensorflow import keras
import random
import matplotlib.pyplot as plt


class DQNAgent():
    def __init__(self, state_size, action_size, gamma=0.95, epsilon=1):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = gamma  # discount rate
        self.epsilon = epsilon  # exploration rate
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995
        self.learning_rate = 0.1
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = keras.Sequential()
        model.add(keras.layers.Dense(
            10, input_dim=self.state_size, activation='relu'))
        model.add(keras.layers.Dense(6, activation='relu'))
        model.add(keras.layers.Dense(self.action_size, activation='linear'))
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
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * \
                    np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            target_f[0][action] = target
            history = self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        return history


if __name__ == "__main__":   

    env = gym.make('CartPole-v1')
    env.max_episode_steps = 500
    state_size =  env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = DQNAgent(state_size, action_size)
    episodes = 200
    batch_size = 32
    history = {'scores': []}

    for episode in range(episodes):
        state = env.reset()
        state = np.reshape(state, [1, state_size])

        for step in range(500):
            # env.render()
            action = agent.act(state)
            next_state, reward, done, info = env.step(action)
            reward = reward if not done else -50
            next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)
            state = next_state

            if done:
                history['scores'].append(step)
                print(f"episode: {episode}/{episodes}, score: {step}")
                break
            if len(agent.memory) > 1800 and len(agent.memory) > batch_size:
                agent.replay(batch_size)

    fig, ax = plt.subplots(nrows=2, ncols=2)
    ax[0, 0].plot(history['scores'], label='scores')
    plt.legend()
    plt.show()

    env.close()
