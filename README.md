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

### What's covered

- **Orders** — limit, market, cancel (single/all), open orders, order history, fill history
- **Trigger orders** — native TP/SL with TAKE_PROFIT / STOP_LOSS, triggered by MARK / INDEX / LAST / MID price
- **Position config** — switch between CROSS and ISOLATED margin, set leverage (1-50x)
- **Market data** — tickers, orderbook depth (10/50/100/500), recent trades, OHLCV candlesticks (16 timeframes), funding rates, instrument discovery
- **Account** — balance, open positions with PnL, account summary, funding payment history

### Not yet covered

- Transfers (trading-to-funding, funding-to-trading, between sub-accounts)
- Withdrawals
- WebSocket real-time streaming

## Setup

1. Install the Python SDK:
   ```bash
   pip install grvt-pysdk
   ```

2. Set credentials via `.env` file (recommended) or environment variables:

   Create a `.env` file in your project root:
   ```bash
   # Trading API Key — for orders, positions, trading account operations
   GRVT_TRADING_API_KEY=<your Trading API Key>
   GRVT_TRADING_PRIVATE_KEY=<private key for Trading API Key>

   # Funding API Key — for funding account transfers (optional)
   GRVT_FUNDING_API_KEY=<your Funding API Key>
   GRVT_FUNDING_PRIVATE_KEY=<private key for Funding API Key>

   GRVT_ENV=testnet  # or prod
   ```

   Or export them directly:
   ```bash
   export GRVT_TRADING_API_KEY="<your Trading API Key>"
   export GRVT_TRADING_PRIVATE_KEY="<private key for Trading API Key>"
   export GRVT_ENV="testnet"
   ```

3. Get your API keys at:
   - Production: [exchange.grvt.io/exchange/account/api-keys](https://exchange.grvt.io/exchange/account/api-keys)
   - Testnet: [exchange.testnet.grvt.io/exchange/account/api-keys](https://exchange.testnet.grvt.io/exchange/account/api-keys)

   Both Trading and Funding API keys are managed on this page. The `trading_account_id` is auto-detected from the login response.

## Recommended: Enable Auto-Run

For the best natural language experience (no code preview prompts), enable auto-run in your AI tool:

- **Claude Code**: `claude --dangerously-skip-permissions`
- **Cursor**: Settings → Features → Enable "Auto-Run"
- **Codex**: Use `--full-auto` flag

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
