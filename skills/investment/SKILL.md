---
name: investment
description: Invest in and redeem from GRVT vaults. Use when the user wants to manage vault investments, check vault summaries, or view redemption queues.
---

# GRVT Vault Investment

## When to Use

Use this skill when the user wants to:
- Invest funds into a GRVT vault
- Redeem (withdraw) from a vault
- Cancel a pending redemption
- Check vault investor summary (LP tokens, PnL, equity)
- View vault redemption queue (for vault managers)
- View vault investor history
- List available vaults

## Prerequisites

```bash
pip install grvt-pysdk
```

GRVT has two types of API keys. Vault operations require **both**:
- **Funding API Key** — for invest, redeem, and vault queries
- **Trading API Key** — needed to initialize GrvtCcxt (provides trading_account_id)

```bash
export GRVT_TRADING_API_KEY="<Trading API Key from GRVT exchange UI>"
export GRVT_TRADING_PRIVATE_KEY="<private key associated with Trading API Key>"
export GRVT_FUNDING_API_KEY="<Funding API Key from GRVT exchange UI>"
export GRVT_FUNDING_PRIVATE_KEY="<private key associated with Funding API Key>"
export GRVT_ENV="testnet"  # or "prod"
```

Both key types can be created at:
- Production: https://exchange.grvt.io/exchange/account/api-keys
- Testnet: https://exchange.testnet.grvt.io/exchange/account/api-keys

## SDK Setup

```python
import os
import requests
from pathlib import Path
from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv

# Load .env file if present
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

env = os.getenv("GRVT_ENV", "testnet")
base = "edge.testnet.grvt.io" if env == "testnet" else "edge.grvt.io"

# Login with Trading API Key to get trading_account_id
trading_login = requests.post(
    f"https://{base}/auth/api_key/login",
    json={"api_key": os.getenv("GRVT_TRADING_API_KEY")},
).json()

# Login with Funding API Key to get funding_account_address
funding_login = requests.post(
    f"https://{base}/auth/api_key/login",
    json={"api_key": os.getenv("GRVT_FUNDING_API_KEY")},
).json()
funding_account_address = funding_login["funding_account_address"]

# Initialize SDK with Funding API Key for vault operations
api = GrvtCcxt(
    env=GrvtEnv.TESTNET if env == "testnet" else GrvtEnv.PRODUCTION,
    parameters={
        "api_key": os.getenv("GRVT_FUNDING_API_KEY"),
        "trading_account_id": trading_login["sub_account_id"],
        "private_key": os.getenv("GRVT_FUNDING_PRIVATE_KEY"),
    },
)

trades_base = "trades.testnet.grvt.io" if env == "testnet" else "trades.grvt.io"
```

## Discover Vaults

Vault IDs are **numeric** (`chain_vault_id`). Discover available vaults via the REST API:

```python
def list_vaults(env="testnet"):
    """List available investment strategies (vaults) with their numeric IDs."""
    base = "edge.testnet.grvt.io" if env == "testnet" else "edge.grvt.io"
    resp = requests.get(f"https://{base}/api/v1/investment/strategies").json()
    return resp.get("strategies", [])


# Usage:
# strategies = list_vaults(env)
# for s in strategies:
#     print(f"{s['chain_vault_id']:>12}  {s['status']:>8}  {s['name']} (by {s['manager_name']})")
```

Each strategy includes:
- `chain_vault_id` — numeric vault ID (use this for invest/redeem)
- `name`, `manager_name`, `status` (active/closed/delisted)
- `type` — "launchpad" or "standard"
- `management_fee`, `performance_fee` (in basis points, divide by 1e6 for %)
- `valuation_cap` — max vault size
- `min_redemption_period`, `max_redemption_period` (seconds)
- `categories` — strategy categories (e.g. "Directional", "Machine learning-driven")
- `estimated_stats` — apr, max_drawdown, sharpe_ratio (if enabled)

## Investor Summary

```python
# Get investment summary for a vault (use numeric vault_id)
result = api._auth_and_post(
    f"https://{trades_base}/full/v1/vault_investor_summary",
    {"main_account_id": funding_account_address, "vault_id": "<numeric_vault_id>"},
)
# Returns: vault_investor_summary list with:
#   sub_account_id, num_lp_tokens, avg_entry_price, current_price,
#   total_equity, all_time_realized_pnl, pending_redemption
```

## Vault Manager Investor History

```python
# For vault managers: view all investor activity
history = api.fetch_vault_manager_investor_history(only_own_investments=False)
# Returns list of: event_time, vault_id, type (VAULT_INVEST/VAULT_REDEEM/VAULT_BURN_LP_TOKEN), price, size, realized_pnl
```

## Vault Redemption Queue

```python
# For vault managers: view pending redemptions
queue = api.fetch_vault_redemption_queue()
# Returns: redemption_queue (list), pending/urgent counts, auto_redeemable_balance, share_price
```

## Invest in a Vault

The SDK does not natively support vault invest. Use this helper with EIP-712 signing:

