"""
GRVT Market Data — Reference Examples

These examples demonstrate how to fetch market data from GRVT.
Market data endpoints are public and do not require authentication.
Requires: pip install grvt-pysdk
"""

from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv


def create_api(env: str = "production") -> GrvtCcxt:
    """Create a GRVT API client for public market data."""
    return GrvtCcxt(env=GrvtEnv(env))


def list_perpetuals(api: GrvtCcxt):
    """List all available perpetual instruments."""
    markets = api.fetch_all_markets()
    perps = [m for m in markets if m["symbol"].endswith("_Perp") and m["active"]]
    for p in perps:
        print(f"  {p['symbol']}")
    return perps


def price_check(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp"):
    """Quick price check — last, bid, ask."""
    ticker = api.fetch_mini_ticker(symbol)
    print(f"{symbol}: Last={ticker['last']} Bid={ticker['bid']} Ask={ticker['ask']}")
    return ticker


def full_ticker(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp"):
    """Full ticker with volume, 24h stats, funding rate."""
    ticker = api.fetch_ticker(symbol)
    print(f"{symbol}:")
    print(f"  Last: {ticker['last']}")
    print(f"  24h High: {ticker['high']}, Low: {ticker['low']}")
    print(f"  24h Volume: {ticker['baseVolume']}")
    print(f"  Funding Rate: {ticker['info'].get('funding_rate', 'N/A')}")
    return ticker


def orderbook_snapshot(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp", depth: int = 10):
    """Fetch and display orderbook."""
    book = api.fetch_order_book(symbol, limit=depth)
    print(f"--- {symbol} Orderbook ---")
    print("Asks (sell):")
    for ask in reversed(book["asks"][:5]):
        print(f"  {ask[0]:>12.2f}  |  {ask[1]}")
    print("  ------------ spread ------------")
    print("Bids (buy):")
    for bid in book["bids"][:5]:
        print(f"  {bid[0]:>12.2f}  |  {bid[1]}")
    return book


def fetch_candles(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp", timeframe: str = "1h", limit: int = 50):
    """Fetch OHLCV candlestick data."""
    ohlcv = api.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    print(f"--- {symbol} {timeframe} candles (last 5) ---")
    for ts, o, h, l, c, v in ohlcv[-5:]:
        print(f"  O:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f} V:{v:.4f}")
    return ohlcv


def candles_to_dataframe(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp", timeframe: str = "1h", limit: int = 200):
    """Fetch OHLCV and convert to pandas DataFrame for analysis."""
    import pandas as pd

    ohlcv = api.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


def funding_rates(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp", limit: int = 24):
    """Fetch recent funding rate history."""
    rates = api.fetch_funding_rate_history(symbol, limit=limit)
    for r in rates[-5:]:
        print(f"  {r['datetime']}: {r['fundingRate']}")
    return rates


if __name__ == "__main__":
    api = create_api("production")
    list_perpetuals(api)
    price_check(api)
    orderbook_snapshot(api)
