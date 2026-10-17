"""MQL5 Signals style collector.

In production this would connect to MQL5 API / scraping layer (with proper
authorization). For an immediately operational product we include a rich
**Demo Mode** that generates realistic, high-quality signal providers so the
full pipeline (discovery → scoring → storage → signal generation) can be
demonstrated and tested without external dependencies.
"""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from .base import (
    BaseCopyTradingCollector,
    CopySignalProvider,
    OpenTrade,
    ProviderType,
    RiskLevel,
)

logger = logging.getLogger(__name__)


class MQL5Collector(BaseCopyTradingCollector):
    """Collector inspired by MQL5 Signals marketplace."""

    def __init__(self, demo_mode: bool = True):
        super().__init__(provider=ProviderType.MQL5)
        self.demo_mode = demo_mode
        self._demo_providers: Optional[List[CopySignalProvider]] = None

    async def fetch_top_providers(
        self,
        min_gain: float = 15.0,
        max_drawdown: float = 25.0,
        min_trades: int = 80,
        limit: int = 25,
    ) -> List[CopySignalProvider]:
        if self.demo_mode:
            return await self._generate_demo_providers(
                min_gain=min_gain,
                max_drawdown=max_drawdown,
                min_trades=min_trades,
                limit=limit,
            )

        # Production path (placeholder for real MQL5 integration)
        logger.warning("Real MQL5 API integration not yet configured. Falling back to demo.")
        return await self._generate_demo_providers(min_gain, max_drawdown, min_trades, limit)

    async def fetch_open_trades(self, signal_id: str) -> List[OpenTrade]:
        if self.demo_mode:
            return self._generate_demo_open_trades(signal_id)

        logger.warning("Real open trades fetch not implemented yet.")
        return []

    async def _generate_demo_providers(
        self,
        min_gain: float,
        max_drawdown: float,
        min_trades: int,
        limit: int,
    ) -> List[CopySignalProvider]:
        """Generate realistic high-quality demo signal providers."""

        if self._demo_providers is None:
            self._demo_providers = self._build_realistic_demo_set()

        filtered = [
            p for p in self._demo_providers
            if p.gain_percent >= min_gain
            and p.max_drawdown <= max_drawdown
            and p.total_trades >= min_trades
            and p.is_active
        ]

        # Sort by quality score descending
        filtered.sort(key=lambda x: x.quality_score, reverse=True)
        return filtered[:limit]

    def _build_realistic_demo_set(self) -> List[CopySignalProvider]:
        """Hand-crafted + procedurally varied realistic providers."""

        base_providers = [
            {
                "signal_id": "mql5_aurora_eurusd",
                "name": "Aurora EURUSD Swing",
                "author": "Marcus V.",
                "gain_percent": 87.4,
                "max_drawdown": 14.2,
                "profit_factor": 1.92,
                "win_rate": 68.5,
                "total_trades": 312,
                "subscribers": 184,
                "risk_level": RiskLevel.LOW,
                "age_days": 420,
                "avg_trade_duration_hours": 38.0,
                "description": "Low-frequency swing trading on EURUSD with strict risk rules.",
            },
            {
                "signal_id": "mql5_nightowl_gbp",
                "name": "NightOwl GBP Scalper",
                "author": "Elena K.",
                "gain_percent": 142.8,
                "max_drawdown": 22.6,
                "profit_factor": 1.67,
                "win_rate": 61.2,
                "total_trades": 891,
                "subscribers": 67,
                "risk_level": RiskLevel.MEDIUM,
                "age_days": 210,
                "avg_trade_duration_hours": 2.4,
                "description": "London session scalping with tight stops.",
            },
            {
                "signal_id": "mql5_quantum_multi",
                "name": "Quantum Multi-Pair",
                "author": "Alex Rivera",
                "gain_percent": 63.1,
                "max_drawdown": 11.8,
                "profit_factor": 2.15,
                "win_rate": 72.0,
                "total_trades": 178,
                "subscribers": 312,
                "risk_level": RiskLevel.LOW,
                "age_days": 510,
                "avg_trade_duration_hours": 56.0,
                "description": "Multi-pair mean-reversion with strong risk control.",
            },
            {
                "signal_id": "mql5_titan_xau",
                "name": "Titan Gold Hunter",
                "author": "Sofia M.",
                "gain_percent": 198.5,
                "max_drawdown": 28.4,
                "profit_factor": 1.78,
                "win_rate": 58.9,
                "total_trades": 245,
                "subscribers": 95,
                "risk_level": RiskLevel.HIGH,
                "age_days": 155,
                "avg_trade_duration_hours": 18.0,
                "description": "Aggressive XAUUSD breakout strategy.",
            },
            {
                "signal_id": "mql5_steady_compass",
                "name": "Steady Compass",
                "author": "David L.",
                "gain_percent": 41.7,
                "max_drawdown": 9.3,
                "profit_factor": 2.41,
                "win_rate": 74.8,
                "total_trades": 156,
                "subscribers": 428,
                "risk_level": RiskLevel.LOW,
                "age_days": 680,
                "avg_trade_duration_hours": 72.0,
                "description": "Conservative long-term portfolio approach.",
            },
            {
                "signal_id": "mql5_velocity_usd",
                "name": "Velocity USDJPY",
                "author": "Kenji T.",
                "gain_percent": 76.2,
                "max_drawdown": 19.1,
                "profit_factor": 1.85,
                "win_rate": 64.3,
                "total_trades": 403,
                "subscribers": 121,
                "risk_level": RiskLevel.MEDIUM,
                "age_days": 290,
                "avg_trade_duration_hours": 9.5,
                "description": "Tokyo + New York session momentum.",
            },
            {
                "signal_id": "mql5_phoenix_recovery",
                "name": "Phoenix Recovery",
                "author": "Isabella R.",
                "gain_percent": 112.0,
                "max_drawdown": 16.7,
                "profit_factor": 1.94,
                "win_rate": 66.1,
                "total_trades": 267,
                "subscribers": 203,
                "risk_level": RiskLevel.MEDIUM,
                "age_days": 340,
                "avg_trade_duration_hours": 25.0,
                "description": "Post-news recovery and trend continuation.",
            },
            {
                "signal_id": "mql5_ironclad_risk",
                "name": "Ironclad Risk Manager",
                "author": "Thomas B.",
                "gain_percent": 38.9,
                "max_drawdown": 7.4,
                "profit_factor": 2.68,
                "win_rate": 78.2,
                "total_trades": 134,
                "subscribers": 516,
                "risk_level": RiskLevel.LOW,
                "age_days": 790,
                "avg_trade_duration_hours": 48.0,
                "description": "Extremely strict risk rules, slow and steady.",
            },
        ]

        providers = []
        for b in base_providers:
            providers.append(
                CopySignalProvider(
                    provider=ProviderType.MQL5,
                    signal_id=b["signal_id"],
                    name=b["name"],
                    author=b["author"],
                    gain_percent=b["gain_percent"],
                    max_drawdown=b["max_drawdown"],
                    profit_factor=b["profit_factor"],
                    win_rate=b["win_rate"],
                    total_trades=b["total_trades"],
                    subscribers=b["subscribers"],
                    risk_level=b["risk_level"],
                    is_active=True,
                    age_days=b["age_days"],
                    avg_trade_duration_hours=b["avg_trade_duration_hours"],
                    description=b["description"],
                    url=f"https://www.mql5.com/en/signals/{b['signal_id']}",
                    last_updated=datetime.now(timezone.utc),
                )
            )

        # Add a few more procedurally generated ones for variety
        for i in range(6):
            gain = round(random.uniform(25, 160), 1)
            dd = round(random.uniform(8, 27), 1)
            trades = random.randint(90, 650)
            providers.append(
                CopySignalProvider(
                    provider=ProviderType.MQL5,
                    signal_id=f"mql5_gen_{i+1:02d}",
                    name=f"Adaptive Strategy #{i+1}",
                    author=f"Trader_{random.randint(100,999)}",
                    gain_percent=gain,
                    max_drawdown=dd,
                    profit_factor=round(random.uniform(1.45, 2.4), 2),
                    win_rate=round(random.uniform(55, 75), 1),
                    total_trades=trades,
                    subscribers=random.randint(20, 280),
                    risk_level=RiskLevel.MEDIUM if dd > 18 else RiskLevel.LOW,
                    is_active=True,
                    age_days=random.randint(120, 600),
                    avg_trade_duration_hours=round(random.uniform(3, 60), 1),
                    description="Procedurally generated high-quality demo signal.",
                    last_updated=datetime.now(timezone.utc),
                )
            )

        return providers

    def _generate_demo_open_trades(self, signal_id: str) -> List[OpenTrade]:
        """Generate plausible open trades for a given signal."""
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "AUDUSD", "USDCAD"]
        sides = ["BUY", "SELL"]
        trades = []

        n = random.randint(1, 4)
        for i in range(n):
            symbol = random.choice(symbols)
            side = random.choice(sides)
            open_price = round(random.uniform(1.05, 1.25), 5) if "USD" in symbol else round(random.uniform(1900, 2100), 2)
            trades.append(
                OpenTrade(
                    provider=ProviderType.MQL5,
                    signal_id=signal_id,
                    ticket=f"T{random.randint(100000,999999)}",
                    symbol=symbol,
                    side=side,
                    volume=round(random.uniform(0.1, 2.5), 2),
                    open_price=open_price,
                    current_price=open_price * (1 + random.uniform(-0.004, 0.006)),
                    stop_loss=open_price * (0.997 if side == "BUY" else 1.003),
                    take_profit=open_price * (1.008 if side == "BUY" else 0.992),
                    profit=round(random.uniform(-80, 220), 2),
                    open_time=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
                )
            )
        return trades

    async def close(self) -> None:
        pass
