import os
from dotenv import load_dotenv
from alpaca.data.live import StockDataStream
from data.live import LiveFeeder
from core.broker import Broker

load_dotenv()

class LiveSimulator:
    def __init__(self, feed, strategy, starting_balance=100000):
        self.api_key = os.getenv('APCA_API_KEY_ID')
        self.secret_key = os.getenv('APCA_API_SECRET_KEY')
        self.stream = StockDataStream(self.api_key, self.secret_key)
        self.feed = feed
        self.strategy = strategy
        self.broker = Broker(starting_balance)

    async def handle_bar(self, bar):
        print(f'[DEBUG] Incoming 1-min bar from Alpaca → {bar.symbol} @ {bar.timestamp} | O:{bar.open} H:{bar.high} L:{bar.low} C:{bar.close} V:{bar.volume}')
        final_bar = self.feed.handle_bar(bar)

        if final_bar:   
            print(f'[DEBUG] Aggregated custom bar stored → {final_bar}')
            ts, price = final_bar.timestamp, final_bar.close
            self.broker.metrics.record(ts, {final_bar.symbol: price})
            signal = self.strategy.generate_signals(self.feed.df.to_dict('records'))
            if signal:
                ts, price, action, allocation = signal
                if action == 'BUY':
                    self.broker.buy(final_bar.symbol, price, allocation_percent=allocation, timestamp=ts)
                elif action == 'SELL':
                    self.broker.sell(final_bar.symbol, price, allocation_percent=allocation, timestamp=ts)


    async def handle_trade(self, trade):
        # print(f'[DEBUG] Trade received → {trade.symbol} | Price:{trade.price} Size:{trade.size} Time:{trade.timestamp}')
        self.feed.handle_trade(trade)
        # ts, price = trade.timestamp, trade.price
        # self.broker.metrics.record(ts, {trade.symbol: price})
        signal = self.strategy.generate_signals(self.feed.df.to_dict('records'))
        if signal:
            ts, price, action, allocation = signal
            if action == 'BUY':
                self.broker.buy(trade.symbol, price, allocation_percent=allocation, timestamp=ts)
            elif action == 'SELL':
                self.broker.sell(trade.symbol, price, allocation_percent=allocation, timestamp=ts)
  

    def get_broker(self):
        return self.broker     

if __name__ == '__main__':
    print('THIS IS RUNNING')
    feeder = LiveFeeder(timeframe='3Min')
    symbol = 'AAPL'
    live_sim = LiveSimulator(feeder)

    print(f'[DEBUG] Subscribing to {symbol} bars and trades')
    live_sim.stream.subscribe_bars(live_sim.handle_bar, symbol)
    live_sim.stream.subscribe_trades(live_sim.handle_trade, symbol)

    print('[DEBUG] Starting stream')
    live_sim.stream.run()