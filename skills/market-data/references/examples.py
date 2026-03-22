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
    perps = [m for m in markets if m["kind"] == "PERPETUAL"]
    for p in perps:
        print(f"  {p['instrument']} (tick: {p['tick_size']}, min: {p['min_size']})")
    return perps


def price_check(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp"):
    """Quick price check — last, bid, ask, mark."""
    ticker = api.fetch_mini_ticker(symbol)
    print(f"{symbol}:")
    print(f"  Last: {ticker['last_price']}")
    print(f"  Bid:  {ticker['best_bid_price']} x {ticker['best_bid_size']}")
    print(f"  Ask:  {ticker['best_ask_price']} x {ticker['best_ask_size']}")
    print(f"  Mark: {ticker['mark_price']}")
    return ticker


def full_ticker(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp"):
    """Full ticker with volume, 24h stats, funding rate."""
    ticker = api.fetch_ticker(symbol)
    print(f"{symbol}:")
    print(f"  Last: {ticker['last_price']}")
    print(f"  24h High: {ticker['high_price']}, Low: {ticker['low_price']}")
    print(f"  24h Buy Volume: {ticker['buy_volume_24h_b']} base / {ticker['buy_volume_24h_q']} quote")
    print(f"  Funding Rate: {ticker['funding_rate']}")
    print(f"  Open Interest: {ticker['open_interest']}")
    print(f"  Long/Short Ratio: {ticker['long_short_ratio']}")
    return ticker


def orderbook_snapshot(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp", depth: int = 10):
    """Fetch and display orderbook."""
    book = api.fetch_order_book(symbol, limit=depth)
    print(f"--- {symbol} Orderbook ---")
    print("Asks (sell):")
    for ask in reversed(book["asks"][:5]):
        print(f"  {ask['price']:>12s}  |  {ask['size']} ({ask['num_orders']} orders)")
    print("  ------------ spread ------------")
    print("Bids (buy):")
    for bid in book["bids"][:5]:
        print(f"  {bid['price']:>12s}  |  {bid['size']} ({bid['num_orders']} orders)")
    return book


def fetch_candles(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp", timeframe: str = "1h", limit: int = 50):
    """Fetch OHLCV candlestick data."""
    data = api.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    candles = data["result"]
    print(f"--- {symbol} {timeframe} candles (last 5) ---")
    for c in candles[-5:]:
        print(f"  O:{c['open']} H:{c['high']} L:{c['low']} C:{c['close']} V:{c['volume_b']}")
    return candles


def candles_to_dataframe(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp", timeframe: str = "1h", limit: int = 200):
    """Fetch OHLCV and convert to pandas DataFrame for analysis."""
    import pandas as pd

    data = api.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data["result"])
    df["open_time"] = pd.to_datetime(df["open_time"].astype(float) / 1e9, unit="s")
    df.set_index("open_time", inplace=True)
    return df


def funding_rates(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp", limit: int = 24):
    """Fetch recent funding rate history."""
    data = api.fetch_funding_rate_history(symbol, limit=limit)
    for r in data["result"][-5:]:
        print(f"  Rate: {r['funding_rate']} (mark: {r['mark_price']})")
    return data["result"]


if __name__ == "__main__":
    api = create_api("testnet")
    list_perpetuals(api)
    price_check(api)
    orderbook_snapshot(api)
