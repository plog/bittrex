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

def find_cointegrated_pairs(data):
  n = data.shape[1]
  score_matrix = np.zeros((n, n))
  pvalue_matrix = np.ones((n, n))
  keys = data.keys()
  pairs = [] # We store the stock pairs that are likely to be cointegrated
  for i in range(n):
    for j in range(i+1, n):
      S1 = data[keys[i]]
      S2 = data[keys[j]]
      result = coint(S1, S2)
      score = result[0] # t-score
      pvalue = result[1]
      score_matrix[i,j] = score
      pvalue_matrix[i, j] = pvalue
      if pvalue < 0.02:
        pairs.append((keys[i], keys[j]))
  return score_matrix, pvalue_matrix, pairs

def zscore(series):
  return (series - series.mean()) / np.std(series)


with open('BTCUSD.json') as json_file:
    btc = json.load(json_file)
btc = [float(d.get('open')) for d in btc]

with open('LTCUSD.json') as json_file:
    ltc = json.load(json_file)
ltc = [float(d.get('open')) for d in ltc]

ltcNorm = []
for num1, num2 in zip(ltc, btc):
	ltcNorm.append(num1 * btc[0]/ltc[0])
    
ltcReturns = np.array(ltcNorm)
ltcRawReturns = np.array(ltc)
btcRreturns = np.array(btc)

# --------------------------------------------
LTC = pd.Series(ltcRawReturns, name='LTCUSD')
#LTC = pd.Series(ltcReturns, name='LTCUSD')

BTC = pd.Series(btcRreturns, name='BTCUSD')
# pd.concat([LTC, BTC], axis=1).plot(ax=axes[0],figsize=(15, 7))

## Cointeration levels

print('Correlation: ' + str(BTC.corr(LTC)))
score, pvalue, _ = coint(BTC, LTC)
print('Cointegration test p-value: ' + str(pvalue))

## Cointeration + Z Score

zscore((LTC/BTC)).plot(figsize=(15,7))
plt.legend(['Cointeration + Z Score', 'Mean'])
plt.xlabel('Time')
plt.axhline(zscore((LTC/BTC)).mean())
plt.axhline(1.0, color='red')
plt.axhline(-1.0, color='green')

ratios = LTC/BTC
print(len(ratios))

plt.savefig('new_figure2.png')

## Trading Signals

### Direction of the ratio

ratios = LTC/BTC
ratios_mavg5  = ratios.rolling(window=5, center=False).mean()
ratios_mavg60 = ratios.rolling(window=60, center=False).mean()
std_60        = ratios.rolling(window=60, center=False).std()

plt.figure(figsize=(15, 7))
plt.plot(ratios.index, ratios.values)
plt.plot(ratios_mavg5.index, ratios_mavg5.values)
plt.plot(ratios_mavg60.index, ratios_mavg60.values)
plt.legend(['Ratio', '5d Ratio MA', '60d Ratio MA'])
plt.ylabel('Ratio')
plt.savefig('new_figure3.png')

### Moving average z-score

zscore_60_5 = (ratios_mavg5 - ratios_mavg60)/std_60
plt.figure(figsize=(15,7))
zscore_60_5.plot()
plt.axhline(0, color='black')
plt.axhline(1.0, color='red', linestyle='--')
plt.axhline(-1.0, color='green', linestyle='--')
plt.legend(['Rolling Ratio z-Score', 'Mean', '+1', '-1'])
plt.savefig('new_figure4.png')

### Signal on the ratios
"""
Buy (1) whenever the z-score is below -1.0 
     because we expect the ratio to increase
Sell (-1) whenever the z-score is above 1.0 
    because we expect the ratio to decrease
"""
plt.figure(figsize=(18,7))
ratios.plot()
buy = ratios.copy()
sell = ratios.copy()
buy[zscore_60_5>-1] = 0
sell[zscore_60_5<1] = 0
buy.plot(color='g', linestyle='None', marker='^')
sell.plot(color='r', linestyle='None', marker='^')
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, ratios.min(), ratios.max()))
plt.legend(['Ratio', 'Buy Signal', 'Sell Signal'])
plt.savefig('new_figure5.png')

### Signal on the coins

plt.figure(figsize=(18,9))
# S1 = all_prices['ADBE'].iloc[:2017]
# S2 = all_prices['MSFT'].iloc[:2017]

LTC.plot(color='b')
BTC.plot(color='c')
buyR = 0*LTC.copy()
sellR = 0*LTC.copy()

# When you buy the ratio, you buy stock S1 and sell S2
buyR[buy!=0] = LTC[buy!=0]
sellR[buy!=0] = BTC[buy!=0]

# When you sell the ratio, you sell stock S1 and buy S2
buyR[sell!=0] = BTC[sell!=0]
sellR[sell!=0] = LTC[sell!=0]

buyR[60:].plot(color='g', linestyle='None', marker='^')
sellR[60:].plot(color='r', linestyle='None', marker='^')
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, min(LTC.min(), BTC.min()), max(LTC.max(), BTC.max())))

plt.legend(['LTC', 'BTC', 'Buy Signal', 'Sell Signal'])
plt.savefig('new_figure6.png')

### Simulation

# Trade using a simple strategy
def trade(S1, S2, window1, window2):
    # If window length is 0, algorithm doesn't make sense, so exit
    if (window1 == 0) or (window2 == 0):
        return 0
    
    # Compute rolling mean and rolling standard deviation
    ratios = S1/S2
    print(ratios)
    ma1 = ratios.rolling(window=window1,center=False).mean()
    ma2 = ratios.rolling(window=window2,center=False).mean()
    std = ratios.rolling(window=window2,center=False).std()
    zscore = (ma1 - ma2)/std
    
    # Simulate trading
    # Start with no money and no positions
    money = 0
    countS1 = 0
    countS2 = 0
    tab = []
    for i in range(len(ratios)):
        # Sell short if the z-score is > 1
        if zscore[i] < -1:
            money += S1[i] - S2[i] * ratios[i]
            countS1 -= 1
            countS2 += ratios[i]
            # print('Selling LTC %s %s LTC %s %s'%(money, ratios[i], countS1, countS2))
            tab.append(['Buy LTC',money, ratios[i], countS1, countS2])
        # Buy long if the z-score is < -1
        elif zscore[i] > 1:
            money -= S1[i] - S2[i] * ratios[i]
            countS1 += 1
            countS2 -= ratios[i]
            # print('Buying BTC %s %s %s %s'%(money, ratios[i], countS1, countS2))
            tab.append(['Buy BTC',money, ratios[i], countS1, countS2])
        # Clear positions if the z-score between -.5 and .5
        elif abs(zscore[i]) < 0.75:
            money += S1[i] * countS1 + S2[i] * countS2
            countS1 = 0
            countS2 = 0
            # print('Exit posit %s %s %s %s'%(money, ratios[i], countS1, countS2))
            tab.append(['Exit',money, ratios[i], countS1, countS2])
    print(tabulate(tab, headers=["","$","Ratio","LTC","BTC"]))
    return money

print(trade(LTC,BTC,60,5))