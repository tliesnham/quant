import pandas as pd
import yfinance as yf
import csv

class Stock:
    def __init__(self, ticker: str, start_date: str, end_date: str):
        self.symbol = ticker
        self.start_date = start_date
        self.end_date = end_date

        # Fetch historical data
        self.data = self._fetch_data()

        # Flatten MultiIndex columns if present and rename Close column
        self._flatten_columns_and_rename()

    def _flatten_columns_and_rename(self):
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = ['_'.join(map(str, col)).strip('_') for col in self.data.columns.values]

        # Rename the Close column to a standard name
        if f'Close_{self.symbol}' in self.data.columns:
            self.data.rename(columns={f'Close_{self.symbol}': 'Close'}, inplace=True)

        # Rename the High and Low columns to standard names if they exist
        if f'High_{self.symbol}' in self.data.columns:
            self.data.rename(columns={f'High_{self.symbol}': 'High'}, inplace=True)
        if f'Low_{self.symbol}' in self.data.columns:
            self.data.rename(columns={f'Low_{self.symbol}': 'Low'}, inplace=True)

    def _fetch_data(self):
        return yf.download(self.symbol, start=self.start_date, end=self.end_date, auto_adjust=True)

    def add_indicator(self, indicator):
        """Applies a single indicator to the stock's data."""
        indicator_data = indicator.calculate(self.data)
        self.data = self.data.assign(**indicator_data)  
    
    def dump(self):
        with open(f"{self.symbol}_data_dump.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.data.columns)
            for index, row in self.data.iterrows():
                writer.writerow([index] + row.tolist())