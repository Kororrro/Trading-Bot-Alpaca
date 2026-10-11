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
    # quoute = bm.getQuoutes() -> QuoteSet returned
    # dailybars_add.add(latest_bar)
    frame="Day"
    timelength=55
    coin="ETH/USD"
    daily_bars = bm.getHistory(currencies=[coin], frame="Day", timelength=3) # BarSet
    latest_bar = bm.getLatestBar(coin=[coin]) #Dict
    #Appending latest bar to the original data without changing it's structure
    daily_bars_list = daily_bars.data[coin]
    daily_bars_list.append(dict(latest_bar[coin])) # append on the end another element
    # daily_bars_list.pop(-1) # Remove last element

def signalMeanReversion():
    print("Mean reversion")

def bars_addition():
    coin="ETH/USD"
    daily_bars = bm.getHistory(currencies=[coin], frame="Day", timelength=3) # BarSet
    latest_bar = bm.getLatestBar(coin=[coin]) #Dict
    #Appending latest bar to the original data without changing it's structure
    daily_bars_list = daily_bars.data[coin]
    daily_bars_list.append(dict(latest_bar[coin])) # append on the end another element
    # daily_bars_list.pop(-1) # Remove last element
    print(daily_bars)
    """
    Managed to append latest bar data into the daily bars list, and for that to work I had to strip away the data.
    Now I have to either append the data without striping or to re-encapsulate the data in what it had before.
    """

bars_addition()