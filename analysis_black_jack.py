

import pandas as pd
import numpy as np
import black_jack as bj


class Analysis:

    player_card = []
    dealer_card = []
    player_score = []
    dealer_score = []
    player_WL = []
    bet_chip = []

    def __init__(self, GAME_TIME=10000):
        self.a = bj.MakeBlackJack(5)
        self.GAME_TIME = GAME_TIME

    def get_game(self):
        (player_card, dealer_card, player_score, dealer_score, player_WL, bet_chip, bet_chip) = self.a.main()
        self.player_card.append(player_card)
        self.dealer_card.append(dealer_card)
        self.player_score.append(player_score)
        self.dealer_score.append(dealer_score)
        self.player_WL.append(player_WL)
        self.bet_chip.append(bet_chip)

    def make_df(self, dicts):
        return pd.DataFrame(dicts)

    def edit_df(self, df):
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

        df["get_coin"] = df.apply(func2, axis=1)
        return df

    def main(self):
        self.a.setup()
        for i in range(self.GAME_TIME):
            self.get_game()
        dicts = {
            "player_card": self.player_card,
            "dealer_card": self.dealer_card,
            "player_score": self.player_score,
            "dealer_score": self.dealer_score,
            "player_WL": self.player_WL,
            "bet_chip": self.bet_chip
        }
        df = self.make_df(dicts)
        df = self.edit_df(df)
        return df
