"""
GRVT Perpetual Trading — Reference Examples

These examples demonstrate common perpetual trading operations using grvt-pysdk.
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


def place_limit_order(api: GrvtCcxt):
    """Place a limit buy order for BTC perpetual.

    Note: create_order returns order_id "0x00" — use metadata.client_order_id to track.
    Min notional is 100 USDT (price * amount >= 100).
    """
    order = api.create_order(
        symbol="BTC_USDT_Perp",
        order_type="limit",
        side="buy",
        amount=0.01,
        price=60000,
        params={"time_in_force": "GTC"},
    )
    cloid = order.get("metadata", {}).get("client_order_id")
    print(f"Order placed, client_order_id={cloid}")
    return order


def place_market_order(api: GrvtCcxt):
    """Place a market sell order for ETH perpetual."""
    order = api.create_order(
        symbol="ETH_USDT_Perp",
        order_type="market",
        side="sell",
        amount=0.1,
        price=0,
    )
    cloid = order.get("metadata", {}).get("client_order_id")
    print(f"Market order placed, client_order_id={cloid}")
    return order


def place_post_only_order(api: GrvtCcxt):
    """Place a post-only (maker) limit order."""
    order = api.create_order(
        symbol="BTC_USDT_Perp",
        order_type="limit",
        side="buy",
        amount=0.01,
        price=60000,
        params={"post_only": True},
    )
    return order


def place_stop_loss(api: GrvtCcxt, price: float, amount: float = 0.01):
    """Place a reduce-only limit sell as stop-loss for a long position.

    Note: SDK only supports 'limit' and 'market' order types.
    This is a limit order, not a true trigger order — it sits on the orderbook.
    For a long position, a sell below market will fill immediately like a market order.
    """
    order = api.create_order(
        symbol="BTC_USDT_Perp",
        order_type="limit",
        side="sell",
        amount=amount,
        price=price,
        params={"reduce_only": True},
    )
    return order


def place_take_profit(api: GrvtCcxt, price: float, amount: float = 0.01):
    """Place a reduce-only limit sell as take-profit for a long position.

    Note: SDK only supports 'limit' and 'market' order types.
    This is a limit order, not a true trigger order — it sits on the orderbook.
    For a long position, a sell above market will wait until price reaches the level.
    """
    order = api.create_order(
        symbol="BTC_USDT_Perp",
        order_type="limit",
        side="sell",
        amount=amount,
        price=price,
        params={"reduce_only": True},
    )
    return order


def cancel_by_client_order_id(api: GrvtCcxt, client_order_id: str):
    """Cancel an order by client_order_id (preferred method)."""
    result = api.cancel_order(id=None, params={"client_order_id": client_order_id})
    print(f"Cancel result: {result}")
    return result


def show_open_orders(api: GrvtCcxt):
    """Display all open orders with real order IDs."""
    orders = api.fetch_open_orders(symbol="BTC_USDT_Perp")
    for o in orders:
        leg = o["legs"][0]
        side = "buy" if leg["is_buying_asset"] else "sell"
        print(f"  {side} {leg['size']} @ {leg['limit_price']} [{o['order_id']}]")
        print(f"    client_order_id: {o['metadata']['client_order_id']}")
    return orders


if __name__ == "__main__":
    api = create_api("testnet")
    show_open_orders(api)
