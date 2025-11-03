from abc import ABC, abstractmethod
from typing import Generator
import pandas as pd
from stock import Stock
from indicators import SMAIndicator

class TradingStrategy(ABC):
    def __init__(self, stock: Stock):
        self.stock = stock

    @abstractmethod
    def generate_signals(self) -> Generator:
        pass

class MovingAverageStrategy(TradingStrategy):
    def __init__(self, stock: Stock, sma_indicator: SMAIndicator):
        super().__init__(stock)
        self.sma_column = sma_indicator.column_name
        self.prev_position = 0

    def generate_signals(self) -> Generator:
        data = self.stock.data
        
        # CRITICAL: Check if the required data column exists.
        if data is None or self.sma_column not in data.columns:
            print(f"Warning: SMA column '{self.sma_column}' not found in data for {self.stock.symbol}.")
            print(f"Did you forget to call `add_indicator` with the correct SMAIndicator instance?")
            # Yield no signals if the data is missing.
            if data is not None:
                for day in data.itertuples():
                    yield (day.Index, 0)
            return

        # Find the first day where the SMA is not NaN to initialize prev_position
        first_valid_day_series = data[data[self.sma_column].notna()]
        if first_valid_day_series.empty:
            # If no valid SMA values exist, yield no signals for the entire dataset
            for day in data.itertuples():
                yield (day.Index, 0)
            return

        first_valid_day = first_valid_day_series.iloc[0]
        if first_valid_day.Close > first_valid_day[self.sma_column]:
            self.prev_position = 1
        elif first_valid_day.Close < first_valid_day[self.sma_column]:
            self.prev_position = -1

        for day in data.itertuples():
            signal = 0
            
            # Skip days before the moving average is calculated
            if pd.isna(getattr(day, self.sma_column)):
                yield (day.Index, signal)
                continue

            # Determine current position (1 for above, -1 for below)
            current_position = 1 if day.Close > getattr(day, self.sma_column) else -1

            # Generate signal only on a crossover event
            if current_position != self.prev_position:
                signal = current_position
            
            yield (day.Index, signal)

            # CRITICAL: Update previous position for the next day's comparison
            self.prev_position = current_position