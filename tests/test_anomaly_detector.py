"""Tests for Anomaly Detection System."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from adcrewos.core.anomaly_detector import AnomalyDetector
from adcrewos.models.schemas import CampaignMetric, AnomalySeverity, Platform


def _metric(cid: str, spend: float = 100, ctr: float = 2.5, clicks: int = 100,
            impressions: int = 10000, conversions: int = 5, days_ago: int = 0):
    return CampaignMetric(
        campaign_id=cid,
        platform=Platform.GOOGLE,
        timestamp=datetime.now() - timedelta(days=days_ago),
        spend=Decimal(str(spend)),
        impressions=impressions,
        clicks=clicks,
        conversions=conversions,
        ctr=ctr,
    )


class TestAnomalyDetector:
    def test_empty_input(self):
        d = AnomalyDetector()
        assert d.analyze([]) == []

    def test_stable_data_no_anomalies(self):
        metrics = [_metric("c1", spend=100, days_ago=i) for i in range(10)]
        d = AnomalyDetector(z_score_threshold=3.0)
        alerts = d.analyze(metrics)
        # Stable data should produce few or no alerts
        assert len(alerts) == 0

    def test_spend_spike_detected(self):
        metrics = [_metric("c1", spend=100, days_ago=i) for i in range(7)]
        # Add a spike
        metrics.append(_metric("c1", spend=5000, days_ago=0))
        d = AnomalyDetector(z_score_threshold=2.0)
        alerts = d.analyze(metrics)
        spend_alerts = [a for a in alerts if a.metric == "spend"]
        assert len(spend_alerts) > 0

    def test_severity_levels(self):
        metrics = [_metric("c1", spend=100, days_ago=i) for i in range(5)]
        metrics.append(_metric("c1", spend=50000, days_ago=0))  # Extreme spike
        d = AnomalyDetector(z_score_threshold=1.5)
        alerts = d.analyze(metrics)
        severities = [a.severity for a in alerts if a.metric == "spend"]
        assert AnomalySeverity.CRITICAL in severities or AnomalySeverity.WARNING in severities

    def test_multiple_campaigns_independent(self):
        metrics = (
            [_metric("c1", spend=100, days_ago=i) for i in range(7)] +
            [_metric("c2", spend=200, days_ago=i) for i in range(7)]
        )
        # Spike in one
        metrics.append(_metric("c1", spend=10000, days_ago=0))
        d = AnomalyDetector(z_score_threshold=2.0)
        alerts = d.analyze(metrics)
        c1_alerts = [a for a in alerts if a.campaign_id == "c1"]
        c2_alerts = [a for a in alerts if a.campaign_id == "c2"]
        assert len(c1_alerts) > 0  # Spike in c1
        # c2 should have fewer/zero alerts (no spike)
        assert len(c2_alerts) <= len(c1_alerts)

    def test_min_data_points_respected(self):
        d = AnomalyDetector(min_data_points=10)
        metrics = [_metric("c1", spend=100, days_ago=i) for i in range(3)]
        alerts = d.analyze(metrics)
        assert len(alerts) == 0

    def test_missing_data_detected(self):
        # Add data with gaps
        metrics = [
            _metric("c1", days_ago=10),
            _metric("c1", days_ago=9),
            _metric("c1", days_ago=5),  # Gap here
            _metric("c1", days_ago=0),
        ]
        d = AnomalyDetector()
        alerts = d.analyze(metrics)
        missing = [a for a in alerts if a.metric == "data_freshness"]
        assert len(missing) > 0