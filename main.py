from datetime import datetime, timedelta
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, CryptoLatestQuoteRequest, CryptoLatestBarRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest, MarketOrderRequest, LimitOrderRequest 
from alpaca.trading.enums import AssetClass, OrderSide, TimeInForce
import numpy as np
import json

with open("Trading-Bot-Alpaca/account.json") as f:
    config = json.load(f)

api_key = config["api_key"]
sec_key = config["sec_key"]

data_client = CryptoHistoricalDataClient()
trading_client = TradingClient(api_key, sec_key, paper=True)

####################################        Fetching data 
def getAccount():
    print("Getting account data")
    account = trading_client.get_account()
    aapl_position = trading_client.get_open_position('AAPL')

    # Get a list of all of our positions.
    portfolio = trading_client.get_all_positions()

    # Print the quantity of shares for each position.
    for position in portfolio:
        print("{} shares of {}".format(position.qty, position.symbol))

####################################        BUY/SELL Code
def BuySell():
    valInput = input("Buy or sell: ")
    # preparing market order
    market_order_data = MarketOrderRequest(
        symbol="ETH",
        qty=3,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.IOC
    )
    # preparing a limit order
    limit_order_data = LimitOrderRequest(
        symbol="ETH",
        limit_price=19,
        qty=34,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC
    )
    if valInput == "buy":
        print(f"buy: {valInput}")
        # sending an order
        market_order = trading_client.submit_order(
            order_data=market_order_data
        )
    elif valInput == "sell":
        print(f"sell: {valInput}")
        # submitting a limit order
        limit_order = trading_client.submit_order(
            order_data=limit_order_data
            )
    else:
        print(f"Error: invalid input value - {valInput}")

####################################        Historical Data Code
def GetQuoutes():
    quotesRequest = CryptoLatestQuoteRequest(loc="us-1", symbol_or_symbols=["ETH/USD"])
    eth_quotes = data_client.get_crypto_latest_quote(quotesRequest)
    print(f"Printing eth quotes:\n{eth_quotes}")

####################
def GetHistory(timelength = 30, frame = "Week", stop=0, debug=False):
    # We're getting the bars from last month in a specific 
    # timeframe and then we return the bars we fetched
    now = datetime.now()
    delta = timedelta(timelength)
    stop = timedelta(stop)
    if debug:
        print(f"Now\t\tdelta\t\tstop\n{now}\t{delta}\t{stop}")
    #Set the options to get
    request_params = CryptoBarsRequest(
    symbol_or_symbols=["ETH/USD"],
    timeframe=getattr(TimeFrame, frame, "Day"),
    start=now-delta,
    end=now-stop
    )
    #Get price
    eth_bars = data_client.get_crypto_bars(request_params)
    if debug:
        print(f"Printing eth bars:\n{eth_bars}")
    return eth_bars

#####################
def GetAverage(bars, debug=False):
    CloseSum = 0
    barsArr =  bars.df["close"].values
    for i in barsArr:
        CloseSum += i
    change = CloseSum / len(barsArr)
    # print(f"BarsArr: {barsArr}\nArray length: {len(barsArr)}\nAverage: {change}")
    return change

####################################        Predictions
def SMA():
    shortBars = GetHistory(30, "Day")
    longBars = GetHistory(60, "Day")
    shortAverage = GetAverage(shortBars)
    longAverage = GetAverage(longBars)
    if shortAverage > longAverage:
        print("Trend upward")
    elif longAverage > shortAverage:
        print("Trend downward")
    else:
        print("Either the trend is sideways or something went wrong, so here's a debug for you love ;*")
        print(f"long: {longAverage}\nshort: {shortAverage}")

def EMA(barsStart, barsWhole, debug=False):
    barValues = barsWhole.df["close"].values
    barValuesLength = len(barValues)
    startAverage = GetAverage(barsStart)
    smoothing = 2
    emaToday = 0
    emaYesterday = startAverage
    alpha = smoothing/(1+barValuesLength)

    if debug:
        print(f"Bar Values: {barValues}\nBarValues len: {barValuesLength}\nalpha: {alpha}\nSMA: {startAverage}")
    for i in range(1,barValuesLength):
        emaToday = barValues[i]*(alpha)+emaYesterday*(1-alpha)
        if debug:
            print(f"values\t\tEMA today\t\tEMA yesterday")
            print(f"{i}\t\t{emaToday}\t\t{emaYesterday}")
        emaYesterday = emaToday
        if i+1 != barValuesLength:
            emaToday = 0
    print(f"EMA Today: {emaToday}")
        


####################################        Main
def main():
    message = """
    1 - Get Bars
    2 - Buy/Sell
    3 - Get latest quoutes
    4 - Get raw Average
    5 - SMA
    6 - EMA
    0 - Tests"""
    print(message)
    usrInp = int(input("Choose one of the above: "))
    match usrInp:
        case 1:
            try:
                timelengthInput = int(input("Enter timelength (int): "))
                frameInput = input("Enter frame (Hour,Day,Week,Month): ").lower().capitalize()
                bars = GetHistory(timelengthInput, frameInput)
            except:
                print("\nError: Invalid input data. Using default parameters for fetching bars")
                bars = GetHistory()
            print(bars.df)
        case 2:
            BuySell()
        case 3:
            GetQuoutes()
        case 4:
            print("Printing change with variables 30, Week: ")
            bars = GetHistory()
            print(GetAverage(bars))
        case 5:
            SMA()
        case 6:
            bars1 = GetHistory(15,"Day",12)
            bars2 = GetHistory(12,"Day")
            EMA(bars1,bars2)
        case 0:
            print("Tests")

main()


"""
if x:
    #Search for US equities
    search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY,tradable=True)
    #Search for AAPL
    aapl_asset = trading_client.get_asset('AAPL')
    print(f"Printing AAPL:\n{aapl_asset}")

    #Print all assets
    try:
    f = open("assets.txt", 'w')
    except:
    f = open("assets.txt", 'x')
    assets = trading_client.get_all_assets(search_params)
    print(f"\nPrinting assets: {assets}")
    for elem in assets:
    if elem.status == "active" and elem.tradable == True:
        f.write(f"{elem.symbol}\n")

    if frame:
        frame
    else:
        frame = input("Enter Timeframe (Hour,Day,Week,Month): ").lower().capitalize()
"""