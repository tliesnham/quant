from abc import ABC, abstractmethod
import pandas as pd

class SlippageModel(ABC):
    @abstractmethod
    def get_execution_price(self, signal_price: float, trade_side: int, data_row: pd.Series) -> float:
        """
        Calculates the realistic execution price after accounting for slippage.
        
        :param signal_price: The ideal price at which the signal occurred (e.g., Close).
        :param trade_side: The direction of the trade (1 for buy, -1 for sell).
        :param data_row: The pandas Series representing the data for that day, containing necessary columns like ATR.
        :return: The adjusted execution price.
        """
        pass

class ATRBasedSlippage(SlippageModel):
    def __init__(self, atr_column_name: str, slippage_factor: float):
        self.atr_column_name = atr_column_name
        self.slippage_factor = slippage_factor

    def get_execution_price(self, signal_price: float, trade_side: int, data_row: pd.Series) -> float:
        """
        Adjusts the execution price based on the ATR value for the day.
        For buys, the price is adjusted up. For sells, it's adjusted down.
        """
        atr_value = data_row[self.atr_column_name]
        
        # If ATR is NaN (e.g., at the start of the data), assume no slippage
        if pd.isna(atr_value):
            return signal_price

        slippage_amount = atr_value * self.slippage_factor
        
        if trade_side == 1:  # Buy
            return signal_price + slippage_amount
        elif trade_side == -1:  # Sell
            return signal_price - slippage_amount
        else:
            return signal_price