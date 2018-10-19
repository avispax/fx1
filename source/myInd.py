# coding: utf-8
import numpy as np
import pandas as pd
import indicators as ind
import backtest as bt

def revTry(df):
    rsi10 = ind.iRSI(df,10,'Close')
    ema20 = ind.iMA(df, 20, ma_method='EMA')
    enve = ind.iEnvelopes(df, 10, 0.05)
    #ccc = pd.DataFrame({'Close' : df['Close'], 'EMA20': ema20, 'RSI' : rsi10, 'Upper' : enve['Upper'], 'Low' : enve['Lower']})
    #print(ccc)

    # Buy : エンベロープの下に突き抜ける + RSIが30以下で買い。
    be = ((df.Close < enve['Lower']) & rsi10 < 30)
    bExt = ema20 < df.Close

    se = ((enve['Upper'] < df.Close) & 70 < rsi10)
    sExt = df.Close < ema20

    t, pl = bt.Backtest(df, be, se, bExt, sExt, TP=1000, SL=5000, Limit=20)

    eq = bt.BacktestReport(t, pl)

    # グラフで推移を見る時
    #m = 100000
    #df2 = pd.DataFrame({'Equity':eq+m})
    #df2 = pd.DataFrame({'Trade':t})
    #df2 = pd.DataFrame({'Open': df['Open'],'Long': bt.PositionLine(t['Long'].values),'Short': bt.PositionLine(t['Short'].values)})
    #df2.plot(figsize=(15,10))
    #plt.show()

def test2(df) :
    ema2h = ind.iMA(df, 2, ma_method='EMA', applied_price='Hight')
    ema2l = ind.iMA(df, 2, ma_method='EMA', applied_price='Low')
    ema40 = ind.iMA(df, 40, ma_method='EMA')

    # Buy : ema2lがema40よりも上側にあり、Close値がema2lにタッチした場合、エントリーし、
    # BuyExit : High値がema2hにタッチしたら決済。
    be = ((df.Close < enve['Lower']) & rsi10 < 30)
    bExt = ema20 < df.Close

    se = ((enve['Upper'] < df.Close) & 70 < rsi10)
    sExt = df.Close < ema20

    t, pl = bt.Backtest(df, be, se, bExt, sExt, TP=1000, SL=5000, Limit=20)

    eq = bt.BacktestReport(t, pl)
