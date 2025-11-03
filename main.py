from stock import Stock
from trading_strategy import MovingAverageStrategy
from backtest_engine import BacktestEngine

if __name__ == "__main__":
    aapl = Stock("AAPL", "2020-01-01", "2025-01-01")
    tqqq = Stock("TQQQ", "2020-01-01", "2025-01-01")
    aapl_ma = MovingAverageStrategy(aapl)

    pair_backtest = BacktestEngine([aapl, tqqq], aapl_ma)
    pair_backtest.run_backtest()