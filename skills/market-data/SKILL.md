---
name: market-data
description: Fetch market data from GRVT exchange — tickers, orderbooks, trades, candlesticks, funding rates. Use when the user wants price info, charts, or market analysis data.
---

# GRVT Market Data

## When to Use

Use this skill when the user wants to:
- Check current prices, bid/ask spreads
- View orderbook depth
- Get recent trades
- Fetch candlestick/OHLCV data for analysis
- Check funding rates
- Discover available trading instruments

## Prerequisites

```bash
pip install grvt-pysdk
```

Market data endpoints are **public** — no API key is needed for read-only data. However, if the user already has credentials configured, reuse their existing `GrvtCcxt` instance.

## How to Execute

IMPORTANT: Always write Python code to a `.py` file and run it with `python3 <file>.py`.
Never use inline Python (`python3 -c` or `python3 << 'EOF'`) — f-strings with braces trigger
shell obfuscation warnings in many AI coding tools and require manual confirmation.

## SDK Setup

```python
from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv

# For public market data only (no credentials needed)
api = GrvtCcxt(env=GrvtEnv.PRODUCTION)

# Or reuse authenticated instance if available
```

## Symbol Format

Perpetual symbols: `{BASE}_{QUOTE}_Perp` (e.g., `BTC_USDT_Perp`, `ETH_USDT_Perp`)

## Instrument Discovery

```python
# List all available instruments
markets = api.fetch_all_markets()

# Filter for perpetuals
perps = [m for m in markets if m["kind"] == "PERPETUAL"]
for p in perps:
    print(p["instrument"])  # e.g. "BTC_USDT_Perp"

# Get details for a specific instrument
market = api.fetch_market("BTC_USDT_Perp")
# Returns: instrument, base, quote, kind, tick_size, min_size, base_decimals, quote_decimals, etc.
```

## Tickers (Current Prices)

```python
# Mini ticker — mark price, index price, last price, best bid/ask
ticker = api.fetch_mini_ticker("BTC_USDT_Perp")
print(f"Last: {ticker['last_price']}, Bid: {ticker['best_bid_price']}, Ask: {ticker['best_ask_price']}")
print(f"Mark: {ticker['mark_price']}, Index: {ticker['index_price']}")

# Full ticker — includes volume, open interest, funding rate, 24h stats
ticker = api.fetch_ticker("BTC_USDT_Perp")
print(f"24h Buy Volume: {ticker['buy_volume_24h_b']} (base), {ticker['buy_volume_24h_q']} (quote)")
print(f"24h High: {ticker['high_price']}, Low: {ticker['low_price']}")
print(f"Funding Rate: {ticker['funding_rate']}")
print(f"Open Interest: {ticker['open_interest']}")
print(f"Long/Short Ratio: {ticker['long_short_ratio']}")
```

## Orderbook

```python
# Fetch orderbook with depth
book = api.fetch_order_book("BTC_USDT_Perp", limit=10)

# book["bids"] and book["asks"] are lists of dicts with price, size, num_orders
for bid in book["bids"][:5]:
    print(f"Bid: {bid['price']} x {bid['size']} ({bid['num_orders']} orders)")
for ask in book["asks"][:5]:
    print(f"Ask: {ask['price']} x {ask['size']} ({ask['num_orders']} orders)")
```

Available depth levels: 10, 50, 100, 500.

## Recent Trades

```python
trades = api.fetch_recent_trades("BTC_USDT_Perp", limit=20)
for t in trades:
    side = "buy" if t["is_taker_buyer"] else "sell"
    print(f"{side} {t['size']} @ {t['price']} (mark: {t['mark_price']})")
```

## Candlestick / OHLCV Data

```python
# Fetch candlestick data — returns {"result": [...], "next": cursor}
data = api.fetch_ohlcv(
    symbol="BTC_USDT_Perp",
    timeframe="1h",       # 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 2w, 4w
    limit=100,
    params={"candle_type": "TRADE"},  # TRADE (default), MARK, INDEX, MID
)

# Each candle has: open_time, close_time, open, close, high, low, volume_b, volume_q, trades
for candle in data["result"][-5:]:
    print(f"O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']} V:{candle['volume_b']}")
```

**Candle types:**
- `TRADE` — Based on actual trade prices (default)
- `MARK` — Based on mark price
- `INDEX` — Based on index price
- `MID` — Based on mid price

## Funding Rates

```python
# Returns {"result": [...], "next": cursor}
data = api.fetch_funding_rate_history(
    symbol="BTC_USDT_Perp",
    limit=24,  # Last 24 entries
)
for f in data["result"]:
    print(f"Rate: {f['funding_rate']} at {f['funding_time']} (mark: {f['mark_price']})")
```

## Working with DataFrames

For analysis tasks, convert to pandas:

```python
import pandas as pd

# OHLCV to DataFrame
data = api.fetch_ohlcv("BTC_USDT_Perp", timeframe="1h", limit=200)
df = pd.DataFrame(data["result"])
df["open_time"] = pd.to_datetime(df["open_time"].astype(float) / 1e9, unit="s")
df.set_index("open_time", inplace=True)
# Columns: open, close, high, low, volume_b, volume_q, trades
```

## Important Notes

- Market data has ~3 months of historical retention
- Pagination is cursor-based and reverse chronological
- Use `GrvtEnv.PRODUCTION` for real market data, `GrvtEnv.TESTNET` for testing
- Mini ticker is lighter weight than full ticker — use it when you only need price
