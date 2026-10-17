"""Main entry point of Quant Smart Money Tracker."""

import asyncio
import logging
from src.config import settings
from src.ai_engine import BehavioralAIEngine
from src.safety import ExecutionState, ActionType

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


async def run_discovery_loop():
    """Placeholder for continuous leaderboard discovery."""
    logger.info("Starting Dynamic Leaderboard Discovery Engine...")
    # TODO: Implement collectors for Binance / OKX / Bybit
    while True:
        logger.info("Scanning top traders...")
        await asyncio.sleep(30)  # Poll interval placeholder


async def run_ai_analysis():
    """Placeholder for behavioral AI pipeline."""
    engine = BehavioralAIEngine()
    logger.info("Behavioral AI Engine initialized")
    # TODO: Consume from Kafka and run analysis


async def main():
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    logger.info(f"Shadow mode enabled: {settings.enable_shadow_mode}")

    # Run concurrent tasks
    await asyncio.gather(
        run_discovery_loop(),
        run_ai_analysis(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
