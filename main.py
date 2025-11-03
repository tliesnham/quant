from stock import Stock
from indicators import SMAIndicator
from trading_strategy import MovingAverageStrategy
from backtest_engine import BacktestEngine

if __name__ == "__main__":
    START_DATE = "2020-01-01"
    END_DATE = "2025-01-01"

    spy = Stock("SPY", START_DATE, END_DATE)
    tlt = Stock("TLT", START_DATE, END_DATE)

    spy_sma_20 = SMAIndicator(period=20)
    spy.add_indicator(spy_sma_20)

    # Create the strategy using the SAME indicator instance
    spy_ma_strategy = MovingAverageStrategy(spy, sma_indicator=spy_sma_20)

    # Example pair strategy with the MovingAverageStrategy
    pair_backtest = BacktestEngine([spy, tlt], strategy=spy_ma_strategy)
    pair_backtest.run_backtest()
