#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm
import json
import urllib.request as urllib2
from tabulate import tabulate
import datetime

def zscore(series):
  return (series - series.mean()) / np.std(series)

with open('BTCUSD.json') as json_file:
    btc = json.load(json_file)
btc = [float(d.get('open')) for d in btc]

with open('LTCUSD.json') as json_file:
    ltc = json.load(json_file)
ltc = [float(d.get('open')) for d in ltc]

with open('BTCUSD.json') as json_file:
    zeDates = json.load(json_file)
allDates = [datetime.datetime.strptime(d.get('startsAt'),"%Y-%m-%dT%H:%M:%SZ") for d in zeDates]

ltcReturns = np.array(ltc)
btcRreturns = np.array(btc)

LTC = pd.Series(ltcReturns, name='LTCUSD')
BTC = pd.Series(btcRreturns, name='BTCUSD')

# Compute rolling mean and rolling standard deviation
ratios = LTC/BTC
ma1 = ratios.rolling(window=5,center=False).mean()
ma2 = ratios.rolling(window=60,center=False).mean()
std = ratios.rolling(window=60,center=False).std()

zscore = (ma1 - ma2)/std
plt.figure(figsize=(15,7))
zscore.plot()
plt.axhline(0, color='black')
plt.axhline(0.9, color='red', linestyle='--')
plt.axhline(-0.9, color='green', linestyle='--')
plt.legend(['Rolling Ratio z-Score', 'Mean', '+1', '-1'])
plt.savefig('new_figure41.png')

# Simulate trading
# Start with +/- 200 USD
countLTC = 4
countBTC = 0.08
amountLTCinUSD = countLTC * LTC[0]
amountBTCinUSD = countBTC * BTC[0]
money = amountLTCinUSD + amountBTCinUSD
tab = []
transferAmount = 80 # USD

tradeNbr = 0

for i in range(len(ratios)):
    LTCPrice = LTC[i]
    BTCPrice = BTC[i]
    transfLTC = transferAmount / LTCPrice
    transfBTC = transferAmount / BTCPrice
    when = allDates[i]

    # Transfer LTC to BTC
    if zscore[i] < -0.90 and amountLTCinUSD > transferAmount * 1.05:
        testCountLTC = countLTC - transfLTC
        testCountBTC = countBTC + transfBTC
        testMoney = testCountLTC * LTCPrice + testCountBTC * BTCPrice
        if testMoney > money:
            tradeNbr += 1
            countLTC = testCountLTC
            countBTC = testCountBTC
            amountLTCinUSD = countLTC * LTCPrice
            amountBTCinUSD = countBTC * BTCPrice            
            money = amountLTCinUSD + amountBTCinUSD            
            tab.append([tradeNbr,when,"LTC --> BTC", countLTC, countBTC, round(money,2)])
    # Transfer BTC to LTC
    elif zscore[i] > 0.90 and amountBTCinUSD > transferAmount * 1.05:
        testCountLTC = countLTC + transfLTC
        testCountBTC = countBTC - transfBTC
        testMoney = testCountLTC * LTCPrice + testCountBTC * BTCPrice             
        if testMoney > money:
            tradeNbr += 1
            countLTC = testCountLTC
            countBTC = testCountBTC
            amountLTCinUSD = countLTC * LTCPrice
            amountBTCinUSD = countBTC * BTCPrice            
            money = amountLTCinUSD + amountBTCinUSD
            tab.append([tradeNbr,when,"BTC --> LTC", countLTC, countBTC, round(money,2)])
    elif abs(zscore[i]) < 0.75:
         HODLLLL = "yesss..."
    money = amountLTCinUSD + amountBTCinUSD
print(tabulate(tab, headers=["Nbr","Date","Action","LTC","BTC","Money"]))
