import bot_methods as bm
from stock_pandas import StockDataFrame

"""

implement:
trend following
    # Buy when : EMA20 > EMA50 and RSI > 55
mean reversion
    #Price < Lower Bollinger Band AND RSI < 25
dual moving average
    # Buy:   50 MA crosses above 200 MA
    # Sell:  50 crosses below 200 
rsi mean reversion
    # Buy: RSI < 30
    # Sell: RSI > 50

Then check what strategy is the best for a stock.
Decide on the strategy best performing and continue testing.

"""

def fetchDailyBars():
    frame="Day"
    timelength=55
    bars_df = bm.getHistory(timelength=timelength, frame=frame).df
    daily_df = StockDataFrame(bars_df)

    daily_df['ema:50']
    daily_df['ema:20']
    daily_df['rsi:20']
    # print(daily_df)
    return daily_df

def fetchHourlyBars():
    frame="Hour"
    timelength=3
    bars_df = bm.getHistory(timelength=timelength, frame=frame).df
    hourly_df = StockDataFrame(bars_df)

    hourly_df['ema:50']
    hourly_df['ema:20']
    hourly_df['rsi:20']
    print(hourly_df)
    return hourly_df

def signalTrendfollowing():
    print("Signal for trend following")
    # dailybars_add=fetchDailyBars()
    # quoute = bm.getQuoutes() -> QuoteSet returned
    # dailybars_add.add(latest_bar)
    # print(dailybars_add)
    dailybars_append=fetchDailyBars()
    print(f"dailybars:\n{dailybars_append}")
    latest_bar = bm.getLatestBar()
    dailybars_append.append(latest_bar)
    print(f"dailybars_append:\n{dailybars_append}")


def signalMeanReversion():
    print("Mean reversion")

signalTrendfollowing()