from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, name='BaseStrategy', max_lookback=1):
        self.name = name
        self.max_lookback = max_lookback
        
    @abstractmethod
    def generate_signals(self, data):
        pass