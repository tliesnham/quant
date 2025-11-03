from abc import ABC, abstractmethod
from typing import Generator
import pandas as pd
from stock import Stock

class TradingStrategy(ABC):
    def __init__(self, stock: Stock):
        self.stock = stock

    @abstractmethod
    def generate_signals(self) -> Generator:
        pass

class MovingAverageStrategy(TradingStrategy):
    def __init__(self, stock: Stock):
        super().__init__(stock)
        self.prev_position = 0  # 1 for above MA, -1 for below MA

    def generate_signals(self) -> Generator:
        data = self.stock.data
        
        # Ensure data and the SMA column exist
        if data is None or 'SMA' not in data.columns:
            # If not, we cannot generate signals. Yield 0 for all days if data exists.
            if data is not None:
                for day in data.itertuples():
                    yield (day.Index, 0)
            return

        # Find the first day where the SMA is not NaN to initialize prev_position
        first_valid_day_series = data[data['SMA'].notna()]
        if first_valid_day_series.empty:
            # If no valid SMA values exist, yield no signals for the entire dataset
            for day in data.itertuples():
                yield (day.Index, 0)
            return

        first_valid_day = first_valid_day_series.iloc[0]
        if first_valid_day.Close > first_valid_day.SMA:
            self.prev_position = 1
        elif first_valid_day.Close < first_valid_day.SMA:
            self.prev_position = -1

        for day in data.itertuples():
            signal = 0
            
            # Skip days before the moving average is calculated
            if pd.isna(day.SMA):
                yield (day.Index, signal)
                continue

            # Determine current position (1 for above, -1 for below)
            current_position = 1 if day.Close > day.SMA else -1

            # Generate signal only on a crossover event
            if current_position != self.prev_position:
                signal = current_position
            
            yield (day.Index, signal)

            # CRITICAL: Update previous position for the next day's comparison
            self.prev_position = current_position