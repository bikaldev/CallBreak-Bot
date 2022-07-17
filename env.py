import copy
import random
import copy
import numpy as np
from pprint import pprint

from utility import create_vector, card_eval
from fixed_bot import FixedBot


class CallBreakEnv:
    def __init__(self):
        suit = ['S','H','C','D']
        self.all_cards = []
        for i in range(4):
            for j in range(1,10):
                self.all_cards.append(str(j) + suit[i])
            self.all_cards.append('T' + suit[i])
            self.all_cards.append('J' + suit[i])
            self.all_cards.append('Q' + suit[i])
            self.all_cards.append('K' + suit[i])
        
        self.initialize_players(['Train-Bot','bot1','bot2','bot3'])

    def cards_check(self,cards):
        face_check = False
        spade_check = False
        for card in cards:
            if(card[0] == 'K' or card[0] == 'Q' or card[0] == 'J' or card[0] == 'A'):
                face_check = True
            elif(not face_check):
                face_check = False
            if(card[1] == 'S'):
                spade_check = True
            elif(not spade_check):
                spade_check = False
            if(face_check and spade_check):
                return True
        
        return False

    def shuffle_cards(self):
        card_check = False
        while(not card_check):
            shuffled_cards = copy.deepcopy(self.all_cards)
            random.shuffle(shuffled_cards)
            card_list = []
            for i in range(4):
                card_list.append(shuffled_cards[i*13:(i+1)*13])
            
            card_check = True
            for cards in card_list:
                if(not self.cards_check(cards)):
                    card_check = False
                    break
        
        for i in range(len(card_list)):
            card_list[i] = self.order(card_list[i])

        return card_list

    def initialize_players(self,player_list):
        if(len(player_list) != 4):
            print("Error! Need 4 players!")
            exit()
        self.player_list = player_list
        # self.train_bot = TrainBot()
        self.fixed_bot = FixedBot()
    
    def generate_bid_body(self, player,pl_list,cards,context):
        bid_body = {}
        bid_body["playerId"] = player
        bid_body["playerIds"] = pl_list
        bid_body["cards"] = cards
        bid_body["context"] = {}
        bid_body["context"]["players"] = {}
        for player in pl_list:
            bid_body["context"]["players"][player] = {
                "bid": context["players"][player]["bid"] if player in context else 0,
                "won": 0
            }
        return bid_body
    
    def generate_play_body(self, player, pl_list, cards, played_cards, history,trick):
        play_body = {}
        play_body["playerId"] = player
        play_body["playerIds"] = pl_list
        play_body["cards"] = cards
        play_body["played"] = played_cards
        play_body["history"] = history
        play_body["context"] = {}
        play_body["context"]["trick"] = trick
        
        return play_body

    def order(self,cards):
        card_list = [[],[],[],[]]
        for card in cards:
            if(card[1] == 'S'):
                card_list[0].append(card)
            if(card[1] == 'H'):
                card_list[1].append(card)
            if(card[1] == 'C'):
                card_list[2].append(card)
            if(card[1] == 'D'):
                card_list[3].append(card)

        result = []
        for l in card_list:
            result = result + self.sort(l)
        
        return result

    def sort(self,cards):
        for i in range(len(cards) - 1):
            for j in range(len(cards) - 1):
                if(card_eval(cards[j]) < card_eval(cards[j+1])):
                    temp = cards[j]
                    cards[j] = cards[j+1]
                    cards[j+1] = temp

        return cards


    def give_winner(self,starts, played_cards):
        max_val = -10
        i = starts
        ends = -1
        current_suit = played_cards[0][1]
        for card in played_cards:
            current_val = card_eval(card)
            if(max_val < current_val and (card[1] == current_suit or card[1] == 'S')):
                max_val = current_val
                ends = i
            i = (i+1) % 4
        
        return ends

    def gen_state_vector(self, body):
      rem_cards = copy.deepcopy(self.all_cards)

      list_of_cards = body["cards"]
      played_cards = body["played"]

      if(len(body["history"]) != 0):
          flag = -1
          for h_l in body['history']:
              _, card_list,_ = h_l
              for card in card_list:
                  card_vec = create_vector([card])
                  if(flag == -1):
                      history_vector = card_vec
                      flag = 1
                  else:
                      history_vector = np.concatenate([history_vector,card_vec])

          h_len = history_vector.shape[0]
          if(h_len < 2496):
              padding = np.zeros((2496-h_len,1))
              history_vector = np.concatenate([history_vector,padding])
      else:
          history_vector = np.zeros((2496,1))
      # no of played cards
      no_of_played = len(played_cards)

      # deduce the cards remaining at the hands of other players
      for data in body["history"]:
          for card in data[1]:
              if(card in rem_cards):
                  rem_cards.remove(card)


      if(no_of_played != 0):
          for card in played_cards:
              rem_cards.remove(card)
      
      for card in list_of_cards:
          rem_cards.remove(card)

      suit_list = ['S','H','C','D']
      suit_vector = np.zeros((4,1))
      if(no_of_played != 0):
          suit = played_cards[0][1]
          index = suit_list.index(suit)
          suit_vector[index] = 1

      list_of_cards_vector = create_vector(list_of_cards)
      played_cards_vector = create_vector(played_cards)
      rem_cards_vector = create_vector(rem_cards)
      play_round_vector = np.zeros((13,1)) 
      play_round_vector[13 - len(list_of_cards)] = 1
      no_of_played_vector = np.array([[no_of_played]])

      return np.concatenate([list_of_cards_vector,played_cards_vector, rem_cards_vector,play_round_vector,no_of_played_vector,suit_vector,history_vector])


    def reset(self):
      pl_list = copy.deepcopy(self.player_list)
      random.shuffle(pl_list)

      card_list = self.shuffle_cards()

      context = {"players":{}}
      #Bidding Phase
      i = 0
      for player in pl_list:
          context["players"][player] = {}
          if(player != "Train-Bot"):
              # pprint(self.generate_bid_body(player,pl_list,card_list[i],context))
              bid = random.randint(1,8)
              # bid = self.fixed_bot.bid(self.generate_bid_body(player,pl_list,card_list[i],context))
          else:
              bid = random.randint(1,8)
              # bid = self.train_bot.bid(self.generate_bid_body(player,pl_list,card_list[i],context))
          
          context["players"][player]["bid"] = bid
          context["players"][player]["won"] = 0
          i += 1
      
      history = []
      starts = 0
      Episode = []

      played_cards = []

      turn = starts
      for i in range(4):
          self.game_state = (starts,pl_list, context, history, played_cards, card_list, 1)
          play_body = self.generate_play_body(pl_list[turn],pl_list,card_list[turn],played_cards,history,1)
          if(pl_list[turn] == 'Train-Bot'):
              return self.gen_state_vector(play_body), play_body
      
          else:
              play_card = self.fixed_bot.play(play_body)
      
          played_cards.append(play_card)
          card_list[turn].remove(play_card)
          turn = (turn + 1) % 4
          

    def step(self,action):

      # Finishing the old trick
      starts, pl_list, context, history ,played_cards, card_list, trick = self.game_state

      turn = pl_list.index('Train-Bot')
      played_cards.append(card_list[turn][action])
      card_list[turn].remove(card_list[turn][action])

      for i in range(4-len(played_cards)):
          turn = (turn + 1) % 4
          play_body = self.generate_play_body(pl_list[turn],pl_list,card_list[turn],played_cards,history,trick)
          play_card = self.fixed_bot.play(play_body)
          played_cards.append(play_card)
          card_list[turn].remove(play_card)


      ends = self.give_winner(starts,played_cards)
      context["players"][pl_list[ends]]["won"] += 1
      trick += 1
      
      history.append([starts, played_cards, ends])

      if(pl_list[ends] == 'Train-Bot'):
          reward = 1
      else:
          reward = 0
      
      starts = ends

      #New trick begins

      if(trick == 13):
        done = True
      else:
        done = False

      played_cards = []
      turn = starts
      for i in range(4):
          play_body = self.generate_play_body(pl_list[turn],pl_list,card_list[turn],played_cards,history,trick)
          self.game_state = (starts,pl_list, context, history, played_cards, card_list, trick)
          if(pl_list[turn] == 'Train-Bot'):
              if(not done):
                  return self.gen_state_vector(play_body), reward, done, play_body
              else:
                  new_state = self.gen_state_vector(play_body)
                  new_body = copy.deepcopy(play_body)
                  play_card = card_list[turn][0] 
          else:
              play_card = self.fixed_bot.play(play_body)
      
          played_cards.append(play_card)
          card_list[turn].remove(play_card)

          turn = (turn + 1) % 4
        
      ends = self.give_winner(starts,played_cards)
      if(pl_list[ends] == 'Train-Bot'):
          reward += 1

      return new_state, reward, done, new_body