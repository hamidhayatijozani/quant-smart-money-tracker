"""Quant Smart Money Tracker – continuous shadow-mode signal discovery."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from src.config import settings
from src.collectors.copytrading import MQL5Collector
from src.engine import SignalEngine
from src.storage import ClickHouseStorage
from src.storage.signal_journal import SignalJournal

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("quant")


def print_header():
    print("\n" + "=" * 72)
    print("  QUANT SMART MONEY TRACKER – Continuous Shadow Mode")
    print("  DATA MODE: DEMO (synthetic providers; not live exchange data)")
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
        action_icon = {"COPY": "COPY", "WATCH": "WATCH", "AVOID": "AVOID"}.get(s.recommended_action, s.recommended_action)
        print(f"  {i:<5} {action_icon:<10} {s.strength:<9.3f} {s.name[:27]:<28} {s.gain_percent:<8.1f} {s.max_drawdown:<8.1f} {s.risk_level}")
    print("\n  -- Detailed Reasoning (Top 3) --\n")
    for i, s in enumerate(signals[:3], 1):
        print(f"  #{i} {s.name} [{s.recommended_action}]")
        print(f"      Strength: {s.strength:.3f} | Quality: {s.quality_score:.3f}")
        print(f"      Gain: {s.gain_percent:.1f}% | Max DD: {s.max_drawdown:.1f}%")
        for reason in s.reasoning:
            print(f"        - {reason}")
        print()


async def run_copytrading_pipeline(journal: SignalJournal):
    """Generate and journal a complete signal snapshot every 60 seconds."""
    # Real MQL5 integration is not implemented; keep the source explicitly in demo mode.
    collector = MQL5Collector(demo_mode=True)
    engine = SignalEngine()
    logger.info("Starting continuous discovery. Source mode=DEMO; execution=SHADOW only.")
    cycle = 0
    while True:
        cycle += 1
        try:
            providers = await collector.fetch_top_providers(
                min_gain=20.0, max_drawdown=28.0, min_trades=80, limit=20
            )
            signals = engine.rank_signals(providers, top_n=10)
            print_header()
            print_signals(signals)
            cycle_id = journal.record_cycle(signals, source_mode="demo")
            logger.info("Cycle %s journaled: %s signals (journal cycle id=%s)", cycle, len(signals), cycle_id)
            copies = sum(s.recommended_action == "COPY" for s in signals)
            logger.info("COPY candidates=%s; no real orders are sent.", copies)
        except Exception:
            logger.exception("Pipeline cycle %s failed; retrying after interval", cycle)
        await asyncio.sleep(60)


async def main():
    print_header()
    logger.info("Launching %s", settings.app_name)
    journal = SignalJournal()
    storage = None
    try:
        # ClickHouse is optional. The SQLite journal remains the default audit trail.
        try:
            storage = ClickHouseStorage()
            storage.init_schema()
            logger.info("Optional ClickHouse connected")
        except Exception as exc:
            logger.warning("Optional ClickHouse unavailable; SQLite journal remains active: %s", exc)
            storage = None
        logger.info("SQLite signal journal: %s", journal.path.resolve())
        await run_copytrading_pipeline(journal)
    finally:
        journal.close()
        if storage:
            storage.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down gracefully.\n")
