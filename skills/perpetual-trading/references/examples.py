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


def create_trigger_order(api, symbol, side, amount, limit_price, trigger_type, trigger_price, trigger_by="MARK", reduce_only=True, private_key=None):
    """Place a native trigger order (TP/SL).

    The order stays dormant until trigger_price is reached, then becomes a limit order.
    Trigger metadata is unsigned — injected into the payload after EIP-712 signing.

    Args:
        trigger_type: "TAKE_PROFIT" or "STOP_LOSS"
        trigger_by: "MARK" (default), "INDEX", "LAST", or "MID"
    """
    from pysdk.grvt_ccxt_utils import get_grvt_order, get_order_payload
    from pysdk.grvt_ccxt_env import get_grvt_endpoint

    order = get_grvt_order(
        sub_account_id=api.get_trading_account_id(),
        symbol=symbol,
        order_type="limit",
        side=side,
        amount=amount,
        limit_price=limit_price,
        order_duration_secs=24 * 60 * 60,
        params={"reduce_only": reduce_only},
    )
    payload = get_order_payload(order, private_key=private_key, env=api.env, instruments=api.markets)
    payload["order"]["metadata"]["trigger"] = {
        "trigger_type": trigger_type,
        "tpsl": {
            "trigger_by": trigger_by,
            "trigger_price": str(trigger_price),
            "close_position": False,
        },
    }
    path = get_grvt_endpoint(api.env, "CREATE_ORDER")
    return api._auth_and_post(path, payload)


def place_stop_loss(api: GrvtCcxt, trigger_price: float, limit_price: float, amount: float = 0.01, private_key: str = None):
    """Place a stop-loss trigger order to protect a long position."""
    return create_trigger_order(
        api, "BTC_USDT_Perp", side="sell", amount=amount,
        limit_price=limit_price, trigger_type="STOP_LOSS",
        trigger_price=trigger_price, private_key=private_key,
    )


def place_take_profit(api: GrvtCcxt, trigger_price: float, limit_price: float, amount: float = 0.01, private_key: str = None):
    """Place a take-profit trigger order to lock in gains on a long position."""
    return create_trigger_order(
        api, "BTC_USDT_Perp", side="sell", amount=amount,
        limit_price=limit_price, trigger_type="TAKE_PROFIT",
        trigger_price=trigger_price, private_key=private_key,
    )


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
