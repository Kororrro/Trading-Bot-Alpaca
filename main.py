import numpy as np
import logging

LOGGER = logging.getLOGGER(__name__)
logging.basicConfig(format='%(asctime)s %(message)s',filename='Bot.log', level=logging.INFO)

def initializeVariables():
    from alpaca.data.historical import CryptoHistoricalDataClient
    from alpaca.trading.client import TradingClient
    import json

    with open("Trading-Bot-Alpaca/account.json") as f:
        config = json.load(f)
    LOGGER.info("Reading initial variables")

    api_key = config["api_key"]
    sec_key = config["sec_key"]
    gmail_user = config["gmail_user"]
    gmail_pwd = config["gmail_pwd"]
    recipients = config["recipient"]
    trading_client = TradingClient(api_key, sec_key, paper=True)
    data_client = CryptoHistoricalDataClient()

    return trading_client, data_client, gmail_user, gmail_pwd, recipients

TRADING_CLIENT, DATA_CLIENT, GMAIL_USER, GMAIL_PWD, RECIPIENTS = initializeVariables()

####################################        Email        #################################### 

def sendEmail(user, pwd, RECIPIENT, custom=""):
    import smtplib
    LOGGER.info("Trying to send an email")
    subject = "test"
    text = "Sent from python script\n%s" % (custom)
    FROM = user
    TO = RECIPIENT

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), subject, text)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user,pwd)
            server.sendmail(FROM, TO, message)
            LOGGER.info("Successfully sent email")
    except:
        LOGGER.info("Failed to send an email")
    
####################################        Fetching data       #################################### 

def getAccount():
    LOGGER.info("Getting account data")
    account = TRADING_CLIENT.get_account()
    eth_position = TRADING_CLIENT.get_open_position('ETH')

    # Get a list of all of our positions.
    portfolio = TRADING_CLIENT.get_all_positions()
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

def getQuoutes():
    from alpaca.data.requests import CryptoLatestQuoteRequest
    LOGGER.info("Requesting latest quotes")
    quotes_request = CryptoLatestQuoteRequest(loc="us-1", symbol_or_symbols=["ETH/USD"])
    eth_quotes = DATA_CLIENT.get_crypto_latest_quote(quotes_request)
    print(f"Printing eth quotes:\n{eth_quotes}")

####################

def getHistory(currencies=["ETH/USD"], timelength = 30, frame = "Week", stop=0, debug=False):
    from alpaca.data.timeframe import TimeFrame
    from alpaca.data.requests import CryptoBarsRequest
    from datetime import datetime, timedelta

    LOGGER.info(f"Fetching history data of {currencies}")
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
    eth_bars = DATA_CLIENT.get_crypto_bars(request_params)
    if debug:
        print(f"Printing eth bars:\n{eth_bars}")
    return eth_bars

####################################        BUY/SELL Code       #################################### 

def buySell():
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest 
    from alpaca.trading.enums import OrderSide, TimeInForce
    val_input = input("Buy or sell: ")

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

    if val_input == "buy":
        LOGGER.info(f"buying {valInput}")
        # sending an order
        market_order = TRADING_CLIENT.submit_order(
            order_data=market_order_data
        )
    elif val_input == "sell":
        print(f"Selling {valInput}")
        # submitting a limit order
        limit_order = TRADING_CLIENT.submit_order(
            order_data=limit_order_data
            )
    else:
        print(f"Error: invalid input value - {val_input}")


####################################        Calculations         #################################### 

def getAverage(bars, debug=False):
    LOGGER.info("Calculating basic average")
    CloseSum = 0
    barsArr =  bars.df["close"].values
    for i in barsArr:
        CloseSum += i
    change = CloseSum / len(barsArr)
    # print(f"BarsArr: {barsArr}\nArray length: {len(barsArr)}\nAverage: {change}")
    return change

####################

def calculateSMA(asset):
    LOGGER.info("Calculating calculateSMA")
    shortBars = getHistory(currencies=asset,timelength=30, frame="Day")
    longBars = getHistory(currencies=asset, timelength=60, frame="Day")
    shortAverage = getAverage(shortBars)
    longAverage = getAverage(longBars)

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

def calculateEMA(barsStart, barsWhole, debug=False):
    LOGGER.info("Calculating EMA")
    barValues = barsWhole.df["close"].values
    barValuesLength = len(barValues)
    startAverage = getAverage(barsStart)
    smoothing = 2
    emaToday = 0
    emaYesterday = startAverage
    alpha = smoothing/(1+barValuesLength)

    if debug:
        print(f"Bar Values: {barValues}\nBarValues len: {barValuesLength}\nalpha: {alpha}\ncalculateSMA: {startAverage}")
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
    LOGGER.info("Determiting assets available for purchase")

    search_params = GetAssetsRequest(asset_class=AssetClass.CRYPTO, tradable=True)
    assets = TRADING_CLIENT.get_all_assets(search_params)
    # print(assets)
    upwardAssets = []

    for i in assets:
        # print(f"\n\nI\n\n{i}")
        trend = calculateSMA(i.symbol)
        if trend == 1:
            upwardAssets.append(i.symbol)
        else:
            continue
    return upwardAssets


def runBot():
    LOGGER.info("Running TradingBot 1.0")

####################################        Main        #################################### 

def main():
    message = """
    1 - Get Bars
    2 - Buy/Sell
    3 - Get latest quoutes
    4 - Get raw Average
    5 - calculateSMA
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
                bars = getHistory(coins, timelengthInput, frameInput)
            except:
                print("\nError: Invalid input data. Using default parameters for fetching bars")
                bars = getHistory()
            print(bars.df)
        case 2:
            buySell()
        case 3:
            getQuoutes()
        case 4:
            print("Printing change with variables 30, Week: ")
            bars = getHistory()
            print(getAverage(bars))
        case 5:
            calculateSMA()
        case 6:
            bars1 = getHistory(timelength=15,frame="Day",stop=12)
            bars2 = getHistory(timelength=12,frame="Day")
            calculateEMA(bars1,bars2)
        case 7:
            bars = getHistory().df
            sendEmail(GMAIL_USER, GMAIL_PWD, RECIPIENTS, bars)
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
    aapl_asset = TRADING_CLIENT.get_asset('AAPL')
    print(f"Printing AAPL:\n{aapl_asset}")

    #Print all assets
    try:
    f = open("assets.txt", 'w')
    except:
    f = open("assets.txt", 'x')
    assets = TRADING_CLIENT.get_all_assets(search_params)
    print(f"\nPrinting assets: {assets}")
    for elem in assets:
    if elem.status == "active" and elem.tradable == True:
        f.write(f"{elem.symbol}\n")

    if frame:
        frame
    else:
        frame = input("Enter Timeframe (Hour,Day,Week,Month): ").lower().capitalize()
"""