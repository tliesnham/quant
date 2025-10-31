class BacktestEngine:
    def __init__(self, strategy, initial_capital=100000, position_size=1000):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.position_size = position_size

        self.position_open = False
        self.position_price = 0

    def run_backtest(self):
        print("--- Running Backtest ---")
        signal_generator = self.strategy.generate_signals()
        
        for date, signal in signal_generator:
            # Ensure we have data for the given date
            if date not in self.strategy.stock.data.index:
                continue

            current_price = self.strategy.stock.data.loc[date, 'Close']

            if signal == 1:  # Buy signal
                if self.initial_capital < self.position_size:
                    print(f"Insufficient capital to open position on {date}.")
                    continue
                if not self.position_open:
                    self.position_open = True
                    self.position_price = current_price
                    # The cost of the position is the position_size
                    self.initial_capital -= self.position_size
                    print(f"[{date}] BUY signal. Opened position at ${current_price:.2f}. Capital: ${self.initial_capital:.2f}")

            elif signal == -1:  # Sell signal
                if self.position_open:
                    # Calculate profit/loss based on position size and price change
                    profit = self.calculate_delta(self.position_price, current_price)
                    
                    # The return is the original position size plus the profit
                    self.initial_capital += self.position_size + profit
                    
                    print(f"[{date}] SELL signal. Closed position at ${current_price:.2f}. P/L: ${profit:.2f}. Capital: ${self.initial_capital:.2f}")
                    self.position_open = False
                    self.position_price = 0

        print("\n--- Backtest Finished ---")
        final_capital = self.initial_capital
        # If a position is still open at the end, calculate its current value
        if self.position_open:
            last_price = self.strategy.stock.data['Close'][-1]
            profit = self.calculate_delta(self.position_price, last_price)
            final_capital += self.position_size + profit
            print("Position still open at end of backtest.")
            print(f"Closing at last price ${last_price:.2f} for P/L of ${profit:.2f}")

        print(f"Initial Capital: ${self.initial_capital:.2f}")
        print(f"Final Capital:   ${final_capital:.2f}")
        
        total_return = ((final_capital - 100000) / 100000) * 100
        print(f"Total Return:    {total_return:.2f}%")

    def calculate_delta(self, price_buy, price_sell):
        # This should calculate the actual profit based on the number of shares
        num_shares = self.position_size / price_buy
        return (price_sell - price_buy) * num_shares