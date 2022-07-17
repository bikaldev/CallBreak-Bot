import numpy as np
from tensorflow import keras
from collections import deque
import random

from env import CallBreakEnv

from utility import pick_action, valid_action_space


np.random.seed(10)
random.seed(10)

def create_model(state_length, action_length):

      initializer = keras.initializers.HeUniform()
      model = keras.Sequential([
                               keras.layers.Flatten(input_shape = (state_length,1)),
                               keras.layers.Dense(256, activation = 'relu', kernel_initializer=initializer),
                               keras.layers.Dense(256, activation = 'relu', kernel_initializer=initializer),
                               keras.layers.Dense(52, activation = 'relu', kernel_initializer=initializer),
                               keras.layers.Dense(action_length, activation = 'linear', kernel_initializer=initializer)
                               
      ])

      model.compile(loss = keras.losses.Huber(), optimizer = keras.optimizers.Adam(learning_rate = 0.00001), metrics = ['accuracy'])
      # model.load_weights('weights.h5')
      return model





def train(replay_buffer, model, target_model, GAMMA, BATCH_SIZE):
  
    mini_batch = random.sample(replay_buffer, BATCH_SIZE)
    current_states = np.array([transition[0] for transition in mini_batch])
    current_qs_list = model.predict(current_states, verbose = 0)
    new_current_states = np.array([transition[3] for transition in mini_batch])
    future_qs_list = target_model.predict(new_current_states, verbose = 0)


    X = []
    Y = []
    for index, (observation, action, reward, new_observation, action_space) in enumerate(mini_batch):
        # if not done:
        while(1):
          max_next_q = np.max(future_qs_list[index])
          max_next_action = np.argmax(future_qs_list[index])
          if(max_next_action not in action_space):
              future_qs_list[index][max_next_action] = -np.inf
          else:
            break
        if(np.squeeze(new_observation[168]) == 1):
          max_future_q = reward
        else:
          max_future_q = reward + GAMMA * max_next_q

        current_qs = current_qs_list[index]
        current_qs[action] = max_future_q

        X.append(observation)
        Y.append(current_qs)
    model.fit(np.array(X), np.array(Y), verbose=0, shuffle=True)

    return model

LEARNING_RATE = 0.081
MIN_BUFFER_SIZE = 1000
MAX_BUFFER_SIZE = 2000
BATCH_SIZE = 512
GAMMA = 0.999999

EPSILON = 0.99
EPSILON_DECAY_RATE = 0.0001
MAX_EPSILON = 0.99
MIN_EPSILON = 0.01

NUM_OF_EPISODES = 1000000

env = CallBreakEnv()

state_length = 2670
action_length = 13

#main model
model = create_model(state_length, action_length)
#target model
target_model = create_model(state_length,action_length)

replay_buffer = deque(maxlen = MAX_BUFFER_SIZE)

epsilon = EPSILON

sum_reward = 0.0
reward_list = []

for episode in range(NUM_OF_EPISODES):
    state, body = env.reset()
    done = False
    while(not done):
      action = pick_action(state, body, epsilon, model)
      next_state, reward, done, body = env.step(action)
      
      action_space = valid_action_space(body)
      replay_buffer.append((state, action, reward, next_state, action_space))
      sum_reward += reward
      
    
    # break
    if len(replay_buffer) >= MIN_BUFFER_SIZE:  
      model = train(replay_buffer, model, target_model, GAMMA, BATCH_SIZE)
      target_model.set_weights(model.get_weights())


    if(episode % 100 == 0):
      print('Training Episode: ',episode, " current reward avg: ",sum_reward/100)
      reward_list.append(sum_reward/100)
      sum_reward = 0.0
      # make the target model the same as working model
      model.save_weights('weights.h5')
    
    epsilon = MIN_EPSILON + (MAX_EPSILON - MIN_EPSILON) * np.exp(-EPSILON_DECAY_RATE * episode)


model.save_weights('weights.h5')

import matplotlib.pyplot as plt


plt.plot(reward_list)
plt.ylabel('average reward')
plt.xlabel('episodes (100\'s)')
plt.show()