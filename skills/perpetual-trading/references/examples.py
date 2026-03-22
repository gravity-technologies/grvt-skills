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
    """Place a limit buy order for BTC perpetual."""
    order = api.create_order(
        symbol="BTC_USDT_Perp",
        order_type="limit",
        side="buy",
        amount=0.01,
        price=90000,
        params={"time_in_force": "GTC"},
    )
    print(f"Order placed: {order['order_id']} status={order['status']}")
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
    print(f"Market order: {order['order_id']} filled={order['filled']}")
    return order


def place_post_only_order(api: GrvtCcxt):
    """Place a post-only (maker) limit order."""
    order = api.create_order(
        symbol="BTC_USDT_Perp",
        order_type="limit",
        side="buy",
        amount=0.01,
        price=89000,
        params={"post_only": True},
    )
    return order


def place_stop_loss(api: GrvtCcxt, trigger_price: float):
    """Place a stop-loss market order to protect a long position."""
    order = api.create_order(
        symbol="BTC_USDT_Perp",
        order_type="stop_market",
        side="sell",
        amount=0.01,
        price=0,
        params={
            "trigger_price": trigger_price,
            "reduce_only": True,
        },
    )
    return order


def place_take_profit(api: GrvtCcxt, trigger_price: float):
    """Place a take-profit market order to lock in gains on a long position."""
    order = api.create_order(
        symbol="BTC_USDT_Perp",
        order_type="take_profit_market",
        side="sell",
        amount=0.01,
        price=0,
        params={
            "trigger_price": trigger_price,
            "reduce_only": True,
        },
    )
    return order


def cancel_and_check(api: GrvtCcxt, order_id: str):
    """Cancel an order and verify cancellation."""
    api.cancel_order(id=order_id)
    order = api.fetch_order(id=order_id)
    print(f"Order {order_id} status: {order['status']}")
    return order


def show_open_orders(api: GrvtCcxt):
    """Display all open orders."""
    orders = api.fetch_open_orders(symbol="BTC_USDT_Perp")
    for o in orders:
        print(f"  {o['side']} {o['amount']} @ {o['price']} [{o['status']}]")
    return orders


if __name__ == "__main__":
    api = create_api("testnet")
    show_open_orders(api)
