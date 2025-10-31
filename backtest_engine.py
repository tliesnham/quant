class BacktestEngine:
    def __init__(self, strategy, initial_capital=100000, position_size=10000):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.position_size = position_size

        self.position_open = False

    def run_backtest(self):
        signal_generator = self.strategy.generate_signals()
        for date, signal in signal_generator:
            if signal == 1:  # Buy signal
                print(f"{date.date()}: Buy signal received.")
                self.position_open = True
            elif signal == -1:  # Sell signal
                print(f"{date.date()}: Sell signal received.")
                self.position_open = False
            else:
                print(f"{date.date()}: Hold signal received.")