import re
from datetime import datetime
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.timeframe import TimeFrameUnit

API_KEY = "PKXKUBE9N3O8N6XBYCLA"
API_SECRET = "rnQEvojcKXg1kkK4Yln59kZFCZgfFtYUfHvXXcjA"

client = StockHistoricalDataClient(API_KEY, API_SECRET)

def parse_timeframe(user_input):
    match = re.match(r"(\d+)([a-zA-Z]+)", user_input)
    # add error handling
    value, unit = match.groups()
    value = int(value)
    unit = unit.lower()

    if unit == 'min':
        return TimeFrame(value, TimeFrameUnit.Minute)
    elif unit == 'hour':
        return TimeFrame(value, TimeFrameUnit.Hour)
    elif unit == 'week':
        return TimeFrame(value, TimeFrameUnit.Week)
    elif unit == 'month':
        return TimeFrame(value, TimeFrameUnit.Month)

def main():
    symbol = 'AAPL'
    user_int = input('enter timeframe: ')
    timeframe = parse_timeframe(user_int)
    print(timeframe)
    start_date = datetime.fromisoformat("2023-01-01") 
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=timeframe,
        start=start_date,
        limit=5
    )
    bars = client.get_stock_bars(request_params).df

    print(f"\n5 Historical Bars for {symbol} starting {start_date.date()} with timeframe {user_int}")
    print(bars)

main()