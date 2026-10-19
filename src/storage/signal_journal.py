"""Append-only local journal for every generated signal cycle.

This is an audit log, not a trading execution engine. On hosts with ephemeral
filesystems, configure a persistent disk or external database before relying on
the journal across restarts.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from src.engine.signal_engine import ActionableSignal


class SignalJournal:
    """Durably append cycle snapshots to SQLite and expose a small audit trail."""

    def __init__(self, path: str | None = None) -> None:
        configured = path or os.getenv("SIGNAL_JOURNAL_PATH", "data/signals.sqlite3")
        self.path = Path(configured)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(self.path), timeout=30)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS signal_cycles (
                cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                observed_at TEXT NOT NULL,
                source_mode TEXT NOT NULL,
                signal_count INTEGER NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        self._db.commit()

    def record_cycle(self, signals: Sequence[ActionableSignal], source_mode: str) -> int:
        observed_at = datetime.now(timezone.utc).isoformat()
        payload = [signal.model_dump(mode="json") for signal in signals]
        with self._db:
            cursor = self._db.execute(
                "INSERT INTO signal_cycles (observed_at, source_mode, signal_count, payload_json) VALUES (?, ?, ?, ?)",
                (observed_at, source_mode, len(payload), json.dumps(payload, separators=(",", ":"))),
            )
        return int(cursor.lastrowid)

    def close(self) -> None:
        self._db.close()
