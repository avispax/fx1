
path = 'data/DAT_ASCII_USDJPY_M1_2011.csv'

with open(path) as f:
    s = f.read()
    print(type(s))
    print(s)
