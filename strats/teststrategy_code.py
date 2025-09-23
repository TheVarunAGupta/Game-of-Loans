import numpy as np
from strats.base_strategy import BaseStrategy

class TestStrategy(BaseStrategy):
    def __init__(self, moving_average_window=1, threshold=0.0005, buy_percent=0.01, sell_percent=1.0):
        super().__init__('TestStrat', max_lookback=moving_average_window)
        self.moving_average_window = moving_average_window
        self.threshold = threshold
        self.buy_percent = buy_percent
        self.sell_percent = sell_percent

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