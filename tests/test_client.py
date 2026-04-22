import pytest
from unittest.mock import AsyncMock, patch

from banaperp import BanaClient, Market, Position, PositionSide
from banaperp.perp import calculate_pnl, required_collateral
from banaperp.markets import FundingRate


class TestMarket:
    def test_spread(self):
        m = Market(
            symbol="SOL-PERP",
            base_asset="SOL",
            mark_price=152.50,
            index_price=152.00,
            open_interest=5_000_000,
            volume_24h=12_000_000,
            funding_rate=0.0012,
        )
        assert m.spread == pytest.approx(0.50)
        assert m.spread_bps == pytest.approx(32.89, rel=1e-2)

    def test_str_representation(self):
        m = Market("BTC-PERP", "BTC", 65000.0, 64980.0, 1e8, 2e8, -0.0005)
        assert "BTC-PERP" in str(m)
        assert "65000" in str(m)


class TestPosition:
    def _make_long(self) -> Position:
        return Position(
            symbol="SOL-PERP",
            side=PositionSide.LONG,
            size=10.0,
            entry_price=140.0,
            mark_price=155.0,
            leverage=5.0,
            collateral=280.0,
        )

    def _make_short(self) -> Position:
        return Position(
            symbol="SOL-PERP",
            side=PositionSide.SHORT,
            size=10.0,
            entry_price=155.0,
            mark_price=140.0,
            leverage=5.0,
            collateral=310.0,
        )

    def test_long_pnl_positive(self):
        pos = self._make_long()
        assert pos.unrealized_pnl == pytest.approx(150.0)
        assert pos.is_profitable

    def test_short_pnl_positive(self):
        pos = self._make_short()
        assert pos.unrealized_pnl == pytest.approx(150.0)
        assert pos.is_profitable

    def test_long_pnl_negative(self):
        pos = self._make_long()
        pos.mark_price = 120.0
        assert pos.unrealized_pnl == pytest.approx(-200.0)
        assert not pos.is_profitable

    def test_notional(self):
        pos = self._make_long()
        assert pos.notional == pytest.approx(1550.0)

    def test_liquidation_price_long(self):
        pos = self._make_long()
        liq = pos.liquidation_price
        assert liq < pos.entry_price

    def test_liquidation_price_short(self):
        pos = self._make_short()
        liq = pos.liquidation_price
        assert liq > pos.entry_price

    def test_pnl_pct(self):
        pos = self._make_long()
        assert pos.unrealized_pnl_pct == pytest.approx(53.57, rel=1e-2)


class TestPerpUtils:
    def test_calculate_pnl_long(self):
        pnl = calculate_pnl(PositionSide.LONG, 100.0, 120.0, 5.0)
        assert pnl == pytest.approx(100.0)

    def test_calculate_pnl_short(self):
        pnl = calculate_pnl(PositionSide.SHORT, 120.0, 100.0, 5.0)
        assert pnl == pytest.approx(100.0)

    def test_required_collateral(self):
        col = required_collateral(10_000.0, 10.0)
        assert col == pytest.approx(1_000.0)


class TestFundingRate:
    def test_positive_direction(self):
        fr = FundingRate("SOL-PERP", 0.001, 1.0)
        assert fr.is_positive
        assert "longs pay" in fr.direction

    def test_negative_direction(self):
        fr = FundingRate("SOL-PERP", -0.001, -1.0)
        assert not fr.is_positive
        assert "shorts pay" in fr.direction


class TestBanaClient:
    @pytest.mark.asyncio
    async def test_get_spot_prices_empty(self):
        async with BanaClient() as client:
            with patch.object(client._http, "get", new_callable=AsyncMock) as mock_get:
                mock_resp = AsyncMock()
                mock_resp.json.return_value = {"solana": {"usd": 150.0}}
                mock_resp.raise_for_status = lambda: None
                mock_get.return_value = mock_resp

                prices = await client.get_spot_prices(["SOL"])
                assert "SOL" in prices
                assert prices["SOL"] == 150.0

    @pytest.mark.asyncio
    async def test_get_markets_returns_list(self):
        async with BanaClient() as client:
            mock_prices = {"SOL": 150.0, "BTC": 65000.0, "ETH": 3200.0}
            with patch.object(client, "get_spot_prices", new_callable=AsyncMock) as mock_sp:
                mock_sp.return_value = mock_prices
                markets = await client.get_markets()
                assert len(markets) > 0
                for m in markets:
                    assert isinstance(m, Market)
                    assert m.mark_price > 0

    @pytest.mark.asyncio
    async def test_get_market_not_found(self):
        async with BanaClient() as client:
            with patch.object(client, "get_spot_prices", new_callable=AsyncMock) as mock_sp:
                mock_sp.return_value = {}
                result = await client.get_market("FAKE-PERP")
                assert result is None
