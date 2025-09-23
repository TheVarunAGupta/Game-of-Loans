from core.strategy_loader import (discover_strategies, read_strategy_code, save_strategy_code,
                                   delete_strategy_file, add_strategy_file, validate_strategy_code,
                                     generate_strategy_filename, get_strategy_name)
from core.backtester import BackTester
from core.strategy_manager import LiveStrategyManager
import asyncio
import numpy as np

live_running = False
manager = LiveStrategyManager()
active_strategies = []
current_symbol = "AAPL"
current_balance = 10000
current_timeframe = "1Min"

def get_strategies(refresh=False):
    return discover_strategies(refresh=refresh)

def get_strategy(name):
    return get_strategies().get(name)

def list_strategy_names():
    return list(get_strategies().keys())

def read_code(name):
    return read_strategy_code(name)

def save_code(name, code):
    return save_strategy_code(name, code)

def delete_strategy(name):
    return delete_strategy_file(name)

def add_new_strategy(name, code):
    return add_strategy_file(name, code)

def validate_code(code, mode='add', original_name=None):
    '''
    ok, msg, cls = validate_strategy_code(code, mode="add")
    ok, msg, cls = validate_strategy_code(code, mode="edit", original_name="MeanReversionStrategy")

'''
    return validate_strategy_code(code, mode=mode, original_name=original_name)

def make_strategy_filename(name):
    return generate_strategy_filename(name)

def strategy_name(code):
    return get_strategy_name(code)

def get_active_strategies():
    """Return list of currently active strategies."""
    global active_strategies
    return active_strategies

def set_active_strategies(strat_list):
    """Set the active strategies list."""
    global active_strategies
    active_strategies = strat_list

def run_backtest(strategy_name, symbol, start_date, end_date, starting_balance, timeframe):
    strategies = get_strategies()
    if strategy_name not in strategies:
        raise ValueError(f'Unknown strategy: {strategy_name}')
    strategy_class = strategies[strategy_name]
    strategy = strategy_class()
    backtester = BackTester(strategy=strategy, starting_balance=starting_balance)
    pnl_history, trade_history, summary = backtester.run(symbol=symbol, timeframe=timeframe, start=start_date, end=end_date)
    return pnl_history, trade_history, summary

async def run_live():
    global live_running
    print("--- run_live started ---")

    while True:  # never exits
        if live_running and active_strategies:
            try:
                print(f"Running with: {active_strategies}, {current_symbol}, {current_balance}, {current_timeframe}")

                manager.clear_all()

                if len(active_strategies) > 1:
                    raise NotImplementedError("Current version cannot run multiple strategies")

                # Get strategy
                strategies = get_strategies()
                strategy_name = active_strategies[0]

                if strategy_name not in strategies:
                    raise ValueError(f"Unknown strategy: {strategy_name}")

                strategy_class = strategies[strategy_name]
                strategy_instance = strategy_class()

                manager.add_strategy(
                    strategy=strategy_instance,
                    strategy_name=strategy_instance.name,
                    symbol=current_symbol,
                    timeframe=current_timeframe,
                    starting_balance=current_balance
                )

                # Inner loop while live_running is true
                while live_running:
                    print("run_live loop iteration started")
                    try:
                        await manager.run_all()
                    except Exception as e:
                        print("Exception inside manager.run_all():", e)
                    await asyncio.sleep(0.1)
                    print("run_live loop iteration ended")

            except Exception as e:
                print("Error in run_live:", e)

        else:
            # Not running, just idle
            await asyncio.sleep(0.5)

def stop_live():
    global live_running
    live_running = False
    try:
        manager.stop_current()
    except Exception as e:
        print('Error while stopping live:', e)

# async def run_live(selected_strategies: list[dict]):
#     global live_running
#     manager.clear_all()
#     for strat_info in selected_strategies:
#         strat_class = get_strategy(strat_info['name'])
#         if strat_class is None:
#             print(f'[Live] Strategy not found: {strat_info["name"]}')
#             continue
#         strategy = strat_class()
#         manager.add_strategy(
#             strategy=strategy,
#             symbol=strat_info['symbol'],
#             timeframe=strat_info['timeframe'],
#         )
#     live_running = True
#     while live_running:
#         await manager.run_all()
#         await asyncio.sleep(0.1)




# def make_json_safe(obj):
#     if isinstance(obj, (datetime.datetime, datetime.date)):
#         return obj.isoformat()
#     if isinstance(obj, (np.integer,)):
#         # this doesn't run so can get rid maybe
#         return int(obj)
#     if isinstance(obj, (np.floating,)):
#         return float(obj)
#     if isinstance(obj, np.ndarray):
#         # this doesn't run so can get rid maybe
#         return obj.tolist()
#     if isinstance(obj, dict):
#         return {k: make_json_safe(v) for k, v in obj.items()}
#     if isinstance(obj, list):
#         return [make_json_safe(v) for v in obj]
#     return obj

# pnl_history, trade_history, summary = run_backtest('MeanReversionStrategy', 'AAPL', '2023-01-03', '2023-01-06', 10000, '1Min')

# print(trade_history)