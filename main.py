from stock import Stock
from trading_strategy import MovingAverageStrategy
from backtest_engine import BacktestEngine

if __name__ == "__main__":
    spy = Stock("AAPL", "2020-01-01", "2023-01-01")
    d20_ma = MovingAverageStrategy(spy)

    backtest = BacktestEngine(d20_ma)
    backtest.run_backtest()
    print(f"Final capital: ${backtest.initial_capital:.2f}")