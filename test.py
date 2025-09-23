import asyncio
import main
import datetime

async def live_test_loop(symbol="AAPL", starting_balance=10000, timeframe="1Min"):
    """Run live indefinitely and print results every minute."""
    active_strategies = ["Mean Reversion"]  # Replace with your strategy names
    main.set_active_strategies(active_strategies)
    main.live_running = True

    print(f"Starting live_test_loop with strategies: {active_strategies}")

    try:
        last_report = datetime.datetime.now()
        while True:
            if main.live_running:
                try:
                    await main.run_live(
                        strategy_list=active_strategies,
                        symbol=symbol,
                        starting_balance=starting_balance,
                        timeframe=timeframe
                    )
                except Exception as e:
                    print("Error in run_live:", e)

                # Check results every minute
                now = datetime.datetime.now()
                if (now - last_report).total_seconds() >= 60:
                    results = main.manager.get_all_results()
                    print(f"\n--- Results at {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
                    for strat, data in results.items():
                        summary = data['summary']
                        print(f"Strategy: {strat}, Final Cash: {summary.get('Final Cash')}, "
                              f"Portfolio Value: {summary.get('Portfolio Value')}")
                    last_report = now

            await asyncio.sleep(1)  # short sleep to prevent CPU spin
    except asyncio.CancelledError:
        print("Live test loop cancelled")
    finally:
        print("Live test loop finished.")

if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(live_test_loop())