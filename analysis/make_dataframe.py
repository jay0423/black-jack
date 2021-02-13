"""
black_jack.pyから，データを取得してデータフレームを作成する．
self.GAME_TIME：ブラックジャックのプレイ回数．

Get started
    > import analysis_black_jack as abj
    > a = abj.MakeDataFrame(GAME_TIME=1000000, DECK=5, RESET=False, MAX_PLAY_COUNTS=5)
    > df = a.main()
    after finished
    > b = abj.AnalysisDf(df)
    > _ = b.~~~
"""

import pandas as pd
import numpy as np
from tqdm import tqdm

import sys
import os
sys.path.append(os.path.abspath(".."))
import black_jack as bj

class MakeDataFrame:
    """
    指定された回数だけブラックジャックをプレイし，DataFrameを作成する．
    """

    def __init__(self, GAME_TIME=100000, DECK=6, RESET=False, MAX_PLAY_COUNTS=5):
        self.DECK = DECK
        self.a = bj.MakeBlackJack(DECK, RESET=RESET)
        self.GAME_TIME = GAME_TIME
        self.RESET = RESET
        self.MAX_PLAY_COUNTS = MAX_PLAY_COUNTS
        #初期化
        self.player_card = []
        self.dealer_card = []
        self.player_score = []
        self.dealer_score = []
        self.player_WL = []
        self.bet_chip = []
        self.play_counts = []
        self.get_coin = []
        self.first_PC = []
        self.first_DC = []

    def get_game(self):
        (player_card, dealer_card, player_score, dealer_score, player_WL, bet_chip, play_counts, get_coin, first_PC, first_DC) = self.a.main()
        self.player_card.append(player_card)
        self.dealer_card.append(dealer_card)
        self.player_score.append(player_score)
        self.dealer_score.append(dealer_score)
        self.player_WL.append(player_WL)
        self.bet_chip.append(bet_chip)
        self.play_counts.append(play_counts)
        self.get_coin.append(get_coin)
        self.first_PC.append(first_PC)
        self.first_DC.append(first_DC)

    def make_df(self, dicts):
        return pd.DataFrame(dicts)

    def edit_df(self, df):
        #スプリットした回数を追加
        df["split"] = df["player_card"].map(len) - 1
        return df

    def play_black_jack(self):
        for i in tqdm(range(self.GAME_TIME)):
            if self.RESET:
                if self.MAX_PLAY_COUNTS == self.a.play_counts:
                    self.a.play_counts = 0
            self.get_game()
        dicts = {
            "player_card": self.player_card,
            "dealer_card": self.dealer_card,
            "player_score": self.player_score,
            "dealer_score": self.dealer_score,
            "player_WL": self.player_WL,
            "bet_chip": self.bet_chip,
            "play_counts": self.play_counts,
            "get_coin": self.get_coin,
            "first_PC": self.first_PC,
            "first_DC": self.first_DC,
        }
        return self.make_df(dicts)

    def main(self):
        self.a.setup()
        df = self.play_black_jack()
        print("DataFrameを作成")
        df = self.edit_df(df)
        return df
        

class MakeDataFrameCardCustomized(MakeDataFrame):
    """
    black_jack.pyのMakeBlackJackCardCustomizedクラスから，データを取得してデータフレームを作成する．
    カード初期値をカスタマイズできる．
    ベーシックストラテジーのカラム及び指定された回数だけブラックジャックをプレイし，DataFrameを作成する．
    """

    basic_strategy = pd.DataFrame()
    columns = []
    index = []

    dealer_open_card = ""
    player_card_first = []
    
    def import_basic_strategy(self):
        basic_strategy = pd.read_csv('../csv/basic_strategy.csv')
        basic_strategy.index = basic_strategy.PC
        self.basic_strategy = basic_strategy.drop('PC', axis=1)
        self.columns = list(self.basic_strategy.columns)
        self.index = list(self.basic_strategy.index)

    def get_dealer_open_card(self, DC_i):
        DC = self.columns[DC_i]
        if DC != "1":
            dealer_open_card = str(DC) + "♠"
        else:
            dealer_open_card = "A♠"
        return dealer_open_card
    
    def sum_card_two(self, sum_n):
        while True:
            if sum_n >= 12:
                c1 = np.random.randint(21-sum_n) + sum_n - 10
                c2 = sum_n - c1
            else:
                c1 = np.random.randint(sum_n - 3) + 2
                c2 = sum_n - c1
            if c1 != c2:
                break
        return str(c1), str(c2)

    def get_player_card_first(self, PC_i):
        """
        PC_iをもとに，プレイヤーの最初のカードを選択する．
        """
        PC = self.index[PC_i]
        if PC == ":8":
            PC2 = np.random.choice([5,6,7,8])
            c1, c2 = self.sum_card_two(PC2)
            player_card_first = [c1+"♠", c2+"♥"]
        elif PC == "17:":
            player_card_first = ["K♠", "7♠"]
        elif PC[0] == "A" and PC[-1] != "A": #"A~"
            player_card_first = ["A♠", PC[1:]+"♠"]
        elif PC[0] == PC[-1] and PC != "11" and PC != "9": #スプリット（11を見分けている，9のバグ回避）
            player_card_first = [PC[0]+"♠", PC[0]+"♥"]
        elif PC == "1010":
            player_card_first = ["10♠", "J♠"]
        else: #数字単体
            c1, c2 = self.sum_card_two(int(PC))
            player_card_first = [c1+"♠", c2+"♥"]
        return player_card_first

    def get_game(self):
        (player_card, dealer_card, player_score, dealer_score, player_WL, bet_chip, play_counts, get_coin, first_PC, first_DC) = self.a.main(dealer_open_card=self.dealer_open_card, player_card_first=self.player_card_first)
        self.player_card.append(player_card)
        self.dealer_card.append(dealer_card)
        self.player_score.append(player_score)
        self.dealer_score.append(dealer_score)
        self.player_WL.append(player_WL)
        self.bet_chip.append(bet_chip)
        self.play_counts.append(play_counts)
        self.get_coin.append(get_coin)
        self.first_PC.append(first_PC)
        self.first_DC.append(first_DC)

    def play_black_jack(self):
        for i in tqdm(range(self.GAME_TIME)):
            for j in range(10):
                self.dealer_open_card = self.get_dealer_open_card(j)
                for k in range(29):
                    self.player_card_first = self.get_player_card_first(k)
                    if self.RESET:
                        if self.MAX_PLAY_COUNTS == self.a.play_counts:
                            self.a.play_counts = 0
                    self.get_game()
        dicts = {
            "player_card": self.player_card,
            "dealer_card": self.dealer_card,
            "player_score": self.player_score,
            "dealer_score": self.dealer_score,
            "player_WL": self.player_WL,
            "bet_chip": self.bet_chip,
            "play_counts": self.play_counts,
            "get_coin": self.get_coin,
            "first_PC": self.first_PC,
            "first_DC": self.first_DC,
        }
        return self.make_df(dicts)

    def main(self):
        self.a = bj.MakeBlackJackCardCustomized(self.DECK)
        self.a.setup()
        self.import_basic_strategy()
        df = self.play_black_jack()
        print("DataFrameを作成")
        df = self.edit_df(df)
        return df



