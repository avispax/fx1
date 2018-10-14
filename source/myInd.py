# coding: utf-8
import numpy as np
import pandas as pd

#移動平均線(Close) : 5
n = 5
#for i in range(n, df.shape[0]):    #本番用
for i in range(n, 20):
    print(i, "-------------------")
    #sma
    sma = df['Close'][i-n:i].mean()
    
    #wma
    m = 0
    tempsum = 0
    for j in range(0, n) :
        m += j+1
        tempsum += df['Close'][i-n+j] * (j+1)
    wma = tempsum/m

    #ema
    alpha = 2 / (n + 1)
    ema = sma if n == i else ema + (alpha * (df['Close'][i-1] - ema))

    #print('sma:', sma, ' wma:', wma, ' ema:', ema)
