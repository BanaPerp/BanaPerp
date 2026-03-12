from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Market:
    symbol: str
    base_asset: str
    mark_price: float
    index_price: float
    open_interest: float
    volume_24h: float
    funding_rate: float
    max_leverage: int = 20
    extra: dict = field(default_factory=dict)

    @property
    def spread(self) -> float:
        return abs(self.mark_price - self.index_price)

    @property
    def spread_bps(self) -> float:
        if self.index_price == 0:
            return 0.0
        return (self.spread / self.index_price) * 10_000

    def __str__(self) -> str:
        return (
            f"{self.symbol} | Mark: ${self.mark_price:.4f} | "
            f"Index: ${self.index_price:.4f} | "
            f"Funding: {self.funding_rate:.4f}% | "
            f"OI: ${self.open_interest:,.0f}"
        )


@dataclass
class FundingRate:
    symbol: str
    rate: float
    annualized: float
    next_funding_time: Optional[int] = None

    @property
    def is_positive(self) -> bool:
        return self.rate >= 0

    @property
    def direction(self) -> str:
        return "longs pay shorts" if self.is_positive else "shorts pay longs"


JUPITER_PERP_MARKETS = [
    "SOL-PERP",
    "BTC-PERP",
    "ETH-PERP",
    "JUP-PERP",
    "BONK-PERP",
    "WIF-PERP",
]

COINGECKO_IDS = {
    "SOL": "solana",
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "JUP": "jupiter-exchange-solana",
    "BONK": "bonk",
    "WIF": "dogwifhat",
    "BANA": "banaperp",
}
