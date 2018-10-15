# coding: utf-8
import numpy as np
import pandas as pd
from numba import jit

# バックテスト
@jit
def Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots=0.1, spread=3, TP=0, SL=0, Limit=0, Expiration=10):
    Open = ohlc.Open.values #始値
    Low = ohlc.Low.values #安値
    High = ohlc.High.values #高値
    Point = 0.0001 #1pipの値
    if(Open[0] > 50): Point = 0.001 #クロス円の1pipの値
    Spread = spread*Point #スプレッド
    Lots = lots*100000 #実際の売買量
    N = len(ohlc) #FXデータのサイズ
    
    LongTrade = np.zeros(N) #買いトレード情報
    ShortTrade = np.zeros(N) #売りトレード情報

    #買いエントリー価格
    BuyEntryS = np.hstack((False, BuyEntry[:-1])) #買いエントリーシグナルのシフト
    if Limit == 0: LongTrade[BuyEntryS] = Open[BuyEntryS]+Spread #成行買い
    else: #指値買い
        for i in range(N-Expiration):
            if BuyEntryS[i]:
                BuyLimit = Open[i]-Limit*Point #指値
                for j in range(Expiration):
                    if Low[i+j] <= BuyLimit: #約定条件
                        LongTrade[i+j] = BuyLimit+Spread
                        break
    #買いエグジット価格
    BuyExitS = np.hstack((False, BuyExit[:-2], True)) #買いエグジットシグナルのシフト
    LongTrade[BuyExitS] = -Open[BuyExitS]
    
    #売りエントリー価格
    SellEntryS = np.hstack((False, SellEntry[:-1])) #売りエントリーシグナルのシフト
    if Limit == 0: ShortTrade[SellEntryS] = Open[SellEntryS] #成行売り
    else: #指値売り
        for i in range(N-Expiration):
            if SellEntryS[i]:
                SellLimit = Open[i]+Limit*Point #指値
                for j in range(Expiration):
                    if High[i+j] >= SellLimit: #約定条件
                        ShortTrade[i+j] = SellLimit
                        break
    #売りエグジット価格
    SellExitS = np.hstack((False, SellExit[:-2], True)) #売りエグジットシグナルのシフト
    ShortTrade[SellExitS] = -(Open[SellExitS]+Spread)
    
    LongPL = np.zeros(N) # 買いポジションの損益
    ShortPL = np.zeros(N) # 売りポジションの損益
    BuyPrice = SellPrice = 0.0 # 売買価格
    
    for i in range(1,N):
        if LongTrade[i] > 0: #買いエントリーシグナル
            if BuyPrice == 0:
                BuyPrice = LongTrade[i]
                ShortTrade[i] = -BuyPrice #売りエグジット
            else: LongTrade[i] = 0

        if ShortTrade[i] > 0: #売りエントリーシグナル
            if SellPrice == 0:
                SellPrice = ShortTrade[i]
                LongTrade[i] = -SellPrice #買いエグジット
            else: ShortTrade[i] = 0

        if LongTrade[i] < 0: #買いエグジットシグナル
            if BuyPrice != 0:
                LongPL[i] = -(BuyPrice+LongTrade[i])*Lots #損益確定
                BuyPrice = 0
            else: LongTrade[i] = 0
                
        if ShortTrade[i] < 0: #売りエグジットシグナル
            if SellPrice != 0:
                ShortPL[i] = (SellPrice+ShortTrade[i])*Lots #損益確定
                SellPrice = 0
            else: ShortTrade[i] = 0

        if BuyPrice != 0 and SL > 0: #SLによる買いポジションの決済
            StopPrice = BuyPrice-SL*Point
            if Low[i] <= StopPrice:
                LongTrade[i] = -StopPrice
                LongPL[i] = -(BuyPrice+LongTrade[i])*Lots #損益確定
                BuyPrice = 0

        if BuyPrice != 0 and TP > 0: #TPによる買いポジションの決済
            LimitPrice = BuyPrice+TP*Point
            if High[i] >= LimitPrice:
                LongTrade[i] = -LimitPrice
                LongPL[i] = -(BuyPrice+LongTrade[i])*Lots #損益確定
                BuyPrice = 0
                
        if SellPrice != 0 and SL > 0: #SLによる売りポジションの決済
            StopPrice = SellPrice+SL*Point
            if High[i] >= StopPrice+Spread:
                ShortTrade[i] = -StopPrice
                ShortPL[i] = (SellPrice+ShortTrade[i])*Lots #損益確定
                SellPrice = 0

        if SellPrice != 0 and TP > 0: #TPによる売りポジションの決済
            LimitPrice = SellPrice-TP*Point
            if Low[i] <= LimitPrice+Spread:
                ShortTrade[i] = -LimitPrice
                ShortPL[i] = (SellPrice+ShortTrade[i])*Lots #損益確定
                SellPrice = 0
                
    return pd.DataFrame({'Long':LongTrade, 'Short':ShortTrade}, index=ohlc.index),\
            pd.DataFrame({'Long':LongPL, 'Short':ShortPL}, index=ohlc.index)

