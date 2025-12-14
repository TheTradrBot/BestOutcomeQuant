# FTMO 200K Trading Bot

A MetaTrader 5 automated trading bot designed for FTMO 200K challenge accounts, with an integrated optimization system.

## Components

### 1. main_live_bot.py
The primary live trading bot that:
- Runs 24/7 on a Windows VM with MetaTrader 5
- Executes trades using the "7 Confluence Pillars" strategy
- Includes comprehensive risk management for FTMO compliance
- Supports 34 assets (Forex, Metals, Crypto, Indices)

### 2. ftmo_challenge_analyzer.py
An optimization engine that:
- Backtests main_live_bot.py using 2024 historical data
- Runs multiple optimization iterations
- Automatically updates main_live_bot.py with best-performing parameters
- Generates detailed performance reports

## Trading Strategy

The bot employs a "7 Confluence Pillars" strategy:
1. HTF Bias (Monthly/Weekly/Daily trend)
2. Location (S/R zones)
3. Fibonacci (Golden Pocket)
4. Liquidity (Sweep near equal highs/lows)
5. Structure (BOS/CHoCH alignment)
6. Confirmation (4H candle patterns)
7. Risk:Reward (Min 1:1)

## Risk Management

- Dynamic position sizing (0.75-0.95% base risk)
- Maximum 5 concurrent trades, 6 pending orders
- Pre-trade FTMO rule violation checks
- 5 risk modes: Aggressive, Normal, Conservative, Ultra-Safe, Halted

## Setup

### Environment Variables
Create a `.env` file with:
```
MT5_SERVER=FTMO-Demo
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
OANDA_API_KEY=your_oanda_key
OANDA_ACCOUNT_ID=your_account_id
```

### Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Live Trading (Windows VM with MT5)
```bash
python main_live_bot.py
```

### Run Optimization
```bash
python ftmo_challenge_analyzer.py
```

### Status Server
```bash
python main.py
```

## Project Structure

```
├── main_live_bot.py          # Live trading bot
├── ftmo_challenge_analyzer.py # Optimization engine
├── strategy_core.py          # Core strategy logic
├── ftmo_config.py            # FTMO configuration
├── tradr/                    # Trading infrastructure
│   ├── mt5/                  # MT5 client
│   ├── risk/                 # Risk management
│   └── data/                 # Data providers
├── data/ohlcv/               # Historical data (2023-2024)
├── ftmo_analysis_output/     # Analysis results
└── ftmo_optimization_backups/ # Optimization iterations
```

## License

Private - For personal use only.
