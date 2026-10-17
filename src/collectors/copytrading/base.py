"""Base classes for Copy Trading / MetaTrader signal providers.

These providers are fundamentally different from crypto exchange leaderboards:
Traders *explicitly* allow others to copy their trades. Therefore position
and performance data is intentionally shared and more reliable for signal
generation.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    MQL5 = "mql5"
    MYFXBOOK = "myfxbook"
    ZULUTRADE = "zulutrade"
    ETORO = "etoro"
    DARWINEX = "darwinex"
    GENERIC_MT = "metatrader"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class CopySignalProvider(BaseModel):
    """Normalized representation of a copy-trading signal provider."""
    provider: ProviderType
    signal_id: str
    name: str
    author: Optional[str] = None
    gain_percent: float = 0.0          # Total gain %
    max_drawdown: float = 0.0          # Absolute max DD %
    profit_factor: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: int = 0
    subscribers: int = 0
    risk_level: RiskLevel = RiskLevel.MEDIUM
    is_active: bool = True
    age_days: Optional[int] = None
    avg_trade_duration_hours: Optional[float] = None
    leverage: Optional[float] = None
    description: Optional[str] = None
    url: Optional[str] = None
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw: Optional[Dict[str, Any]] = None

    @property
    def quality_score(self) -> float:
        """Simple heuristic quality score (0-1) based on public metrics."""
        score = 0.5

        # Reward consistent positive gain with controlled drawdown
        if self.gain_percent > 20 and self.max_drawdown < 25:
            score += 0.2
        if self.gain_percent > 50 and self.max_drawdown < 20:
            score += 0.15

        # Penalize extreme drawdown
        if self.max_drawdown > 40:
            score -= 0.25
        if self.max_drawdown > 60:
            score -= 0.3

        # Reward sample size
        if self.total_trades > 100:
            score += 0.1
        if self.total_trades > 500:
            score += 0.05

        # Reward popularity (but not too much)
        if self.subscribers > 50:
            score += 0.05
        if self.subscribers > 200:
            score += 0.05

        return max(0.0, min(1.0, score))


class OpenTrade(BaseModel):
    """A currently open trade from a copy signal provider."""
    provider: ProviderType
    signal_id: str
    ticket: Optional[str] = None
    symbol: str
    side: str                          # BUY / SELL
    volume: float
    open_price: float
    current_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    profit: Optional[float] = None
    open_time: datetime
    magic: Optional[int] = None


class BaseCopyTradingCollector(ABC):
    """Abstract base for all copy-trading / MetaTrader signal collectors."""

    def __init__(self, provider: ProviderType):
        self.provider = provider

    @abstractmethod
    async def fetch_top_providers(
        self,
        min_gain: float = 10.0,
        max_drawdown: float = 30.0,
        min_trades: int = 50,
        limit: int = 30,
    ) -> List[CopySignalProvider]:
        """Fetch ranked list of high-quality signal providers."""
        ...

    @abstractmethod
    async def fetch_open_trades(self, signal_id: str) -> List[OpenTrade]:
        """Fetch currently open trades of a specific signal provider."""
        ...

    @abstractmethod
    async def close(self) -> None:
        ...
