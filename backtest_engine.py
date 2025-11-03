import logging

from slippage import SlippageModel

logging.basicConfig(filename="trades.log", level=logging.INFO)
logger = logging.getLogger(__name__)

class BacktestEngine:
    def __init__(self, assets, strategy, initial_capital=100000, position_size=1000, slippage_model: SlippageModel = None):
        self.assets = assets
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.peak_capital = initial_capital
        self.position_size = position_size
        self.slippage_model = slippage_model

        # Calculate the capital allocated to each asset
        self.position_size_per_asset = self.position_size / len(self.assets)

        # Manages the state and entry price for each asset
        self.positions = {asset.symbol: {'open': False, 'price': 0} for asset in self.assets}
        
        self.max_drawdown = 0

    def run_backtest(self):
        print(f"--- Running Backtest for Assets: {[asset.symbol for asset in self.assets]} ---")
        print(f"--- Position Size Per Asset: ${self.position_size_per_asset:.2f} ---")
        if self.slippage_model:
            print(f"--- Slippage Model Applied: {self.slippage_model.__class__.__name__} ---")
        
        signal_generator = self.strategy.generate_signals()
        
        for date, signal in signal_generator:
            if signal == 1:  # Buy signal
                if self.initial_capital < self.position_size:
                    logger.info(f"[{date}] Insufficient capital to open full position. Skipping buy signal.")
                    continue

                for asset in self.assets:
                    if not self.positions[asset.symbol]['open']:
                        signal_price = asset.data.loc[date, 'Close']
                        
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
                        signal_price = asset.data.loc[date, 'Close']
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
        final_capital = self.initial_capital
        
        # Liquidate any open positions at the end of the backtest
        for asset in self.assets:
            if self.positions[asset.symbol]['open']:
                last_price = asset.data['Close'].iloc[-1]
                buy_price = self.positions[asset.symbol]['price']
                profit = self.calculate_delta(buy_price, last_price, self.position_size_per_asset)
                final_capital += self.position_size_per_asset + profit
                logger.info(f"Closing open {asset.symbol} position at last price ${last_price:.2f} for P/L of ${profit:.2f}")

        print(f"\nFinal Capital:   ${final_capital:.2f}")
        print(f"Max Drawdown:    ${self.max_drawdown:.2f}")
        
        total_return = ((final_capital - 100000) / 100000) * 100
        print(f"Total Return:    {total_return:.2f}%")

    def calculate_delta(self, price_buy, price_sell, position_size):
        # Calculates profit based on the number of shares for a given position size
        num_shares = position_size / price_buy
        return (price_sell - price_buy) * num_shares