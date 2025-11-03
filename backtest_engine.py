class BacktestEngine:
    def __init__(self, assets, strategy, initial_capital=100000, position_size=1000):
        self.assets = assets
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.peak_capital = initial_capital
        self.position_size = position_size

        # Calculate the capital allocated to each asset
        self.position_size_per_asset = self.position_size / len(self.assets)

        # Manages the state and entry price for each asset
        self.positions = {asset.symbol: {'open': False, 'price': 0} for asset in self.assets}
        
        self.max_drawdown = 0

    def run_backtest(self):
        print(f"--- Running Backtest for Assets: {[asset.symbol for asset in self.assets]} ---")
        print(f"--- Position Size Per Asset: ${self.position_size_per_asset:.2f} ---")
        
        signal_generator = self.strategy.generate_signals()
        
        for date, signal in signal_generator:
            if signal == 1:  # Buy signal
                # Check for sufficient total capital before entering new positions
                if self.initial_capital < self.position_size:
                    print(f"[{date}] Insufficient capital to open full position. Skipping buy signal.")
                    continue

                for asset in self.assets:
                    if not self.positions[asset.symbol]['open']:
                        current_price = asset.data.loc[date, 'Close']
                        self.positions[asset.symbol]['open'] = True
                        self.positions[asset.symbol]['price'] = current_price
                        self.initial_capital -= self.position_size_per_asset
                        print(f"[{date}] BUY {asset.symbol} at ${current_price:.2f}. Capital: ${self.initial_capital:.2f}")

            elif signal == -1:  # Sell signal
                for asset in self.assets:
                    if self.positions[asset.symbol]['open']:
                        current_price = asset.data.loc[date, 'Close']
                        buy_price = self.positions[asset.symbol]['price']

                        profit = self.calculate_delta(buy_price, current_price, self.position_size_per_asset)
                        self.initial_capital += self.position_size_per_asset + profit

                        # Update peak capital and calculate drawdown
                        self.peak_capital = max(self.peak_capital, self.initial_capital)
                        drawdown = self.initial_capital - self.peak_capital
                        self.max_drawdown = min(self.max_drawdown, drawdown)
                        
                        print(f"[{date}] SELL {asset.symbol} at ${current_price:.2f}. P/L: ${profit:.2f}. Capital: ${self.initial_capital:.2f}")

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
                print(f"Closing open {asset.symbol} position at last price ${last_price:.2f} for P/L of ${profit:.2f}")

        print(f"\nFinal Capital:   ${final_capital:.2f}")
        print(f"Max Drawdown:    ${self.max_drawdown:.2f}")
        
        total_return = ((final_capital - 100000) / 100000) * 100
        print(f"Total Return:    {total_return:.2f}%")

    def calculate_delta(self, price_buy, price_sell, position_size):
        # Calculates profit based on the number of shares for a given position size
        num_shares = position_size / price_buy
        return (price_sell - price_buy) * num_shares