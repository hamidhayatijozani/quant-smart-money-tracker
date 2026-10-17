"""Intelligent Signal Engine.

Combines:
- Copy Trading provider quality metrics
- Behavioral trust scoring
- Risk filters
- Shadow mode safety

Produces ranked, actionable signals ready for human review or automated execution.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.collectors.copytrading import CopySignalProvider, OpenTrade, RiskLevel
from src.ai_engine import BehavioralAIEngine, TrustScore
from src.config import settings

logger = logging.getLogger(__name__)


class ActionableSignal(BaseModel):
    """Final signal that can be reviewed or executed."""
    signal_id: str = Field(default_factory=lambda: str(uuid4()))
    source_type: str                       # "copytrading" | "crypto_leaderboard"
    provider: str
    provider_signal_id: str
    name: str
    symbol: Optional[str] = None
    side: Optional[str] = None
    strength: float                        # 0.0 – 1.0
    trust_score: float
    quality_score: float
    risk_level: str
    gain_percent: float
    max_drawdown: float
    subscribers: int
    recommended_action: str                # "COPY" | "WATCH" | "AVOID"
    reasoning: List[str] = []
    open_trades_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    shadow_mode: bool = True


class SignalEngine:
    """Core intelligence that turns raw providers into ranked actionable signals."""

    def __init__(self):
        self.ai = BehavioralAIEngine()
        self.min_quality = 0.55
        self.min_trust = settings.trust_score_threshold

    def evaluate_provider(
        self,
        provider: CopySignalProvider,
        open_trades: Optional[List[OpenTrade]] = None,
    ) -> ActionableSignal:
        """Evaluate a single provider and produce an actionable signal."""

        quality = provider.quality_score
        reasoning = []

        # Base strength from quality
        strength = quality

        # Risk adjustments
        if provider.risk_level == RiskLevel.LOW:
            strength += 0.08
            reasoning.append("Low risk profile (+)")
        elif provider.risk_level == RiskLevel.HIGH:
            strength -= 0.12
            reasoning.append("High risk profile (-)")
        elif provider.risk_level == RiskLevel.EXTREME:
            strength -= 0.25
            reasoning.append("Extreme risk – heavily penalized")

        # Drawdown penalty / reward
        if provider.max_drawdown < 12:
            strength += 0.07
            reasoning.append(f"Excellent max DD {provider.max_drawdown:.1f}%")
        elif provider.max_drawdown > 25:
            strength -= 0.1
            reasoning.append(f"Elevated max DD {provider.max_drawdown:.1f}%")

        # Consistency reward
        if provider.profit_factor and provider.profit_factor > 1.8:
            strength += 0.06
            reasoning.append(f"Strong profit factor {provider.profit_factor}")

        if provider.win_rate and provider.win_rate > 65:
            strength += 0.05
            reasoning.append(f"High win rate {provider.win_rate}%")

        # Popularity soft signal
        if provider.subscribers > 150:
            strength += 0.03
            reasoning.append("Strong subscriber base")

        strength = max(0.0, min(1.0, strength))

        # Decision logic
        if strength >= 0.78 and provider.max_drawdown <= 20:
            action = "COPY"
            reasoning.append("High conviction – recommended for copy")
        elif strength >= 0.62:
            action = "WATCH"
            reasoning.append("Interesting – monitor before copying")
        else:
            action = "AVOID"
            reasoning.append("Does not meet quality threshold")

        open_count = len(open_trades) if open_trades else 0

        return ActionableSignal(
            source_type="copytrading",
            provider=provider.provider.value,
            provider_signal_id=provider.signal_id,
            name=provider.name,
            strength=round(strength, 3),
            trust_score=round(quality, 3),  # using quality as proxy trust for now
            quality_score=round(quality, 3),
            risk_level=provider.risk_level.value,
            gain_percent=provider.gain_percent,
            max_drawdown=provider.max_drawdown,
            subscribers=provider.subscribers,
            recommended_action=action,
            reasoning=reasoning,
            open_trades_count=open_count,
            shadow_mode=settings.enable_shadow_mode,
        )

    def rank_signals(
        self,
        providers: List[CopySignalProvider],
        top_n: int = 10,
    ) -> List[ActionableSignal]:
        """Evaluate and rank multiple providers."""
        signals = [self.evaluate_provider(p) for p in providers]
        signals.sort(key=lambda s: s.strength, reverse=True)
        return signals[:top_n]