```python
import time, random
from pysdk.grvt_ccxt_utils import get_EIP712_domain_data
from eth_account import Account
from eth_account.messages import encode_typed_data

CURRENCY_MAP = {"USD": 1, "USDC": 2, "USDT": 3, "ETH": 4, "BTC": 5}
CURRENCY_DECIMALS = {"USD": 6, "USDC": 6, "USDT": 6, "ETH": 18, "BTC": 8}

def vault_invest(api, vault_id, currency, amount, funding_account_address, private_key):
    """Invest funds into a GRVT vault.

    Args:
        api: GrvtCcxt instance (authenticated with Funding API Key)
        vault_id: numeric vault ID (chainVaultID from list_vaults)
        currency: "USDT", "USDC", etc.
        amount: human-readable amount (e.g. 100 for 100 USDT)
        funding_account_address: from login response
        private_key: Funding API Key private key
    """
    decimals = CURRENCY_DECIMALS[currency]
    num_tokens = int(amount * (10 ** decimals))
    expiration_ns = int((time.time() + 86400) * 1_000_000_000)
    nonce = random.randint(1, 2**32 - 1)

    domain_data = get_EIP712_domain_data(api.env)
    types = {
        "VaultInvest": [
            {"name": "vaultID", "type": "uint64"},
            {"name": "accountID", "type": "address"},
            {"name": "tokenCurrency", "type": "uint8"},
            {"name": "numTokens", "type": "uint64"},
            {"name": "nonce", "type": "uint32"},
            {"name": "expiration", "type": "int64"},
        ]
    }
    message_data = {
        "vaultID": int(vault_id),
        "accountID": funding_account_address,
        "tokenCurrency": CURRENCY_MAP[currency],
        "numTokens": num_tokens,
        "nonce": nonce,
        "expiration": expiration_ns,
    }

    message = encode_typed_data(domain_data, types, message_data)
    signed = Account.sign_message(message, private_key)
    signer = Account.from_key(private_key)

    payload = {
        "main_account_id": funding_account_address,
        "vault_id": str(vault_id),
        "currency": currency,
        "num_tokens": str(amount),
        "signature": {
            "signer": signer.address,
            "r": hex(signed.r),
            "s": hex(signed.s),
            "v": signed.v,
            "expiration": str(expiration_ns),
            "nonce": nonce,
        },
    }

    env_name = api.env.value
    base = "trades.testnet.grvt.io" if "testnet" in env_name else "trades.grvt.io"
    return api._auth_and_post(f"https://{base}/full/v1/vault_invest", payload)


# Usage:
# vault_invest(api, 1315997999, "USDT", 100, funding_account_address, os.getenv("GRVT_FUNDING_PRIVATE_KEY"))
```

## Redeem from a Vault

```python
def vault_redeem(api, vault_id, currency, num_lp_tokens, funding_account_address, private_key):
    """Redeem LP tokens from a GRVT vault.

    Args:
        api: GrvtCcxt instance (authenticated with Funding API Key)
        vault_id: numeric vault ID (chainVaultID)
        currency: "USDT", "USDC", etc.
        num_lp_tokens: number of LP tokens to redeem (human-readable)
        funding_account_address: from login response
        private_key: Funding API Key private key
    """
    decimals = CURRENCY_DECIMALS[currency]
    num_tokens_raw = int(num_lp_tokens * (10 ** decimals))
    expiration_ns = int((time.time() + 86400) * 1_000_000_000)
    nonce = random.randint(1, 2**32 - 1)

    domain_data = get_EIP712_domain_data(api.env)
    types = {
        "VaultRedeem": [
            {"name": "vaultID", "type": "uint64"},
            {"name": "tokenCurrency", "type": "uint8"},
            {"name": "numLpTokens", "type": "uint64"},
            {"name": "accountID", "type": "address"},
            {"name": "nonce", "type": "uint32"},
            {"name": "expiration", "type": "int64"},
        ]
    }
    message_data = {
        "vaultID": int(vault_id),
        "tokenCurrency": CURRENCY_MAP[currency],
        "numLpTokens": num_tokens_raw,
        "accountID": funding_account_address,
        "nonce": nonce,
        "expiration": expiration_ns,
    }

    message = encode_typed_data(domain_data, types, message_data)
    signed = Account.sign_message(message, private_key)
    signer = Account.from_key(private_key)

    payload = {
        "main_account_id": funding_account_address,
        "vault_id": str(vault_id),
        "currency": currency,
        "num_tokens": str(num_lp_tokens),
        "signature": {
            "signer": signer.address,
            "r": hex(signed.r),
            "s": hex(signed.s),
            "v": signed.v,
            "expiration": str(expiration_ns),
            "nonce": nonce,
        },
    }

    env_name = api.env.value
    base = "trades.testnet.grvt.io" if "testnet" in env_name else "trades.grvt.io"
    return api._auth_and_post(f"https://{base}/full/v1/vault_redeem", payload)


# Usage:
# vault_redeem(api, 1315997999, "USDT", 5.0, funding_account_address, os.getenv("GRVT_FUNDING_PRIVATE_KEY"))
```

## Cancel a Pending Redemption

```python
def vault_redeem_cancel(api, vault_id, funding_account_address):
    """Cancel a pending vault redemption."""
    payload = {
        "main_account_id": funding_account_address,
        "vault_id": str(vault_id),
    }
    env_name = api.env.value
    base = "trades.testnet.grvt.io" if "testnet" in env_name else "trades.grvt.io"
    return api._auth_and_post(f"https://{base}/full/v1/vault_redeem_cancel", payload)
```

## Important Notes

- Vault invest/redeem require a **Funding API Key** (not Trading)
- `vault_id` must be the **numeric `chain_vault_id`** — discover it via `list_vaults()` REST endpoint
- `funding_account_address` is returned from the Funding API Key login response
- Currency amounts use decimal precision: USDT/USDC = 6 decimals, ETH = 18, BTC = 8
- Redemptions may have a waiting period set by the vault manager
- Only one pending redemption per vault per investor at a time
- Some vaults may be closed/delisted or at capacity — check the error message
