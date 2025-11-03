# Python Quantitative Trading Backtesting Engine

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)

A modular and extensible backtesting engine written in Python for developing and evaluating quantitative trading strategies. This engine is designed with a clear separation of concerns, allowing developers to easily create and test new indicators, strategies, and slippage models without modifying the core backtesting logic.

## Key Features

- **Modular Architecture:** Decouples data handling (`Stock`), calculations (`Indicator`), logic (`TradingStrategy`), simulation (`BacktestEngine`), and transaction costs (`SlippageModel`).
- **Extensible by Design:** Easily add new components by inheriting from the provided abstract base classes.
- **Realistic Simulations:** Includes a flexible slippage model framework to simulate transaction costs for more realistic results.
- **Multi-Asset Capability:** Backtest strategies on single assets or a portfolio of multiple assets (e.g., pairs trading).
- **Data Inspection:** A built-in `dump()` method on the `Stock` class allows for easy inspection and debugging of the underlying DataFrame at any stage.
- **Robust and Safe:** The framework includes checks to ensure that strategies and models have the data they need, preventing silent failures and providing clear warnings.

## Architecture Overview

The engine's architecture is built on five key components:

1.  **`Stock`**: A data container that fetches and holds the historical price data for a single asset. It provides an interface to apply indicators and a `dump()` method to export its data to a CSV file for analysis.
2.  **`Indicator`**: A "calculation recipe" that defines a technical indicator (e.g., SMA, ATR). It takes in price data and returns a new data column.
3.  **`TradingStrategy`**: The "logic" component. It consumes data from one or more indicators and generates `buy` (1), `sell` (-1), or `hold` (0) signals.
4.  **`SlippageModel`**: A model for simulating transaction costs. It adjusts the execution price of a trade based on market conditions, such as volatility (e.g., using ATR).
5.  **`BacktestEngine`**: The simulation engine. It takes signals from a strategy, applies a slippage model, and executes trades against a set of assets, managing capital and calculating performance.

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

The main entry point for running a backtest is `main.py`. Here, you orchestrate the setup of assets, indicators, strategies, and slippage models.

```python
# main.py

from stock import Stock
from indicators import SMAIndicator, ATRIndicator
from trading_strategy import MovingAverageStrategy
from backtest_engine import BacktestEngine
from slippage import ATRBasedSlippage

if __name__ == "__main__":
    START_DATE = "2022-01-01"
    END_DATE = "2023-01-01"

    # 1. Define assets and add indicators
    spy = Stock("SPY", START_DATE, END_DATE)
    spy_sma = SMAIndicator(period=50)
    spy_atr = ATRIndicator(period=14)
    spy.add_indicator(spy_sma)
    spy.add_indicator(spy_atr)

    # For debugging, you can inspect the data at any time:
    # spy.dump("spy_data_with_indicators.csv")

    # 2. Create the strategy, linking it to the indicator instance
    spy_ma_strategy = MovingAverageStrategy(spy, sma_indicator=spy_sma)

    # 3. Create the slippage model, linking it to the ATR indicator
    slippage_model = ATRBasedSlippage(atr_column_name=spy_atr.column_name, slippage_factor=0.5)

    # 4. Initialize and run the backtest engine
    backtest = BacktestEngine(
        assets=[spy], 
        strategy=spy_ma_strategy,
        slippage_model=slippage_model
    )
    backtest.run_backtest()
```

## How to Extend the Engine

The primary strength of this project is its extensibility.

### 1. Creating a New Indicator

Create a new class in `indicators.py` that inherits from `Indicator` and implements the `column_name` property and the `calculate` method.

```python
# in indicators.py
class RSIIndicator(Indicator):
    # ... implementation ...
```

### 2. Creating a New Trading Strategy

Create a new class in `trading_strategy.py` that inherits from `TradingStrategy`. The constructor should accept the indicator object(s) it depends on.

```python
# in trading_strategy.py
class RSIStrategy(TradingStrategy):
    # ... implementation ...
```

### 3. Creating a New Slippage Model

Create a new class in `slippage.py` that inherits from `SlippageModel` and implements the `get_execution_price` method.

```python
# in slippage.py
class FixedSlippage(SlippageModel):
    def __init__(self, slippage_points: float):
        self.slippage_points = slippage_points

    def get_execution_price(self, signal_price: float, trade_side: int, data_row: pd.Series) -> float:
        return signal_price + (self.slippage_points * trade_side)
```


