from data.history import DataFetcher
# from strats.mean_reversion import MeanReversionStrategy
from core.broker import Broker
import pandas as pd
import numpy as np
from collections import deque

class BackTester:
    def __init__(self, strategy, starting_balance=100000):
        self.strategy = strategy
        self.datafetcher = DataFetcher()
        self.broker = Broker(starting_balance)
        self.metrics = self.broker.get_metrics()
        self.starting_balance = starting_balance
    
    def run(self, symbol, timeframe, start, end):
        data = self.datafetcher.fetch(symbol, timeframe, start, end)
        if data.empty:
            raise ValueError(f"No data returned for {symbol} from {start} to {end}")

        timestamps = data.index.to_numpy()
        opens = data['open'].to_numpy()
        highs = data['high'].to_numpy()
        lows = data['low'].to_numpy()
        closes = data['close'].to_numpy()
        volumes = data['volume'].to_numpy()

        # Prepare a rolling window deque for the strategy
        max_lookback = self.strategy.max_lookback
        rolling_window = deque(maxlen=max_lookback)

        for i in range(len(closes)):
            ts, open, high, low, close, volume = timestamps[i], opens[i], highs[i], lows[i], closes[i], volumes[i]

            rolling_window.append({
                'timestamp': ts,
                'open': open,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })

            self.metrics.record(ts, {symbol: close})

            signal = self.strategy.generate_signals(rolling_window)
            if not signal:
                continue

            ts, price, action, allocation = signal
            if action == 'BUY':
                self.broker.buy(symbol, price, allocation_percent=allocation, timestamp=ts)
            elif action == 'SELL':
                self.broker.sell(symbol, price, allocation_percent=allocation, timestamp=ts)

        final_price = data['close'].iloc[-1]
        summary = {
            "Final Cash": round(self.metrics.cash, 2),
            "Portfolio Value": round(self.metrics.portfolio_value({symbol: final_price}), 2),
            "Realised PnL": round(self.metrics.get_realised_pnl(), 2),
            "Unrealised PnL": round(self.metrics.get_unrealised_pnl({symbol: final_price}), 2),
            "Total Return %": round(((self.metrics.portfolio_value({symbol: final_price}) / self.starting_balance) - 1) * 100, 2),
            "Trades Executed": len(self.broker.trade_history),
            "Win Rate %": round(self.metrics.win_rate() * 100, 2),
            "Sharpe Ratio": round(self.metrics.sharpe_ratio(timeframe), 2),
            "Max Drawdown %": round(self.metrics.max_drawdown() * 100, 2),
            "Profit Factor": round(self.metrics.profit_factor(), 2)
        }
        pnl_history = self.metrics.get_pnl_dataframe().copy()
        if isinstance(pnl_history['timestamp'].iloc[0], tuple):
            pnl_history['timestamp'] = pnl_history['timestamp'].apply(lambda x: x[1])

        trade_history = self.broker.trade_history.copy()
        if not trade_history.empty and isinstance(trade_history['timestamp'].iloc[0], tuple):
            trade_history['timestamp'] = trade_history['timestamp'].apply(lambda x: x[1])
            
        return pnl_history, trade_history, summary

# if __name__ == '__main__':
#     strategy = MeanReversionStrategy(moving_average_window=10, threshold=0.005)
#     backtester = BackTester(strategy)

#     backtester.run('AAPL', '4Min', '2023-01-03', '2023-01-06')