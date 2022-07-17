import numpy as np
import keras

def bidStateCalc(cards):
    SW = 0
    FS = 0
    RS = 0
    FN = 0
    RN = 0
    
    for card in cards:
        if(card[0] == '1'):
            SW += 1
        else:
            if(card[1] == "S"):
                if(card[0] == "K" or card[0] == "Q" or card[0] == "J"):
                    FS += 1
                else:
                    RS += 1

            else:
                if(card[0] == "K" or card[0] == "Q" or card[0] == "J"):
                    FN += 1
                else:
                    RN += 1
                
                
    state = str(SW) + '-' + str(FS) + '-'+str(RS)+ '-' + str(FN)+ '-' + str(RN)
    return state


def find_playable_list(list_of_cards, suit):
    playable_list = []
    isFace = True
    isSpade = False
    isNone = False
    for card in list_of_cards:
        if(card[1] == suit):
            playable_list.append(card)
    
    if(len(playable_list) == 0):
        isFace = False
        isSpade = True
    
        for card in list_of_cards:
            if(card[1] == 'S'):
                playable_list.append(card)
    
        if(len(playable_list) == 0):
            isSpade = False
            isNone = True

            playable_list = list_of_cards.copy()

    return (playable_list,isFace,isSpade,isNone)

def weak_cardinality(cards):
    spade = [0,0]
    heart = [0,0]
    club = [0,0]
    diamond = [0,len(cards)-1]
    temp = 'S'
    i = 0
    for card in cards:
        if(card[1] == 'S'):
            spade[0] += 1
        if(card[1] == 'H'):
            heart[0] += 1
            if(temp != 'H'):
                spade[1] = i-1
        if(card[1] == 'D'):
            diamond[0] += 1
            if(temp != 'D'):
                club[1] = i-1
        if(card[1] == 'C'):
            club[0] += 1
            if(temp != 'C'):
                heart[1] = i-1

        temp = card[1]
        i += 1
    if(spade[0] != 0):
        spade[0] = -10
    list_of_list = [spade,heart,club,diamond]
    max_cardinality = -100
    play_card = ''
    for card_list in list_of_list:
        if(card_list[0] > max_cardinality and card_list[0] != 0):
            play_card = cards[card_list[1]]
            max_cardinality = card_list[0]
    
    return play_card

def get_max_card(cards, face_check = False, face = 'H', include_spade = True):
    max_val =  0
    max_card = ""
    for card in cards:
        if(len(card) == 2):
            card_val = card_eval(card)
            if(card_val > max_val and not face_check ):
                max_card = card
                max_val = card_val
            if(card_val > max_val and face_check and (card[1] == face or (card[1] == 'S' and include_spade))):
                max_card = card
                max_val = card_val
    return max_card

def get_min_card(cards):
    min_val = 1000
    min_card = ""
    for card in cards:
        card_val = card_eval(card)
        if(card_val < min_val):
            min_card = card
            min_val = card_val
    return min_card

def card_eval(card):
    if(card[1] == 'S'):
            card_val = 14
    else:
        card_val = 1
    if(card[0] >= '2' and card[0] <= '9'):
        card_val *= int(card[0])
    elif(card[0] == '1'):
        card_val *= 14
    elif(card[0] == 'T'):
        card_val *= 10
    elif(card[0] == 'J'):
        card_val *= 11
    elif(card[0] == 'Q'):
        card_val  *= 12
    else:
        card_val *= 13
    return card_val

def arrange_by_cardinality(cards_list):
    for i in range(2):
        for j in range(2):
            if(len(cards_list[j]) > len(cards_list[j+1])):
                temp = cards_list[j]
                cards_list[j] = cards_list[j+1]
                cards_list[j+1] = temp
    
    return cards_list


def card_to_val(card):
    
    if(card[1] == 'S'):
        mult =  0
    if(card[1] == 'H'):
        mult =  1
    if(card[1] == 'C'):
        mult =  2
    if(card[1] == 'D'):
        mult =  3
    
    if(card[0] == 'K'):
        return mult * 13 + 12
    if(card[0] == 'Q'):
        return mult * 13 + 11
    if(card[0] == 'J'):
        return mult * 13 + 10
    if(card[0] == 'T'):
        return mult * 13 + 9
    
    return mult * 13 + (int(card[0])-1)

def create_vector(cards):
    res = -np.ones((52,1))
    for card in cards:
        res[card_to_val(card)] = 1
    
    return res

def pick_action(state, body, epsilon,model):
    
    action_space = valid_action_space(body)
    if(np.random.uniform() > epsilon):
      # print('picking action')
      state = state.reshape(1,2670,1)
      # print(state.shape)
      result = model.predict(state, verbose = 0).flatten()
      # print(result.shape)
      while(1):
        action = np.argmax(result)
        if(action in action_space):
          return action
        else:
          result[action] = -np.inf
    else:
      return np.random.choice(action_space)  
      
    
def valid_action_space(body):
  playable_list = []
    
  list_of_cards = body['cards']

  if(len(body['played']) == 0):
      return list(np.arange(len(list_of_cards)))

  suit = body['played'][0][1]
  max_played_card = get_max_card(body['played'])

  for card in list_of_cards:
      if(card[1] == suit):
          playable_list.append(card)

  if(len(playable_list) == 0):
      
      for card in list_of_cards:
          if(card[1] == 'S'):
              playable_list.append(card)
      
      if(len(playable_list) == 0):
          return list(np.arange(len(list_of_cards)))
      
      else:
          max_playable_card = get_max_card(playable_list)

          if(card_eval(max_playable_card) > card_eval(max_played_card)):
              new_list = []
              for card in playable_list:
                  if(card_eval(card) > card_eval(max_played_card)):
                      new_list.append(list_of_cards.index(card))
          else:
              new_list = []
              for card in playable_list:
                  new_list.append(list_of_cards.index(card))
  
  else:
      max_playable_card = get_max_card(playable_list)
      if(card_eval(max_playable_card) > card_eval(max_played_card)):
          new_list = []
          for card in playable_list:
              if(card_eval(card) > card_eval(max_played_card)):
                  new_list.append(list_of_cards.index(card))
      else:
          new_list = []
          for card in playable_list:
              new_list.append(list_of_cards.index(card))

  return new_list

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
