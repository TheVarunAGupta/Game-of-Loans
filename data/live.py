from datetime import time
import pandas as pd
from data.custom_bars import CustomBar

class LiveFeeder:
    def __init__(self, timeframe='1Min', max_bars=500, session_start=time(9, 30)):
        self.timeframe = pd.Timedelta(timeframe)
        self.session_start = session_start
        self.current_bars = {} # {symbol: CustomBar}
        self.df = pd.DataFrame(columns=['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
        self.max_bars = max_bars
        self.last_prices = {}


    def _get_bucket_start(self, ts):
        session_open = ts.normalize() + pd.Timedelta(
            hours=self.session_start.hour, minutes=self.session_start.minute
        )
        offset = (ts - session_open) // self.timeframe
        return session_open + offset * self.timeframe
    
    # this was for testing crypto
    # def _get_bucket_start(self, ts):
    #     # Anchor at midnight UTC
    #     midnight = ts.normalize()  # midnight of that day
    #     offset = (ts - midnight) // self.timeframe
    #     return midnight + offset * self.timeframe
    
    def _update_dataframe(self, bar):
        bar_dict = {
            'timestamp': bar.timestamp,
            'symbol': bar.symbol,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        }

        mask = (self.df['timestamp'] == bar.timestamp) & (self.df['symbol'] == bar.symbol)
        if mask.any():
            idx = self.df[mask].index[0]
            self.df.loc[idx, 'high'] = max(self.df.loc[idx, 'high'], bar.high)
            self.df.loc[idx, 'low'] = min(self.df.loc[idx, 'low'], bar.low)
            self.df.loc[idx, 'close'] = bar.close
            self.df.loc[idx, 'volume'] += bar.volume
        else:
            columns = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']
            self.df = pd.concat([self.df, pd.DataFrame([bar_dict], columns=columns)], ignore_index=True)

    def _update_current_bar(self, symbol, price, size, timestamp):
        ts = pd.to_datetime(timestamp)
        bucket_start = self._get_bucket_start(ts)
        
        if symbol not in self.current_bars or self.current_bars[symbol].timestamp != bucket_start:
                
            self.current_bars[symbol] = CustomBar(
                symbol=symbol,
                timestamp=bucket_start,
                open_price=price,
                high_price=price,
                low_price=price,
                close_price=price,
                volume=size
            )
            return None
        else:
            # Update existing bar
            agg = self.current_bars[symbol]
            agg.high = max(agg.high, price)
            agg.low = min(agg.low, price)
            agg.close = price
            agg.volume += size
            self._update_dataframe(agg)
            # print(f'[DEBUG] Updated current bar: {agg}')
            return None

    def handle_bar(self, bar):
        self.last_prices[bar.symbol] = bar.close
        if not hasattr(self, '_bar_buffer'):
            self._bar_buffer = {}  # {symbol: list of 1-min bars}

        buffer = self._bar_buffer.setdefault(bar.symbol, [])
        buffer.append(bar)
        bars_per_custom = int(self.timeframe / pd.Timedelta('1min'))

        if len(buffer) >= bars_per_custom:
            combined_open = buffer[0].open
            combined_close = buffer[-1].close
            combined_high = max(b.high for b in buffer[:bars_per_custom])
            combined_low = min(b.low for b in buffer[:bars_per_custom])
            combined_volume = sum(b.volume for b in buffer[:bars_per_custom])

            bucket_start = self._get_bucket_start(pd.to_datetime(buffer[0].timestamp))

            final_bar = CustomBar(
                symbol=bar.symbol,
                timestamp=bucket_start,
                open_price=combined_open,
                high_price=combined_high,
                low_price=combined_low,
                close_price=combined_close,
                volume=combined_volume
            )

            self.current_bars[bar.symbol] = final_bar
            self._update_dataframe(final_bar)
            print(f'[DEBUG] Final bar committed from Alpaca: {final_bar}')
            self._bar_buffer[bar.symbol] = buffer[bars_per_custom:]
            return final_bar
    
        return None
    
    def handle_trade(self, trade):
        return self._update_current_bar(trade.symbol, trade.price, trade.size, trade.timestamp)
    
    def get_last_price(self, symbol):
        return self.last_prices[symbol]
