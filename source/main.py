import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import indicators as ind #indicators.pyのインポート
import backtest as bt
import myInd as mi

csvfile = 'data/DAT_ASCII_USDJPY_M1_2017.csv'

df = pd.read_csv(csvfile, sep=';',
                     names=('Time','Open','High','Low','Close', ''),
                     index_col='Time', parse_dates=True)

df.index += pd.offsets.Hour(7) #7時間のオフセット

#df = ind.TF_ohlc(df, 'H') #1時間足データの作成

#mi.revTry(df)

mi.test2(df)
