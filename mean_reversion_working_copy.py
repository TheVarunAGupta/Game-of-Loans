from data.history import DataFetcher
import pandas as pd
import numpy as np
from strats.base_strategy import BaseStrategy

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, moving_average_window=10, threshold=0.005, buy_percent=0.01, sell_percent=1.0):
        super().__init__('Mean Reversion', max_lookback=moving_average_window)
        self.moving_average_window = moving_average_window
        self.threshold = threshold
        self.buy_percent = buy_percent
        self.sell_percent = sell_percent

    # def generate_signals(self, data):
    #     if data is None or data.empty:
    #         return None
        
    #     window = self.moving_average_window
    #     if len(data) < window:
    #         return None
        
    #     tail = data.tail(window)
    #     ma = tail['close'].mean()
    #     price = data['close'].iloc[-1]
    #     ts = data['timestamp'].iloc[-1]

    #     if pd.isna(ma) or ma == 0:
    #         return None
        
    #     deviation = (price - ma) / ma
    #     if deviation <= -self.threshold:
    #         return (ts, price, 'BUY', self.buy_percent)
    #     elif deviation >= self.threshold:
    #         return (ts, price, 'SELL', self.sell_percent)
    #     return None

    def generate_signals(self, data):
        if data is None or len(data) < self.moving_average_window:
            return None
        
        last_bar = data[-1]
        price = last_bar['close']
        ts = last_bar['timestamp']

        closes = np.fromiter((d['close'] for d in data), dtype=float)
        ma = closes.mean()
        if ma == 0:
            return None
        
        deviation = (price - ma) / ma
        if deviation <= -self.threshold:
            return (ts, price, 'BUY', self.buy_percent)
        elif deviation >= self.threshold:
            return (ts, price, 'SELL', self.sell_percent)
        return None
# if __name__ == '__main__':
#     datafetcher = DataFetcher()
#     data = datafetcher.fetch('AAPL', '4Min', '2014-01-03', '2024-01-04')
#     print(data)
#     strategy = MeanReversionStrategy(10, 0.005)
#     signals = strategy.generate_signals(data)

#     print("Running Mean Reversion Strategy...\n")
#     for timestamp, price, signal in signals:
#         print(f"{timestamp} | Price: {price:.2f}: {signal}")