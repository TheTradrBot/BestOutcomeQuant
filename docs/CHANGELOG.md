# Changelog

**Last Updated**: 2025-12-28  
**Auto-generated**: From git commits

---

## Recent Changes

### Features
- [c6da3a2] feat: Comprehensive auto-updating documentation system (2025-12-28)
- [56850d8] feat: Add --single flag and separate NSGA/TPE output directories (2025-12-28)
- [5c926b5] feat: Smart NSGA-II flow with OOS validation (2025-12-28)
- [0c4f28d] feat: Expand NSGA-II parameter space (25+ params) (2025-12-28)

### Bug Fixes

### Documentation
- [CURRENT] docs: Add comprehensive baseline performance analysis (BASELINE_ANALYSIS.md) (2025-12-28)
- [00e8d26] docs: Add AI Assistant Quick Start Guide (2025-12-28)

### Refactoring
- [2210195] refactor: Remove december_atr_multiplier parameter and legacy logging (2025-12-28)
- [cdd082f] refactor: Final cleanup - organize codebase structure (2025-12-28)
- [b4e01f6] refactor: Clean output system with human-readable log (2025-12-28)
- [6e0ad97] refactor: Unified optimization config system (2025-12-28)
- [81b0940] refactor: reorganize project structure for better maintainability (2025-12-28)


---

## Version History

### v3.2 (2025-12-28)
**Update**: Baseline Performance Analysis

**New Documentation**:
- ✅ **BASELINE_ANALYSIS.md**: Comprehensive 15-25 page technical analysis
  - Baseline performance metrics (Trial #0: 25.9% DD, 48.6% WR, +99.88R)
  - Architecture breakdown (15-flag confluence system, ADX regime detection)
  - Parameter space mapping (19 current, 30+ hardcoded, 14 disabled filters)
  - Improvement roadmap (P0-P3 priorities with impact estimates)
  - Code quality assessment and performance projections

**Key Findings**:
- ⚠️ CRITICAL: 25.9% max drawdown exceeds FTMO 10% limit
- ⚠️ HIGH: 12+ trading filters currently disabled
- ⚠️ HIGH: Q3 seasonality problem (-80R July-September)
- 🎯 Top 3 priorities: Drawdown protection, filter enablement, Q3 fix

---

### v3.1 (2025-12-28)
**Update**: History Archiving + Trading Filters

**New Features**:
- ✅ History archiving at END of run (run_001, run_002, etc.)
- ✅ Holiday filter: blocks trades on Jan 1, Dec 24-25, Good Friday
- ✅ Opposing position filter: prevents FTMO hedging rule violations
- ✅ run_optimization.sh helper script for background runs
- ✅ Sync best_score with Optuna database on resume

**Bug Fixes**:
- Fixed CSV export to use correct output directory
- Fixed false "NEW BEST" messages when resuming studies

---

### v3.0 (2025-12-28)
**Major Update**: Unified Optimization Config + Smart NSGA-II Flow

**New Features**:
- ✅ Unified config system (params/optimization_config.json)
- ✅ Smart NSGA-II flow with OOS validation
- ✅ Separate NSGA/TPE output directories
- ✅ --single and --multi CLI flags
- ✅ OutputManager with mode-specific logging
- ✅ Comprehensive documentation auto-update system

**Optimizations**:
- 25+ parameter search space (was 15)
- Top-5 Pareto OOS validation (prevents overfitting)
- Fixed Optuna step divisibility warnings
- Default config: NSGA-II + ADX regime filtering

**Breaking Changes**:
- None (backwards compatible)

---

### v2.5 (2025-12-26)
**Update**: Parameter Space Expansion

**Changes**:
- Expanded parameter ranges (confluence 2-6, risk 0.2-1.0%)
- Added summer_risk_multiplier (Q3 drawdown protection)
- Added max_concurrent_trades limit

---

### v2.0 (2025-12-20)
**Major Update**: Regime-Adaptive Trading

**Features**:
- ADX regime detection (Trend/Range/Transition)
- Regime-specific confluence requirements
- RSI filters for range mode
- Partial exits and ATR trailing stops

---

### v1.0 (2024-06-15)
**Initial Release**: Production-Ready FTMO Bot

**Core Features**:
- 7-Pillar Confluence System
- Optuna TPE optimization
- FTMO risk management
- MT5 integration (Windows)
- 34 tradable assets

---

**Full commit history**: Run `git log --oneline` in repository root
