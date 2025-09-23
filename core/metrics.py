import pandas as pd
import numpy as np

class MetricsTracker:
    def __init__(self, starting_balance=100000):
        self.starting_balance = starting_balance
        self.cash = starting_balance
        self.positions = {} # {symbol: {'quantity': x, 'avg_price': y}}
        self.pnl_history = []
        self.realised_pnl = 0.0

    def update_cash(self, cash):
        self.cash = cash

    def update_positions(self, positions):
        self.positions = positions.copy()
    
    def get_unrealised_pnl(self, market_prices):
        total = 0
        for symbol, pos in self.positions.items():
            price = market_prices.get(symbol, pos['avg_price'])
            total += (price - pos['avg_price']) * pos['quantity']
        return total

    def get_realised_pnl(self):
        return self.realised_pnl
        
    def portfolio_value(self, market_prices):
        value = self.cash
        for symbol, pos in self.positions.items():
            value += pos['quantity'] * market_prices.get(symbol, pos['avg_price'])
        return value

    def record(self, timestamp, market_prices):
        realised = self.get_realised_pnl()
        unrealised = self.get_unrealised_pnl(market_prices)
        portfolio_val = self.portfolio_value(market_prices)
        self.pnl_history.append({
            'timestamp': timestamp,
            'portfolio_value': portfolio_val,
            'realised_pnl': realised,
            'unrealised_pnl': unrealised,
            'cash': self.cash,
            'positions': self.positions.copy()
        })

    def sharpe_ratio(self, timeframe):
        df = self.get_pnl_dataframe()
        if df.empty or len(df) < 2:
            return 0.0

        df['returns'] = df['portfolio_value'].pct_change().fillna(0)
        mean = df['returns'].mean()
        std = df['returns'].std()
        if std == 0:
            return 0.0
        # Assuming 252 trading days
        periods_per_year = 252  # default daily
        if timeframe.endswith('Min'):
            minutes = int(timeframe[:-3])
            periods_per_day = 6.5 * 60 / minutes  # 6.5 hours trading day
            periods_per_year = 252 * periods_per_day
        elif timeframe.endswith('H'):
            hours = int(timeframe[:-1])
            periods_per_day = 6.5 / hours
            periods_per_year = 252 * periods_per_day
        elif timeframe.endswith('D'):
            days = int(timeframe[:-1])
            periods_per_year = 252 / days

        return (mean / std) * (periods_per_year ** 0.5)

    def max_drawdown(self):
        df = self.get_pnl_dataframe()
        if df.empty:
            return 0.0
        cum_max = df['portfolio_value'].cummax()
        dd = (df['portfolio_value'] - cum_max) / cum_max
        return dd.min()

    def profit_factor(self):
        realised_changes = np.diff([h['realised_pnl'] for h in self.pnl_history])
        gains = sum(x for x in realised_changes if x > 0)
        losses = -sum(x for x in realised_changes if x < 0)
        if losses == 0:
            return float('inf') if gains > 0 else 0.0
        return gains / losses

    def win_rate(self):
        realised_changes = np.diff([h['realised_pnl'] for h in self.pnl_history])
        wins = sum(1 for x in realised_changes if x > 0)
        total = sum(1 for x in realised_changes if x != 0)
        return wins / total if total > 0 else 0.0 

    def get_pnl_dataframe(self):
        return pd.DataFrame(self.pnl_history)