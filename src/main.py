"""Main entry point of Quant Smart Money Tracker."""

import asyncio
import logging
from src.config import settings
from src.collectors import BinanceCollector
from src.storage import ClickHouseStorage
from src.ai_engine import BehavioralAIEngine

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def run_discovery_loop(storage: ClickHouseStorage):
    """Continuous leaderboard discovery using Binance (and later other exchanges)."""
    logger.info("Starting Dynamic Leaderboard Discovery Engine...")

    collector = BinanceCollector(
        api_key=settings.binance_api_key,
        api_secret=settings.binance_api_secret,
    )

    try:
        while True:
            try:
                # Fetch weekly and daily leaderboards
                for period in ("weekly", "daily"):
                    entries = await collector.fetch_leaderboard(period=period, limit=30)
                    if entries:
                        storage.insert_leaderboard(entries)
                        logger.info(
                            f"[{period.upper()}] Top trader: "
                            f"{entries[0].nickname or entries[0].trader_id} | "
                            f"ROI={entries[0].roi:.2%} | Rank=1"
                        )
            except Exception as e:
                logger.error(f"Discovery cycle failed: {e}", exc_info=True)

            await asyncio.sleep(45)  # Poll every 45 seconds
    finally:
        await collector.close()


async def run_ai_analysis():
    """Placeholder for behavioral AI pipeline."""
    engine = BehavioralAIEngine()
    logger.info("Behavioral AI Engine initialized (ready for Kafka consumption)")
    # Future: consume from Kafka topic and run trust scoring + signal generation
    while True:
        await asyncio.sleep(60)


async def main():
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    logger.info(f"Shadow mode enabled: {settings.enable_shadow_mode}")

    # Initialize storage and schema
    storage = ClickHouseStorage()
    try:
        storage.init_schema()
    except Exception as e:
        logger.warning(f"Could not initialize ClickHouse schema (is Docker running?): {e}")
        logger.warning("Continuing without persistent storage for this run...")

    try:
        await asyncio.gather(
            run_discovery_loop(storage),
            run_ai_analysis(),
        )
    finally:
        storage.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
