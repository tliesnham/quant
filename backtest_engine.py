import logging
import pandas as pd
import numpy as np

from data_provider import RiskFreeRateProvider
from slippage import SlippageModel

logging.basicConfig(filename="trades.log", level=logging.INFO)
logger = logging.getLogger(__name__)

class BacktestEngine:
    def __init__(self, assets, strategy, initial_capital=100000, position_size=1000, slippage_model: SlippageModel = None, risk_free_rate: RiskFreeRateProvider = None):
        self.assets = assets
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.peak_capital = initial_capital
        self.position_size = position_size
        self.slippage_model = slippage_model
        self.risk_free_rate = risk_free_rate

        # Calculate the capital allocated to each asset
        self.position_size_per_asset = self.position_size / len(self.assets)

        # Manages the state and entry price for each asset
        self.positions = {asset.symbol: {'open': False, 'price': 0} for asset in self.assets}
        
        self.max_drawdown = 0
        self.portfolio_history = [] # To store daily portfolio values for Sharpe Ratio

    def _get_total_asset_value(self, current_date):
        """Calculates the total market value of the portfolio for a given day."""
        total_value = self.initial_capital
        for asset in self.assets:
            if self.positions[asset.symbol]['open']:
                try:
                    current_price = asset.data.loc[current_date, 'Close']
                    buy_price = self.positions[asset.symbol]['price']
                    
                    # Calculate the current value of the open position
                    num_shares = self.position_size_per_asset / buy_price
                    market_value = num_shares * current_price
                    total_value += market_value
                except KeyError:
                    # If date is not in this asset's data, we can't value it.
                    # This can happen if assets have different trading calendars.
                    # We'll just use the cost basis in this rare case.
                    total_value += self.position_size_per_asset
        return total_value

    def run_backtest(self):
        print(f"--- Running Backtest for Assets: {[asset.symbol for asset in self.assets]} ---")
        print(f"--- Position Size Per Asset: ${self.position_size_per_asset:.2f} ---")
        if self.slippage_model:
            print(f"--- Slippage Model Applied: {self.slippage_model.__class__.__name__} ---")
        
        signal_generator = self.strategy.generate_signals()
        
        for date, signal in signal_generator:
            # Mark-to-market the portfolio at the start of each day
            self.portfolio_history.append({'date': date, 'value': self._get_total_asset_value(date)})

            if signal == 1:  # Buy signal
                if self.initial_capital < self.position_size:
                    logger.info(f"[{date}] Insufficient capital to open full position. Skipping buy signal.")
                    continue

                for asset in self.assets:
                    if not self.positions[asset.symbol]['open']:
                        try:
                            signal_price = asset.data.loc[date, 'Close']
                        except KeyError:
                            continue # Skip if asset has no data for this day
                        
                        # Apply slippage model to get execution price
                        execution_price = signal_price
                        if self.slippage_model:
                            execution_price = self.slippage_model.get_execution_price(signal_price, 1, asset.data.loc[date])

                        self.positions[asset.symbol]['open'] = True
                        self.positions[asset.symbol]['price'] = execution_price
                        self.initial_capital -= self.position_size_per_asset
                        logger.info(f"[{date}] BUY {asset.symbol} at ${execution_price:.2f} (Signal Price: ${signal_price:.2f}). Capital: ${self.initial_capital:.2f}")

            elif signal == -1:  # Sell signal
                for asset in self.assets:
                    if self.positions[asset.symbol]['open']:
                        try:
                            signal_price = asset.data.loc[date, 'Close']
                        except KeyError:
                            continue # Skip if asset has no data for this day

                        buy_price = self.positions[asset.symbol]['price']

                        # Apply slippage model to get execution price
                        execution_price = signal_price
                        if self.slippage_model:
                            execution_price = self.slippage_model.get_execution_price(signal_price, -1, asset.data.loc[date])

                        profit = self.calculate_delta(buy_price, execution_price, self.position_size_per_asset)
                        self.initial_capital += self.position_size_per_asset + profit

                        # Update peak capital and calculate drawdown
                        self.peak_capital = max(self.peak_capital, self.initial_capital)
                        drawdown = self.initial_capital - self.peak_capital
                        self.max_drawdown = min(self.max_drawdown, drawdown)
                        
                        logger.info(f"[{date}] SELL {asset.symbol} at ${execution_price:.2f} (Signal Price: ${signal_price:.2f}). P/L: ${profit:.2f}. Capital: ${self.initial_capital:.2f}")

                        # Reset position state
                        self.positions[asset.symbol]['open'] = False
                        self.positions[asset.symbol]['price'] = 0

        print("\n--- Backtest Finished ---")
        final_capital = self._get_total_asset_value(self.strategy.stock.data.index[-1])

        print(f"\nFinal Capital:   ${final_capital:.2f}")
        
        total_return = ((final_capital - 100000) / 100000) * 100
        print(f"Total Return:    {total_return:.2f}%")
        print(f"Max Drawdown:    ${self.max_drawdown:.2f}")

        # --- Sharpe Ratio Calculation ---
        portfolio_df = pd.DataFrame(self.portfolio_history).set_index('date')
        portfolio_df['daily_return'] = portfolio_df['value'].pct_change()
        
        # The risk-free rate from the provider is an ANNUALIZED rate.
        if self.risk_free_rate:
            # Create a series of annualized risk-free rates matching the portfolio's dates
            annualized_risk_free_rate = self.risk_free_rate.get_rate(portfolio_df.index)
            # Now, calculate the daily equivalent of the risk-free rate
            daily_risk_free_rate = annualized_risk_free_rate / 252
        else:
            daily_risk_free_rate = 0.0

        excess_returns = (portfolio_df['daily_return'] - daily_risk_free_rate).dropna()

        if not excess_returns.empty and excess_returns.std() != 0:
            # The mean of daily excess returns is then annualized by multiplying by sqrt(252)
            sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
            print(f"Sharpe Ratio:    {sharpe_ratio:.2f}")
        else:
            print("Sharpe Ratio:    N/A (no variance in returns or insufficient data)")

    def calculate_delta(self, price_buy, price_sell, position_size):
        # Calculates profit based on the number of shares for a given position size
        if price_buy == 0: return 0
        num_shares = position_size / price_buy
        return (price_sell - price_buy) * num_shares