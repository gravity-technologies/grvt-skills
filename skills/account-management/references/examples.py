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
    print(f"USDT Balance: {balance['total']['USDT']}")
    print(f"  Available: {balance['free']['USDT']}")
    print(f"  In Use:    {balance['used']['USDT']}")

    # Detailed info from balance["info"]
    for entry in balance["info"]:
        print(f"  {entry['currency']}: unrealized_pnl={entry['unrealized_pnl']}")

    print(f"\nOpen Positions ({len(positions)}):")
    total_pnl = 0
    for pos in positions:
        pnl = float(pos.get("unrealized_pnl", 0))
        total_pnl += pnl
        side = "long" if float(pos["size"]) > 0 else "short"
        print(f"  {pos['instrument']}: {pos['size']} ({side})")
        print(f"    Entry: {pos['entry_price']} | Mark: {pos['mark_price']} | PnL: {pnl:.2f}")
        print(f"    Leverage: {pos['leverage']}x | Margin: {pos['margin_type']}")

    print(f"\nTotal Unrealized PnL: {total_pnl:.2f} USDT")


def check_balance(api: GrvtCcxt):
    """Check account balance."""
    balance = api.fetch_balance()
    print(f"Total:     {balance['total']['USDT']} USDT")
    print(f"Available: {balance['free']['USDT']} USDT")
    print(f"In Use:    {balance['used']['USDT']} USDT")
    return balance


def check_positions(api: GrvtCcxt, symbols: list[str] | None = None):
    """Check open positions, optionally filtered by symbols."""
    positions = api.fetch_positions(symbols=symbols)
    if not positions:
        print("No open positions")
    for pos in positions:
        side = "long" if float(pos["size"]) > 0 else "short"
        print(f"  {pos['instrument']}: {pos['size']} ({side})")
        print(f"    Entry: {pos['entry_price']}, PnL: {pos['unrealized_pnl']}")
    return positions


def recent_trades(api: GrvtCcxt, symbol: str = "BTC_USDT_Perp", limit: int = 20):
    """Show recent fills/trades for a symbol."""
    fills = api.fetch_my_trades(symbol=symbol, limit=limit)
    for f in fills:
        side = "buy" if f.get("is_taker_buyer") else "sell"
        print(f"  {side} {f['size']} @ {f['price']} — trade_id: {f['trade_id']}")
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
