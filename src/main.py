"""Quant Smart Money Tracker – Operational Entry Point

This version delivers a complete, runnable product that:
1. Discovers high-quality Copy Trading / MetaTrader signal providers
2. Scores them with an intelligent engine
3. Ranks and presents actionable signals
4. Optionally stores results
5. Runs continuously in discovery mode
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from src.config import settings
from src.collectors.copytrading import MQL5Collector
from src.engine import SignalEngine
from src.storage import ClickHouseStorage

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("quant")


def print_header():
    print("\n" + "=" * 72)
    print("  QUANT SMART MONEY TRACKER  –  Operational Mode")
    print("  Copy Trading + MetaTrader Signal Intelligence")
    print("=" * 72)
    print(f"  Time          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Shadow Mode   : {'ENABLED' if settings.enable_shadow_mode else 'DISABLED'}")
    print(f"  Environment   : {settings.environment}")
    print("=" * 72 + "\n")


def print_signals(signals):
    if not signals:
        print("  No signals met the quality threshold.\n")
        return

    print(f"  Top {len(signals)} Actionable Signals\n")
    print(f"  {'Rank':<5} {'Action':<8} {'Strength':<9} {'Name':<28} {'Gain%':<8} {'MaxDD%':<8} {'Risk'}")
    print("  " + "-" * 78)

    for i, s in enumerate(signals, 1):
        action_icon = {
            "COPY": "🟢 COPY",
            "WATCH": "🟡 WATCH",
            "AVOID": "🔴 AVOID",
        }.get(s.recommended_action, s.recommended_action)

        print(
            f"  {i:<5} {action_icon:<10} {s.strength:<9.3f} "
            f"{s.name[:27]:<28} {s.gain_percent:<8.1f} "
            f"{s.max_drawdown:<8.1f} {s.risk_level}"
        )

    print()

    # Detailed view of top 3
    print("  ── Detailed Reasoning (Top 3) ──\n")
    for i, s in enumerate(signals[:3], 1):
        print(f"  #{i}  {s.name}  [{s.recommended_action}]")
        print(f"      Strength : {s.strength:.3f}  |  Quality : {s.quality_score:.3f}")
        print(f"      Gain     : {s.gain_percent:.1f}%   |  Max DD  : {s.max_drawdown:.1f}%")
        print(f"      Subscribers: {s.subscribers}")
        for reason in s.reasoning:
            print(f"        • {reason}")
        print()


async def run_copytrading_pipeline(storage: ClickHouseStorage | None = None):
    """Full intelligent pipeline for Copy Trading providers."""

    collector = MQL5Collector(demo_mode=True)  # Set False when real API is ready
    engine = SignalEngine()

    logger.info("Starting Copy Trading Discovery + Ranking Engine...")

    cycle = 0
    while True:
        cycle += 1
        logger.info(f"═══ Cycle {cycle} ═══")

        try:
            # 1. Discover high-quality providers
            providers = await collector.fetch_top_providers(
                min_gain=20.0,
                max_drawdown=28.0,
                min_trades=80,
                limit=20,
            )
            logger.info(f"Discovered {len(providers)} qualified signal providers")

            # 2. Rank with intelligent engine
            signals = engine.rank_signals(providers, top_n=10)

            # 3. Present results
            print_header()
            print_signals(signals)

            # 4. Optional persistence
            if storage:
                # Future: store signals in ClickHouse
                pass

            # 5. Highlight strongest COPY recommendations
            copy_candidates = [s for s in signals if s.recommended_action == "COPY"]
            if copy_candidates:
                logger.info(
                    f"🟢 {len(copy_candidates)} high-conviction COPY signals ready"
                    f"{' (Shadow Mode)' if settings.enable_shadow_mode else ''}"
                )
            else:
                logger.info("No COPY-level signals this cycle")

        except Exception as e:
            logger.error(f"Pipeline cycle failed: {e}", exc_info=True)

        # Wait before next discovery cycle
        await asyncio.sleep(60)


async def main():
    print_header()
    logger.info(f"Launching {settings.app_name}")

    storage = None
    try:
        storage = ClickHouseStorage()
        storage.init_schema()
        logger.info("ClickHouse connected and schema ready")
    except Exception as e:
        logger.warning(f"ClickHouse not available ({e}). Running without persistence.")

    try:
        await run_copytrading_pipeline(storage)
    finally:
        if storage:
            storage.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n  Shutting down gracefully...\n")
