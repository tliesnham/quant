from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict

class Indicator(ABC):
    @property
    @abstractmethod
    def column_name(self) -> str:
        """The name of the column this indicator will generate."""
        pass

    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        pass

class SMAIndicator(Indicator):
    def __init__(self, period: int):
        self.period = period
        self._column_name = f"SMA_{self.period}"

    @property
    def column_name(self) -> str:
        return self._column_name

    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        return {self.column_name: data['Close'].rolling(window=self.period).mean()}

class ATRIndicator(Indicator):
    def __init__(self, period: int = 14):
        self.period = period
        self._column_name = f"ATR_{self.period}"

    @property
    def column_name(self) -> str:
        return self._column_name

    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculates the Average True Range (ATR)."""
        data_copy = data.copy()
        
        # Calculate the components of True Range
        high_low = data_copy['High'] - data_copy['Low']
        high_prev_close = abs(data_copy['High'] - data_copy['Close'].shift(1))
        low_prev_close = abs(data_copy['Low'] - data_copy['Close'].shift(1))

        # Determine the True Range (TR)
        tr = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)

        # Calculate the Average True Range (ATR) using an exponential moving average
        atr = tr.ewm(span=self.period, adjust=False).mean()
        return {self.column_name: atr}
