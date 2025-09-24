import os
import re
from dotenv import load_dotenv
from datetime import datetime
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.timeframe import TimeFrameUnit

load_dotenv()

class DataFetcher:
    def __init__(self):
        self.api_key = os.getenv('APCA_API_KEY_ID')
        self.secret_key = os.getenv('APCA_API_SECRET_KEY')
        self.historical = StockHistoricalDataClient(self.api_key, self.secret_key)

    def fetch(self, symbol, timeframe, start_date, end_date):
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
        tf = self.parse_timeframe(timeframe)

        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf,
            start=start_date,
            end=end_date,
        )

        bars = self.historical.get_stock_bars(request_params).df
        return bars
    
    def parse_timeframe(self, timeframe):
        match = re.match(r'(\d+)([a-zA-Z]+)', timeframe)
        if not match:
            raise ValueError('Invalid format')
        value, unit = match.groups()
        value = int(value)
        unit = unit.lower()

        if unit == 'min':
            return TimeFrame(value, TimeFrameUnit.Minute)
        elif unit == 'hour':
            return TimeFrame(value, TimeFrameUnit.Hour)
        elif unit == 'day':
            return TimeFrame(value, TimeFrameUnit.Day)
        elif unit == 'week':
            return TimeFrame(value, TimeFrameUnit.Week)
        elif unit == 'month':
            return TimeFrame(value, TimeFrameUnit.Month)
        else:
            raise ValueError('Unsupported time unit. Use Min, Hour, Day, Week, or Month.')
