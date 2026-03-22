---
name: perpetual-trading
description: Trade perpetual futures on GRVT exchange using the grvt-pysdk. Use when the user wants to place, cancel, or manage perpetual orders.
---

# Perpetual Trading on GRVT

## When to Use

Use this skill when the user wants to:
- Place buy/sell orders on GRVT perpetual markets
- Cancel orders (single or all)
- Set take-profit / stop-loss orders
- Check order status or open orders
- View order history or fill history

## Prerequisites

```bash
pip install grvt-pysdk
```

The user must set these environment variables:
```bash
export GRVT_API_KEY="<from GRVT exchange UI>"
export GRVT_TRADING_ACCOUNT_ID="<trading account ID>"
export GRVT_PRIVATE_KEY="<private key for order signing>"
```

If the user hasn't configured these, guide them to create an API key at https://exchange.grvt.io (production) or https://exchange.testnet.grvt.io (testnet).

## SDK Setup

```python
import os
from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv

api = GrvtCcxt(
    env=GrvtEnv.TESTNET,  # Use GrvtEnv.PRODUCTION for real trading
    parameters={
        "api_key": os.getenv("GRVT_API_KEY"),
        "trading_account_id": os.getenv("GRVT_TRADING_ACCOUNT_ID"),
        "private_key": os.getenv("GRVT_PRIVATE_KEY"),
    },
)
```

## Symbol Format

Perpetual symbols follow the pattern: `{BASE}_{QUOTE}_Perp`

Examples: `BTC_USDT_Perp`, `ETH_USDT_Perp`, `SOL_USDT_Perp`

To discover available perpetuals:
```python
markets = api.fetch_markets()
perps = [m for m in markets if m["symbol"].endswith("_Perp")]
```

## Placing Orders

### Limit Order

```python
order = api.create_order(
    symbol="BTC_USDT_Perp",
    order_type="limit",
    side="buy",        # "buy" for long, "sell" for short
    amount=0.01,       # Size in base currency (BTC)
    price=90000,       # Limit price in quote currency (USDT)
)
```

### Market Order

```python
order = api.create_order(
    symbol="BTC_USDT_Perp",
    order_type="market",
    side="buy",
    amount=0.01,
    price=0,  # Price is ignored for market orders
)
```

### Order Parameters

Additional parameters can be passed via `params`:

```python
order = api.create_order(
    symbol="BTC_USDT_Perp",
    order_type="limit",
    side="buy",
    amount=0.01,
    price=90000,
    params={
        "client_order_id": 12345,          # Optional custom ID
        "time_in_force": "GTC",            # GTC (default), IOC, FOK, AON
        "post_only": True,                 # Maker-only order
        "reduce_only": True,               # Only reduce existing position
    },
)
```

**Time-in-force options:**
- `GTC` — Good Till Cancel (default)
- `IOC` — Immediate or Cancel (fill what you can, cancel rest)
- `FOK` — Fill or Kill (all or nothing)
- `AON` — All or None

### Take-Profit / Stop-Loss Orders

Use trigger orders for TP/SL:

```python
# Stop-loss: sell when mark price drops to 88000
order = api.create_order(
    symbol="BTC_USDT_Perp",
    order_type="stop_market",
    side="sell",
    amount=0.01,
    price=0,
    params={
        "trigger_price": 88000,
        "reduce_only": True,
    },
)

# Take-profit: sell when mark price reaches 95000
order = api.create_order(
    symbol="BTC_USDT_Perp",
    order_type="take_profit_market",
    side="sell",
    amount=0.01,
    price=0,
    params={
        "trigger_price": 95000,
        "reduce_only": True,
    },
)
```

## Cancelling Orders

```python
# Cancel a specific order
api.cancel_order(id=order["order_id"])

# Cancel by client order ID
api.cancel_order(id=None, params={"client_order_id": 12345})

# Cancel all open orders
api.cancel_all_orders()

# Cancel all perpetual orders only
api.cancel_all_orders(params={"kind": "PERPETUAL"})
```

## Querying Orders

```python
# Get a specific order
order = api.fetch_order(id="<order_id>")

# Get all open orders
open_orders = api.fetch_open_orders(symbol="BTC_USDT_Perp")

# Get order history
history = api.fetch_order_history()

# Get fill/trade history
fills = api.fetch_my_trades(symbol="BTC_USDT_Perp", limit=50)
```

## Order Response

A successful order returns a dict with these key fields:
- `order_id` — Exchange-assigned order ID
- `client_order_id` — Your custom ID (if provided)
- `status` — `PENDING`, `OPEN`, `FILLED`, `REJECTED`, `CANCELLED`
- `filled` — Amount filled so far
- `remaining` — Amount still open
- `price` — Order price
- `side` — `buy` or `sell`

## Important Notes

- All orders on perpetuals require EIP-712 signing — the SDK handles this automatically using `GRVT_PRIVATE_KEY`
- The SDK auto-manages authentication sessions and refreshes cookies before expiry
- Use `GrvtEnv.TESTNET` for testing before moving to `GrvtEnv.PRODUCTION`
- Prices use 9 decimal precision internally; the SDK handles conversion
- Always confirm the user wants to proceed before placing real orders on production
