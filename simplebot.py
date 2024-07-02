from datetime import datetime, timedelta
from polygon import RESTClient
from polygon.exceptions import BadResponse, AuthError
import pandas as pd
import numpy as np
import time




#set up polygon client
API_KEY = 'YOUR-API-KEY-HERE'
client = RESTClient(API_KEY)


#example historical data
def get_historical_data(symbol, start_date, end_date):
    return client.get_aggs(ticker=symbol, multiplier=1, timespan="day", 
                           from_=start_date, to=end_date)


end_date = datetime.now()
start_date = end_date - timedelta(days=30)
historical_data = get_historical_data('AAPL', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
for bar in historical_data:
    print(f"Date: {bar.timestamp}, Close: ${bar.close}")

# example using real-time data. You will need a paid subscription for this. It's not required for the trading bot though.
def get_real_time_data(symbol):
   return client.get_last_trade(symbol)

# Example usage
# data = get_real_time_data('AAPL')
# print(f"Last trade price for AAPL: ${data.price}")


# A simple implementation of a Relative Strength Index trading strategy
def calculate_rsi(data, window=14):
    df = pd.DataFrame([bar.__dict__ for bar in data])
    df['close'] = df['close'].astype(float)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]


rsi = calculate_rsi(historical_data)
print(f"Current RSI: {rsi}")

##mock broker stub for placing trades
def place_order(symbol, side, quantity):
    #  Replace with actual brokerage API call.
    print(f"Placing {side} order for {quantity} shares of {symbol}")

# Example usage
# place_order('AAPL', 'buy', 10)

# The start of our trading bot
def simple_trading_bot(symbol):
    while True:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        historical_data = get_historical_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        rsi = calculate_rsi(historical_data)
        print(f"Current RSI for {symbol}: {rsi}")

        if rsi < 30:
            place_order(symbol, 'buy', 10)
        elif rsi > 70:
            place_order(symbol, 'sell', 10)

        time.sleep(300)  # Wait for 5 minutes before checking again

# Example usage
simple_trading_bot('AAPL')


# Requires a paid Polygon.io subscription to retrieve data in real-time
def realtime_trading_bot(symbol):
    while True:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        rt_data = get_data_with_retry(symbol=symbol)
        
        rsi = calculate_rsi(historical_data)
        print(f"Realtime: Current RSI for {symbol}: {rsi}")

        if rsi < 30:
            place_order(symbol, 'buy', 10)
        elif rsi > 70:
            place_order(symbol, 'sell', 10)

        time.sleep(300)  # Wait for 5 minutes before checking again


def get_data_with_retry(symbol, retries=3):
    for attempt in range(retries):
        try:
            return get_real_time_data(symbol)
        except AuthError as e:
            print(f"Could not authenticate: {e}")
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
        except BadResponse as e:
            print(f"Error fetching data: {e}")
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
        

# Example usage
#realtime_trading_bot('AAPL')
