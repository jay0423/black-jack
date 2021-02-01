import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class MakeBlackJack:

    card_list_index = [] #デッキのカードリスト
    basic_strategy = pd.DataFrame() #ベーシックストラテジーの表

    dealer_card = [] #ディーラーのカード
    player_card = [] #プレイヤーのカード

    player_score = [0] #プレイヤーのスコア

    chip_list = []
    chip_over = 0

    def __init__(self):
        self.first_chip = 20

    def import_cards(self):
        #AからKのカードのリストをインポート
        card_list = pd.read_csv('playing_card.csv')
        card_list.index = card_list.card_num
        card_list.drop('card_num', axis=1, inplace=True)
        for i in range(deck):
            self.card_list_index += list(card_list.index)
    
    def import_basic_strategy(self):
        #ベーシックストラテジーの表をcsvファイルからインポート
        self.basic_strategy = pd.read_csv('BlackJack_table{}.csv'.format(table_choice))
        self.basic_strategy.index = self.basic_strategy.PC
        self.basic_strategy.drop('PC', axis=1, inplace=True)

    def shuffle_card(self, card):
        #カードデッキをシャッフルする
        return np.random.shuffle(card)

    def get_dealer_card(self):
        #ディーラーがカードを引く
        self.dealer_card = [card_list_index[0], card_list_index[2]]
        del self.card_list_index[:2] #引いた分のカードを削除

    def get_player_card(self):
        #プレイヤーがカードを引く
        self.player_card = [[card_list_index[0], card_list_index[2]]]
        del self.card_list_index[:2] #引いた分のカードを削除
    
    def check_natural_black_jack(self):
        #ディーラーのナチュラルブラックジャック確認
        dealer_score_start = 0
        for i in range(2):
            dealer_score_start += int(card_list.loc[self.dealer_card[i]].num)
        if dealer_score_start == 11 and 'A' in str(self.dealer_card):
            self.basic_strategy.replace(['H', 'D', 'P'], 'S', inplace=True)




    

    def main(self):
        #前処理
        self.import_cards()
        self.import_basic_strategy()
        self.shuffle_card()
        self.get_dealer_card()
        self.get_player_card()
        