class MakeDataFrameActionCustomized(MakeDataFrameCardCustomized):
    """
    black_jack.pyのMakeBlackJackCardCustomizedクラスから，データを取得してデータフレームを作成する．
    カード初期値，プレイヤーのファーストアクションを指定することができる．
    ベーシックストラテジーのカラム及び指定された回数だけブラックジャックをプレイし，DataFrameを作成する．
    """

    first_P_action = ""

    def __init__(self, GAME_TIME=100000, DECK=6, RESET=False, MAX_PLAY_COUNTS=5):
        self.DECK = DECK
        self.a = bj.MakeBlackJack(DECK, RESET=RESET)
        self.GAME_TIME = GAME_TIME
        self.RESET = RESET
        self.MAX_PLAY_COUNTS = MAX_PLAY_COUNTS
        #初期化
        self.player_card = []
        self.dealer_card = []
        self.player_score = []
        self.dealer_score = []
        self.player_WL = []
        self.bet_chip = []
        self.play_counts = []
        self.get_coin = []
        self.first_PC = []
        self.first_DC = []
        #追加
        self.first_P_action = []
        
    # def get_first_P_action(self):
    #     self.first_P_action = "H"

    def get_game(self, action):
        (player_card, dealer_card, player_score, dealer_score, player_WL, bet_chip, play_counts, get_coin, first_PC, first_DC, first_P_action) = self.a.main(dealer_open_card=self.dealer_open_card, player_card_first=self.player_card_first, first_P_action=action)
        self.player_card.append(player_card)
        self.dealer_card.append(dealer_card)
        self.player_score.append(player_score)
        self.dealer_score.append(dealer_score)
        self.player_WL.append(player_WL)
        self.bet_chip.append(bet_chip)
        self.play_counts.append(play_counts)
        self.get_coin.append(get_coin)
        self.first_PC.append(first_PC)
        self.first_DC.append(first_DC)
        self.first_P_action.append(first_P_action)

    def play_black_jack(self):
        for action in ["H", "S", "D", "P"]:
            for i in tqdm(range(self.GAME_TIME)):
                for j in range(10):
                    self.dealer_open_card = self.get_dealer_open_card(j)
                    for k in range(29):
                        if action != "P": #スプリットの回避
                            self.player_card_first = self.get_player_card_first(k)
                            if self.RESET:
                                if self.MAX_PLAY_COUNTS == self.a.play_counts:
                                    self.a.play_counts = 0
                            self.get_game(action)
                        else:
                            if k >= 19:
                                self.player_card_first = self.get_player_card_first(k)
                                if self.RESET:
                                    if self.MAX_PLAY_COUNTS == self.a.play_counts:
                                        self.a.play_counts = 0
                                self.get_game(action)
                                
        dicts = {
            "player_card": self.player_card,
            "dealer_card": self.dealer_card,
            "player_score": self.player_score,
            "dealer_score": self.dealer_score,
            "player_WL": self.player_WL,
            "bet_chip": self.bet_chip,
            "play_counts": self.play_counts,
            "get_coin": self.get_coin,
            "first_PC": self.first_PC,
            "first_DC": self.first_DC,
            "first_P_action": self.first_P_action,
        }
        return self.make_df(dicts)
    
    def main(self):
        self.a = bj.MakeBlackJackActionCustomized(self.DECK)
        self.a.setup()
        self.import_basic_strategy()
        # self.get_first_P_action()
        df = self.play_black_jack()
        print("DataFrameを作成")
        df = self.edit_df(df)
        return df, self.basic_strategy
