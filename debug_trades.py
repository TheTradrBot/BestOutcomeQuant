#!/usr/bin/env python3
"""Debug single asset to see where trades block"""
import sys
from datetime import datetime, timedelta
from ftmo_challenge_analyzer import (
    load_ohlcv_data, get_all_trading_assets, 
    run_full_period_backtest
)
from backtest import simulate_trades
from strategy_core import StrategyParams, detect_regime

assets = get_all_trading_assets()
symbol = assets[0]  # First asset

start = datetime(2023, 1, 1)
end = datetime(2024, 3, 31)

print(f"Testing {symbol}...")

# Load data
d1 = load_ohlcv_data(symbol, "D1", start - timedelta(days=100), end)
h4 = load_ohlcv_data(symbol, "H4", start - timedelta(days=50), end)
w1 = load_ohlcv_data(symbol, "W1", start - timedelta(days=365), end)
mn = load_ohlcv_data(symbol, "MN", start - timedelta(days=730), end)

print(f"  D1 candles: {len(d1)}")
if not d1 or len(d1) < 30:
    print("  ✗ Not enough D1 data")
    sys.exit(1)

# Check regime
regime = detect_regime(d1, adx_trend_threshold=25.0, adx_range_threshold=20.0, use_adx_slope_rising=False)
print(f"  Regime: {regime['mode']} (ADX={regime.get('adx', 0):.1f})")

# Create params with VERY relaxed settings
params = StrategyParams(
    min_confluence=2,           # Minimum possible
    min_quality_factors=0,      # No quality requirement
    trend_min_confluence=2,
    range_min_confluence=1,
    risk_per_trade_pct=0.5,
)

print(f"  Calling simulate_trades...")
trades = simulate_trades(
    candles=d1,
    symbol=symbol,
    params=params,
    h4_candles=h4,
    weekly_candles=w1,
    monthly_candles=mn,
    include_transaction_costs=True,
)

print(f"  ✓ Result: {len(trades)} trades generated")
if trades:
    print(f"    First trade: {trades[0]}")
else:
    print(f"    ✗ NO TRADES - simulate_trades is returning empty list")
