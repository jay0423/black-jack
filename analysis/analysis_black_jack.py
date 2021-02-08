"""
black_jack.pyから，データを取得してデータフレームを作成する．
self.GAME_TIME：ブラックジャックのプレイ回数．

Get started
    > import analysis_black_jack as abj
    > a = abj.MakeDataFrame(GAME_TIME=1000000, DECK=5, RE_PLAY=False, MAX_PLAY_COUNTS=5)
    > df = a.main()
    after finished
    > b = abj.AnalysisDf(df)
    > _ = b.~~~
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
from tqdm import tqdm

import sys
import os
sys.path.append(os.path.abspath(".."))
import black_jack as bj


class MakeDataFrame:

    def __init__(self, GAME_TIME=100000, DECK=6, RE_PLAY=False, MAX_PLAY_COUNTS=5):
        self.a = bj.MakeBlackJack(DECK)
        self.GAME_TIME = GAME_TIME
        self.RE_PLAY = RE_PLAY
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
            if self.RE_PLAY:
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


class WinPercentage:
    """
    MakeDataFrame().main()をもとに作られたDataFrameを用いて，データ分析を行う．
    """

    def __init__(self, df):
        self.df = df
    
    def win_percentage(self, how="cut", split=10, cut_num_list=[], plot=True):
        """
        勝率を返すメソッド．
        引数howがデフォルトのallのとき，ブラックジャック全体の勝率を返す．
        howがcutのとき，複数の要素にカットされたcut_num_listに従い，その要素時点のプレイ回数時の勝率を算出しlistで返す．
        つまり，勝率が回数に応じてどのように移行するのかを見ることができる．
        その際の出力はどこでカットされているかを示す，cut_num_listと，percentageを返す．
        プレイ回数を等分してほしい場合は，cut_num_listに引数を渡さない．
        また，等分数はsplitを与えれば指定できる．デフォルトは10分割となっている．
        plot==Trueのとき，横軸にプレイ回数，縦軸にパーセンテージを出力．
        exp) _,_ = a.win_percentage(split=1000, plot=True)
        """
        if how == "all":
            percentage = round(self.df["get_coin"].sum() / len(self.df), 5) * 100 + 50
            return percentage
        elif how == "cut":
            #dfのget_coin列をスプリット数に等分したcut_num_listを生成．
            if cut_num_list == []: #split数にしたがって等分割
                CUT_NUM = int(len(self.df)/split)
                cut_num_list = [(i+1)*CUT_NUM for i in range(split)]
                cut_num_list.insert(0, 0)
            else:
                if cut_num_list[0] != 0:
                    cut_num_list.insert(0, 0)
                #受け取ったcut_num_listの最後の要素がdfの長さと一致していない場合，後ろにdfの長さを追加．
                if cut_num_list[-1] != len(self.df):
                    cut_num_list.append(len(self.df))
            #各プレイ回数における勝率を算出
            percentage = [0]
            for i in range(len(cut_num_list)-1):
                percentage.append((self.df["get_coin"][:cut_num_list[i+1]].sum()) / cut_num_list[i+1])
            percentage = list(map(lambda x: round(x*100+50, 3), percentage))
            print("{}%".format(percentage[-1]))
            #描画
            if plot:
                fig = plt.figure()# Figureを設定
                ax = fig.add_subplot(111)# Axesを追加
                ax.set_title("Transition of win rate.", fontsize = 16) # Axesのタイトルを設定
                percentage_all = round(percentage[-1], 1)
                max_p = max(np.percentile(percentage, 99.5), percentage_all)
                min_p = min(np.percentile(percentage, 0.5), percentage_all)
                ax.set_ylim(min_p-0.1, max_p+0.1)
                ax.plot(cut_num_list, percentage)
                plt.show()
            return cut_num_list, percentage

    def play_counts_win_percent(self, func="rate", plot=True):
        """
        ディーラと連続で戦う場合に勝率が変化するのかを分析する．
        play_counts（連続して何回目の勝負か）ごとに分けて，勝敗をみる．
        play_countsごとに分け，get_coinを引数のfunctionで算出する．
        デフォルトのfunctionはsum．
        """
        def func2(x):
            return round(x.sum() / len(x), 5) * 100 + 50

        if func == "sum":
            func = sum
        elif func == "mean":
            func = np.mean
        else:
            func = func2

        df2 = self.df.groupby("play_counts")["get_coin"].apply(func)
        #描画
        if plot:
            fig = plt.figure()# Figureを設定
            ax = fig.add_subplot(111)# Axesを追加
            ax.set_title("Transition of win rate.", fontsize = 16) # Axesのタイトルを設定
            ax.plot(df2.index, df2.values, marker=".")
            plt.show()
        return  self.df.groupby("play_counts")["get_coin"].apply(func)
    
    def basic_strategy_win_percentage(self, plot=True, win_coin=True, prints=False, kind="percentage"):
        """
        ベーシックストラテジーの各勝率を求める．
        win_coinは，勝率の算出法を示しており，Trueのときは勝った枚数から独自のアルゴリズムで勝率を算出している．
        Falseの場合は，単純に'勝利した回数/勝負した回数'で算出している．
        """
        basic_strategy = pd.read_csv('../csv/basic_strategy.csv')
        basic_strategy.index = basic_strategy.PC
        basic_strategy.drop('PC', axis=1, inplace=True)
        columns = list(basic_strategy.columns)
        index = list(basic_strategy.index)

        if win_coin:
            df = self.df
            df["split2"] = df["split"].map(lambda x: x+1)
            basic_strategy_sum = pd.crosstab(index=df["first_PC"], columns=df["first_DC"], values=df["get_coin"], aggfunc="sum").reindex(index=index, columns=columns)
            basic_strategy_count = pd.crosstab(index=df["first_PC"], columns=df["first_DC"]).reindex(index=index, columns=columns)
            basic_strategy_percentage = basic_strategy_sum / basic_strategy_count
            basic_strategy_percentage = basic_strategy_percentage.applymap(lambda x: round(x*100+50, 2))
            basic_strategy_percentage = basic_strategy_percentage.iloc[1:18]
        else:
            df = self.df
            df["split2"] = df["split"].map(lambda x: x+1)
            def func(x):
                if x > 0:
                    return 1
                else:
                    return 0
            df["W_L"] = df["get_coin"].map(func)
            basic_strategy_sum = pd.crosstab(index=df["first_PC"], columns=df["first_DC"], values=df["W_L"], aggfunc="sum").reindex(index=index, columns=columns)
            basic_strategy_count = pd.crosstab(index=df["first_PC"], columns=df["first_DC"], values=df["split2"], aggfunc="sum").reindex(index=index, columns=columns)
            basic_strategy_percentage = basic_strategy_sum / basic_strategy_count
            basic_strategy_percentage = basic_strategy_percentage.applymap(lambda x: round(x*100, 2))
        if prints:
            print("sum")
            print(basic_strategy_sum)
            print("\ncount")
            print(basic_strategy_count)
        if plot:
            if kind == "sum":
                fig, ax = plt.subplots(figsize=(9, 9))
                fig = sns.heatmap(basic_strategy_sum, center=8000, square=False, ax=ax, fmt=".0f")
                ax.set_ylim(len(basic_strategy_sum), 0)
                ax.set_xlabel("Dealer's open card")
                ax.set_ylabel("Player's card")
                ax.set_title("sum of get win coin of 'Basic strategy'")
                plt.show()
                return basic_strategy_sum
            elif kind == "count":
                fig, ax = plt.subplots(figsize=(9, 9))
                fig = sns.heatmap(basic_strategy_count, center=20000, square=False, ax=ax, fmt=".0f")
                ax.set_ylim(len(basic_strategy_count), 0)
                ax.set_xlabel("Dealer's open card")
                ax.set_ylabel("Player's card")
                ax.set_title("count of 'Basic strategy'")
                plt.show()
                return basic_strategy_count
            else:
                fig, ax = plt.subplots(figsize=(9, 9))
                fig = sns.heatmap(basic_strategy_percentage, cmap='Blues', annot=True, square=False, ax=ax, fmt=".0f")
                ax.set_ylim(len(basic_strategy_percentage), 0)
                ax.set_xlabel("Dealer's open card")
                ax.set_ylabel("Player's card")
                ax.set_title("Win rate of 'Basic strategy'")
                plt.show()
                return basic_strategy_percentage


class AnalysisAll:

    def deck_analysis(self, deck_list=[1,2,4,6,8], GAME_TIME=1000000, plot=True):
        """
        Deck数の影響を調べる．
        """
        percentage_list = []
        cut_num_list = [] # plot == 1のとき用
        for deck in deck_list:
            a = MakeDataFrame(GAME_TIME=GAME_TIME, RE_PLAY=False, DECK=deck)
            print("\nDECK数：{}".format(deck))
            df = a.main()
            c, p = AnalysisDf(df).win_percentage(how="cut", split=100, plot=False)
            cut_num_list.append(c)
            percentage_list.append(p)
        last_percentage_list = [p[-1] for p in percentage_list]
        if plot:
            #描画１
            fig = plt.figure()# Figureを設定
            ax = fig.add_subplot(111)# Axesを追加
            ax.set_title("Changing deck affects win rate.", fontsize=16) # Axesのタイトルを設定
            ax.plot(deck_list, last_percentage_list, marker=".")
            #描画２
            fig = plt.figure() # Figureを設定
            ax2 = fig.add_subplot(111) # Axesを追加
            ax2.set_title("Changing deck affects win rate.", fontsize=16) # Axesのタイトルを設定
            for c, p, d in zip(cut_num_list, percentage_list, deck_list):
                ax2.plot(c, p, label=d)
            plt.legend(bbox_to_anchor=(1, 1), loc='best', borderaxespad=0, fontsize=8)
            plt.show()
            print(last_percentage_list)
        else:
            return last_percentage_list
        


if __name__ == "__main__":
    a = MakeDataFrame(10000, 6, True, 10)
    a.main()