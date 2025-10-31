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
            # You must now reference the new, full column names
            if day.SMA_20 > day.Close: # <-- Renamed columns
                signal = -1  # Sell signal
            elif day.SMA_20 < day.Close:
                signal = 1   # Buy signal
            yield (day.Index, signal)