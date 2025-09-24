import asyncio
from core.strategy_runner import StrategyRunner

class LiveStrategyManager:
    def __init__(self):
        self.runners = []

    def add_strategy(self, strategy, strategy_name, symbol, timeframe, starting_balance=100000):
        runner = StrategyRunner(strategy, symbol, timeframe, starting_balance=starting_balance)
        self.runners.append({'name': strategy_name, 'runner': runner, 'running': True})

    def remove_strategy(self, name):
        self.runners = [r for r in self.runners if r['name'] != name]

    def toggle_strategy(self, name, state):
        for r in self.runners:
            if r['name'] == name:
                r['running'] = state
    
    def get_all_results(self):
        results = {}
        for r in self.runners:
            pnl, trades, summary = r['runner'].get_results()
            results[r['name']] = {
                'pnl_history': pnl,
                'trade_history': trades,
                'summary': summary
            }
        return results

    async def run_all(self):
        active_runners = [r['runner'].run() for r in self.runners if r['running']]
        if active_runners:
            try:
                await asyncio.gather(*active_runners)
            except Exception as e:
                print('Exception in run_all', e)

    def clear_all(self):
        self.runners = []

    def stop_current(self):
        if self.runners:
            try:
                self.runners[0]['runner'].stop()
            except Exception as e:
                print('Exception stopping current runner', e)
        self.clear_all()