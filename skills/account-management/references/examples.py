"""
GRVT Account Management — Reference Examples

These examples demonstrate account and position management on GRVT.
Requires: pip install grvt-pysdk
"""

import os
from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv


def create_api(env: str = "testnet") -> GrvtCcxt:
    """Create an authenticated GRVT API client."""
    return GrvtCcxt(
        env=GrvtEnv(env),
        parameters={
            "api_key": os.getenv("GRVT_API_KEY"),
            "trading_account_id": os.getenv("GRVT_TRADING_ACCOUNT_ID"),
            "private_key": os.getenv("GRVT_PRIVATE_KEY"),
        },
    )


def portfolio_overview(api: GrvtCcxt):
    """Print a full portfolio overview: balance + positions + PnL."""
    balance = api.fetch_balance()
    positions = api.fetch_positions()

    print("=== Portfolio Overview ===")
    print(f"USDT Balance: {balance['USDT']['total']}")
    print(f"  Available: {balance['USDT']['free']}")
    print(f"  In Use:    {balance['USDT']['used']}")

    print(f"\nOpen Positions ({len(positions)}):")
    total_pnl = 0
    for pos in positions:
        pnl = float(pos.get("unrealizedPnl", 0))
        total_pnl += pnl
        print(f"  {pos['symbol']}: {pos['contracts']} ({pos['side']})")
        print(f"    Entry: {pos['entryPrice']} | Mark: {pos['markPrice']} | PnL: {pnl:.2f}")
        print(f"    Margin: {pos['initialMargin']}")

    print(f"\nTotal Unrealized PnL: {total_pnl:.2f} USDT")


def check_balance(api: GrvtCcxt):
    """Check account balance."""
    balance = api.fetch_balance()
    for currency, info in balance.items():
        if isinstance(info, dict) and float(info.get("total", 0)) > 0:
            print(f"  {currency}: {info['total']} (free: {info['free']})")
    return balance


def check_positions(api: GrvtCcxt, symbols: list[str] | None = None):
    """Check open positions, optionally filtered by symbols."""
    positions = api.fetch_positions(symbols=symbols)
    if not positions:
        print("No open positions")
    for pos in positions:
        print(f"  {pos['symbol']}: {pos['contracts']} ({pos['side']})")
        print(f"    Entry: {pos['entryPrice']}, Unrealized PnL: {pos['unrealizedPnl']}")
    return positions


def recent_trades(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp", limit: int = 20):
    """Show recent fills/trades for a symbol."""
    fills = api.fetch_my_trades(symbol=symbol, limit=limit)
    for f in fills:
        print(f"  {f['datetime']}: {f['side']} {f['amount']} @ {f['price']}")
        print(f"    Fee: {f['fee']['cost']} {f['fee']['currency']}")
    return fills


def account_summary(api: GrvtCcxt):
    """Get detailed account summary."""
    summary = api.get_account_summary(type="sub-account")
    print("=== Account Summary ===")
    print(summary)
    return summary


if __name__ == "__main__":
    api = create_api("testnet")
    portfolio_overview(api)
