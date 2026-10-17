"""Multi-Layer Behavioral AI Engine.

- Transformer for sequence modeling of position behavior
- Autoencoder for anomaly / fake trader detection
- Dynamic trust score calculation
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import numpy as np
from datetime import datetime


@dataclass
class BehavioralFeatures:
    """Extracted features from a trader's position history."""
    trader_id: str
    sequence_length: int
    avg_holding_time: float
    win_rate: float
    avg_leverage: float
    entry_timing_score: float   # How early relative to move
    exit_smoothness: float      # Gradual vs sudden exit
    size_consistency: float
    timestamp: datetime


@dataclass
class TrustScore:
    trader_id: str
    score: float                # 0.0 - 1.0
    anomaly_score: float        # higher = more suspicious
    reasons: List[str]
    updated_at: datetime


class BehavioralAIEngine:
    """Core behavioral analysis engine.

    In production this would load trained Transformer + Autoencoder models.
    Currently provides a clean interface and placeholder logic.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self._transformer = None
        self._autoencoder = None
        # TODO: Load models when available

    def extract_features(self, positions: List[Dict[str, Any]]) -> BehavioralFeatures:
        """Convert raw position history into behavioral features."""
        # Placeholder implementation
        if not positions:
            raise ValueError("Empty position history")

        # Simple heuristics for now
        sizes = [p.get("size", 0) for p in positions]
        leverages = [p.get("leverage", 1) for p in positions]

        return BehavioralFeatures(
            trader_id=positions[0].get("trader_id", "unknown"),
            sequence_length=len(positions),
            avg_holding_time=0.0,  # TODO: calculate from timestamps
            win_rate=0.5,
            avg_leverage=float(np.mean(leverages)) if leverages else 1.0,
            entry_timing_score=0.5,
            exit_smoothness=0.5,
            size_consistency=float(1.0 - np.std(sizes) / (np.mean(sizes) + 1e-8)) if sizes else 0.0,
            timestamp=datetime.utcnow(),
        )

    def compute_trust_score(self, features: BehavioralFeatures) -> TrustScore:
        """Compute dynamic trust score + anomaly detection."""
        reasons = []
        anomaly = 0.0

        # Simple rule-based anomaly for now
        if features.avg_leverage > 50:
            anomaly += 0.3
            reasons.append("Extremely high average leverage")
        if features.sequence_length < 5:
            anomaly += 0.2
            reasons.append("Very short trading history")
        if features.size_consistency < 0.3:
            anomaly += 0.15
            reasons.append("Highly inconsistent position sizing")

        base_score = 0.7
        score = max(0.0, min(1.0, base_score - anomaly))

        return TrustScore(
            trader_id=features.trader_id,
            score=score,
            anomaly_score=anomaly,
            reasons=reasons,
            updated_at=datetime.utcnow(),
        )

    def predict_signal_strength(self, features: BehavioralFeatures, trust: TrustScore) -> float:
        """Final signal strength combining behavior + trust."""
        # Placeholder: combine multiple factors
        strength = (
            0.4 * features.entry_timing_score
            + 0.3 * features.exit_smoothness
            + 0.3 * trust.score
        )
        return float(np.clip(strength, 0.0, 1.0))
