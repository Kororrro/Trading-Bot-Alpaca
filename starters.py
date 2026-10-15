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

def fetchBars(frame="Day", timelength=55, coin="ETH/USD"):
    daily_bars = bm.getHistory(currencies=[coin], frame=frame, timelength=timelength) # BarSet
    latest_bar = bm.getLatestBar(coin=[coin]) #Dict
    #Appending latest bar to the original data without changing it's structure
    # daily_bars_list = daily_bars.data[coin]
    # daily_bars_list.append(latest_bar[coin]) # append on the end another element
    # daily_bars_list.pop(-1) # Remove last element
    daily_df = StockDataFrame(daily_bars.df)
    daily_df['ema:50']
    daily_df['ema:20']
    daily_df['rsi:20']
    # print(daily_df)
    return daily_df

def signalTrendfollowing(dataframe):
    print("Signal for trend following")
    df_index = dataframe.index[-1]
    #TODO: 
    # 1. Create an order with stop loss and take profit
    # 2. Loop this behaviour so that it can run all the time
    # 3. Buy only a set amount of the stock. We don't want to throw all our money on one stock, do we? ;)
    if(dataframe['ema:20'][df_index] > dataframe['ema:50'][df_index] and dataframe['rsi:20'][df_index] > 45):
        print("Buy")
        bm.buySell('ETH/USD', 5, 30, dataframe['close'][df_index]-5)
    else:
        print("Not buy")

def signalMeanReversion():
    print("Mean reversion")

# fetchHourlyBars()
dataframe = fetchBars()
signalTrendfollowing(dataframe)