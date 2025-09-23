class CustomBar:
    def __init__(self, symbol, timestamp, open_price, high_price, low_price, close_price, volume):
        self.symbol = symbol
        self.timestamp = timestamp   # start time of the bar
        self.open = open_price
        self.high = high_price
        self.low = low_price
        self.close = close_price
        self.volume = volume 

    def __repr__(self):
        return f'<Bar {self.symbol} {self.timestamp} O:{self.open} H:{self.high} L:{self.low} C:{self.close} V:{self.volume}>'       
