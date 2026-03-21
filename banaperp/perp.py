from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"


@dataclass
class Position:
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    mark_price: float
    leverage: float
    collateral: float
    wallet: Optional[str] = None

    @property
    def notional(self) -> float:
        return self.size * self.mark_price

    @property
    def unrealized_pnl(self) -> float:
        if self.side == PositionSide.LONG:
            return (self.mark_price - self.entry_price) * self.size
        return (self.entry_price - self.mark_price) * self.size

    @property
    def unrealized_pnl_pct(self) -> float:
        if self.collateral == 0:
            return 0.0
        return (self.unrealized_pnl / self.collateral) * 100

    @property
    def liquidation_price(self) -> float:
        margin_ratio = 1 / self.leverage
        if self.side == PositionSide.LONG:
            return self.entry_price * (1 - margin_ratio + 0.005)
        return self.entry_price * (1 + margin_ratio - 0.005)

    @property
    def is_profitable(self) -> bool:
        return self.unrealized_pnl > 0

    def __str__(self) -> str:
        pnl_sign = "+" if self.unrealized_pnl >= 0 else ""
        return (
            f"{self.side.value.upper()} {self.symbol} | "
            f"Size: {self.size:.4f} | "
            f"Entry: ${self.entry_price:.4f} | "
            f"Mark: ${self.mark_price:.4f} | "
            f"PnL: {pnl_sign}{self.unrealized_pnl:.4f} ({pnl_sign}{self.unrealized_pnl_pct:.2f}%) | "
            f"Liq: ${self.liquidation_price:.4f}"
        )


def calculate_pnl(side: PositionSide, entry: float, mark: float, size: float) -> float:
    if side == PositionSide.LONG:
        return (mark - entry) * size
    return (entry - mark) * size


def required_collateral(notional: float, leverage: float) -> float:
    return notional / leverage
