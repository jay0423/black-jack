"""
black_jack.pyから，データを取得してデータフレームを作成する．
self.GAME_TIME：ブラックジャックのプレイ回数
"""

import pandas as pd
import numpy as np
from tqdm import tqdm
import black_jack as bj


class MakeDataFrame:

    player_card = []
    dealer_card = []
    player_score = []
    dealer_score = []
    player_WL = []
    bet_chip = []
    play_counts = []

    def __init__(self, GAME_TIME=100000, DECK=5, RE_PLAY=False, MAX_PLAY_COUNTS=5):
        self.a = bj.MakeBlackJack(DECK)
        self.GAME_TIME = GAME_TIME
        self.RE_PLAY = RE_PLAY
        self.MAX_PLAY_COUNTS = MAX_PLAY_COUNTS

    def get_game(self):
        (player_card, dealer_card, player_score, dealer_score, player_WL, bet_chip, play_counts) = self.a.main()
        self.player_card.append(player_card)
        self.dealer_card.append(dealer_card)
        self.player_score.append(player_score)
        self.dealer_score.append(dealer_score)
        self.player_WL.append(player_WL)
        self.bet_chip.append(bet_chip)
        self.play_counts.append(play_counts)

    def make_df(self, dicts):
        return pd.DataFrame(dicts)

    def edit_df(self, df):
        #スプリットした回数を追加
        df["split"] = df["player_card"].map(len) - 1

        def func2(row):
            def func(xi):
                ai = []
                for x in xi:
                    if x == "WIN":
                        ai.append(1)
                    elif x == "LOSE":
                        ai.append(-1)
                    elif x == "Black Jack":
                        ai.append(1.5)
                    elif x == "PUSH":
                        ai.append(0)
                return ai
            return np.dot(func(row["player_WL"]), row["bet_chip"])
        #獲得したコインの枚数を追加
        df["get_coin"] = df.apply(func2, axis=1)
        return df

    def main(self):
        self.a.setup()
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
        }
        df = self.make_df(dicts)
        df = self.edit_df(df)
        return df

if __name__ == "__main__":
    a = MakeDataFrame(10000, 5, True, 10)
    a.main()