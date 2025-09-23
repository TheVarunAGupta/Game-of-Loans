import numpy as np
from strats.base_strategy import BaseStrategy

class MovingAverageCrossoverStrategy(BaseStrategy):
    def __init__(self, short_window=5, long_window=20, buy_percent=0.01, sell_percent=1.0):
        super().__init__('Moving Average Crossover', max_lookback=long_window)
        self.short_window = short_window
        self.long_window = long_window
        self.buy_percent = buy_percent
        self.sell_percent = sell_percent

    def generate_signals(self, data):
        if data is None or len(data) < self.long_window:
            return None
        
        last_bar = data[-1]
        price = last_bar['close']
        ts = last_bar['timestamp']

        closes = np.fromiter((d['close'] for d in data), dtype=float)

        short_ma = closes[-self.short_window:].mean()
        long_ma = closes[-self.long_window:].mean()

        # Buy signal: short MA crosses above long MA
        if short_ma > long_ma:
            return (ts, price, 'BUY', self.buy_percent)
        # Sell signal: short MA crosses below long MA
        elif short_ma < long_ma:
            return (ts, price, 'SELL', self.sell_percent)

        return None