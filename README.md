# Python Quantitative Trading Backtesting Engine

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)

A modular and extensible backtesting engine written in Python for developing and evaluating quantitative trading strategies. This engine is designed with a clear separation of concerns, allowing developers to easily create and test new indicators and strategies without modifying the core backtesting logic.

## Key Features

- **Modular Architecture:** Decouples data handling (`Stock`), calculations (`Indicator`), logic (`TradingStrategy`), and simulation (`BacktestEngine`).
- **Extensible by Design:** Easily add new indicators or complex trading strategies by inheriting from base classes.
- **Multi-Asset Capability:** Backtest strategies on single assets or a portfolio of multiple assets (e.g., pairs trading).
- **Clear and Readable:** The design encourages explicit and readable strategy definitions, reducing common errors.
- **Robust and Safe:** Strategies automatically validate that their required data columns exist, preventing silent failures.

## Architecture Overview

The engine's architecture is built on four key components:

1.  **`Stock`**: A data container that fetches and holds the historical price data for a single asset. It provides a simple interface to have indicators applied to its data.
2.  **`Indicator`**: A "calculation recipe" that defines a technical indicator (e.g., SMA, RSI). It takes in price data and returns a new data column.
3.  **`TradingStrategy`**: The "logic" component. It consumes data from one or more indicators and generates `buy` (1), `sell` (-1), or `hold` (0) signals.
4.  **`BacktestEngine`**: The simulation engine. It takes signals from a strategy and executes them against a set of assets, managing capital, tracking positions, and calculating performance metrics.

## Getting Started

### Prerequisites

- Python 3.9 or higher

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tliesnham/quant.git
    cd quant/backtest
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *Note: While `venv` and `pip` are used in this example, other package managers like `uv`, `conda`, or `poetry` will also work perfectly.*

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The main entry point for running a backtest is `main.py`. Here, you orchestrate the setup of assets, indicators, and strategies.

```python
# main.py

from stock import Stock
from indicators import SMAIndicator
from trading_strategy import MovingAverageStrategy
from backtest_engine import BacktestEngine

if __name__ == "__main__":
    START_DATE = "2022-01-01"
    END_DATE = "2023-01-01"

    # --- Example 1: Single Asset Strategy ---
    
    # 1. Define the asset and the indicator
    spy = Stock("SPY", START_DATE, END_DATE)
    spy_sma_50 = SMAIndicator(period=50)

    # 2. Add the indicator to the asset's data
    spy.add_indicator(spy_sma_50)

    # 3. Create the strategy, linking it to the indicator instance
    spy_ma_strategy = MovingAverageStrategy(spy, sma_indicator=spy_sma_50)

    # 4. Initialize and run the backtest engine
    single_asset_backtest = BacktestEngine(assets=[spy], strategy=spy_ma_strategy)
    single_asset_backtest.run_backtest()


    # --- Example 2: Pair Trading Strategy ---

    # 1. Define the assets for the pair
    tlt = Stock("TLT", START_DATE, END_DATE)
    
    # The same signal from the SPY strategy will be used to trade both assets
    
    # 2. Initialize the engine with multiple assets
    pair_backtest = BacktestEngine(assets=[spy, tlt], strategy=spy_ma_strategy)
    pair_backtest.run_backtest()
```

## How to Extend the Engine

The primary strength of this project is its extensibility.

### 1. Creating a New Indicator

To create a new indicator (e.g., Relative Strength Index - RSI):

1.  Create a new class in `indicators.py` that inherits from `Indicator`.
2.  Implement the `column_name` property and the `calculate` method.

```python
# in indicators.py
class RSIIndicator(Indicator):
    def __init__(self, period: int = 14):
        self.period = period
        self._column_name = f"RSI_{self.period}"

    @property
    def column_name(self) -> str:
        return self._column_name

    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        # ... RSI calculation logic ...
        # return {self.column_name: rsi_series}
        pass
```

### 2. Creating a New Trading Strategy

To create a new strategy that trades on your new indicator:

1.  Create a new class in `trading_strategy.py` that inherits from `TradingStrategy`.
2.  The constructor should accept the indicator object(s) it depends on.
3.  Implement the `generate_signals` method to produce a stream of signals.

```python
# in trading_strategy.py
class RSIStrategy(TradingStrategy):
    def __init__(self, stock: Stock, rsi_indicator: RSIIndicator, upper_bound=70, lower_bound=30):
        super().__init__(stock)
        self.rsi_column = rsi_indicator.column_name
        # ... other params

    def generate_signals(self) -> Generator:
        # ... logic to generate signals based on RSI oversold/overbought levels ...
        pass
```


