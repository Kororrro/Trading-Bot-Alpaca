import numpy as np
import logging

class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

LOGGER = logging.getLogger(__name__)
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

def sendEmail(user, pwd, recipient, custom=""):
    import smtplib
    LOGGER.info("Trying to send an email")
    subject = "test"
    text = f"Sent from python script\n{custom}"
    FROM = user
    TO = recipient

    message = f"""From: {FROM}\n
    To: {", ".join(TO)}\nSubject: {subject}\n\n{text}
    """
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user,pwd)
            server.sendmail(FROM, TO, message)
            LOGGER.info("Successfully sent email")
    except:
        LOGGER.info("Failed to send an email")
    
################################        Fetching data       #################################### 

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

####################

def getQuoutes(coin=["ETH/USD"]):
    from alpaca.data.requests import CryptoLatestQuoteRequest
    LOGGER.info("Requesting latest quotes")
    quotes_request = CryptoLatestQuoteRequest(loc="us-1", symbol_or_symbols=coin)
    coin_quotes = DATA_CLIENT.get_crypto_latest_quote(quotes_request)
    print(f"Printing {coin} quotes:\n{coin_quotes}")
    return coin_quotes


####################

def getLatestBar(coin=["ETH/USD"]):
    from alpaca.data.requests import CryptoLatestBarRequest
    LOGGER.info("Requesting latest bar")
    bar_request = CryptoLatestBarRequest(loc="us-1", symbol_or_symbols=coin)
    coin_bar = DATA_CLIENT.get_crypto_latest_bar(bar_request)
    # print(f"Printing {coin} quotes:\n{coin_bar}")
    return coin_bar

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

    if debug == True:
        print(f"Now\t\tdelta\t\tstop\n{now}\t{delta}\t{stop}")
    #Set the options to get
    request_params = CryptoBarsRequest(
    symbol_or_symbols=currencies,
    timeframe=getattr(TimeFrame, frame),
    start=now-delta,
    end=now-stop
    )

    #Get price
    bars = DATA_CLIENT.get_crypto_bars(request_params)
    if debug == True:
        print(f"Printing eth bars:\n{bars}")
    return bars

####################################        BUY/SELL Code       #################################### 

def buySell(coin, quantity, limit_price, stop_price, buy=True):
    #buying is true, selling is false
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopLossRequest
    from alpaca.trading.enums import OrderSide, TimeInForce

    if(buy):
        # preparing market order
        market_order_data = MarketOrderRequest(
            symbol=coin,
            qty=quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.IOC)
        LOGGER.info(f"buying {quantity} of {coin}")
        # sending an order
        market_order = TRADING_CLIENT.submit_order(
            order_data=market_order_data
        )
    elif(not buy):
        # preparing a limit order
        limit_order_data = LimitOrderRequest(
            symbol=coin,
            limit_price=limit,
            qty=quantity,
            side=OrderSide.SELL,
            stop_loss=StopLossRequest(stop_price=stop_price),
            time_in_force=TimeInForce.GTC
        )
        LOGGER.info(f"Selling {quantity} of {coin}")
        # submitting a limit order
        limit_order = TRADING_CLIENT.submit_order(
            order_data=limit_order_data
            )
    else:
        LOGGER.error(f"Error")


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


####################################        Logics        #################################### 

def getAssetsToBuy():
    from alpaca.trading.requests import AssetClass, GetAssetsRequest
    LOGGER.info("Determiting assets available for purchase")

    search_params = GetAssetsRequest(asset_class=AssetClass.CRYPTO, tradable=True)
    assets = TRADING_CLIENT.get_all_assets(search_params)
    # print(assets)
    upward_assets = []
    cheap_assets = {}

    for i in assets:
        # print(f"\n\nI\n\n{i}")
        # trend = calculateSMA(i.symbol)
        if trend == 1:
            upward_assets.append(i.symbol)
        else:
            continue

    for i in assets:
        quoute = getQuoutes(i.symbol)
        quoute_price = quoute[i.symbol].bid_price
        if quoute_price < 20:
            cheap_assets[i.symbol] = quoute_price
        else:
            continue

    print(f"Assets with upwards trend: {upward_assets}")
    print(f"Cheap assets (up to 20 dollars): {cheap_assets}")

####################################        Plotly        #################################### 

def makeAGraph(stockdf):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from datetime import datetime
    st=0
    dfpl = stockdf[st:st+50]
    dfpl.reset_index(inplace=True)

    fig = go.Figure(
        data=[go.Candlestick(x=dfpl.index,
                            open=dfpl['open'],
                            high=dfpl['high'],
                            low=dfpl['low'],
                            close=dfpl['close']),
                    

                go.Scatter(x=dfpl.index, y=dfpl['ema:50'], 
                           line=dict(color='green', width=1), 
                           name="ema 50"),
                go.Scatter(x=dfpl.index, y=dfpl['ema:30'], 
                           line=dict(color='green', width=1), 
                           name="ema 30"),
                go.Scatter(x=dfpl.index, y=dfpl['rsi:14'], 
                           line=dict(color='black', width=1), 
                           name="rsi")
            ],
        layout_yaxis_range=[1500,2500]
    )

    if(dfpl['pointpos']):
        fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                    marker=dict(size=5, color="MediumPurple"),
                    name="entry")

    fig.show()

####################################        Main        #################################### 

def main():
    message = """
    1 - Get Bars
    2 - Buy/Sell
    3 - Get latest quoutes
    4 - Get raw Average
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
                debugInput = input("Enable debuging? [y/n]: ")

                for i in range(len(coinsInput)):
                    coins.append(coinsInput[i])

                debug = False
                if debugInput == "y":
                        debug = True

                bars = getHistory(currencies=coins, timelength=timelengthInput, frame=frameInput, debug=debug)
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
        case 7:
            bars = getHistory().df
            sendEmail(GMAIL_USER, GMAIL_PWD, RECIPIENTS, bars)
        case 8:
            getAccount()
        case 9:
            runBot()
        case 0:
            # print("Tests")
            # # x=getAssetsToBuy()
            # # print(x)
            import pandas as pd
            from stock_pandas import StockDataFrame

            barsdf = getHistory(timelength=50, frame="Day").df
            stock = StockDataFrame(barsdf)
            bars1 = getHistory( timelength=30, frame="Day", stop=20)
            bars2= getHistory(timelength=20, frame="Day")
            stock['ema:50']
            stock['ema:30']
            stock['rsi:14']
            print(stock["ema:30"])



if __name__ == '__main__':
    main()