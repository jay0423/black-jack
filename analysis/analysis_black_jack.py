"""
black_jack.py及び，make_dataframe.pyを用いて作成されるブラックジャックの勝敗DataFrameを元に，データ分析を行う．

WinPercentage
    DataFrameを元に様々なパータンで勝率を出力する．

AnalysisAll
    ブラックジャックの設定を変更させてDataFrameを作成し，データ分析を行う．
    Deck数のよって変化するのかを求める．

MakeBasicStrategy
    最も勝率が高くなるベーシックストラテジーを最適化する．

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

from make_dataframe import MakeDataFrame, MakeDataFrameCardCustomized, MakeDataFrameActionCustomized

class WinPercentage:
    """
    MakeDataFrame().main()をもとに作られたDataFrameを用いて，データ分析を行う．
    主に勝率を算出する．
    """

    def __init__(self, df):
        self.df = df
    
    def win_percentage(self, how="cut", split=10, cut_num_list=[], plot=True, coin=False):
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
        # split数がdfの長さを超えれいる場合，エラーが生じるため，警告しsplitをdf長さと一致させる．
        if split > len(self.df):
            split = len(self.df)
            print("'split' exceeds the length of the DataFrame. Change 'split' to {}.".format(len(self.df)))

        if how == "all":
            if not coin:
                p = self.df[self.df["get_coin"] > 0]["get_coin"].sum()
                n = self.df[self.df["get_coin"] < 0]["get_coin"].sum()
                percentage = round((p / (p - n)) * 100, 5)
            else:
                percentage.append(df["get_coin"].sum())
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
                df = self.df[:cut_num_list[i+1]]
                if not coin:
                    p = df[df["get_coin"] > 0]["get_coin"].sum()
                    n = df[df["get_coin"] < 0]["get_coin"].sum()
                    percentage.append(round((p / (p - n)) * 100, 5))
                else: #コイン数を表示するとき
                    percentage.append(df["get_coin"].sum())
            if not coin:
                print("{}%".format(percentage[-1]))
            else:
                print(percentage[-1])

            percentage = [0 if str(i) == str(np.nan) else i for i in percentage]
            #描画
            if plot:
                fig = plt.figure()# Figureを設定
                ax = fig.add_subplot(111)# Axesを追加
                if not coin:
                    ax.set_title("Transition of win rate.", fontsize = 16) # Axesのタイトルを設定
                    percentage_all = round(percentage[-1], 1)
                    max_p = max(np.percentile(percentage, 99.5), percentage_all)
                    min_p = min(np.percentile(percentage, 0.5), percentage_all)
                    ax.set_ylim(min_p-0.1, max_p+0.1)
                else: #コイン数を表示するとき
                    ax.set_title("Changes in the number of coins.", fontsize = 16) # Axesのタイトルを設定
                ax.plot(cut_num_list, percentage)
                plt.show()
            return cut_num_list, percentage

    def play_count_win_percentage(self, func="rate", plot=True):
        """
        ディーラと連続で戦う場合に勝率が変化するのかを分析する．
        play_counts（連続して何回目の勝負か）ごとに分けて，勝敗をみる．
        play_countsごとに分け，get_coinを引数のfunctionで算出する．
        デフォルトのfunctionはsum．
        """
        def func2(x):
            p = x[x > 0].sum()
            n = x[x < 0].sum()
            return round((p / (p - n)) * 100, 5)

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
            if func == sum:
                ax.set_title("Transition of get coin.", fontsize = 16) # Axesのタイトルを設定
            if func == np.mean:
                ax.set_title("Transition of get coin average.", fontsize = 16) # Axesのタイトルを設定
            else:
                ax.set_title("Transition of win rate.", fontsize = 16) # Axesのタイトルを設定
            ax.plot(df2.index, df2.values, marker=".")
            plt.show()
        return  self.df.groupby("play_counts")["get_coin"].apply(func)
    
    def basic_strategy_win_percentage(self, plot=True, how="coin", prints=False, split_count=True):
        """
        ベーシックストラテジーの各勝率を求める．
        howは，勝率の算出法を示しており，'coin'のときは勝ったコイン枚数から勝率を算出している．
        'count'の場合は，単純に'勝利した回数/勝負した回数'で算出している．
        split_countは，howが'count'のとき，分母にスプリットで増えた勝負数を加算するかを指定することができる．
        """
        basic_strategy = pd.read_csv('../csv/basic_strategy.csv')
        basic_strategy.index = basic_strategy.PC
        basic_strategy.drop('PC', axis=1, inplace=True)
        columns = list(basic_strategy.columns)
        index = list(basic_strategy.index)

        if how == "coin":
            # 勝利したコイン枚数 / （勝利したコイン枚数　＋　敗北したコイン枚数）で勝率を算出
            df = self.df
            df_p = df[df["get_coin"] > 0]
            df_n = df[df["get_coin"] < 0]
            basic_strategy_p = pd.crosstab(index=df_p["first_PC"], columns=df_p["first_DC"], values=df_p["get_coin"], aggfunc="sum").reindex(index=index, columns=columns)
            basic_strategy_n = pd.crosstab(index=df_n["first_PC"], columns=df_n["first_DC"], values=df_n["get_coin"], aggfunc="sum").reindex(index=index, columns=columns).fillna(0)
            basic_strategy_percentage = basic_strategy_p / (basic_strategy_p - basic_strategy_n)
            basic_strategy_percentage = basic_strategy_percentage.applymap(lambda x: round(x*100, 2))
            if prints:
                print(basic_strategy)
                print("win_coin")
                print(basic_strategy_p)
                print("\nlose_coin")
                print(basic_strategy_n)
        elif how == "count":
            # 単純に勝負にかつ確率を算出．引き分けが含まれない分勝率は低くなる傾向にある．
            df = self.df
            def func(x):
                if x > 0:
                    return 1
                else:
                    return 0
            df["W_L"] = df["get_coin"].map(func)
            basic_strategy_sum = pd.crosstab(index=df["first_PC"], columns=df["first_DC"], values=df["W_L"], aggfunc="sum").reindex(index=index, columns=columns)
            if split_count:
                #分母にスプリットして増加した勝負回数を増やす．→　勝率は下がる．スプリットしたものを分けて一グループあたりの勝率がわかる．
                df["split2"] = df["split"].map(lambda x: x+1)
                basic_strategy_count = pd.crosstab(index=df["first_PC"], columns=df["first_DC"], values=df["split2"], aggfunc="sum").reindex(index=index, columns=columns)
            else:
                #初手でスプリットの手になったときの勝率を算出する．
                basic_strategy_count = pd.crosstab(index=df["first_PC"], columns=df["first_DC"], values=df["split"], aggfunc="count").reindex(index=index, columns=columns)
            basic_strategy_percentage = basic_strategy_sum / basic_strategy_count
            basic_strategy_percentage = basic_strategy_percentage.applymap(lambda x: round(x*100, 2))
            if prints:
                print(basic_strategy)
                print("sum")
                print(basic_strategy_sum)
                print("\ncount")
                print(basic_strategy_count)
        if plot:
        #描画
            fig, ax = plt.subplots(figsize=(9, 9))
            fig = sns.heatmap(basic_strategy_percentage, cmap='Blues', annot=True, square=False, ax=ax, fmt=".0f")
            ax.set_ylim(len(basic_strategy_percentage), 0)
            ax.set_xlabel("Dealer's open card")
            ax.set_ylabel("Player's card")
            if how == "coin":
                ax.set_title("Win rate of 'Basic strategy' calculated on coin. \n(win_coin / (win_coin + lose_coin))")
            elif how == "count":
                if split_count:
                    ax.set_title("Win rate of 'Basic strategy' calculated on win count.\nInclude the number of splits.(time_of_win / play_count)")
                else:
                    ax.set_title("Win rate of 'Basic strategy' calculated on win count.\nDoes not include the number of splits.(time_of_win / play_count)")
            plt.show()
            return basic_strategy_percentage


class AnalysisAll:
    """
    ブラックジャックの設定を変更させてDataFrameを作成し，データ分析を行うクラス
    """

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
            c, p = WinPercentage(df).win_percentage(how="cut", split=300, plot=False)
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
        

class MakeBasicStrategy:
    """
    make_dataframe.pyのMakeDataFrameActionCustomizedで生成されたゲーム記録のDataFrameから，最適なベーシックストラテジーを作成する．
    
    ベーシックストラテジー最適化アルゴリズム
        1. 全てがS（スタンド）の初期ベーシックストラテジーを用意する．
        2. 新ベーシックストラテジーを元に指定回数だけブラックジャックをプレイし，DataFrameを生成．
        3. DataFrameを元にH, S, D, Pの勝率が最も高いものを組み込み，新たなベーシックストラテジーを生成．
        4. 2に戻り，新たに生成されたベーシックストラテジーを使用して上記の工程を繰り返す．
        5. generatoins回終了後，最適化が完了．
    """

    basic_strategy = pd.read_csv('../csv/basic_strategy.csv')
    basic_strategy.index = basic_strategy.PC
    basic_strategy.drop('PC', axis=1, inplace=True)
    columns = list(basic_strategy.columns)
    index = list(basic_strategy.index)
    
    def __init__(self, df=0, GAME_TIME=100, generations=2):
        self.df = df
        self.GAME_TIME = GAME_TIME
        self.generations = generations

    def action_df(self, action):
        """
        指定されたactionを抽出したデータフレームからクラステーブルを作成して返す．
        return: クロステーブル
        """
        df_A = self.df[self.df["first_P_action"]==action]
        df_A = pd.crosstab(index=df_A["first_PC"], columns=df_A["first_DC"], values=df_A["get_coin"], aggfunc="sum").reindex(index=self.index, columns=self.columns)
        return df_A
    
    def select_SHDP(self, q1,q2,q3,q4):
        """
        get_coinの合計が最大値のアクションを返す．
        """
        if q4 == np.nan:
            q4 = -9999
        if q1 == max(q1, q2, q3, q4):
            return "S"
        elif q2 == max(q1, q2, q3, q4):
            return "H"
        elif q3 == max(q1, q2, q3, q4):
            return "D"
        else:
            return "P"
    
    def make_basic_strategy(self, prints=False):
        """
        最適なベーシックストラテジーを作成する．
        """
        df_H = self.action_df("H")
        df_S = self.action_df("S")
        df_D = self.action_df("D")
        df_P = self.action_df("P")
        if prints:
            print("H", df_H)
            print("S", df_S)
            print("D", df_D)
            print("P", df_P)
        new_bs = self.basic_strategy.copy()
        for i in self.columns:
            for j in self.index:
                try:
                    new_bs.loc[j,i] = self.select_SHDP(df_S.loc[j,i], df_H.loc[j,i], df_D.loc[j,i], df_P.loc[j,i])
                except:
                    new_bs.loc[j,i] = self.select_SHDP(df_S.loc[j,i], df_H.loc[j,i], df_D.loc[j,i])
        return new_bs

    def make_game_time_list(self):
        """
        ゲーム回数のリストを作成して返す．
        return: list exp) [100, 250, 500, 500, 500, 1000, 2000]
        """
        game_time_list = [self.GAME_TIME] * self.generations
        if self.generations >= 4 and self.generations <= 5:
            game_time_list[0] = int(self.GAME_TIME / 5)
            game_time_list[1] = int(self.GAME_TIME / 2)
            game_time_list[-1] = int(self.GAME_TIME * 2)
        elif self.generations >= 6:
            game_time_list[0] = int(self.GAME_TIME / 5)
            game_time_list[1] = int(self.GAME_TIME / 2)
            game_time_list[-2] = int(self.GAME_TIME * 2)
            game_time_list[-1] = int(self.GAME_TIME * 4)
        return game_time_list

    def main(self):
        """
        新しいベーシックストラテジーを生成する．
        初期は全てがSのベーシックストラテジー．
        """
        a = MakeDataFrameActionCustomized(self.GAME_TIME, 6, False)
        bs_chage = pd.read_csv('../csv/basic_strategy2.csv')
        game_time_list = self.make_game_time_list()
        print(game_time_list)
        nan_count_list = []
        for game_time in tqdm(game_time_list):
            a.GAME_TIME = game_time
            df = a.main(bs_chage)
            self.df = df.copy()
            new_bs = self.make_basic_strategy()
            nan_count_list.append(self.basic_strategy[new_bs == self.basic_strategy].isnull().sum().sum())
            bs_chage = new_bs.copy()
        print(nan_count_list)
        return bs_chage