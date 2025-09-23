from core.live_sim import LiveSimulator
from data.live import LiveFeeder
import pandas as pd
import asyncio

class StrategyRunner:
    def __init__(self, strategy, symbol, timeframe, starting_balance=100000):
        self.strategy = strategy
        self.symbol = symbol
        self.timeframe = timeframe
        self.feed = LiveFeeder(timeframe=self.timeframe)
        self.live_sim = LiveSimulator(self.feed, self.strategy, starting_balance=starting_balance)
        self.broker = self.live_sim.get_broker()
        self.metrics = self.broker.get_metrics()
        self.starting_balance = starting_balance

    async def run(self):
        self.live_sim.stream.subscribe_bars(self.live_sim.handle_bar, self.symbol)
        self.live_sim.stream.subscribe_trades(self.live_sim.handle_trade, self.symbol)
        await self.live_sim.stream._run_forever()

    def stop(self):
        try:
            stop_fn = getattr(self.live_sim.stream, 'stop', None)
            if callable(stop_fn):
                result = stop_fn()
                if asyncio.iscoroutine(result):
                    asyncio.create_task(result)
        except Exception as e:
            print('Error stopping stream:', e)

    def get_results(self):
        pnl_history = self.metrics.get_pnl_dataframe().copy()

        if pnl_history.empty:
            return pd.DataFrame(columns=['timestamp', 'portfolio_value']), pd.DataFrame(), {}
        
        if isinstance(pnl_history['timestamp'].iloc[0], tuple):
            pnl_history['timestamp'] = pnl_history['timestamp'].apply(lambda x: x[1])

        trade_history = self.broker.trade_history.copy()
        if not trade_history.empty and isinstance(trade_history['timestamp'].iloc[0], tuple):
            trade_history['timestamp'] = trade_history['timestamp'].apply(lambda x: x[1])

        final_price = self.feed.get_last_price(self.symbol)
        summary = {
            "Final Cash": round(self.metrics.cash, 2),
            "Portfolio Value": round(self.metrics.portfolio_value({self.symbol: final_price}), 2),
            "Realised PnL": round(self.metrics.get_realised_pnl(), 2),
            "Unrealised PnL": round(self.metrics.get_unrealised_pnl({self.symbol: final_price}), 2),
            "Total Return %": round(((self.metrics.portfolio_value({self.symbol: final_price}) / self.starting_balance) - 1) * 100, 2),
            "Trades Executed": len(self.broker.trade_history),
            "Win Rate %": round(self.metrics.win_rate() * 100, 2),
            "Sharpe Ratio": round(self.metrics.sharpe_ratio(self.timeframe), 2),
            "Max Drawdown %": round(self.metrics.max_drawdown() * 100, 2),
            "Profit Factor": round(self.metrics.profit_factor(), 2)
        }
        return pnl_history, trade_history, summary