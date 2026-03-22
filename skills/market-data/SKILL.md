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

# Filter for active perpetuals
perps = [m for m in markets if m["symbol"].endswith("_Perp") and m["active"]]
for p in perps:
    print(p["symbol"])

# Get details for a specific instrument
market = api.fetch_market("BTC_USDT_Perp")
```

## Tickers (Current Prices)

```python
# Mini ticker — mark price, index price, last price, best bid/ask
ticker = api.fetch_mini_ticker("BTC_USDT_Perp")
print(f"Last: {ticker['last']}, Bid: {ticker['bid']}, Ask: {ticker['ask']}")

# Full ticker — includes volume, open interest, funding rate, 24h stats
ticker = api.fetch_ticker("BTC_USDT_Perp")
print(f"24h Volume: {ticker['baseVolume']}")
print(f"24h High: {ticker['high']}, Low: {ticker['low']}")
print(f"Funding Rate: {ticker['info']['funding_rate']}")
```

## Orderbook

```python
# Fetch orderbook with depth
book = api.fetch_order_book("BTC_USDT_Perp", limit=10)

# book["bids"] = [[price, amount], ...] sorted highest first
# book["asks"] = [[price, amount], ...] sorted lowest first
for bid in book["bids"][:5]:
    print(f"Bid: {bid[0]} x {bid[1]}")
for ask in book["asks"][:5]:
    print(f"Ask: {ask[0]} x {ask[1]}")
```

Available depth levels: 10, 50, 100, 500.

## Recent Trades

```python
trades = api.fetch_recent_trades("BTC_USDT_Perp", limit=20)
for t in trades:
    print(f"{t['side']} {t['amount']} @ {t['price']} at {t['datetime']}")
```

## Candlestick / OHLCV Data

```python
# Fetch candlestick data
ohlcv = api.fetch_ohlcv(
    symbol="BTC_USDT_Perp",
    timeframe="1h",       # 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 2w, 4w
    limit=100,
    params={"candle_type": "TRADE"},  # TRADE (default), MARK, INDEX, MID
)

# Each entry: [timestamp, open, high, low, close, volume]
for candle in ohlcv[-5:]:
    ts, o, h, l, c, v = candle
    print(f"O:{o} H:{h} L:{l} C:{c} V:{v}")
```

**Candle types:**
- `TRADE` — Based on actual trade prices (default)
- `MARK` — Based on mark price
- `INDEX` — Based on index price
- `MID` — Based on mid price

## Funding Rates

```python
funding = api.fetch_funding_rate_history(
    symbol="BTC_USDT_Perp",
    limit=24,  # Last 24 entries
)
for f in funding:
    print(f"Rate: {f['fundingRate']} at {f['datetime']}")
```

## Working with DataFrames

For analysis tasks, convert to pandas:

```python
import pandas as pd

# OHLCV to DataFrame
ohlcv = api.fetch_ohlcv("BTC_USDT_Perp", timeframe="1h", limit=200)
df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df.set_index("timestamp", inplace=True)
```

## Important Notes

- Market data has ~3 months of historical retention
- Pagination is cursor-based and reverse chronological
- Use `GrvtEnv.PRODUCTION` for real market data, `GrvtEnv.TESTNET` for testing
- Mini ticker is lighter weight than full ticker — use it when you only need price
