# These functions are probably no longer usefull, because of built-in functions in e.g. pandas or
# stock-pandas modules. I won't delete them however if they turned out to be usefull in the future

def calculateSMA(asset):
    LOGGER.info("Calculating SMA")
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
        print("Either the trend is sideways or something went wrong, so here's a hint for you love ;*")
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
        
####################

def CalculateRSI(timelength = 14):
    LOGGER.info("Calculating RSI")
    currency = ["ETH/USD"]
    bars = getHistory(currencies=currency, timelength=timelength, frame="Day", debug=True)
    gain = 0
    loss = 0
    for day in range(14):
        if day == 0:
            continue
        close_today = bars[currency[0]][day].close
        close_yesterday = bars[currency[0]][day-1].close
        diff = close_today - close_yesterday

        if diff > 0:
            gain += diff
        else:
            loss += diff
    loss *= -1
    print(f"gain: {gain}\nloss: {loss}")
    avg_gain = gain/timelength
    avg_loss = loss/timelength
    rs = avg_gain/avg_loss
    rsi = 100 - (100/(1+rs))
    print(f"RS: {rs}\nRSI: {rsi}")