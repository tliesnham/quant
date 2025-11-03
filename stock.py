import pandas as pd
import yfinance as yf

from indicators import SMAIndicator

class Stock:
    def __init__(self, ticker: str, start_date: str, end_date: str):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

        # Fetch historical data
        self.data = self._fetch_data()

        # Add technical indicators
        self._add_technical_indicators()

        # Flatten MultiIndex columns if present and rename Close column
        self._flatten_columns_and_rename()

    def _flatten_columns_and_rename(self):
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = ['_'.join(map(str, col)).strip('_') for col in self.data.columns.values]

        # Rename the Close column to a standard name
        self.data.rename(columns={f'Close_{self.ticker}': 'Close'}, inplace=True)

    def _fetch_data(self):
        return yf.download(self.ticker, start=self.start_date, end=self.end_date, auto_adjust=True)

    def _add_technical_indicators(self):
        # Dictionary to hold indicator columns
        indicators = {}
        sma_indicator = SMAIndicator(20)
        indicators.update(sma_indicator.calculate(self.data))

        self.data = self.data.assign(**indicators)  