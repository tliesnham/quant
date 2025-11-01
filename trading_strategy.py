from abc import ABC, abstractmethod

from stock import Stock

class TradingStrategy(ABC):
    def __init__(self, stock: Stock):
        self.stock = stock

    @abstractmethod
    def generate_signals(self):
        pass

class MovingAverageStrategy(TradingStrategy):
    def __init__(self, stock: Stock):
        super().__init__(stock)

    def generate_signals(self):
        data = self.stock.data

        for day in data.itertuples():
            signal = 0
            if day.SMA_20 > day.Close:
                signal = -1
            elif day.SMA_20 < day.Close:
                signal = 1
            yield (day.Index, signal)

class PairMovingAverageStrategy(TradingStrategy):
    def __init__(self, signal_stock: Stock, pair_stock: Stock):
        super().__init__(signal_stock)
        self.pair_stock = pair_stock

    def generate_signals(self):
        signal_data = self.stock.data

        for day in signal_data.itertuples():
            signal = 0
            if day.SMA_20 > day.Close:
                signal = -1
            elif day.SMA_20 < day.Close:
                signal = 1
            yield (day.Index, signal)