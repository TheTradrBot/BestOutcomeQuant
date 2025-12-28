# MT5 FTMO Trading Bot

Automated MetaTrader 5 trading bot for FTMO 200K Challenge accounts. Uses a 7-Pillar Confluence system with ADX regime detection.

## Quick Start

```bash
# Run optimization
python ftmo_challenge_analyzer.py --trials 100

# Check optimization status
python ftmo_challenge_analyzer.py --status

# Run live bot (Windows VM with MT5)
python main_live_bot.py
```

## Project Structure

```
├── strategy_core.py          # Core trading logic (7 Confluence Pillars)
├── ftmo_challenge_analyzer.py # Optuna optimization & backtesting
├── main_live_bot.py          # Live MT5 trading entry point
├── config.py                 # Account settings, CONTRACT_SPECS
├── ftmo_config.py            # FTMO challenge rules & risk limits
├── docs/                     # Documentation (system guide, strategy analysis)
├── scripts/                  # Utility scripts (monitoring, debugging)
├── params/                   # Optimized parameters (current_params.json)
└── data/ohlcv/               # Historical OHLCV data (2003-2025)
```

## Optimization & Backtesting

The optimizer uses professional quant best practices:

- **TRAINING PERIOD**: January 1, 2023 – September 30, 2024 (in-sample optimization)
- **VALIDATION PERIOD**: October 1, 2024 – December 26, 2025 (out-of-sample test)
- **FINAL BACKTEST**: Full period 2023-2025 (December fully open for trading)
- **ADX > 25 trend-strength filter** applied to avoid ranging markets.

All trades from the final backtest are exported to:
`ftmo_analysis_output/all_trades_2023_2025_full.csv`

Parameters are saved to `params/current_params.json`

Optimization is resumable and can be checked with: `python ftmo_challenge_analyzer.py --status`

## Documentation

- [PROFESSIONAL_SYSTEM_GUIDE.md](docs/PROFESSIONAL_SYSTEM_GUIDE.md) - Full system documentation
- [TRADING_STRATEGY_ANALYSIS.txt](docs/TRADING_STRATEGY_ANALYSIS.txt) - Strategy deep dive
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - High-level project summary