#!/usr/bin/env python3

import stocker
import pandas as pd
from stocker import Stocker

data = pd.DataFrame()
stocks = ['AAPL', 'ADBE', 'SYMC', 'EBAY', 'MSFT', 'QCOM', 'HPQ', 'JNPR', 'AMD', 'IBM']
apple = Stocker('AAPL')
print(apple)
df = apple.make_df('1990-12-12', '2016-12-12')
df = df.set_index(['Date'])
apple_closes = df['Adj. Close']
df.head()
apple_closes.head()