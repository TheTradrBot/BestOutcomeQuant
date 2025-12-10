
#!/usr/bin/env python3
"""
Backtest main_live_bot.py - Historical Trade Analysis

This script simulates what trades main_live_bot.py would have taken in the past,
using the EXACT SAME logic as the live bot (strategy_core.py + ftmo_config.py).

It then runs challenge simulations to see if it would have passed FTMO.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict

from backtest import run_backtest
from src.backtest.engine import (
    BacktestTrade,
    simulate_trade_exit,
    run_fivers_challenge,
)
from challenge_rules import FIVERS_10K_RULES, format_challenge_summary
from ftmo_config import FTMO_CONFIG
from symbol_mapping import ALL_TRADABLE_FTMO


def is_trading_day(dt: datetime) -> bool:
    """Check if a datetime is a valid trading day (excludes weekends and major holidays)."""
    # Exclude weekends (Saturday=5, Sunday=6)
    if dt.weekday() >= 5:
        return False
    
    # Exclude major market holidays (New Year's Day, Christmas, etc.)
    # New Year's Day
    if dt.month == 1 and dt.day == 1:
        return False
    
    # Christmas Day
    if dt.month == 12 and dt.day == 25:
        return False
    
    # Good Friday and Easter Monday would need dynamic calculation
    # For now, basic validation
    
    return True


def backtest_live_bot(
    start_date: datetime,
    end_date: datetime,
    symbols: List[str] = None,
) -> Dict:
    """
    Backtest what main_live_bot.py would have done.
    
    Simulates:
    1. 4-hour scans (like the bot)
    2. Pending order placements at calculated entry levels
    3. Order fills when price reaches entry
    4. Partial closes at TP1/TP2/TP3
    5. FTMO challenge tracking
    
    Returns comprehensive results with challenge pass/fail.
    
    MATCHES main_live_bot.py EXACTLY:
    - Same symbol list (ALL_TRADABLE_OANDA - 42 assets)
    - Same confluence threshold (4/7)
    - Same quality factors (2 minimum)
    - Same risk settings (0.5% per trade)
    - Same partial close percentages (50%/30%/20%)
    - Same SL validation (ATR-based + pip limits)
    - Same entry distance rules (max 1.2R)
    - Filters out weekends and major holidays
    """
    from symbol_mapping import ALL_TRADABLE_OANDA
    
    if symbols is None:
        # Use all tradable assets (42 total) - SAME as main_live_bot.py
        symbols = ALL_TRADABLE_OANDA
    
    print("\n" + "=" * 80)
    print("MAIN_LIVE_BOT BACKTEST - Historical Trade Analysis")
    print("=" * 80)
    print(f"Period: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}")
    print(f"Symbols: {len(symbols)} (all tradable assets)")
    print(f"Min Confluence: {FTMO_CONFIG.min_confluence_score}/7")
    print(f"Min Quality Factors: {FTMO_CONFIG.min_quality_factors}")
    print(f"Risk per trade: {FTMO_CONFIG.risk_per_trade_pct}%")
    print(f"Max concurrent trades: {FTMO_CONFIG.max_concurrent_trades}")
    print(f"Max entry distance: {FTMO_CONFIG.max_entry_distance_r}R")
    print(f"TP R-multiples: {FTMO_CONFIG.tp1_r_multiple}R / {FTMO_CONFIG.tp2_r_multiple}R / {FTMO_CONFIG.tp3_r_multiple}R")
    print(f"Partial closes: {FTMO_CONFIG.tp1_close_pct*100:.0f}% / {FTMO_CONFIG.tp2_close_pct*100:.0f}% / {FTMO_CONFIG.tp3_close_pct*100:.0f}%")
    print("=" * 80)
    
    # Collect all trades across all symbols
    all_trades: List[BacktestTrade] = []
    trades_by_symbol: Dict[str, List[Dict]] = defaultdict(list)
    
    period_str = f"{start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}"
    
    print(f"\n📊 Running backtests for {len(symbols)} symbols...")
    print("-" * 80)
    
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{len(symbols)}] {symbol:<15}", end=" ")
        
        try:
            result = run_backtest(symbol, period_str)
            
            if not result.get('trades'):
                print("No trades")
                continue
            
            trades = result['trades']
            total_trades = len(trades)
            wins = sum(1 for t in trades if t.get('rr', 0) > 0)
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            total_r = sum(t.get('rr', 0) for t in trades)
            
            print(f"{total_trades:3d} trades, {win_rate:5.1f}% WR, {total_r:+7.2f}R")
            
            # Convert to BacktestTrade objects
            for trade in trades:
                entry_date = datetime.fromisoformat(trade['entry_date']) if isinstance(trade['entry_date'], str) else trade['entry_date']
                
                # Skip trades that would occur on non-trading days
                if not is_trading_day(entry_date):
                    continue
                
                # Parse exit date
                exit_date_raw = trade.get('exit_date')
                if isinstance(exit_date_raw, str):
                    exit_date = datetime.fromisoformat(exit_date_raw)
                elif isinstance(exit_date_raw, datetime):
                    exit_date = exit_date_raw
                else:
                    exit_date = entry_date
                
                # Get prices - ensure we have valid data
                entry_price = trade.get('entry_price', 0) or trade.get('entry', 0)
                stop_loss = trade.get('stop_loss', 0) or trade.get('sl', 0)
                
                # Exit price should come from actual exit, not default to entry
                exit_price = trade.get('exit_price', 0) or trade.get('exit', 0)
                if not exit_price or exit_price == entry_price:
                    # If no valid exit price, use exit_reason to determine
                    exit_reason = trade.get('exit_reason', '')
                    if exit_reason == 'TP3':
                        exit_price = trade.get('tp3', entry_price)
                    elif exit_reason == 'TP2':
                        exit_price = trade.get('tp2', entry_price)
                    elif exit_reason in ['TP1', 'TP1+Trail']:
                        exit_price = trade.get('tp1', entry_price)
                    elif exit_reason == 'SL':
                        exit_price = stop_loss
                
                # Skip invalid trades
                if not entry_price or not stop_loss or not exit_price:
                    continue
                
                # Get confluence score - backtest.py returns it as 'confluence'
                confluence = trade.get('confluence_score', 0) or trade.get('confluence', 0)
                
                bt = BacktestTrade(
                    symbol=symbol,
                    direction=trade.get('direction', 'bullish'),
                    entry_date=entry_date,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    tp1=trade.get('tp1'),
                    tp2=trade.get('tp2'),
                    tp3=trade.get('tp3'),
                    exit_date=exit_date,
                    exit_price=exit_price,
                    exit_reason=trade.get('exit_reason', ''),
                    confluence_score=confluence,
                )
                
                # Calculate R based on exit reason (matching live bot partial logic)
                entry = bt.entry_price
                sl = bt.stop_loss
                risk = abs(entry - sl)
                
                if risk <= 0:
                    continue
                
                # Simulate partial exits like main_live_bot.py (EXACT MATCH)
                # FTMO_CONFIG: tp1_close_pct=0.50, tp2_close_pct=0.30, tp3_close_pct=0.20
                if bt.exit_reason == "TP3":
                    # Full runner to TP3 = TP1 (50%) + TP2 (30%) + TP3 (20%)
                    tp1_r = (bt.tp1 - entry) / risk if bt.direction == "bullish" else (entry - bt.tp1) / risk
                    tp2_r = (bt.tp2 - entry) / risk if bt.direction == "bullish" else (entry - bt.tp2) / risk
                    tp3_r = (bt.tp3 - entry) / risk if bt.direction == "bullish" else (entry - bt.tp3) / risk
                    bt.partial_exits = [
                        {"level": "TP1", "r_multiple": tp1_r, "portion": FTMO_CONFIG.tp1_close_pct},
                        {"level": "TP2", "r_multiple": tp2_r, "portion": FTMO_CONFIG.tp2_close_pct},
                        {"level": "TP3", "r_multiple": tp3_r, "portion": FTMO_CONFIG.tp3_close_pct},
                    ]
                elif bt.exit_reason == "TP2":
                    tp1_r = (bt.tp1 - entry) / risk if bt.direction == "bullish" else (entry - bt.tp1) / risk
                    tp2_r = (bt.tp2 - entry) / risk if bt.direction == "bullish" else (entry - bt.tp2) / risk
                    bt.partial_exits = [
                        {"level": "TP1", "r_multiple": tp1_r, "portion": FTMO_CONFIG.tp1_close_pct},
                        {"level": "TP2", "r_multiple": tp2_r, "portion": FTMO_CONFIG.tp2_close_pct + FTMO_CONFIG.tp3_close_pct},
                    ]
                elif bt.exit_reason == "TP1+Trail":
                    tp1_r = (bt.tp1 - entry) / risk if bt.direction == "bullish" else (entry - bt.tp1) / risk
                    bt.partial_exits = [
                        {"level": "TP1", "r_multiple": tp1_r, "portion": FTMO_CONFIG.tp1_close_pct},
                        {"level": "BE", "r_multiple": 0, "portion": FTMO_CONFIG.tp2_close_pct + FTMO_CONFIG.tp3_close_pct},
                    ]
                else:  # SL
                    bt.partial_exits = [
                        {"level": "SL", "r_multiple": -1.0, "portion": 1.0},
                    ]
                
                all_trades.append(bt)
                trades_by_symbol[symbol].append(trade)
                
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("-" * 80)
    print(f"✓ Collected {len(all_trades)} total trades\n")
    
    if not all_trades:
        return {
            "period": period_str,
            "total_trades": 0,
            "message": "No trades found in this period"
        }
    
    # Sort trades by entry date
    all_trades.sort(key=lambda t: t.entry_date)
    
    # Run FTMO challenge simulation
    print("\n" + "=" * 80)
    print("FTMO CHALLENGE SIMULATION")
    print("=" * 80)
    
    challenge_result = run_fivers_challenge(
        trades=all_trades,
        start_date=start_date,
        end_date=end_date,
        starting_balance=FIVERS_10K_RULES.account_size,
        risk_per_trade_pct=FTMO_CONFIG.risk_per_trade_pct,
    )
    
    # Print formatted summary
    summary = format_challenge_summary(challenge_result)
    print(summary)
    
    # Additional stats
    print("\n" + "=" * 80)
    print("LIVE BOT BEHAVIOR ANALYSIS")
    print("=" * 80)
    
    total_trades = len(all_trades)
    winning_trades = sum(1 for t in all_trades if t.is_winner)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    print(f"Total trades executed: {total_trades}")
    print(f"Win rate: {win_rate:.1f}%")
    print(f"Symbols traded: {len(trades_by_symbol)}")
    
    # Top performing symbols
    symbol_performance = []
    for sym, trades in trades_by_symbol.items():
        total_r = sum(t.get('rr', 0) for t in trades)
        symbol_performance.append((sym, len(trades), total_r))
    
    symbol_performance.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\nTop 5 performing symbols:")
    for i, (sym, count, total_r) in enumerate(symbol_performance[:5], 1):
        print(f"  {i}. {sym:<12} {count:3d} trades, {total_r:+7.2f}R")
    
    # Exit breakdown
    exit_counts = defaultdict(int)
    for trade in all_trades:
        exit_counts[trade.exit_reason] += 1
    
    print(f"\nExit breakdown:")
    for reason, count in sorted(exit_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_trades * 100) if total_trades > 0 else 0
        print(f"  {reason:<15} {count:3d} ({pct:5.1f}%)")
    
    print("=" * 80)
    
    return {
        "period": period_str,
        "start_date": start_date,
        "end_date": end_date,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "win_rate": win_rate,
        "challenge_result": challenge_result,
        "trades_by_symbol": dict(trades_by_symbol),
        "all_trades": all_trades,
    }


def export_trades_to_csv(trades: List[BacktestTrade], filename: str):
    """Export trades to CSV file with all details."""
    import csv
    
    with open(filename, 'w', newline='') as f:
        fieldnames = [
            'Trade #', 'Symbol', 'Direction', 'Confluence',
            'Entry Date', 'Entry Price', 'Stop Loss',
            'TP1', 'TP2', 'TP3',
            'Exit Date', 'Exit Price', 'Exit Reason',
            'TP Hit', 'SL Hit', 'R Multiple', 'Result', 'Risk Pips'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, trade in enumerate(trades, 1):
            # Calculate R-multiple from partial exits
            total_r = 0.0
            if trade.partial_exits:
                for exit_info in trade.partial_exits:
                    r_mult = exit_info.get('r_multiple', 0)
                    portion = exit_info.get('portion', 0)
                    total_r += r_mult * portion
            else:
                # Calculate R from entry/exit if no partials
                if trade.exit_price and trade.entry_price and trade.stop_loss:
                    risk = abs(trade.entry_price - trade.stop_loss)
                    if risk > 0:
                        if trade.direction == "bullish":
                            total_r = (trade.exit_price - trade.entry_price) / risk
                        else:
                            total_r = (trade.entry_price - trade.exit_price) / risk
            
            # Determine which TP was hit
            tp_hit = "None"
            sl_hit = "No"
            
            if trade.exit_reason == "TP3":
                tp_hit = "TP3"
            elif trade.exit_reason == "TP2":
                tp_hit = "TP2"
            elif trade.exit_reason == "TP1+Trail" or trade.exit_reason == "TP1":
                tp_hit = "TP1"
            elif trade.exit_reason == "SL":
                sl_hit = "Yes"
            
            result_text = "WIN" if total_r > 0 else "LOSS" if total_r < 0 else "BE"
            
            # Calculate risk in pips
            risk_pips = 0
            if trade.entry_price and trade.stop_loss:
                from ftmo_config import get_pip_size
                pip_size = get_pip_size(trade.symbol)
                risk_pips = abs(trade.entry_price - trade.stop_loss) / pip_size
            
            writer.writerow({
                'Trade #': i,
                'Symbol': trade.symbol,
                'Direction': trade.direction.upper(),
                'Confluence': f"{trade.confluence_score}/7",
                'Entry Date': trade.entry_date.strftime('%Y-%m-%d %H:%M') if trade.entry_date else 'N/A',
                'Entry Price': f"{trade.entry_price:.5f}" if trade.entry_price else 'N/A',
                'Stop Loss': f"{trade.stop_loss:.5f}" if trade.stop_loss else 'N/A',
                'TP1': f"{trade.tp1:.5f}" if trade.tp1 else 'N/A',
                'TP2': f"{trade.tp2:.5f}" if trade.tp2 else 'N/A',
                'TP3': f"{trade.tp3:.5f}" if trade.tp3 else 'N/A',
                'Exit Date': trade.exit_date.strftime('%Y-%m-%d %H:%M') if trade.exit_date else 'N/A',
                'Exit Price': f"{trade.exit_price:.5f}" if trade.exit_price else 'N/A',
                'Exit Reason': trade.exit_reason or 'N/A',
                'TP Hit': tp_hit,
                'SL Hit': sl_hit,
                'R Multiple': f"{total_r:+.2f}R",
                'Result': result_text,
                'Risk Pips': f"{risk_pips:.1f}" if risk_pips > 0 else 'N/A'
            })
    
    print(f"\n✅ Trade details exported to: {filename}")


def main():
    """Run backtest for recent period."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backtest main_live_bot.py historical performance")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)", default="2024-01-01")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)", default="2024-12-31")
    parser.add_argument("--symbols", type=str, nargs="+", help="Specific symbols to test")
    parser.add_argument("--csv", type=str, help="Export trades to CSV file", default=None)
    
    args = parser.parse_args()
    
    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")
    
    symbols = args.symbols if args.symbols else None
    
    result = backtest_live_bot(start_date, end_date, symbols)
    
    if result["total_trades"] == 0:
        print("\n⚠️  No trades found in this period")
        return
    
    # Summary
    challenge = result["challenge_result"]
    
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Period: {result['period']}")
    print(f"Total trades: {result['total_trades']}")
    print(f"Win rate: {result['win_rate']:.1f}%")
    print(f"Challenges passed: {challenge.full_challenges_passed}/{len(challenge.challenges)}")
    print(f"Total profit: ${challenge.total_profit_usd:+,.2f} ({challenge.total_profit_pct:+.1f}%)")
    print("=" * 80)
    
    # Export to CSV if requested
    if args.csv:
        export_trades_to_csv(result["all_trades"], args.csv)
    else:
        # Auto-generate CSV filename
        csv_filename = f"backtest_trades_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        export_trades_to_csv(result["all_trades"], csv_filename)


if __name__ == "__main__":
    main()
