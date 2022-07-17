from env import CallBreakEnv
import json
from math import floor

from utility import bidStateCalc, create_model, pick_action

class TrainBot:
    def __init__(self):
        
        with open('bidValue.json','r') as fp:
            self.bidValue = json.load(fp)
        
        self.state_length = 2670
        self.action_length = 13

        self.model = create_model(self.state_length, self.action_length)
        self.env = CallBreakEnv()
        self.model.load_weights('weights.h5')
        
        

    def bid(self,body):
        state = bidStateCalc(body["cards"])
        if(state in self.bidValue):
            avg,freq = self.bidValue[state]
            action = floor(avg)
            if(action <= 0):
                action = 1
            if(action > 8):
                action = 8

        else:
            action = 2
        
        return action
    
    def play(self, body):
        state = self.env.gen_state_vector(body)
        action = pick_action(state, body, 0.0, self.model)
        return action


    