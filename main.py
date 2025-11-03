from stock import Stock
from indicators import SMAIndicator, ATRIndicator
from trading_strategy import MovingAverageStrategy
from backtest_engine import BacktestEngine
from slippage import ATRBasedSlippage

if __name__ == "__main__":
    START_DATE = "2020-01-01"
    END_DATE = "2025-01-01"

    spy = Stock("SPY", START_DATE, END_DATE)
    tlt = Stock("TLT", START_DATE, END_DATE)

    # Add SMA 20 day indicator to SPY
    spy_sma_20 = SMAIndicator(period=20)
    spy.add_indicator(spy_sma_20)

    # Add ATR indicator for slippage model
    spy_atr_14 = ATRIndicator(period=14)
    spy.add_indicator(spy_atr_14)

    tlt_atr_14 = ATRIndicator(period=14)
    tlt.add_indicator(tlt_atr_14)

    # Create the ATR-based slippage model
    atr_slippage = ATRBasedSlippage(atr_column_name=spy_atr_14.column_name, slippage_factor=0.5)

    # Create the strategy using the SAME indicator instance
    spy_ma_strategy = MovingAverageStrategy(spy, sma_indicator=spy_sma_20)

    # Example pair strategy with the MovingAverageStrategy
    pair_backtest = BacktestEngine([spy, tlt], strategy=spy_ma_strategy, slippage_model=atr_slippage)
    pair_backtest.run_backtest()

    spy.dump()