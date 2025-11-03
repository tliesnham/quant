import yfinance as yf
import pandas as pd

class RiskFreeRateProvider:
    """
    A data provider for fetching and managing historical risk-free rate data.
    Uses the 13-week Treasury Bill (^IRX) as a proxy for the risk-free rate.
    """
    def __init__(self, start_date, end_date):
        self._data = self._fetch_data(start_date, end_date)

    def _fetch_data(self, start_date, end_date):
        """
        Fetches and cleans the risk-free rate data from Yahoo Finance.
        """
        print("Fetching risk-free rate data (^IRX)...")
        # Use auto_adjust=False for better reliability with index tickers.
        data = yf.download('^IRX', start=start_date, end=end_date, progress=False, auto_adjust=False)
        
        if data is None or data.empty or 'Adj Close' not in data.columns:
            print("Warning: Could not fetch risk-free rate data. Defaulting to 0.")
            return pd.Series(0.0, name='risk_free_rate')

        # The 'Adj Close' for ^IRX is the annualized yield as a percentage.
        # Convert it to a decimal. Squeeze ensures we have a Series, not a DataFrame.
        risk_free_rate = data['Adj Close'].squeeze() / 100
        
        # The data has NaNs on non-trading days. First, forward-fill, then back-fill.
        # This ensures that any NaNs at the beginning of the series are also handled.
        risk_free_rate = risk_free_rate.ffill().bfill()

        if risk_free_rate.isnull().all():
            print("Warning: Risk-free rate data is all NaN after cleaning. Defaulting to 0.")
            return pd.Series(0.0, name='risk_free_rate')
            
        return risk_free_rate.rename('risk_free_rate')

    def get_rate(self, dates):
        """
        Gets the risk-free rate for a series of dates.
        For each date in the input, it finds the last known rate.
        This is the correct and efficient pandas-native way to do this lookup.
        """
        # Reindex the stored data to match the requested dates, forward-filling any gaps.
        # .fillna(0.0) handles cases where dates are before the start of the data.
        return self._data.reindex(dates, method='ffill').fillna(0.0)
