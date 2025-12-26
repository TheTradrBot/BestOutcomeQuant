"""
FTMO Challenge Rules Definition
Defines the rules for the FTMO 200K challenge
"""

from dataclasses import dataclass


@dataclass
class ChallengeRules:
    """FTMO Challenge rules and constraints"""
    account_currency: str = "USD"
    account_size: float = 200000.0  # $200K
    max_daily_loss_pct: float = 5.0  # 5% daily loss limit
    max_total_drawdown_pct: float = 10.0  # 10% total drawdown limit
    risk_per_trade_pct: float = 0.5  # 0.5% risk per trade
    max_open_risk_pct: float = 3.0  # Max 3% cumulative open risk
    
    # Profit targets
    step1_profit_target_pct: float = 10.0  # Phase 1: 10% profit target
    step2_profit_target_pct: float = 5.0   # Phase 2: 5% profit target
    
    # Trading requirements
    min_profitable_days: int = 0  # FTMO has no minimum profitable days
    profitable_day_threshold_pct: float = 0.0  # N/A for FTMO
    
    # Position limits
    max_concurrent_trades: int = 7
    max_pending_orders: int = 20
    max_trades_per_day: int = 10


# Create the default FTMO 200K rules
FIVERS_10K_RULES = ChallengeRules(
    account_currency="USD",
    account_size=200000.0,
    max_daily_loss_pct=5.0,
    max_total_drawdown_pct=10.0,
    risk_per_trade_pct=0.5,
    max_open_risk_pct=3.0,
    step1_profit_target_pct=10.0,
    step2_profit_target_pct=5.0,
    min_profitable_days=0,
    profitable_day_threshold_pct=0.0,
    max_concurrent_trades=7,
    max_pending_orders=20,
    max_trades_per_day=10,
)
