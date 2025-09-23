from strats.base_strategy import BaseStrategy

class Test1(BaseStrategy):
    def __init__(self,):
        super().__init__('Test1', max_lookback=1)

    def generate_signals(self, data):
        return super().generate_signals(data)