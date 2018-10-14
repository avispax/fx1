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

df = ind.TF_ohlc(df0, 'H') #1時間足データの作成

FastMA = ind.iMA(df, 10) #エントリー用短期移動平均
SlowMA = ind.iMA(df, 30) #エントリー用長期移動平均
ExitMA = ind.iMA(df, 5) #エグジット用移動平均

be = ((FastMA > SlowMA) & (FastMA.shift() <= SlowMA.shift())).values
se = ((FastMA < SlowMA) & (FastMA.shift() >= SlowMA.shift())).values
bExt = ((df.Close < ExitMA) & (df.Close.shift() >= ExitMA.shift())).values
sExt = ((df.Close > ExitMA) & (df.Close.shift() <= ExitMA.shift())).values

t, pl = bt.Backtest(df, be, se, bExt, sExt, TP=100, SL=50, Limit=20)

eq = bt.BacktestReport(t, pl)

m = 100000
df2 = pd.DataFrame({'Equity':eq+m})
df2.plot(figsize=(15,10))
plt.show()
