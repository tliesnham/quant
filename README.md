# Quantitative Trading Backtest Engine

This project is a simple backtesting engine for quantitative trading strategies.

## Prerequisites

- Python 3.x

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tliesnham/quant.git
    cd quant/backtest
    ```

2.  **Create a virtual environment:**
    It's recommended to use a virtual environment to manage dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    Install the required Python packages from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

## Running the Backtest

To run the backtesting simulation, execute the `main.py` script:
```bash
python3 main.py
```

This will run the moving average crossover strategy defined in the code and print the backtest results to the console.

