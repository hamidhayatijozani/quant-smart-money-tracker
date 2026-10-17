"""Idempotency and safe execution state management."""

from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import hashlib
import json


class ExecutionState(str, Enum):
    PENDING = "PENDING"
    DISPATCHED = "DISPATCHED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"  # Timeout or ambiguous state
    CANCELLED = "CANCELLED"


class Maturity(str, Enum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class ActionType(str, Enum):
    REFRESH = "REFRESH"          # Non-destructive
    PUBLISH = "PUBLISH"          # Open new position (destructive)
    CLOSE = "CLOSE"
    ADJUST = "ADJUST"


class ExecutionRecord(BaseModel):
    """Immutable record of an execution attempt."""
    action_id: str
    action_type: ActionType
    trader_id: str
    symbol: str
    payload_hash: str
    state: ExecutionState = ExecutionState.PENDING
    maturity: Maturity = Maturity.DRAFT
    evidence_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None

    def mark_unknown(self, reason: str) -> None:
        """Transition to UNKNOWN on timeout or ambiguity."""
        if self.state in (ExecutionState.DISPATCHED, ExecutionState.PENDING):
            self.state = ExecutionState.UNKNOWN
            self.error_message = reason
            self.updated_at = datetime.now(timezone.utc)

    def is_safe_to_retry(self) -> bool:
        """Only allow retry if state is FAILED (not UNKNOWN)."""
        return self.state == ExecutionState.FAILED


def compute_payload_hash(payload: dict) -> str:
    """Deterministic hash for idempotency key."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def compute_evidence_hash(record: ExecutionRecord, runtime_data: dict) -> str:
    """Generate evidence hash for maturity verification."""
    data = {
        "action_id": record.action_id,
        "payload_hash": record.payload_hash,
        "runtime": runtime_data,
        "timestamp": record.updated_at.isoformat(),
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()
