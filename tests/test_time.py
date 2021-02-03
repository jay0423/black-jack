
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from functools import wraps
import time


class MakeBlackJack:

    card_list = []
    card_list_index = [] #デッキのカードリスト
    card_list_index_original = []
    basic_strategy = pd.DataFrame() #ベーシックストラテジーの表
    basic_strategy_original = pd.DataFrame()
    ##時間短縮させるため，セットアップ時に置換の処理を終わらせておく
    basic_strategy_HDP_S  = pd.DataFrame()
    basic_strategy_D_H  = pd.DataFrame()

    dealer_card = [] #ディーラーのカード
    player_card = [] #プレイヤーのカード

    player_score = [0] #プレイヤーのスコア
    bet_chip = [1] #ベットするチップの枚数（ダブルダウンの時だけ2枚）

    j_adj = 0
    

    def __init__(self, DECK=1):
        self.DECK = DECK #使用するトランプのデッキ数
        ##time
        self.time_dict = {
            # "import_cards": 0,
            # "import_basic_strategy": 0,
            "shuffle_card": 0,
            "get_dealer_card": 0,
            "get_player_card": 0,
            "check_natural_black_jack": 0,
            "make_player_score": 0,
            "decide_PC": 0,
            "select_HDPS_from_basic_strategy": 0,
            "change_doubledown": 0,
            "get_H_action": 0,
            "get_D_action": 0,
            "get_P_action": 0,
            "get_player_score": 0,
            "dealer_draw": 0,
            "get_winner": 0
        }
        self.num_time_dict = {
            # "import_cards": 0,
            # "import_basic_strategy": 0,
            "shuffle_card": 0,
            "get_dealer_card": 0,
            "get_player_card": 0,
            "check_natural_black_jack": 0,
            "make_player_score": 0,
            "decide_PC": 0,
            "select_HDPS_from_basic_strategy": 0,
            "change_doubledown": 0,
            "get_H_action": 0,
            "get_D_action": 0,
            "get_P_action": 0,
            "get_player_score": 0,
            "dealer_draw": 0,
            "get_winner": 0
        }
        self.times = 0

    def StopWatch(func) :
        @wraps(func)
        def wrapper(self, *args, **kargs) :
            start = time.time()
            result = func(self, *args,**kargs)
            elapsed_time =  time.time() - start
            self.time_dict[str(func.__name__)] += elapsed_time
            self.num_time_dict[str(func.__name__)] += 1
            self.times += elapsed_time
            # print(f"{func.__name__}は{elapsed_time}秒かかりました")
            return result
        return wrapper
    
    def percent(self):
        total = sum(self.time_dict.values())
        values = list(map(lambda x: round(x/total*100, 1), list(self.time_dict.values())))
        keys = list(self.time_dict)
        return dict(zip(keys, values))
    
    def percent_per_one(self):
        values = [a / b for a, b in zip(list(self.time_dict.values()), list(self.num_time_dict.values()))]
        total = sum(values)
        values = list(map(lambda x: round(x/total*100, 1), values))
        keys = list(self.time_dict)
        return dict(zip(keys, values))

    # @StopWatch
    def import_cards(self):
        #AからKのカードのリストをインポート
        card_list = pd.read_csv('../csv/playing_card.csv')
        card_list.index = card_list.card_num
        card_list.drop('card_num', axis=1, inplace=True)
        for i in range(self.DECK):
            self.card_list_index += list(card_list.index)
        self.card_list = card_list
        self.card_list_index_original = self.card_list_index.copy()
    
    # @StopWatch
    def import_basic_strategy(self):
        #ベーシックストラテジーの表をcsvファイルからインポート
        self.basic_strategy = pd.read_csv('../csv/basic_strategy.csv')
        self.basic_strategy.index = self.basic_strategy.PC
        self.basic_strategy.drop('PC', axis=1, inplace=True)
        self.basic_strategy_original = self.basic_strategy.copy()
    
    def make_replaced_basic_strategy(self):
        ##時間短縮させるため，セットアップ時に置換の処理を終わらせておく
        self.basic_strategy_HDP_S = self.basic_strategy.replace(['H', 'D', 'P'], 'S')
        self.basic_strategy_D_H = self.basic_strategy.replace('D', 'H')
        self.basic_strategy_D_H.iloc[15, 1:5] = 'S' #A17を変更

    def setup(self):
        #前処理
        self.import_cards()
        self.import_basic_strategy()
        self.make_replaced_basic_strategy()
        return self.card_list_index, self.card_list, self.basic_strategy

    @StopWatch
    def shuffle_card(self):
        #カードデッキをシャッフルする
        np.random.shuffle(self.card_list_index)

    @StopWatch
    def get_dealer_card(self):
        #ディーラーがカードを引く
        self.dealer_card = [self.card_list_index[0], self.card_list_index[2]]
        del self.card_list_index[:2] #引いた分のカードを削除

    @StopWatch
    def get_player_card(self):
        #プレイヤーがカードを引く
        self.player_card = [[self.card_list_index[0], self.card_list_index[2]]]
        del self.card_list_index[:2] #引いた分のカードを削除
    
    @StopWatch
    def check_natural_black_jack(self):
        #ディーラーのナチュラルブラックジャック確認
        dealer_score_start = 0
        for i in range(2):
            dealer_score_start += int(self.card_list.loc[self.dealer_card[i]].num)
        if dealer_score_start == 11 and 'A' in str(self.dealer_card):
            self.basic_strategy = self.basic_strategy_HDP_S.copy()



    @StopWatch
    def make_player_score(self):
        #プレイヤーの点数
        self.player_score[self.j_adj] = 0
        for i in range(len(self.player_card[self.j_adj])):
            self.player_score[self.j_adj] += int(self.card_list.loc[self.player_card[self.j_adj][i]].num)


    @StopWatch
    def decide_PC(self):
        """
        PC：player cardをベーシックストラテジ－の縦軸と同じ表記で出力する．
        """
        #表から行動を決める
        player_card = self.player_card
        player_score = self.player_score
        j_adj = self.j_adj
        card_list = self.card_list
        #スプリット時の処理
        if card_list.loc[player_card[j_adj][0]].num == card_list.loc[player_card[j_adj][1]].num \
            and len(player_card[j_adj]) == 2 and player_card[j_adj][0][0] != 'A':
            if str(player_card[j_adj]).count('A') == 2:
                PC = 'AA'
            else:
                PC = str(card_list.loc[player_card[j_adj][0]].num) + str(card_list.loc[player_card[j_adj][1]].num)
        #ソフトハンド
        elif 'A' in str(player_card[j_adj]):
            if len(player_card[j_adj]) == 2 and player_score == 11:
                PC = '17:'
            else:
                player_card_check = player_card[j_adj].copy()
                for card in player_card_check:
                    if 'A' in card:
                        player_card_check.remove(card)
                        break
                remainder = 0
                for i in range(len(player_card_check)):
                    remainder += card_list.loc[player_card_check[i]].num
                if remainder <= 10:
                    PC = 'A' + str(remainder)
                    if PC =='A1': #スプリットした際に生じるバグの修正
                        PC = 'A2'
                elif 17 <= player_score[j_adj] <= 21:
                    PC = '17:'
                else:
                    PC = player_score[j_adj]
        #ハードハンド
        else:
            if self.player_score[self.j_adj] <= 8:
                PC = ':8'
            elif 17 <= self.player_score[self.j_adj] <= 21:
                PC = '17:'
            else:
                PC = self.player_score[self.j_adj]
        return PC

    @StopWatch
    def select_HDPS_from_basic_strategy(self, PC, DC):
        '''
        ベーシックストラテジ－からHDPSの選択
        入力 → 縦軸：PC (player card)，横軸：DC (dealer card)
        出力 → H:ヒット, D:ダブルダウン, P:スプリット, S:スタンド
        '''
        return self.basic_strategy.loc[str(PC), str(DC)]
    
    @StopWatch
    def change_doubledown(self):
        #ダブルダウン処理を無くす
        self.basic_strategy = self.basic_strategy_D_H.copy()

    @StopWatch
    def get_H_action(self):
        #P_actionがH（ヒット）となった際の処理．
        self.player_card[self.j_adj].append(self.card_list_index[0])
        self.card_list_index.pop(0)
        self.change_doubledown()

    @StopWatch
    def get_D_action(self):
        #P_actionがD（ダブルダウン）となった際の処理．
        self.bet_chip[self.j_adj] += self.bet_chip[self.j_adj]
        self.player_card[self.j_adj].append(self.card_list_index[0])
        self.player_score[self.j_adj] += int(self.card_list.loc[self.card_list_index[0]].num)
        self.card_list_index.pop(0)

    @StopWatch
    def get_P_action(self):
        #P_actionがP（スプリット）となった際の処理．
        self.bet_chip.append(self.bet_chip[self.j_adj])
        self.player_card.insert(len(self.player_card), [self.player_card[self.j_adj][1]])
        self.player_card[self.j_adj].pop(1)
        self.player_score.append(0) #プレイヤーのスコアを分割
        self.card_list_index.pop(0)
        #Aでスプリットした場合にダブルダウンを無くす
        if 'A' in self.player_card[self.j_adj][0]:
            self.change_doubledown()

    def player_draw(self):
        #プレイヤ―がヒットし続けるまで処理を続ける．
        while True:
            self.make_player_score()

            #プレイヤーがバストしたときの処理
            if self.player_score[self.j_adj] >= 22:
                break
            
            PC = self.decide_PC()
            DC = self.card_list.loc[self.dealer_card[1]].num
            #プレイヤーの行動を取得
            P_action = self.select_HDPS_from_basic_strategy(PC, DC)
            
            #プレイヤーが行動を実行
            if P_action == 'S':
                break
            elif P_action == 'H':
                self.get_H_action()
            elif P_action == 'D':
                self.get_D_action()
                break
            elif P_action == 'P':
                self.get_P_action()
                break
        
    @StopWatch
    def get_player_score(self):
        #プレイヤーの最終得点
        for i in range(len(self.player_score)):
            if self.player_score[i] <= 11:
                self.player_score[i] += 10
            elif self.player_score[i] >= 22:
                self.player_score[i] = 'BUST'


    @StopWatch
    def dealer_draw(self):
        """
        ディーラーがカードを引く処理
        """
        #プレイヤーのBUSTを数値化
        player_score_B = self.player_score.copy()
        for i, score in enumerate(self.player_score):
            if score == 'BUST':
                player_score_B[i] = 0
        #ディーラーがカードを引く
        while True:
            #ディーラーのスコア
            dealer_score = 0
            for card in self.dealer_card:
                dealer_score += self.card_list.loc[card].num
            #Aが含まれている場合の処理
            if 'A' in str(self.dealer_card):
                if 18 <= dealer_score + 10 <= 21:
                    break
                elif 18 <= dealer_score <= 21:
                    break
                elif dealer_score >= 22:
                    break
                elif dealer_score + 10 == 17 and player_score_B[self.j_adj] <= 16:
                    break
            else:
                if dealer_score >= 17:
                    break
            #ヒット
            self.dealer_card.append(self.card_list_index[0])
            self.card_list_index.pop(0)
        #ディーラーの最終得点
        if dealer_score <= 11:
            dealer_score += 10
        elif dealer_score >= 22:
            dealer_score = 'BUST'
        return dealer_score

    @StopWatch
    def get_winner(self, dealer_score):
        """
        player_scoreとdealer_scoreを比較し，勝敗を算出
        """
        player_WL = []
        for i, score in enumerate(self.player_score):
            if score == 'BUST':
                player_WL.append('LOSE')
            elif score == 21 and len(self.player_card[i]) == 2 and \
                 dealer_score == 21 and len(self.dealer_card) == 2:
                player_WL.append('PUSH')
            elif score == 21 and len(self.player_card[i]) == 2:
                player_WL.append('Black Jack')
            elif dealer_score == 'BUST' and score != 'BUST':
                player_WL.append('WIN')
            elif score == dealer_score:
                player_WL.append('PUSH')
            elif score >= dealer_score:
                player_WL.append('WIN')
            else:
                player_WL.append('LOSE')
        return player_WL


    def main(self):
        # print("カードの枚数：{}".format(len(self.card_list_index)))
        #初期化
        self.j_adj = 0 #player_cardの処理する場所
        self.dealer_card = [] #ディーラーのカード
        self.player_card = [] #プレイヤーのカード
        self.player_score = [0] #プレイヤーのスコア
        self.basic_strategy = self.basic_strategy_original.copy()
        self.card_list_index = self.card_list_index_original.copy()

        
        self.shuffle_card()
        self.get_dealer_card()
        self.get_player_card()
        self.check_natural_black_jack()

        #掛け金の設定
        self.bet_chip = [1]
        #スプリットした際の繰り返し
        j = 0
        while True:
            #勝負が終わった際の処理
            #プレイヤーがスプリットしている際
            if len(self.player_card) >= 2 and len(self.player_card[-1]) != 1:
                break
            #プレイヤーがスプリットしていない場合
            elif len(self.player_card) == 1 and j != 0:
                break
            #スプリットしているときの位置調整の処理
            if len(self.player_card) >= 2:
                for i, card in enumerate(self.player_card):
                    if len(card) == 1:
                        self.j_adj = i
                        break
                self.player_card[self.j_adj].append(self.card_list_index[0])
                self.card_list_index.pop(0)
            
            #プレイヤーがカードを引く処理
            self.player_draw()
            j += 1

        #プレイヤーのスコアを算出
        self.get_player_score()
        #ディーラーがカードを引く処理
        dealer_score = self.dealer_draw()
        player_WL = self.get_winner(dealer_score)
        # print(self.player_card, self.dealer_card, self.player_score, dealer_score, player_WL, self.bet_chip, self.bet_chip)
        return self.player_card, self.dealer_card, self.player_score, dealer_score, player_WL, self.bet_chip, self.bet_chip