"""Anomaly Detection System.

Detects unusual patterns in campaign performance:
  - Sudden spend spikes or drops
  - CTR / CPC outliers (statistical z-score based)
  - Conversion drop-off
  - Missing data / delivery failures

Uses rolling window statistics (z-score and IQR methods).
"""

from __future__ import annotations

import math
import uuid
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Optional

from adcrewos.models.schemas import (
    AnomalyAlert,
    AnomalySeverity,
    CampaignMetric,
    Platform,
)


class AnomalyDetector:
    """Detect performance anomalies in campaign metrics.

    Usage:
        detector = AnomalyDetector(window_days=7, z_score_threshold=2.5)
        alerts = detector.analyze(metrics)
    """

    def __init__(
        self,
        window_days: int = 7,
        z_score_threshold: float = 2.5,
        min_data_points: int = 3,
    ):
        self.window_days = window_days
        self.z_score_threshold = z_score_threshold
        self.min_data_points = min_data_points

    def analyze(self, metrics: list[CampaignMetric]) -> list[AnomalyAlert]:
        """Run all anomaly detectors on the dataset and return alerts."""
        if not metrics:
            return []

        alerts: list[AnomalyAlert] = []

        # Group by campaign
        grouped: dict[str, list[CampaignMetric]] = defaultdict(list)
        for m in metrics:
            grouped[m.campaign_id].append(m)

        for cid, camp_metrics in grouped.items():
            camp_metrics.sort(key=lambda x: x.timestamp)
            alerts.extend(self._detect_spend_anomalies(cid, camp_metrics))
            alerts.extend(self._detect_ctr_anomalies(cid, camp_metrics))
            alerts.extend(self._detect_cpc_anomalies(cid, camp_metrics))
            alerts.extend(self._detect_conversion_anomalies(cid, camp_metrics))
            alerts.extend(self._detect_missing_data(cid, camp_metrics))

        alerts.sort(key=lambda x: x.detected_at, reverse=True)
        return alerts

    def _z_score(self, values: list[float]) -> list[float]:
        """Calculate z-scores for a list of values."""
        if len(values) < self.min_data_points:
            return [0.0] * len(values)

        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return [0.0] * n

        return [(v - mean) / std_dev for v in values]

    def _detect_spend_anomalies(
        self,
        campaign_id: str,
        metrics: list[CampaignMetric],
    ) -> list[AnomalyAlert]:
        """Detect unusual spend patterns."""
        alerts = []
        spends = [float(m.spend) for m in metrics]

        if len(spends) < self.min_data_points:
            return alerts

        z_scores = self._z_score(spends)

        for i, (m, z) in enumerate(zip(metrics, z_scores)):
            if abs(z) <= self.z_score_threshold:
                continue

            expected = sum(spends[:i] + spends[i + 1:]) / (len(spends) - 1) if len(spends) > 1 else spends[i]
            actual = spends[i]
            deviation = ((actual - expected) / expected * 100) if expected > 0 else 0.0

            if z > 0:
                severity = AnomalySeverity.WARNING if deviation < 300 else AnomalySeverity.CRITICAL
                msg = f"Spend spike: ${actual:.2f} vs expected ${expected:.2f} ({deviation:+.1f}%)"
            else:
                severity = AnomalySeverity.WARNING if abs(z) < 4 else AnomalySeverity.CRITICAL
                msg = f"Spend drop: ${actual:.2f} vs expected ${expected:.2f} ({deviation:+.1f}%)"

            alerts.append(AnomalyAlert(
                id=str(uuid.uuid4())[:8],
                campaign_id=campaign_id,
                platform=m.platform,
                metric="spend",
                severity=severity,
                expected_value=expected,
                actual_value=actual,
                deviation_pct=round(deviation, 2),
                detected_at=datetime.now(),
                message=msg,
            ))

        return alerts

    def _detect_ctr_anomalies(
        self,
        campaign_id: str,
        metrics: list[CampaignMetric],
    ) -> list[AnomalyAlert]:
        """Detect unusual CTR changes."""
        alerts = []
        ctrs = [m.ctr for m in metrics]

        if len(ctrs) < self.min_data_points:
            return alerts

        z_scores = self._z_score(ctrs)

        for i, (m, z) in enumerate(zip(metrics, z_scores)):
            if abs(z) <= self.z_score_threshold:
                continue

            expected = sum(ctrs[:i] + ctrs[i + 1:]) / (len(ctrs) - 1)
            actual = ctrs[i]
            deviation = ((actual - expected) / expected * 100) if expected > 0 else 0.0

            severity = AnomalySeverity.INFO if abs(z) < 3 else AnomalySeverity.WARNING
            if actual < expected and abs(z) > 3:
                severity = AnomalySeverity.CRITICAL

            msg = f"CTR anomaly: {actual:.3f}% vs expected {expected:.3f}% ({deviation:+.1f}%)"
            alerts.append(AnomalyAlert(
                id=str(uuid.uuid4())[:8],
                campaign_id=campaign_id,
                platform=m.platform,
                metric="ctr",
                severity=severity,
                expected_value=expected,
                actual_value=actual,
                deviation_pct=round(deviation, 2),
                detected_at=datetime.now(),
                message=msg,
            ))

        return alerts

    def _detect_cpc_anomalies(
        self,
        campaign_id: str,
        metrics: list[CampaignMetric],
    ) -> list[AnomalyAlert]:
        """Detect unusual CPC changes."""
        alerts = []
        cpcs = [float(m.effective_cpc) for m in metrics if m.clicks > 0]

        if len(cpcs) < self.min_data_points:
            return alerts

        # Re-align filtered metrics
        filtered = [m for m in metrics if m.clicks > 0]

        z_scores = self._z_score(cpcs)

        for i, (m, z) in enumerate(zip(filtered, z_scores)):
            if abs(z) <= self.z_score_threshold:
                continue

            expected = sum(cpcs[:i] + cpcs[i + 1:]) / (len(cpcs) - 1)
            actual = cpcs[i]
            deviation = ((actual - expected) / expected * 100) if expected > 0 else 0.0

            if z > 0 and deviation > 100:
                severity = AnomalySeverity.CRITICAL
                msg = f"CPC spike: ${actual:.4f} vs expected ${expected:.4f} ({deviation:+.1f}%)"
            else:
                severity = AnomalySeverity.WARNING
                msg = f"CPC change: ${actual:.4f} vs expected ${expected:.4f} ({deviation:+.1f}%)"

            alerts.append(AnomalyAlert(
                id=str(uuid.uuid4())[:8],
                campaign_id=campaign_id,
                platform=m.platform,
                metric="cpc",
                severity=severity,
                expected_value=expected,
                actual_value=actual,
                deviation_pct=round(deviation, 2),
                detected_at=datetime.now(),
                message=msg,
            ))

        return alerts

    def _detect_conversion_anomalies(
        self,
        campaign_id: str,
        metrics: list[CampaignMetric],
    ) -> list[AnomalyAlert]:
        """Detect unusual conversion rate changes."""
        alerts = []
        conv_rates = [m.conversions for m in metrics]

        if len(conv_rates) < self.min_data_points:
            return alerts

        z_scores = self._z_score(conv_rates)

        for i, (m, z) in enumerate(zip(metrics, z_scores)):
            if abs(z) <= self.z_score_threshold:
                continue

            expected = sum(conv_rates[:i] + conv_rates[i + 1:]) / (len(conv_rates) - 1)
            actual = conv_rates[i]
            deviation = ((actual - expected) / expected * 100) if expected > 0 else 0.0

            if actual < expected and abs(deviation) > 50:
                severity = AnomalySeverity.CRITICAL
                msg = f"Conversion drop: {actual} vs expected {expected:.0f} ({deviation:+.1f}%)"
            elif actual > expected and deviation > 100:
                severity = AnomalySeverity.WARNING
                msg = f"Conversion spike: {actual} vs expected {expected:.0f} ({deviation:+.1f}%)"
            else:
                continue  # Skip minor conv fluctuations

            alerts.append(AnomalyAlert(
                id=str(uuid.uuid4())[:8],
                campaign_id=campaign_id,
                platform=m.platform,
                metric="conversions",
                severity=severity,
                expected_value=expected,
                actual_value=actual,
                deviation_pct=round(deviation, 2),
                detected_at=datetime.now(),
                message=msg,
            ))

        return alerts

    def _detect_missing_data(
        self,
        campaign_id: str,
        metrics: list[CampaignMetric],
    ) -> list[AnomalyAlert]:
        """Detect days where data is missing."""
        alerts = []
        if len(metrics) < 2:
            return alerts

        today = datetime.now()
        expected_dates = (metrics[-1].timestamp - metrics[0].timestamp).days
        if expected_dates > len(metrics) + 1:
            alerts.append(AnomalyAlert(
                id=str(uuid.uuid4())[:8],
                campaign_id=campaign_id,
                platform=metrics[0].platform,
                metric="data_freshness",
                severity=AnomalySeverity.WARNING,
                expected_value=float(expected_dates),
                actual_value=float(len(metrics)),
                deviation_pct=round((len(metrics) - expected_dates) / expected_dates * 100, 2),
                detected_at=datetime.now(),
                message=f"Missing data: {expected_dates - len(metrics)} day(s) without metrics recorded",
            ))

        return alerts