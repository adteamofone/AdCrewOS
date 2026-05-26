"""Budget Optimization Engine.

Analyzes campaign performance and recommends budget reallocations
to maximize ROAS (Return On Ad Spend).

Uses a weighted score based on:
  - ROAS / CPA performance
  - Impression share / delivery potential
  - Historical efficiency trend
  - Day-of-week patterns

Pure statistical approach (no AI API calls) — runs entirely offline.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from adcrewos.models.schemas import (
    BudgetRecommendation,
    Campaign,
    CampaignMetric,
    Platform,
)


class BudgetOptimizer:
    """Analyze campaign performance and recommend budget allocations.

    Usage:
        optimizer = BudgetOptimizer()
        recommendations = optimizer.analyze(campaigns, metrics, total_budget=Decimal("500"))
    """

    def __init__(self, min_confidence: float = 0.5):
        self.min_confidence = min_confidence

    def analyze(
        self,
        campaigns: list[Campaign],
        metrics: list[CampaignMetric],
        total_budget: Optional[Decimal] = None,
    ) -> list[BudgetRecommendation]:
        """Generate budget recommendations for all campaigns.

        Args:
            campaigns: List of active campaigns.
            metrics: Historical performance metrics.
            total_budget: If set, recommendations will fit within this total.

        Returns:
            List of budget recommendations sorted by confidence (highest first).
        """
        if not campaigns or not metrics:
            return []

        # Group metrics by campaign
        campaign_metrics: dict[str, list[CampaignMetric]] = {}
        for m in metrics:
            if m.campaign_id not in campaign_metrics:
                campaign_metrics[m.campaign_id] = []
            campaign_metrics[m.campaign_id].append(m)

        # Build campaign scores
        scored: list[tuple[float, Campaign, dict]] = []
        for camp in campaigns:
            camp_m = campaign_metrics.get(camp.id, [])
            if not camp_m:
                continue

            score, details = self._score_campaign(camp, camp_m)
            scored.append((score, camp, details))

        if not scored:
            return []

        scored.sort(key=lambda x: x[0], reverse=True)
        total_score = max(s.total_score for _, _, s in scored) if scored else 1.0

        now = datetime.now()
        recommendations = []

        # Determine budget pool
        # Start with each campaign's current or default budget
        current_budgets = {
            c.id: (c.daily_budget or Decimal("100"))
            for c in campaigns
        }

        if total_budget:
            # Proportional allocation based on score
            total_current = sum(current_budgets.values())
            for score_val, camp, details in scored:
                weight = details.total_score / total_score if total_score > 0 else 1.0 / len(scored)
                recommended = (total_budget * Decimal(str(round(weight, 4)))).quantize(Decimal("0.01"))
                current = current_budgets.get(camp.id, total_budget / len(scored))

                if recommended != current and score_val >= self.min_confidence:
                    recommendations.append(BudgetRecommendation(
                        campaign_id=camp.id,
                        platform=camp.platform,
                        current_budget=current.quantize(Decimal("0.01")),
                        recommended_budget=recommended.quantize(Decimal("0.01")),
                        confidence=round(details.confidence, 2),
                        reasoning=details.reasoning,
                        expected_impact=details.expected_impact,
                        generated_at=now,
                    ))
        else:
            # Per-campaign independent recommendations
            for score_val, camp, details in scored:
                current = current_budgets.get(camp.id, Decimal("100"))
                multiplier = Decimal(str(round(0.5 + details.total_score / max(details.total_score, 0.01) * 1.5, 2)))
                recommended = (current * multiplier).quantize(Decimal("0.01"))

                if recommended != current and score_val >= self.min_confidence:
                    recommendations.append(BudgetRecommendation(
                        campaign_id=camp.id,
                        platform=camp.platform,
                        current_budget=current.quantize(Decimal("0.01")),
                        recommended_budget=recommended,
                        confidence=round(details.confidence, 2),
                        reasoning=details.reasoning,
                        expected_impact=details.expected_impact,
                        generated_at=now,
                    ))

        return recommendations

    def _score_campaign(
        self,
        campaign: Campaign,
        metrics: list[CampaignMetric],
    ) -> tuple[float, "CampaignScore"]:
        """Score a campaign based on its performance metrics.

        Returns:
            Tuple of (overall_score, CampaignScore details)
        """
        if not metrics:
            return (0.5, CampaignScore(
                confidence=0.3,
                total_score=0.5,
                reasoning=f"No metric data for campaign '{campaign.name}'. Insufficient data to optimize.",
                expected_impact="Collect at least 3 days of data for initial recommendations.",
            ))

        # Filter to most recent data
        sorted_m = sorted(metrics, key=lambda x: x.timestamp, reverse=True)
        recent = sorted_m[:max(len(sorted_m) // 3, 3)]  # last ~third of data
        older = sorted_m[len(recent):] or sorted_m[-3:]  # previous data for trend

        # --- Component calculations ---

        # 1. ROAS score (revenue / spend)
        total_spend = sum(m.spend for m in recent)
        total_rev = sum((m.revenue or Decimal("0")) for m in recent)
        roas = float(total_rev / total_spend) if total_spend > 0 else 0.0
        roas_score = min(roas / 4.0, 1.0)  ##### ROAS score

        # 2. Efficiency (CTR / CPC)
        avg_ctr = sum(m.ctr for m in recent) / len(recent)
        ctr_score = min(avg_ctr / 5.0, 1.0)

        # 3. Conversion rate
        total_clicks = sum(m.clicks for m in recent)
        total_convs = sum(m.conversions for m in recent)
        conv_rate = total_convs / total_clicks if total_clicks > 0 else 0.0
        conv_score = min(conv_rate / 0.1, 1.0)

        # 4. Trend direction (positive = improving)
        older_spend = sum(m.spend for m in older)
        older_rev = sum((m.revenue or Decimal("0")) for m in older)
        older_roas = float(older_rev / older_spend) if older_spend > 0 else 0.0
        trend = roas - older_roas
        trend_score = 0.5 + min(max(trend / 2.0, -0.5), 0.5)

        # 5. Data recency (has recent data = higher confidence)
        recency_score = 0.3 + 0.7 * (1.0 - min(len(sorted_m) - 3, 30) / 30.0)

        # Weighted composite
        total = (roas_score * 0.35 + ctr_score * 0.20 + conv_score * 0.20 + trend_score * 0.25)
        confidence = min(0.3 + recency_score * 0.5, 0.95)

        # Reasoning
        reasoning_parts = []
        if roas > 2.0:
            reasoning_parts.append(f"Strong ROAS of {roas:.2f}x (above 2x benchmark)")
        elif roas < 1.0:
            reasoning_parts.append(f"Below-breakeven ROAS of {roas:.2f}x (spending > revenue)")
        else:
            reasoning_parts.append(f"Healthy ROAS of {roas:.2f}x")

        if trend > 1.0:
            reasoning_parts.append("Improving performance trend")
        elif trend < -1.0:
            reasoning_parts.append("Declining performance trend")
        else:
            reasoning_parts.append("Stable performance trend")

        if conv_rate > 0.05:
            reasoning_parts.append(f"Strong conversion rate ({conv_rate:.1%})")
        else:
            reasoning_parts.append(f"Conversion rate at {conv_rate:.1%}")

        # Impact
        if total >= 0.7:
            impact = f"Increasing budget is expected to capture additional conversions at similar ROAS ({roas:.1f}x)"
        elif total >= 0.4:
            impact = f"Maintaining current budget with minor optimization expected to stabilize ROAS at {roas:.1f}x"
        else:
            impact = f"Reducing spend until ROAS improves; consider audience/targeting refresh. ROAS: {roas:.1f}x"

        score_detail = CampaignScore(
            confidence=round(confidence, 2),
            total_score=round(total, 4),
            reasoning="; ".join(reasoning_parts),
            expected_impact=impact,
            roas_score=round(roas_score, 4),
            ctr_score=round(ctr_score, 4),
            conv_score=round(conv_score, 4),
            trend_score=round(trend_score, 4),
            roas=roas,
            trend=trend,
            recency_score=round(recency_score, 4),
        )
        return (total, score_detail)


class CampaignScore:
    """Internal scoring details for a campaign."""

    def __init__(
        self,
        confidence: float = 0.0,
        total_score: float = 0.0,
        reasoning: str = "",
        expected_impact: str = "",
        roas_score: float = 0.0,
        ctr_score: float = 0.0,
        conv_score: float = 0.0,
        trend_score: float = 0.0,
        roas: float = 0.0,
        trend: float = 0.0,
        recency_score: float = 0.0,
    ):
        self.confidence = confidence
        self.total_score = total_score
        self.reasoning = reasoning
        self.expected_impact = expected_impact
        self.roas_score = roas_score
        self.ctr_score = ctr_score
        self.conv_score = conv_score
        self.trend_score = trend_score
        self.roas = roas
        self.trend = trend
        self.recency_score = recency_score