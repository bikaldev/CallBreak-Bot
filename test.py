import numpy as np

def valid_action_space(body):
  playable_list = []
  isFace = True
  isSpade = False
  isNone = False

  list_of_cards = body['cards']
  suit = body['played'][0][1] if len(body['played']) > 0 else 'N'

  for card in list_of_cards:
      if(card[1] == suit):
          playable_list.append(list_of_cards.index(card))
  
  if(len(playable_list) == 0):
      isFace = False
      isSpade = True
  
      for card in list_of_cards:
          if(card[1] == 'S'):
              playable_list.append(list_of_cards.index(card))
  
      if(len(playable_list) == 0):
          isSpade = False
          isNone = True

          playable_list = list(np.arange(len(list_of_cards)))
  
  # if(len(playable_list) == 0):
    # print(body)

  return playable_list


x = {'cards': ['JS', '6S', '3S', '1H', 'QH', '3H', '2H', '9D', '5D', '4D', '2D'],
 'context': {'trick': 3},
 'history': [[0, ['1C', '2C', 'QS', '3C'], 2],
             [2, ['TS', '2S', 'KS', '1S'], 1]],
 'played': ['KD'],
 'playerId': 'Train-Bot',
 'playerIds': ['bot2', 'bot3', 'Train-Bot', 'bot1']}

print(valid_action_space(x))