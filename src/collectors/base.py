"""Base collector interface for exchange data collection."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


class Position(BaseModel):
    """Normalized position data across exchanges."""
    exchange: str
    trader_id: str
    symbol: str
    side: str  # LONG / SHORT
    size: float
    entry_price: float
    mark_price: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    leverage: Optional[float] = None
    timestamp: datetime
    raw: Optional[Dict[str, Any]] = None


class LeaderboardEntry(BaseModel):
    """Normalized leaderboard entry."""
    exchange: str
    trader_id: str
    nickname: Optional[str] = None
    roi: float
    pnl: float
    period: str  # daily / weekly / monthly / all
    rank: Optional[int] = None
    timestamp: datetime


class BaseCollector(ABC):
    """Abstract base class for all exchange collectors."""

    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name

    @abstractmethod
    async def fetch_leaderboard(
        self, period: str = "weekly", limit: int = 50
    ) -> List[LeaderboardEntry]:
        """Fetch top traders from leaderboard."""
        ...

    @abstractmethod
    async def fetch_positions(self, trader_id: str) -> List[Position]:
        """Fetch current open positions of a specific trader."""
        ...

    @abstractmethod
    async def stream_positions(self, trader_ids: List[str]) -> AsyncIterator[Position]:
        """Stream real-time position updates via WebSocket."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""
        ...
