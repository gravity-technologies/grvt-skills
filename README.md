# GRVT Skills

AI agent skills for trading on [GRVT](https://grvt.io) — a high-performance derivatives exchange.

## Installation

```bash
npx skills add gravity-technologies/grvt-skills
```

Or install individual skills:

```bash
npx skills add gravity-technologies/grvt-skills/skills/perpetual-trading
npx skills add gravity-technologies/grvt-skills/skills/market-data
npx skills add gravity-technologies/grvt-skills/skills/account-management
```

Works with Claude Code, Cursor, Codex, GitHub Copilot, Windsurf, Gemini CLI, and any agent supporting the [open skills ecosystem](https://github.com/vercel-labs/skills).

## Skills

| Skill | Description |
|-------|-------------|
| **perpetual-trading** | Place, cancel, and manage perpetual futures orders |
| **market-data** | Fetch prices, orderbooks, candles, funding rates |
| **account-management** | Check balances, positions, PnL, trade history |

## Setup

1. Install the Python SDK:
   ```bash
   pip install grvt-pysdk
   ```

2. Set environment variables:
   ```bash
   export GRVT_API_KEY="<from GRVT exchange UI>"
   export GRVT_TRADING_ACCOUNT_ID="<your trading account ID>"
   export GRVT_PRIVATE_KEY="<your private key>"
   ```

3. Get your API key at [exchange.grvt.io](https://exchange.grvt.io) (production) or [exchange.testnet.grvt.io](https://exchange.testnet.grvt.io) (testnet).

## Usage

Once installed, ask your AI agent things like:

- "Buy 0.01 BTC perpetual at market price on GRVT"
- "What's the current ETH funding rate on GRVT?"
- "Show me my open positions and PnL"
- "Cancel all my open orders"
- "Get the 1h candles for BTC_USDT_Perp"

## Resources

- [GRVT API Documentation](https://api-docs.grvt.io/)
- [grvt-pysdk on GitHub](https://github.com/gravity-technologies/grvt-pysdk)
- [grvt-pysdk on PyPI](https://pypi.org/project/grvt-pysdk/)

## License

MIT
