from stock import Stock
from trading_strategy import MovingAverageStrategy, PairMovingAverageStrategy
from backtest_engine import BacktestEngine, PairBacktestEngine

if __name__ == "__main__":
    spy = Stock("SPY", "2020-01-01", "2025-01-01")
    d20_ma = MovingAverageStrategy(spy)

    backtest = BacktestEngine(d20_ma)
    backtest.run_backtest()

    #aapl = Stock("AAPL", "2020-01-01", "2025-01-01")
    #gld = Stock("GLD", "2020-01-01", "2025-01-01")
    #aapl_ma = PairMovingAverageStrategy(aapl, gld)

    #pair_backtest = PairBacktestEngine(aapl_ma)
    #pair_backtest.run_backtest()