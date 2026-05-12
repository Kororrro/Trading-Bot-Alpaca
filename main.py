import numpy as np
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s',filename='Bot.log', level=logging.INFO)

def initializeVariables():
    from alpaca.data.historical import CryptoHistoricalDataClient
    from alpaca.trading.client import TradingClient
    import json

    with open("Trading-Bot-Alpaca/account.json") as f:
        config = json.load(f)
    logger.info("Reading initial variables")

    api_key = config["api_key"]
    sec_key = config["sec_key"]
    gmail_user = config["gmail_user"]
    gmail_pwd = config["gmail_pwd"]
    recipients = config["recipient"]
    trading_client = TradingClient(api_key, sec_key, paper=True)
    data_client = CryptoHistoricalDataClient()

    return trading_client, data_client, gmail_user, gmail_pwd, recipients

trading_client, data_client, gmail_user, gmail_pwd, recipients = initializeVariables()

####################################        Email        #################################### 

def sendEmail(user, pwd, recipient, custom=""):
    import smtplib
    logger.info("Trying to send an email")
    subject = "test"
    text = "Sent from python script\n%s" % (custom)
    FROM = user
    TO = recipient

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), subject, text)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user,pwd)
            server.sendmail(FROM, TO, message)
            logger.info("Successfully sent email")
    except:
        logger.info("Failed to send an email")
    
####################################        Fetching data       #################################### 

def getAccount():
    logger.info("Getting account data")
    account = trading_client.get_account()
    eth_position = trading_client.get_open_position('ETH')

    # Get a list of all of our positions.
    portfolio = trading_client.get_all_positions()
    print(f"""
--------------------------   Printing account   --------------------------
{account}
--------------------------   Printing position  --------------------------
{eth_position}
--------------------------   Printing portfolio  -------------------------
{portfolio}
""")

    # Print the quantity of shares for each position.
    for position in portfolio:
        print("{} shares of {}".format(position.qty, position.symbol))

def GetQuoutes():
    from alpaca.data.requests import CryptoLatestQuoteRequest
    logger.info("Requesting latest quotes")
    quotesRequest = CryptoLatestQuoteRequest(loc="us-1", symbol_or_symbols=["ETH/USD"])
    eth_quotes = data_client.get_crypto_latest_quote(quotesRequest)
    print(f"Printing eth quotes:\n{eth_quotes}")

####################

def GetHistory(currencies=["ETH/USD"], timelength = 30, frame = "Week", stop=0, debug=False):
    from alpaca.data.timeframe import TimeFrame
    from alpaca.data.requests import CryptoBarsRequest
    from datetime import datetime, timedelta

    logger.info(f"Fetching history data of {currencies}")
    # We're getting the bars from last month in a specific 
    # timeframe and then we return the bars we fetched
    now = datetime.now()
    delta = timedelta(timelength)
    stop = timedelta(stop)

    if debug:
        print(f"Now\t\tdelta\t\tstop\n{now}\t{delta}\t{stop}")
    #Set the options to get
    request_params = CryptoBarsRequest(
    symbol_or_symbols=currencies,
    timeframe=getattr(TimeFrame, frame),
    start=now-delta,
    end=now-stop
    )

    #Get price
    eth_bars = data_client.get_crypto_bars(request_params)
    if debug:
        print(f"Printing eth bars:\n{eth_bars}")
    return eth_bars

####################################        BUY/SELL Code       #################################### 

def BuySell():
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest 
    from alpaca.trading.enums import OrderSide, TimeInForce
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
        logger.info(f"buying {valInput}")
        # sending an order
        market_order = trading_client.submit_order(
            order_data=market_order_data
        )
    elif valInput == "sell":
        print(f"Selling {valInput}")
        # submitting a limit order
        limit_order = trading_client.submit_order(
            order_data=limit_order_data
            )
    else:
        print(f"Error: invalid input value - {valInput}")


####################################        Calculations         #################################### 

def GetAverage(bars, debug=False):
    logger.info("Calculating basic average")
    CloseSum = 0
    barsArr =  bars.df["close"].values
    for i in barsArr:
        CloseSum += i
    change = CloseSum / len(barsArr)
    # print(f"BarsArr: {barsArr}\nArray length: {len(barsArr)}\nAverage: {change}")
    return change

####################

def SMA(asset):
    logger.info("Calculating SMA")
    shortBars = GetHistory(currencies=asset,timelength=30, frame="Day")
    longBars = GetHistory(currencies=asset, timelength=60, frame="Day")
    shortAverage = GetAverage(shortBars)
    longAverage = GetAverage(longBars)

    if shortAverage > longAverage:
        print("Trend upward")
        return 1
    elif longAverage > shortAverage:
        print("Trend downward")
        return 0
    else:
        print("Either the trend is sideways or something went wrong, so here's a debug for you love ;*")
        print(f"long: {longAverage}\nshort: {shortAverage}")

####################

def EMA(barsStart, barsWhole, debug=False):
    logger.info("Calculating EMA")
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
        
####################################        Logic        #################################### 

def getAssetsToBuy():
    from alpaca.trading.requests import AssetClass, GetAssetsRequest
    logger.info("Determiting assets available for purchase")

    search_params = GetAssetsRequest(asset_class=AssetClass.CRYPTO, tradable=True)
    assets = trading_client.get_all_assets(search_params)
    # print(assets)
    upwardAssets = []

    for i in assets:
        # print(f"\n\nI\n\n{i}")
        trend = SMA(i.symbol)
        if trend == 1:
            upwardAssets.append(i.symbol)
        else:
            continue
    return upwardAssets


def runBot():
    logger.info("Running TradingBot 1.0")

####################################        Main        #################################### 

def main():
    message = """
    1 - Get Bars
    2 - Buy/Sell
    3 - Get latest quoutes
    4 - Get raw Average
    5 - SMA
    6 - EMA
    7 - Mail
    8 - getAccount
    9 - Run automated
    0 - Tests"""
    print(message)
    usrInp = int(input("Choose one of the above: "))

    match usrInp:
        case 1:
            try:
                timelengthInput = int(input("Enter timelength (int): "))
                frameInput = input("Enter frame (Hour,Day,Week,Month): ").lower().capitalize()
                coins = []
                coinsInput = input("Input what currencies' bars you want: ").split()
                for i in range(len(coinsInput)):
                    coins.append(coinsInput[i])
                bars = GetHistory(coins, timelengthInput, frameInput)
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
            bars1 = GetHistory(timelength=15,frame="Day",stop=12)
            bars2 = GetHistory(timelength=12,frame="Day")
            EMA(bars1,bars2)
        case 7:
            bars = GetHistory().df
            sendEmail(gmail_user, gmail_pwd, recipients, bars)
        case 8:
            getAccount()
        case 9:
            runBot()
        case 0:
            print("Tests")
            x=getAssetsToBuy()
            print(x)

if __name__ == '__main__':
    main()


"""
CryptoLatestBarRequest
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