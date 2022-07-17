from math import floor
import json
import copy

from utility import bidStateCalc,arrange_by_cardinality, card_eval, weak_cardinality, get_max_card, get_min_card, find_playable_list

class FixedBot:

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

        with open('bidValue.json','r') as fp:
            self.bidValue = json.load(fp)

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

    def play(self,body):
        state = ''
        rem_cards = copy.deepcopy(self.all_cards)

        list_of_cards = body["cards"]
        played_cards = body["played"]

        # no of played cards
        no_of_played = len(played_cards)

        spent_list = {'S':[],'H':[],'C':[],'D':[]} # list of spade,heart,club,diamond suit list of players with corresponding suit empty

        #removing cards present in history
        current_starter = 0
        for data in body["history"]:

            started = data[0]
            current_suit = data[1][0][1]
            current_starter = data[2]
            for card in data[1]:
                if(card[1] != current_suit and card[1] != 'S'):
                    spent_list['S'].append(started)
                elif(card[1] != current_suit):
                    spent_list[current_suit].append(started)
                started = (started + 1) % 4
                try:
                    rem_cards.remove(card)
                except:
                    continue
        
        rem_to_play = []
        # determine who are the remaining to play if any
        if(no_of_played != 3 and len(body["history"]) != 0):
            turn = current_starter
            for card in played_cards:
                turn = (turn + 1) % 4

            for i in range(3-no_of_played):
                turn = (turn + 1) % 4
                rem_to_play.append(turn)


        for card in list_of_cards:
            try:
                rem_cards.remove(card)
            except:
                continue
        
        if(no_of_played == 0):
            state = '1st Play'

            spade_list = ['S']
            heart_list = ['H']
            club_list = ['C']
            diamond_list = ['D']
            for card in rem_cards:
                if(card[1] == 'S'):
                    spade_list.append(card)
                elif(card[1] == 'H'):
                    heart_list.append(card)
                elif(card[1] == 'C'):
                    club_list.append(card)
                else:
                    diamond_list.append(card)
            
            max_rem_spade = get_max_card(spade_list)
            max_rem_heart = get_max_card(heart_list)
            max_rem_club = get_max_card(club_list)
            max_rem_diamond = get_max_card(diamond_list)

            max_spade = ''
            max_heart = ''
            max_diamond = ''
            max_club = ''
            for card in list_of_cards:
                    if(max_rem_spade != '' and card_eval(card) > card_eval(max_rem_spade) and card[1] == 'S'):
                        max_spade = card
                    if(max_rem_heart != '' and card_eval(card) > card_eval(max_rem_heart) and card[1] == 'H'):
                        max_heart = card
                    if(max_rem_club != '' and card_eval(card) > card_eval(max_rem_club) and card[1] == 'C'):
                        max_club = card
                    if(max_rem_diamond != '' and card_eval(card) > card_eval(max_rem_diamond) and card[1] == 'D'):
                        max_diamond = card

            
            if(max_spade == '' and max_heart == '' and max_club == '' and max_diamond == ''):
                state += '-without any card that can beat rem cards'
                #choose the weakest card from the card face(except spade) with least cardinality
                weak_card = weak_cardinality(list_of_cards)
                min_card = get_min_card(list_of_cards)
                if(card_eval(weak_card) > 8):
                    state += '-with least cardinality card > 8'
                    play_card = min_card
                else:
                    state += '-with least cardinality card < 8'
                    play_card = weak_card
            else:
                state += '-with cards that can beat rem cards'
                if(not max_heart == '' or not max_club == '' or not max_diamond == ''):
                    state += '-with beating card other than spade'
                    list_of_options = [heart_list, club_list, diamond_list]
                    list_of_options = arrange_by_cardinality(list_of_options)
                    for list_option in list_of_options:
                        if(list_option[0] == 'H' and not max_heart == ''):
                            for player in rem_to_play:
                                if(player in spent_list['H'] and player not in spent_list['S']):
                                    continue
                            play_card = max_heart
                            break
                        if(list_option[0] == 'C' and not max_club == ''):
                            for player in rem_to_play:
                                if(player in spent_list['C'] and player not in spent_list['S']):
                                    continue
                            play_card = max_club
                            break
                        if(list_option[0] == 'D' and not max_diamond == ''):
                            for player in rem_to_play:
                                if(player in spent_list['D'] and player not in spent_list['S']):
                                    continue
                            play_card = max_diamond
                            break
                else:
                    state += '-with beating card spade'
                    play_card = max_spade

                if play_card == '':
                    state += '-but spent list not empty'
                    weak_card = weak_cardinality(list_of_cards)
                    min_card = get_min_card(list_of_cards)
                    if(card_eval(weak_card) > 8):
                        play_card = min_card
                    else:
                        play_card = weak_card


        else:
            state = 'Not 1st play'
            for card in played_cards:
                try:
                    rem_cards.remove(card)
                except:
                    continue
            
            dealt_type = played_cards[0][1]
            playable_list, isFace, isSpade, isNone = find_playable_list(list_of_cards,dealt_type)
            max_played_card = get_max_card(played_cards,face_check=True, face = dealt_type)

            if(isFace):
                state += '-isFace'
                barely_beat_card = ''
                for card in playable_list:
                    if(card_eval(card) > card_eval(max_played_card)):
                        barely_beat_card = card

                if(barely_beat_card == ''):
                    state += '-no barely beating card available'
                    play_card = get_min_card(playable_list)
                else:
                    state += '-barely beating card available'
                    if(len(played_cards) == 3):
                        state += '-last play'
                        play_card = barely_beat_card
                    else:
                        state += '-not last play'
                        canBeatBarely = False
                        canBeatMax = False
                        max_playable_card = get_max_card(playable_list)
                        for card in rem_cards:
                            if(card_eval(card) > card_eval(max_playable_card) and card[1] == dealt_type):
                                canBeatBarely = True
                                canBeatMax = True
                                break

                            if(card_eval(card) > card_eval(barely_beat_card) and card[1] == dealt_type):
                                canBeatBarely = True

                        if(canBeatMax and canBeatBarely):
                            state += '-rem card can beat max card as well as barely beating card'
                            play_card = barely_beat_card
                        elif(not canBeatMax and canBeatBarely):
                            state += '-rem card can beat barely but not max'
                            if(len(rem_to_play) == 0):
                                max_rem_card = get_max_card(rem_cards,True,dealt_type,False)
                                for card in playable_list:
                                    if(card_eval(max_rem_card) < card_eval(card)):
                                        play_card = card
                                # play_card = max_playable_card
                            else:
                                for player in rem_to_play:
                                    if(player in spent_list[dealt_type] and player not in spent_list['S']):
                                        play_card = barely_beat_card
                                        break
                                    else:
                                        play_card = max_playable_card
                        else:
                            state += '-rem card cannot beat barely'
                            play_card = barely_beat_card
                
            if(isSpade):
                state += '-isSpade'
                min_spade_card = get_min_card(playable_list)
                if(card_eval(min_spade_card) > card_eval(max_played_card)):
                    state += '-min spade card can beat max played card'
                    play_card = min_spade_card
                else:
                    state += '-min spade card cannot beat max played card'
                    spade_beating_card = ''
                    for card in playable_list:
                        if(card_eval(card) > card_eval(max_played_card)):
                            spade_beating_card = card

                    if(spade_beating_card == ''):
                        state += '-no spade card that can beat max played card'
                        playable_list = []
                        for card in list_of_cards:
                            if(card[1] != 'S'):
                                playable_list.append(card)
                        if(len(playable_list) == 0):
                            play_card = min_spade_card
                        else:
                            isNone = True 
                    else:
                        state += '-there exists a spade card that can beat the max played card'
                        spade_threat = False
                        play_card = spade_beating_card
                        for player in rem_to_play:
                            if(player in spent_list[dealt_type] and player not in spent_list['S']):
                                spade_threat = True
                                break
                        
                        if(spade_threat):
                            max_spade_rem = get_max_card(rem_cards, True, 'S',False)
                            if(max_spade_rem == ''):
                                play_card = spade_beating_card
                            else:
                                if(card_eval(spade_beating_card) > card_eval(max_spade_rem)):
                                    play_card = spade_beating_card
                                else:
                                    for card in playable_list:
                                        if(card_eval(card) > card_eval(max_spade_rem)):
                                            play_card = card
                                    


            if(isNone):
                state += '-isNone'
                weak_card = weak_cardinality(playable_list)
                min_card = get_min_card(playable_list)

                if(card_eval(weak_card) > 8):
                    state += '-lowest cardinality card > 8'
                    play_card = min_card
                else:
                    state += '-lowest cardinality card < 8'
                    play_card = weak_card
        
        return play_card