from stock import Stock
from trading_strategy import MovingAverageStrategy
from backtest_engine import BacktestEngine

if __name__ == "__main__":
    START_DATE = "2020-01-01"
    END_DATE = "2025-01-01"

    aapl = Stock("AAPL", START_DATE, END_DATE)
    tqqq = Stock("TQQQ", START_DATE, END_DATE)

    aapl_ma = MovingAverageStrategy(aapl)

    pair_backtest = BacktestEngine([aapl, tqqq], aapl_ma)
    pair_backtest.run_backtest()