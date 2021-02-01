import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class MakeBlackJack:

    card_list_index = []
    basic_strategy = pd.DataFrame()
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

    


