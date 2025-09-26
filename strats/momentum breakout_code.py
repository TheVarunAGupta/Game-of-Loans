import numpy as np
from strats.base_strategy import BaseStrategy

class MomentumBreakoutStrategy(BaseStrategy):
    def __init__(self, lookback_period=20, buy_percent=0.01, sell_percent=1.0):
        super().__init__('Momentum Breakout', max_lookback=lookback_period)
        self.lookback_period = lookback_period
        self.buy_percent = buy_percent
        self.sell_percent = sell_percent

    def generate_signals(self, data):
        if data is None or len(data) < self.lookback_period:
            return None
        
        last_bar = data[-1]
        price = last_bar['close']
        ts = last_bar['timestamp']

        closes = np.fromiter((d['close'] for d in data), dtype=float)
        recent_high = closes[-self.lookback_period:].max()
        recent_low = closes[-self.lookback_period:].min()

        if price > recent_high:
            return (ts, price, 'BUY', self.buy_percent)
        elif price < recent_low:
            return (ts, price, 'SELL', self.sell_percent)
        
        return None