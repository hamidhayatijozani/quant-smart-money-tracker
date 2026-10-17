"""ClickHouse storage layer for time-series data."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

from clickhouse_connect import get_client
from clickhouse_connect.driver.client import Client

from src.config import settings
from src.collectors.base import LeaderboardEntry, Position

logger = logging.getLogger(__name__)


class ClickHouseStorage:
    """High-performance time-series storage using ClickHouse."""

    def __init__(self):
        self._client: Optional[Client] = None

    def connect(self) -> Client:
        if self._client is None:
            self._client = get_client(
                host=settings.clickhouse_host,
                port=settings.clickhouse_port,
                username=settings.clickhouse_user,
                password=settings.clickhouse_password,
                database=settings.clickhouse_db,
            )
            logger.info("Connected to ClickHouse")
        return self._client

    def init_schema(self) -> None:
        """Create necessary tables if they do not exist."""
        client = self.connect()

        # Leaderboard snapshots
        client.command("""
            CREATE TABLE IF NOT EXISTS leaderboard_snapshots
            (
                exchange LowCardinality(String),
                trader_id String,
                nickname Nullable(String),
                roi Float64,
                pnl Float64,
                period LowCardinality(String),
                rank UInt32,
                ts DateTime64(3, 'UTC')
            )
            ENGINE = MergeTree()
            PARTITION BY toYYYYMM(ts)
            ORDER BY (exchange, period, ts, rank)
            TTL ts + INTERVAL 180 DAY
        """)

        # Position updates
        client.command("""
            CREATE TABLE IF NOT EXISTS position_updates
            (
                exchange LowCardinality(String),
                trader_id String,
                symbol LowCardinality(String),
                side LowCardinality(String),
                size Float64,
                entry_price Float64,
                mark_price Nullable(Float64),
                unrealized_pnl Nullable(Float64),
                leverage Nullable(Float64),
                ts DateTime64(3, 'UTC')
            )
            ENGINE = MergeTree()
            PARTITION BY toYYYYMM(ts)
            ORDER BY (exchange, trader_id, symbol, ts)
            TTL ts + INTERVAL 90 DAY
        """)

        # Generated signals
        client.command("""
            CREATE TABLE IF NOT EXISTS signals
            (
                signal_id String,
                trader_id String,
                symbol LowCardinality(String),
                side LowCardinality(String),
                strength Float64,
                trust_score Float64,
                anomaly_score Float64,
                status LowCardinality(String),
                ts DateTime64(3, 'UTC')
            )
            ENGINE = MergeTree()
            PARTITION BY toYYYYMM(ts)
            ORDER BY (ts, signal_id)
        """)

        logger.info("ClickHouse schema initialized")

    def insert_leaderboard(self, entries: List[LeaderboardEntry]) -> None:
        if not entries:
            return
        client = self.connect()
        rows = [
            [
                e.exchange,
                e.trader_id,
                e.nickname,
                e.roi,
                e.pnl,
                e.period,
                e.rank or 0,
                e.timestamp,
            ]
            for e in entries
        ]
        client.insert(
            "leaderboard_snapshots",
            rows,
            column_names=[
                "exchange",
                "trader_id",
                "nickname",
                "roi",
                "pnl",
                "period",
                "rank",
                "ts",
            ],
        )
        logger.info(f"Inserted {len(entries)} leaderboard entries")

    def insert_positions(self, positions: List[Position]) -> None:
        if not positions:
            return
        client = self.connect()
        rows = [
            [
                p.exchange,
                p.trader_id,
                p.symbol,
                p.side,
                p.size,
                p.entry_price,
                p.mark_price,
                p.unrealized_pnl,
                p.leverage,
                p.timestamp,
            ]
            for p in positions
        ]
        client.insert(
            "position_updates",
            rows,
            column_names=[
                "exchange",
                "trader_id",
                "symbol",
                "side",
                "size",
                "entry_price",
                "mark_price",
                "unrealized_pnl",
                "leverage",
                "ts",
            ],
        )
        logger.info(f"Inserted {len(positions)} position updates")

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
