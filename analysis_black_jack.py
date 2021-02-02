import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class MakeBlackJack:

    card_list = []
    card_list_index = [] #デッキのカードリスト
    basic_strategy = pd.DataFrame() #ベーシックストラテジーの表

    dealer_card = [] #ディーラーのカード
    player_card = [] #プレイヤーのカード

    player_score = [0] #プレイヤーのスコア
    bet_chip = [1]

    j_adj = 0
    split = 0

    def __init__(self, deck=1):
        self.deck = deck

    def import_cards(self):
        #AからKのカードのリストをインポート
        card_list = pd.read_csv('playing_card.csv')
        card_list.index = card_list.card_num
        card_list.drop('card_num', axis=1, inplace=True)
        for i in range(self.deck):
            self.card_list_index += list(card_list.index)
        self.card_list = card_list
    
    def import_basic_strategy(self):
        #ベーシックストラテジーの表をcsvファイルからインポート
        self.basic_strategy = pd.read_csv('basic_strategy.csv')
        self.basic_strategy.index = self.basic_strategy.PC
        self.basic_strategy.drop('PC', axis=1, inplace=True)
    
    def setup(self):
        #前処理
        self.import_cards()
        self.import_basic_strategy()
        return self.card_list_index, self.card_list, self.basic_strategy

    def shuffle_card(self):
        #カードデッキをシャッフルする
        np.random.shuffle(self.card_list_index)

    def get_dealer_card(self):
        #ディーラーがカードを引く
        self.dealer_card = [self.card_list_index[0], self.card_list_index[2]]
        del self.card_list_index[:2] #引いた分のカードを削除

    def get_player_card(self):
        #プレイヤーがカードを引く
        self.player_card = [[self.card_list_index[0], self.card_list_index[2]]]
        del self.card_list_index[:2] #引いた分のカードを削除
    
    def check_natural_black_jack(self):
        #ディーラーのナチュラルブラックジャック確認
        dealer_score_start = 0
        for i in range(2):
            dealer_score_start += int(self.card_list.loc[self.dealer_card[i]].num)
        if dealer_score_start == 11 and 'A' in str(self.dealer_card):
            self.basic_strategy.replace(['H', 'D', 'P'], 'S', inplace=True)



    def make_player_score(self):
        #プレイヤーの点数
        self.player_score[self.j_adj] = 0
        for i in range(len(self.player_card[self.j_adj])):
            self.player_score[self.j_adj] += int(self.card_list.loc[self.player_card[self.j_adj][i]].num)


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

    def select_HDPS_from_basic_strategy(self, PC, DC):
        '''
        ベーシックストラテジ－からHDPSの選択
        入力 → 縦軸：PC (player card)，横軸：DC (dealer card)
        出力 → H:ヒット, D:ダブルダウン, P:スプリット, S:スタンド
        '''
        return self.basic_strategy.loc[str(PC), str(DC)]
    
    def change_doubledown(self):
        #ダブルダウン処理を無くす
        self.basic_strategy.replace('D', 'H', inplace=True)
        self.basic_strategy.loc['A7', 1:5] = 'S'

    def H_action(self):
        #P_actionがH（ヒット）となった際の処理．
        self.player_card[self.j_adj].append(self.card_list_index[0])
        self.card_list_index.pop(0)
        self.change_doubledown()

    def D_action(self):
        #P_actionがD（ダブルダウン）となった際の処理．
        self.bet_chip[self.j_adj] += self.bet_chip[self.j_adj]
        self.player_card[self.j_adj].append(self.card_list_index[0])
        self.player_score[self.j_adj] += int(self.card_list.loc[self.card_list_index[0]].num)
        self.card_list_index.pop(0)

    def P_action(self):
        #P_actionがP（スプリット）となった際の処理．
        self.split += 1
        self.bet_chip.append(self.bet_chip[self.j_adj])
        self.player_card.insert(len(self.player_card), [self.player_card[self.j_adj][1]])
        self.player_card[self.j_adj].pop(1)
        self.player_score.append(0) #プレイヤーのスコアを分割
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
                self.H_action()
            elif P_action == 'D':
                self.D_action()
                break
            elif P_action == 'P':
                self.P_action()
                break
        
    def get_player_score(self):
        #プレイヤーの最終得点
        for i in range(len(self.player_score)):
            if self.player_score[i] <= 11:
                self.player_score[i] += 10
            elif self.player_score[i] >= 22:
                self.player_score[i] = 'BUST'


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
        self.shuffle_card()
        self.get_dealer_card()
        self.get_player_card()
        self.check_natural_black_jack()
        #掛け金の設定
        self.bet_chip = [1]
        #初回なのかスプリットしていないのかを見分けるために設定
        self.split = 0
        self.j_adj = 0 #player_cardの処理する場所
        #スプリットした際の繰り返し
        j = 0
        while True:
            #勝負が終わった際の処理
            if len(self.player_card) != 1 and len(self.player_card[-1]) != 1:
                print(1)
                break
            #プレイヤーがスプリットしていない場合
            if len(self.player_card) == 1 and j != 0:
                print(2)
                break
            elif len(self.player_card) >= 2:
                for i, card in enumerate(self.player_card):
                    if len(card) == 1:
                        self.j_adj = i
                        break
                self.player_card[self.j_adj].append(self.card_list_index[0])
                self.card_list_index.pop(0)
            
            #プレイヤーがカードを引く処理
            print(self.player_card)
            self.player_draw()
            j += 1
        #プレイヤーのスコアを算出
        self.get_player_score()
        #ディーラーがカードを引く処理
        dealer_score = self.dealer_draw()
        player_WL = self.get_winner(dealer_score)
        print(self.player_card, self.split, self.j_adj, self.player_score, self.dealer_card, dealer_score, player_WL)

        return self.player_card, self.dealer_card, self.player_score, dealer_score, player_WL, self.bet_chip