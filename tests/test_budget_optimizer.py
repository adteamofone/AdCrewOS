"""Tests for Budget Optimization Engine."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from adcrewos.core.budget_optimizer import BudgetOptimizer
from adcrewos.models.schemas import Campaign, CampaignMetric, Platform


def _make_metric(campaign_id: str, spend: float, revenue: float, clicks: int = 100,
                 impressions: int = 10000, conversions: int = 5, days_ago: int = 0):
    return CampaignMetric(
        campaign_id=campaign_id,
        platform=Platform.GOOGLE,
        timestamp=datetime.now() - timedelta(days=days_ago),
        spend=Decimal(str(spend)),
        impressions=impressions,
        clicks=clicks,
        conversions=conversions,
        revenue=Decimal(str(revenue)),
    )


class TestBudgetOptimizer:
    def test_empty_inputs(self):
        opt = BudgetOptimizer()
        assert opt.analyze([], []) == []

    def test_single_campaign_generates_recommendation(self):
        camp = Campaign(
            id="camp-1",
            account_id="acc-1",
            platform=Platform.GOOGLE,
            name="Test Campaign",
            daily_budget=Decimal("100"),
        )
        metrics = [_make_metric("camp-1", 100, 400, days_ago=i) for i in range(7)]
        opt = BudgetOptimizer()
        recs = opt.analyze([camp], metrics)
        assert len(recs) >= 1
        assert recs[0].campaign_id == "camp-1"

    def test_multiple_campaigns_scored_independently(self):
        camps = [
            Campaign(id="camp-a", account_id="acc-1", platform=Platform.GOOGLE, name="Camp A", daily_budget=Decimal("100")),
            Campaign(id="camp-b", account_id="acc-1", platform=Platform.GOOGLE, name="Camp B", daily_budget=Decimal("100")),
        ]
        metrics = (
            [_make_metric("camp-a", 100, 500, days_ago=i) for i in range(7)] +
            [_make_metric("camp-b", 100, 100, days_ago=i) for i in range(7)]
        )
        opt = BudgetOptimizer()
        recs = opt.analyze(camps, metrics, total_budget=Decimal("500"))
        assert len(recs) >= 1
        # Camp A (high ROAS) should get higher recommendation than Camp B
        rec_a = [r for r in recs if r.campaign_id == "camp-a"]
        rec_b = [r for r in recs if r.campaign_id == "camp-b"]
        if rec_a and rec_b:
            assert rec_a[0].recommended_budget >= rec_b[0].recommended_budget

    def test_low_confidence_filtered(self):
        camp = Campaign(
            id="camp-1",
            account_id="acc-1",
            platform=Platform.GOOGLE,
            name="Test",
        )
        opt = BudgetOptimizer(min_confidence=0.9)
        recs = opt.analyze([camp], [_make_metric("camp-1", 100, 200, days_ago=0)])
        assert all(r.confidence >= 0.9 for r in recs) or len(recs) == 0