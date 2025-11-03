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