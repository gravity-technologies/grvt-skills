---
name: account-management
description: Manage GRVT trading account — check balances, positions, margin, and trade history. Use when the user asks about their portfolio, PnL, or account status.
---

# GRVT Account Management

## When to Use

Use this skill when the user wants to:
- Check account balance or portfolio value
- View open positions and unrealized PnL
- Manage position margin (add margin, check limits)
- View trade/fill history
- Check funding payment history

## Prerequisites

```bash
pip install grvt-pysdk
```

All account endpoints require authentication:
```bash
export GRVT_API_KEY="<from GRVT exchange UI>"
export GRVT_TRADING_ACCOUNT_ID="<trading account ID>"
export GRVT_PRIVATE_KEY="<private key for order signing>"
```

## SDK Setup

```python
import os
from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv

api = GrvtCcxt(
    env=GrvtEnv.TESTNET,
    parameters={
        "api_key": os.getenv("GRVT_API_KEY"),
        "trading_account_id": os.getenv("GRVT_TRADING_ACCOUNT_ID"),
        "private_key": os.getenv("GRVT_PRIVATE_KEY"),
    },
)
```

## Account Balance

```python
# Get account balance
balance = api.fetch_balance()
# Returns dict with currency balances: free, used, total
print(f"USDT: free={balance['USDT']['free']}, used={balance['USDT']['used']}, total={balance['USDT']['total']}")
```

## Account Summary

```python
# Sub-account summary — balances, margin usage, equity
summary = api.get_account_summary(type="sub-account")

# Aggregated summary across all sub-accounts
agg_summary = api.get_account_summary(type="aggregated")
```

## Positions

```python
# Fetch all open positions
positions = api.fetch_positions()

# Fetch positions for specific symbols
positions = api.fetch_positions(symbols=["BTC_USDT_Perp", "ETH_USDT_Perp"])

for pos in positions:
    print(f"{pos['symbol']}: size={pos['contracts']} side={pos['side']}")
    print(f"  Entry: {pos['entryPrice']}, Mark: {pos['markPrice']}")
    print(f"  Unrealized PnL: {pos['unrealizedPnl']}")
    print(f"  Margin: {pos['initialMargin']}")
```

## Position Margin Management

```python
# Add margin to a position (reduce liquidation risk)
api.add_position_margin(
    symbol="BTC_USDT_Perp",
    amount=100,  # Additional USDT margin
)

# Check margin limits
limits = api.get_position_margin_limits(symbol="BTC_USDT_Perp")
```

## Trade / Fill History

```python
# Recent fills
fills = api.fetch_my_trades(symbol="BTC_USDT_Perp", limit=50)
for fill in fills:
    print(f"{fill['side']} {fill['amount']} @ {fill['price']} — {fill['datetime']}")
    print(f"  Fee: {fill['fee']['cost']} {fill['fee']['currency']}")
```

## Funding Payment History

```python
# Check funding payments received/paid on perpetual positions
funding = api.fetch_funding_payment_history(symbol="BTC_USDT_Perp", limit=24)
for f in funding:
    print(f"Payment: {f['amount']} at {f['datetime']}")
```

## Account History

```python
# Full account history (deposits, withdrawals, transfers, settlements)
history = api.fetch_account_history()
```

## Common Patterns

### Portfolio Overview

```python
def portfolio_overview(api):
    balance = api.fetch_balance()
    positions = api.fetch_positions()

    print(f"Account Balance: {balance['USDT']['total']} USDT")
    print(f"Available: {balance['USDT']['free']} USDT")
    print(f"\nOpen Positions ({len(positions)}):")
    total_pnl = 0
    for pos in positions:
        pnl = float(pos.get("unrealizedPnl", 0))
        total_pnl += pnl
        print(f"  {pos['symbol']}: {pos['contracts']} ({pos['side']})")
        print(f"    Entry: {pos['entryPrice']} | PnL: {pnl}")
    print(f"\nTotal Unrealized PnL: {total_pnl}")
```

## Important Notes

- All account data requires authentication — ensure env vars are set
- Position PnL is calculated against current mark price
- Funding payments occur at regular intervals on perpetual positions (typically every 8 hours)
- Use `GrvtEnv.TESTNET` for testing before production
