# 🍌 BANAPERP

> Perpetual trading SDK for Solana — peel the market, go long or short.

[![Python](https://img.shields.io/badge/python-3.11+-yellow.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/nujar00t/banaperp/actions/workflows/ci.yml/badge.svg)](https://github.com/nujar00t/banaperp/actions)
[![PyPI](https://img.shields.io/pypi/v/banaperp.svg)](https://pypi.org/project/banaperp)

BANAPERP is a lightweight Python SDK for interacting with Solana perpetual markets. Built for traders, bots, and degens who want programmatic access to on-chain perps without the overhead of a full trading framework.

It connects to Jupiter Perps and on-chain price feeds — giving you real-time position data, mark prices, funding rates, and trade execution in a clean Python interface.

---

## Features

- Fetch live perpetual market data (mark price, funding rate, OI)
- Open and track long/short positions via Solana RPC
- CLI tool for quick terminal-based market checks
- Async-first design — non-blocking, fast
- CoinGecko integration for spot price reference
- Fully typed with dataclasses

---

## Install

```bash
pip install banaperp
```

Or from source:

```bash
git clone https://github.com/nujar00t/banaperp
cd banaperp
pip install -e .
```

---

## Quickstart

```python
from banaperp import BanaClient

client = BanaClient()

# get all available perp markets
markets = await client.get_markets()
for m in markets:
    print(m.symbol, m.mark_price, m.funding_rate)

# get SOL-PERP details
sol = await client.get_market("SOL-PERP")
print(f"SOL Mark: ${sol.mark_price:.2f} | Funding: {sol.funding_rate:.4f}%")
```

---

## CLI

```bash
# list all markets
banaperp markets

# get specific market
banaperp market SOL-PERP

# check funding rates
banaperp funding

# watch prices live
banaperp watch SOL-PERP
```

---

## Config

Set via `.env` or environment variables:

```env
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
COINGECKO_API_KEY=your_key_here   # optional, for higher rate limits
REFRESH_INTERVAL=5                # seconds between price updates
```

---

## Architecture

```
banaperp/
├── client.py     # main SDK client, async HTTP
├── markets.py    # market data models + fetchers
├── perp.py       # position management, PnL calculations
└── cli.py        # Click CLI entrypoint
```

---

## Supported Markets

| Symbol | Exchange | Status |
|--------|----------|--------|
| SOL-PERP | Jupiter Perps | ✅ Live |
| BTC-PERP | Jupiter Perps | ✅ Live |
| ETH-PERP | Jupiter Perps | ✅ Live |
| BANA-PERP | BANAPERP Native | 🔜 Soon |

---

## License

MIT — see [LICENSE](LICENSE)
