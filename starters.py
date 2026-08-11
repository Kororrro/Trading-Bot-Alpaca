import bot_methods as bm
from stock_pandas import StockDataFrame

"""

implement:
trend following
mean reversion
dual moving average
rsi mean reversion

Then check what strategy is the best for a stock.
Decide on the strategy best performing and continue testing.

"""

def fetchDailyBars():
    frame="Day"
    timelength=100
    bars_df = bm.getHistory(timelength=timelength, frame=frame).df
    daily_df = StockDataFrame(bars_df)

    daily_df['ema:50']
    daily_df['ema:20']
    daily_df['rsi:20']
    print(daily_df)
    return daily_df

fetchDailyBars()