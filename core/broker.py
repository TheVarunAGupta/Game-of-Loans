import pandas as pd
from core.metrics import MetricsTracker

class Broker:
    def __init__(self, starting_balance=100000):
        self.starting_balance = starting_balance
        self.cash = starting_balance
        self.positions = {} # {symbol: {'quantity': x, 'avg_price': y}}
        # self.trade_history = pd.DataFrame(columns=['timestamp', 'symbol', 'side', 'price', 'quantity'])
        self.trade_history = pd.DataFrame({
            'timestamp': pd.Series(dtype='datetime64[ns]'),
            'symbol': pd.Series(dtype='str'),
            'side': pd.Series(dtype='str'),
            'price': pd.Series(dtype='float'),
            'quantity': pd.Series(dtype='float')
        })
        self.metrics = MetricsTracker(starting_balance)

    def buy(self, symbol, price, allocation_percent=None, quantity=None, timestamp=None):
        if allocation_percent is not None:
            quantity = round((self.cash * allocation_percent) / price, 4)
        if quantity is None or quantity <= 0 or quantity * price > self.cash:
            print('Not enough cash to execute buy')
            return
        
        cost = price * quantity
        self.cash -= cost
        if symbol in self.positions:
            pos = self.positions[symbol]
            total_quantity = pos['quantity'] + quantity
            pos['avg_price'] = ((pos['avg_price'] * pos['quantity']) + (cost)) / total_quantity
            pos['quantity'] = total_quantity
        else:
            self.positions[symbol] = {'quantity': quantity, 'avg_price': price}

        if timestamp is None:
            timestamp = pd.Timestamp.now()

        new_trade = pd.DataFrame([{
            'timestamp': timestamp,
            'symbol': symbol,
            'side': 'BUY',
            'price': price,
            'quantity': quantity
        }])
        self.trade_history = pd.concat([self.trade_history, new_trade], ignore_index=True)
        self.metrics.update_cash(self.cash)
        self.metrics.update_positions(self.positions.copy())
        # self.metrics.record(timestamp, {symbol: price})
        # print(f'BUY {quantity} {symbol} @ {price:.2f}')

    def sell(self, symbol, price, allocation_percent=None, quantity=None, timestamp=None):
        if symbol not in self.positions:
            # print('No position to sell')
            return
        
        pos_qty = self.positions[symbol]['quantity']
        if allocation_percent is not None:
            quantity = max(int(pos_qty * allocation_percent), 1)
            quantity = round(pos_qty * allocation_percent, 4)
        if quantity is None or quantity <= 0:
            return
        if quantity > pos_qty:
            quantity = pos_qty

        avg_price = self.positions[symbol]['avg_price']
        realised_gain = (price - avg_price) * quantity
        self.metrics.realised_pnl += realised_gain
        
        self.cash += price * quantity
        self.positions[symbol]['quantity'] -= quantity
        if self.positions[symbol]['quantity'] == 0:
            del self.positions[symbol]

        if timestamp is None:
            timestamp = pd.Timestamp.now()

        new_trade = pd.DataFrame([{
            'timestamp': timestamp,
            'symbol': symbol,
            'side': 'SELL',
            'price': price,
            'quantity': quantity
        }])
        self.trade_history = pd.concat([self.trade_history, new_trade], ignore_index=True)
        self.metrics.update_cash(self.cash)
        self.metrics.update_positions(self.positions.copy())
        # self.metrics.record(timestamp, {symbol: price})    
        # print(f'SELL {quantity} {symbol} @ {price:.2f}')

    def get_metrics(self):
        return self.metrics