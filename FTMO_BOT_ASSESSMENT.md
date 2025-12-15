# FTMO 200K Trading Bot - Comprehensive Assessment

## Executive Summary

**Overall Rating: 3/10**
**Realistic Probability of Passing FTMO 200K Challenge: ~15-20% (LOW)**
**Edge Sustainability: POOR**

This is an ambitious project with well-structured code, but it contains critical flaws that would likely result in failure during a live FTMO challenge.

---

## 1. Strategy Logic Analysis

### The 7 Confluence Pillars
The strategy implements a Smart Money Concepts (SMC) / price-action approach with 7 checkpoints:

| Pillar | Description | Implementation |
|--------|-------------|----------------|
| HTF Bias | Monthly/Weekly/Daily trend alignment | EMA crossover + price action |
| Location | Price at key support/resistance zones | Swing high/low proximity |
| Fibonacci | Price in retracement zone (38.2%-78.6%) | Dynamic swing leg calculation |
| Liquidity | Near equal highs/lows or sweep detected | Pattern recognition |
| Structure | BOS/CHoCH confirmation | Higher highs/lows analysis |
| Confirmation | 4H timeframe entry trigger | Engulfing patterns, momentum |
| Risk:Reward | Minimum 1:1 RR available | ATR-based calculation |

### Issues Identified:
- **Confluence scoring is simplistic**: Just counts boolean flags without weighting importance
- **MIN_CONFLUENCE reduced to 5** in live bot (from 6), allowing trades with only 5/7 checks
- **Multi-timeframe slicing uses approximations**: Monthly = last 60 daily candles (can misclassify trend during volatility shifts)
- **No slippage or partial-fill modeling** in entry validation

---

## 2. Risk Management Assessment

### FTMO Rules Addressed:
- 5% daily loss limit
- 10% max drawdown
- 10% Phase 1 profit target
- 5% Phase 2 profit target
- Minimum 4 trading days

### Configuration:
```
Base risk per trade: 0.5%
Max concurrent trades: 7
Max cumulative risk: 5%
Dynamic lot sizing with confluence scaling
```

### CRITICAL BUG FOUND:
**The `potential_loss_usd()` function uses a hardcoded 0.0001 pip size:**

```python
def potential_loss_usd(self) -> float:
    stop_pips = abs(self.entry_price - self.stop_loss) / 0.0001  # BUG!
    pip_value = get_pip_value(self.symbol, self.entry_price)
    return stop_pips * pip_value * self.lot_size
```

This **grossly underestimates risk** for:
- JPY pairs (pip size = 0.01)
- Gold/XAUUSD (pip size = 0.01)
- Indices (pip size = 1.0)

**Impact**: Cumulative exposure checks (3% cap) can be breached in live trading, potentially causing immediate challenge failure.

### Stress Test Scenario:
- 7 concurrent trades x 0.5% risk = 3.5% exposure
- Add spread + slippage = ~4%+ exposure
- One bad day = dangerously close to 5% limit

---

## 3. Backtest Quality Concerns

### Data Period:
- **Training**: January - September 2024
- **Validation**: October - December 2024
- **Out-of-sample**: 2023 data

### Problems:
1. **Only 2 years of data** for a strategy with ~30 tunable parameters
2. **Optimizer rewrites live code files** during optimization:
   - `ftmo_config.py`
   - `strategy_core.py`
   - `main_live_bot.py`
3. **No transaction costs modeled**: No spread variability, commissions, slippage, or trade rejections
4. **Same indicators for training and validation** = target leakage

### Reported Results (Likely Inflated):
- Win Rate: 76.5%
- Average R: +0.28R
- Total Trades: 302
- Challenges Passed: 4/5 (80%)

**But**: "CRITERIA NOT MET - need 14 passed, only 4"

---

## 4. Live Trading Readiness

### Strengths:
- Symbol mapping between OANDA and FTMO formats
- Pending order management
- Challenge state persistence
- Partial take-profit at TP1, TP2, TP3, TP4, TP5
- Trailing stop after TP hits

### Weaknesses:
- **No robust MT5 reconnection logic** - Windows VM stability concerns
- **Minimal partial-fill handling**
- **No spread checking before entry** (configured but may not be enforced)
- **No news filter** - trading during high-impact events

---

## 5. Signs of Overfitting

| Red Flag | Evidence |
|----------|----------|
| Too many parameters | ~30 tunable knobs for 2-year dataset |
| In-sample optimization | Optimizer modifies live code files |
| Unrealistic results | 76.5% win rate without transaction costs |
| Limited out-of-sample | Only 3 months validation + 1 year OOS |
| Result variance | 4 passed vs. target of 14 |

### Classic Overfitting Pattern:
The `MainLiveBotModifier` class literally rewrites strategy code based on backtest results - this is textbook data snooping.

---

## 6. Biggest Strengths

1. **Well-structured codebase** with clear separation of concerns
2. **Comprehensive FTMO rule awareness** - daily loss tracking, drawdown monitoring
3. **Dynamic position sizing** with confluence-based scaling
4. **Multi-layered risk protection** (7 safety layers in ChallengeRiskManager)
5. **Multi-timeframe analysis** approach is conceptually sound
6. **Trailing stops and partial take-profits** for trade management

---

## 7. Biggest Weaknesses

1. **Risk calculation bug** will cause position sizing errors in live
2. **Optimizer data snooping** invalidates backtest results
3. **Limited backtest period** (2 years) for a parameterized strategy
4. **No realistic execution modeling** (slippage, spread, commissions)
5. **Confluence scoring is too simple** - no weighting of pillar importance
6. **Live robustness gaps** - no reconnection logic, limited error handling

---

## 8. Recommended Improvements (Priority Order)

### Immediate (Before Any Live Trading):
1. **Fix pip/point calculation** - use proper `get_pip_size()` in all risk functions
2. **Freeze strategy code** - never let optimizer modify live code
3. **Add spread/slippage modeling** to backtests (2-5 pips depending on pair)

### Short-term:
4. **Extend dataset** to 5+ years (2019-2024 minimum)
5. **Implement proper walk-forward optimization** with out-of-fold testing
6. **Add news filter** to avoid high-impact events
7. **Implement robust MT5 reconnection** with exponential backoff

### Long-term:
8. **Paper trade for 3+ months** before any live challenge
9. **Consider Monte Carlo simulation** for parameter robustness
10. **Simplify confluence logic** - fewer, better-validated rules

---

## 9. Final Verdict

### Can This Bot Pass a Real FTMO 200K Challenge?

**Probability: LOW (~15-20%)**

**Reasoning**:
- The risk calculation bug alone could cause account failure on any JPY/Gold trade
- Backtest results are inflated by data snooping and lack of transaction costs
- 2-year optimization on 30 parameters is classic overfitting
- No evidence of forward testing or paper trading validation

### Is the Edge Sustainable?

**No** - The strategy relies on curve-fitted parameters that will likely fail in live market conditions where:
- Spreads widen during volatility
- Slippage occurs on entries and stops
- Market regimes shift (trending vs. ranging)

### Recommendation

**DO NOT deploy this bot live** until:
1. Risk calculation bugs are fixed
2. Backtests are rerun with realistic transaction costs
3. 5+ years of data are used for validation
4. 3+ months of forward paper trading shows consistent results

---

*Analysis completed: December 15, 2025*
