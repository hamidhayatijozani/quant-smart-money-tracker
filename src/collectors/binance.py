"""Binance Futures Collector.

Supports:
- Public Leaderboard (ROI / PnL)
- Position fetching for specific traders (requires authenticated endpoints or third-party sources)
- WebSocket market data (placeholder for user data stream)
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseCollector, LeaderboardEntry, Position

logger = logging.getLogger(__name__)


class BinanceCollector(BaseCollector):
    """Collector for Binance USD-M Futures."""

    BASE_URL = "https://fapi.binance.com"
    # Public leaderboard endpoint (unofficial but widely used)
    LEADERBOARD_URL = "https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherLeaderboardBaseInfo"
    LEADERBOARD_RANK_URL = "https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getLeaderboardRank"

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        timeout: float = 15.0,
    ):
        super().__init__(exchange_name="binance")
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {}
            if self.api_key:
                headers["X-MBX-APIKEY"] = self.api_key
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=self.timeout,
                headers=headers,
            )
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def fetch_leaderboard(
        self, period: str = "WEEKLY", limit: int = 50
    ) -> List[LeaderboardEntry]:
        """
        Fetch top traders from Binance Futures Leaderboard.

        period: DAILY | WEEKLY | MONTHLY | ALL
        """
        period_map = {
            "daily": "DAILY",
            "weekly": "WEEKLY",
            "monthly": "MONTHLY",
            "all": "ALL",
        }
        period_key = period_map.get(period.lower(), "WEEKLY")

        payload = {
            "isShared": True,
            "isTrader": False,
            "periodType": period_key,
            "statisticsType": "ROI",  # or "PNL"
            "tradeType": "PERPETUAL",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Primary rank endpoint
            resp = await client.post(
                self.LEADERBOARD_RANK_URL,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        entries: List[LeaderboardEntry] = []
        raw_list = data.get("data", []) if isinstance(data, dict) else []

        for idx, item in enumerate(raw_list[:limit]):
            try:
                trader_id = str(item.get("encryptedUid") or item.get("uid") or item.get("userId") or f"unknown_{idx}")
                roi = float(item.get("roi", 0) or item.get("value", 0) or 0)
                pnl = float(item.get("pnl", 0) or 0)
                nickname = item.get("nickName") or item.get("nickname")

                entries.append(
                    LeaderboardEntry(
                        exchange="binance",
                        trader_id=trader_id,
                        nickname=nickname,
                        roi=roi,
                        pnl=pnl,
                        period=period.lower(),
                        rank=idx + 1,
                        timestamp=datetime.now(timezone.utc),
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to parse leaderboard item: {e}")
                continue

        logger.info(f"Fetched {len(entries)} Binance leaderboard entries for period={period_key}")
        return entries

    async def fetch_positions(self, trader_id: str) -> List[Position]:
        """
        Fetch open positions for a specific trader.

        Note: Official Binance API does not expose other users' positions publicly.
        This method is a placeholder that can be extended with:
        - Third-party scrapers / Apify actors
        - Shared position endpoints if available
        - Your own copy-trading data source
        """
        logger.warning(
            f"fetch_positions for {trader_id} is not fully implemented via public API. "
            "Use a dedicated data provider or scraper for production."
        )
        # Return empty for now – real implementation would call a data provider
        return []

    async def stream_positions(self, trader_ids: List[str]) -> AsyncIterator[Position]:
        """
        Placeholder for real-time position stream.

        In production this would connect to a custom WebSocket feed or
        a service that pushes position updates of tracked traders.
        """
        logger.info(f"Starting position stream for {len(trader_ids)} traders (placeholder)")
        # Infinite placeholder generator
        while True:
            await asyncio.sleep(10)
            # In real version: yield Position(...) when update arrives
            if False:  # keep type checker happy
                yield Position(  # type: ignore
                    exchange="binance",
                    trader_id="",
                    symbol="",
                    side="LONG",
                    size=0.0,
                    entry_price=0.0,
                    timestamp=datetime.now(timezone.utc),
                )

    async def get_mark_price(self, symbol: str) -> Optional[float]:
        """Get current mark price for a symbol."""
        client = await self._get_client()
        resp = await client.get("/fapi/v1/premiumIndex", params={"symbol": symbol})
        resp.raise_for_status()
        data = resp.json()
        return float(data.get("markPrice", 0))

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