# バックテストレポート
def BacktestReport(Trade, PL):
    LongPL = PL['Long']
    LongTrades = np.count_nonzero(Trade['Long'])//2
    LongWinTrades = np.count_nonzero(LongPL.clip_lower(0))
    LongLoseTrades = np.count_nonzero(LongPL.clip_upper(0))
    print('買いトレード数 =', LongTrades)
    print('勝トレード数 =', LongWinTrades)
    print('最大勝トレード =', LongPL.max())
    print('平均勝トレード =', round(LongPL.clip_lower(0).sum()/LongWinTrades, 2))
    print('負トレード数 =', LongLoseTrades)
    print('最大負トレード =', LongPL.min())
    print('平均負トレード =', round(LongPL.clip_upper(0).sum()/LongLoseTrades, 2))
    print('勝率 =', round(LongWinTrades/LongTrades*100, 2), '%\n')

    ShortPL = PL['Short']
    ShortTrades = np.count_nonzero(Trade['Short'])//2
    ShortWinTrades = np.count_nonzero(ShortPL.clip_lower(0))
    ShortLoseTrades = np.count_nonzero(ShortPL.clip_upper(0))
    print('売りトレード数 =', ShortTrades)
    print('勝トレード数 =', ShortWinTrades)
    print('最大勝トレード =', ShortPL.max())
    print('平均勝トレード =', round(ShortPL.clip_lower(0).sum()/ShortWinTrades, 2))
    print('負トレード数 =', ShortLoseTrades)
    print('最大負トレード =', ShortPL.min())
    print('平均負トレード =', round(ShortPL.clip_upper(0).sum()/ShortLoseTrades, 2))
    print('勝率 =', round(ShortWinTrades/ShortTrades*100, 2), '%\n')

    Trades = LongTrades + ShortTrades
    WinTrades = LongWinTrades+ShortWinTrades
    LoseTrades = LongLoseTrades+ShortLoseTrades
    print('総トレード数 =', Trades)
    print('勝トレード数 =', WinTrades)
    print('最大勝トレード =', max(LongPL.max(), ShortPL.max()))
    print('平均勝トレード =', round((LongPL.clip_lower(0).sum()+ShortPL.clip_lower(0).sum())/WinTrades, 2))
    print('負トレード数 =', LoseTrades)
    print('最大負トレード =', min(LongPL.min(), ShortPL.min()))
    print('平均負トレード =', round((LongPL.clip_upper(0).sum()+ShortPL.clip_upper(0).sum())/LoseTrades, 2))
    print('勝率 =', round(WinTrades/Trades*100, 2), '%\n')

    GrossProfit = LongPL.clip_lower(0).sum()+ShortPL.clip_lower(0).sum()
    GrossLoss = LongPL.clip_upper(0).sum()+ShortPL.clip_upper(0).sum()
    Profit = GrossProfit+GrossLoss
    Equity = (LongPL+ShortPL).cumsum()
    MDD = (Equity.cummax()-Equity).max()
    print('総利益 =', round(GrossProfit, 2))
    print('総損失 =', round(GrossLoss, 2))
    print('総損益 =', round(Profit, 2))
    print('プロフィットファクター =', round(-GrossProfit/GrossLoss, 2))
    print('平均損益 =', round(Profit/Trades, 2))
    print('最大ドローダウン =', round(MDD, 2))
    print('リカバリーファクター =', round(Profit/MDD, 2))
    return Equity

def PositionLine(trade):
    PosPeriod = 0 #ポジションの期間
    Position = False #ポジションの有無
    Line = trade.copy()
    for i in range(len(Line)):
        if trade[i] > 0: Position = True 
        elif Position: PosPeriod += 1 # ポジションの期間をカウント
        if trade[i] < 0:
            if PosPeriod > 0:
                Line[i] = -trade[i]
                diff = (Line[i]-Line[i-PosPeriod])/PosPeriod
                for j in range(i-1, i-PosPeriod, -1):
                    Line[j] = Line[j+1]-diff # ポジションの期間を補間
                PosPeriod = 0
                Position = False
        if trade[i] == 0 and not Position: Line[i] = 'NaN'
    return Line


# 各関数のテスト
if __name__ == '__main__':
	pass
