import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import indicators as ind #indicators.pyのインポート
import backtest as bt

csvfile = 'data/DAT_ASCII_USDJPY_M1_2015.csv'

df0 = pd.read_csv(csvfile, sep=';',
                     names=('Time','Open','High','Low','Close', ''),
                     index_col='Time', parse_dates=True)

df0.index += pd.offsets.Hour(7) #7時間のオフセット

#df = ind.TF_ohlc(df0, 'H') #1時間足データの作成
df = df0

rsi10 = ind.iRSI(df,10,'Close')
ema20 = ind.iMA(df, 20, ma_method='EMA')
enve = ind.iEnvelopes(df, 10, 0.06)
#ccc = pd.DataFrame({'Close' : df['Close'], 'EMA20': ema20, 'RSI' : rsi10, 'Upper' : enve['Upper'], 'Low' : enve['Lower']})
#print(ccc)

# Buy : エンベロープの下に突き抜ける + RSIが30以下で買い。
be = ((df.Close < enve['Lower']) & rsi10 < 30)
bExt = ema20 < df.Close

se = ((enve['Upper'] < df.Close) & 70 < rsi10)
sExt = df.Close < ema20

t, pl = bt.Backtest(df, be, se, bExt, sExt, TP=100, SL=50, Limit=20)

eq = bt.BacktestReport(t, pl)

# グラフで推移を見る時
m = 100000
#df2 = pd.DataFrame({'Equity':eq+m})
#df2 = pd.DataFrame({'Trade':t})
#df2 = pd.DataFrame({'Open': df['Open'],'Long': bt.PositionLine(t['Long'].values),'Short': bt.PositionLine(t['Short'].values)})
#df2.plot(figsize=(15,10))
#plt.show()
