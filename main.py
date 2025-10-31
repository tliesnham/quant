import pandas as pd

from stock import Stock
from trading_strategy import MovingAverageStrategy
from backtest_engine import BacktestEngine

if __name__ == "__main__":
    # Try a more volatile stock that likely had crossovers
    spy = Stock("AAPL", "2022-01-01", "2023-01-01")  # SPY during 2022 bear market
    d20_ma = MovingAverageStrategy(spy)

    backtest = BacktestEngine(d20_ma)
    backtest.run_backtest()
