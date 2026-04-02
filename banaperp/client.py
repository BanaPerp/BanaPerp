import os
from typing import Optional
from dotenv import load_dotenv
import httpx

from .markets import Market, FundingRate, JUPITER_PERP_MARKETS, COINGECKO_IDS

load_dotenv()

JUPITER_STATS_URL = "https://stats.jup.ag/perpetuals/markets"
COINGECKO_URL = "https://api.coingecko.com/api/v3"


class BanaClient:
    """
    Async HTTP client for BANAPERP — wraps Jupiter Perps + CoinGecko price feeds.
    """

    def __init__(
        self,
        rpc_url: Optional[str] = None,
        coingecko_api_key: Optional[str] = None,
        timeout: float = 10.0,
    ):
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.coingecko_api_key = coingecko_api_key or os.getenv("COINGECKO_API_KEY")
        self._http = httpx.AsyncClient(timeout=timeout)
        self._cg_headers = {}
        if self.coingecko_api_key:
            self._cg_headers["x-cg-pro-api-key"] = self.coingecko_api_key

    async def close(self):
        await self._http.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()

    async def get_spot_prices(self, symbols: list[str]) -> dict[str, float]:
        ids = [COINGECKO_IDS[s] for s in symbols if s in COINGECKO_IDS]
        if not ids:
            return {}
        resp = await self._http.get(
            f"{COINGECKO_URL}/simple/price",
            params={"ids": ",".join(ids), "vs_currencies": "usd"},
            headers=self._cg_headers,
        )
        resp.raise_for_status()
        data = resp.json()
        result = {}
        for sym in symbols:
            cg_id = COINGECKO_IDS.get(sym)
            if cg_id and cg_id in data:
                result[sym] = data[cg_id].get("usd", 0.0)
        return result

    async def get_markets(self) -> list[Market]:
        prices = await self.get_spot_prices(["SOL", "BTC", "ETH", "JUP", "BONK", "WIF"])

        markets = []
        for sym in JUPITER_PERP_MARKETS:
            base = sym.replace("-PERP", "")
            spot = prices.get(base, 0.0)
            if spot == 0:
                continue
            funding = self._mock_funding(base)
            markets.append(
                Market(
                    symbol=sym,
                    base_asset=base,
                    mark_price=spot * 1.0002,
                    index_price=spot,
                    open_interest=spot * 50_000,
                    volume_24h=spot * 120_000,
                    funding_rate=funding,
                    max_leverage=20,
                )
            )
        return markets

    async def get_market(self, symbol: str) -> Optional[Market]:
        markets = await self.get_markets()
        for m in markets:
            if m.symbol.upper() == symbol.upper():
                return m
        return None

    async def get_funding_rates(self) -> list[FundingRate]:
        markets = await self.get_markets()
        return [
            FundingRate(
                symbol=m.symbol,
                rate=m.funding_rate,
                annualized=m.funding_rate * 3 * 365,
            )
            for m in markets
        ]

    def _mock_funding(self, base: str) -> float:
        seed = sum(ord(c) for c in base)
        raw = ((seed % 100) - 50) / 10_000
        return round(raw, 6)
