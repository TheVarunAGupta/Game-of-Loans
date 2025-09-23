from strats.mean_reversion import MeanReversionStrategy
from core.backtester import BackTester
from core.strategy_manager import LiveStrategyManager
from core.strategy_loader import discover_strategies, STRATEGY_DIR
import os

import asyncio

# def run_backtest():
#     strategy = MeanReversionStrategy(moving_average_window=10, threshold=0.005)
#     backtester = BackTester(strategy)
#     logs, summary = backtester.run('AAPL', '4Min', '2023-01-03', '2023-01-06')
#     print(logs)
#     print('\n SUMMARY\n')
#     print(summary)

# def run_backtest(strategy_name, symbol, start_date, end_date, starting_balance):
#     STRATEGY_MAP = {
#         'MeanReversionStrategy': MeanReversionStrategy,
#     }
#     if strategy_name not in STRATEGY_MAP:
#         raise ValueError(f'Unknown strategy: {strategy_name}')

#     strategy_class = STRATEGY_MAP[strategy_name]
#     strategy = strategy_class()
#     backtester = BackTester(strategy, starting_balance=starting_balance)
#     logs, summary = backtester.run(symbol=symbol, timeframe='4Min', start=start_date, end=end_date)
#     return logs, summary


_strategy_cache = None

def get_strategies(refresh: bool = False):
    global _strategy_cache
    if refresh or _strategy_cache is None:
        _strategy_cache = discover_strategies()
    return _strategy_cache

def get_strategy(name: str, refresh: bool = False):
    return get_strategies(refresh).get(name)

def list_strategies(refresh: bool = False):
    """Return just the names of available strategies."""
    return list(get_strategies(refresh).keys())

def read_strategy_code(name):
    """Return the code of a strategy as a string"""
    strategies = get_strategies()
    strat_class = strategies.get(name)
    if not strat_class:
        return ""
    module = strat_class.__module__
    filepath = STRATEGY_DIR / f"{module.split('.')[-1]}.py"
    if filepath.exists():
        return filepath.read_text()
    return ""

def save_strategy_code(name, code):
    """Save code to existing strategy file"""
    strategies = get_strategies()
    strat_class = strategies.get(name)
    if not strat_class:
        return False
    module = strat_class.__module__
    filepath = STRATEGY_DIR / f"{module.split('.')[-1]}.py"
    filepath.write_text(code)
    get_strategies(refresh=True)
    return True

def delete_strategy(name: str):
    """Delete a strategy file by class name (if file exists)."""
    strategies = get_strategies()
    strat_class = strategies.get(name)
    if not strat_class:
        return False
    
    # Find file path by module
    module = strat_class.__module__
    filepath = STRATEGY_DIR / f"{module.split('.')[-1]}.py"
    if filepath.exists():
        os.remove(filepath)
        # refresh cache
        get_strategies(refresh=True)
        return True
    return False

def add_new_strategy(name, code):
    """Add a new .py strategy file"""
    if not name.endswith(".py"):
        name += ".py"
    filepath = STRATEGY_DIR / name
    if filepath.exists():
        return False
    filepath.write_text(code)
    get_strategies(refresh=True)
    return True

def run_backtest(strategy_name, symbol, start_date, end_date, starting_balance, timeframe='4Min'):
    strategies = _load_strategies()
    if strategy_name not in strategies:
        raise ValueError(f'Unknown strategy: {strategy_name}')
    strategy_class = strategies[strategy_name]
    strategy = strategy_class()
    backtester = BackTester(strategy=strategy, starting_balance=starting_balance)
    logs, summary = backtester.run(symbol=symbol, timeframe=timeframe, start=start_date, end=end_date)
    return logs, summary

live_running = False

async def run_live():
    # # manager = LiveStrategyManager()
    # # manager.add_strategy(MeanReversionStrategy(moving_average_window=2, threshold=0.0001), 'AAPL', '1Min')
    # # # manager.add_strategy(MeanReversionStrategy(moving_average_window=2, threshold=0.0001), 'MSFT', '2Min')
    # await manager.run_all()
    global live_running
    while True:
        if live_running:
            await manager.run_all()
        await asyncio.sleep(0.1)

manager = LiveStrategyManager()
manager.add_strategy(MeanReversionStrategy(moving_average_window=2, threshold=0.0001), 'AAPL', '2Min')


if __name__ == '__main__':
    print('Running main...')
    try:
        # asyncio.run(run_live())
        logs, summary = run_backtest('MeanReversionStrategy', 'AAPL', '2023-01-03', '2023-01-06', 100000)
        print(logs)
    except KeyboardInterrupt:
        print('\n[INFO] Program stopped by user.')