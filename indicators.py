from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict

class Indicator(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        pass

class SMAIndicator(Indicator):
    def __init__(self, period: int):
        super().__init__(f"SMA_{period}")
        self.period = period

    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        return {f"SMA_{self.period}": data['Close'].rolling(window=self.period).mean()}