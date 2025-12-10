
"""
FTMO 10K Challenge Configuration - ULTRA CONSERVATIVE
Only takes the highest probability setups to pass challenge safely.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class FTMO10KConfig:
    """FTMO 10K Challenge - Ultra Conservative Quality-First Mode."""

    # === ACCOUNT SETTINGS ===
    account_size: float = 10000.0
    account_currency: str = "USD"

    # === FTMO RULES (HARD LIMITS - NEVER BREACH) ===
    max_daily_loss_pct: float = 5.0
    max_total_drawdown_pct: float = 10.0
    phase1_target_pct: float = 10.0
    phase2_target_pct: float = 5.0

    # === SAFETY BUFFERS (Stop BEFORE breach) ===
    daily_loss_warning_pct: float = 1.5  # Very early warning
    daily_loss_reduce_pct: float = 2.5   # Reduce risk early
    daily_loss_halt_pct: float = 3.5     # Halt well before limit
    total_dd_warning_pct: float = 3.0    # Early warning
    total_dd_reduce_pct: float = 5.0     # Reduce risk
    total_dd_halt_pct: float = 7.0       # Halt well before limit

    # === POSITION SIZING (ULTRA CONSERVATIVE) ===
    risk_per_trade_pct: float = 0.5      # Lower risk = safer
    risk_per_trade_reduced_pct: float = 0.3
    risk_per_trade_minimal_pct: float = 0.2
    max_cumulative_risk_pct: float = 1.5  # Max 3 trades open (0.5% each)

    # === TRADE LIMITS (QUALITY OVER QUANTITY) ===
    max_concurrent_trades: int = 2       # Only 2 positions max
    max_pending_orders: int = 3
    max_trades_per_day: int = 2          # Max 2 trades per day
    max_trades_per_week: int = 5         # Max 5 trades per week
    max_trades_per_symbol: int = 1

    # === ENTRY OPTIMIZATION ===
    max_entry_distance_r: float = 1.2    # Allow entries up to 1.2R from ideal
    immediate_entry_r: float = 0.4       # Market order if within 0.4R

    # SL validation - ATR-based is primary, pips are fallback per asset type
    min_sl_atr_ratio: float = 0.5
    max_sl_atr_ratio: float = 2.5        # Allow reasonable ATR-based stops

    # === CONFLUENCE SETTINGS (BALANCED) ===
    min_confluence_score: int = 4        # 4/7 minimum for more opportunities
    min_quality_factors: int = 2         # 2 quality factors (balanced)

    # === TAKE PROFIT SETTINGS ===
    tp1_r_multiple: float = 1.5          # Longer TP1 for better R:R
    tp2_r_multiple: float = 3.0
    tp3_r_multiple: float = 5.0

    # === PARTIAL CLOSE PERCENTAGES ===
    tp1_close_pct: float = 0.50          # Close half at TP1
    tp2_close_pct: float = 0.30
    tp3_close_pct: float = 0.20

    # === BREAKEVEN SETTINGS ===
    move_sl_to_be_after_tp1: bool = True
    be_buffer_pips: float = 3.0

    # === ULTRA SAFE MODE ===
    ultra_safe_profit_threshold_pct: float = 7.0  # Earlier protection
    ultra_safe_risk_pct: float = 0.2
    ultra_safe_max_trades: int = 1

    require_rr_flag: bool = True
    require_confirmation: bool = False   # 4H confirmation optional
    require_htf_alignment: bool = False  # HTF alignment optional

    # === ASSET WHITELIST (TOP PERFORMERS ONLY) ===
    # Based on backtest: SPX500, NAS100, AUD_NZD, GBP_JPY, USD_JPY, XAU_USD
    whitelist_assets: list = None
    
    # === PROTECTION LOOP ===
    protection_interval_sec: float = 20.0
    
    # === WEEKLY TRACKING ===
    current_week_trades: int = 0
    week_start_date: str = ""

    def __post_init__(self):
        if self.whitelist_assets is None:
            # Top 10 performers from backtest (highest R and win rate)
            self.whitelist_assets = [
                "SPX500_USD",   # 58.70R, 85.7% WR
                "NAS100_USD",   # 47.80R, 77.1% WR
                "AUD_NZD",      # 46.60R, 77.8% WR
                "GBP_JPY",      # 45.00R, 84.4% WR
                "USD_JPY",      # 42.00R, 91.9% WR
                "XAU_USD",      # 41.40R, 90.9% WR
                "CAD_JPY",      # 41.00R, 87.5% WR
                "CHF_JPY",      # 40.50R, 74.4% WR
                "GBP_CAD",      # 39.20R, 76.2% WR
                "EUR_GBP",      # 33.70R, 78.4% WR
            ]

    def get_risk_pct(self, daily_loss_pct: float, total_dd_pct: float) -> float:
        """Get adjusted risk percentage based on current drawdown."""
        if daily_loss_pct >= self.daily_loss_halt_pct or total_dd_pct >= self.total_dd_halt_pct:
            return 0.0
        elif daily_loss_pct >= self.daily_loss_reduce_pct or total_dd_pct >= self.total_dd_reduce_pct:
            return self.risk_per_trade_minimal_pct
        elif daily_loss_pct >= self.daily_loss_warning_pct or total_dd_pct >= self.total_dd_warning_pct:
            return self.risk_per_trade_reduced_pct
        else:
            return self.risk_per_trade_pct

    def get_max_trades(self, profit_pct: float) -> int:
        """Get max concurrent trades based on profit level."""
        if profit_pct >= self.ultra_safe_profit_threshold_pct:
            return self.ultra_safe_max_trades
        return self.max_concurrent_trades
    
    def is_asset_whitelisted(self, symbol: str) -> bool:
        """Check if asset is in whitelist."""
        return symbol in self.whitelist_assets


FTMO_CONFIG = FTMO10KConfig()

PIP_SIZES = {
    "forex_jpy": 0.01,
    "forex_standard": 0.0001,
    "xauusd": 0.1,
    "xagusd": 0.01,
    "indices": 1.0,
    "crypto": 1.0,
}


def get_pip_size(symbol: str) -> float:
    """Get pip size for a symbol."""
    s = symbol.upper()
    if "JPY" in s:
        return PIP_SIZES["forex_jpy"]
    elif "XAU" in s or "GOLD" in s:
        return PIP_SIZES["xauusd"]
    elif "XAG" in s or "SILVER" in s:
        return PIP_SIZES["xagusd"]
    elif any(idx in s for idx in ["US30", "US500", "NAS100", "SPX500", "DAX", "USTEC", "DJ30"]):
        return PIP_SIZES["indices"]
    elif any(crypto in s for crypto in ["BTC", "ETH", "LTC"]):
        return PIP_SIZES["crypto"]
    else:
        return PIP_SIZES["forex_standard"]


def get_sl_limits(symbol: str) -> tuple:
    """
    Get min/max SL in pips for a specific symbol.
    
    Different asset classes have different pip sizes and typical ranges.
    Values based on realistic ATR-based stops for swing trading.
    """
    s = symbol.upper()
    
    if any(idx in s for idx in ["US30", "US500", "NAS100", "SPX500", "DAX", "USTEC", "DJ30"]):
        return (50.0, 1500.0)  # Indices: 50-1500 points (typical intraday/swing range)
    elif "JPY" in s:
        return (30.0, 400.0)   # JPY pairs: 30-400 pips (3-4 yen move typical)
    elif "XAU" in s or "GOLD" in s:
        return (50.0, 500.0)   # Gold: 50-500 pips ($50-$500 move)
    elif "XAG" in s or "SILVER" in s:
        return (30.0, 200.0)   # Silver: 30-200 pips
    elif any(crypto in s for crypto in ["BTC", "ETH", "LTC"]):
        return (100.0, 3000.0) # Crypto: 100-3000 points (high volatility)
    else:
        return (15.0, 150.0)   # Standard forex: 15-150 pips
