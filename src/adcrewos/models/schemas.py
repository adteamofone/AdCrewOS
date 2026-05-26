"""Pydantic schemas for AdCrewOS data models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Platform(str, Enum):
    """Supported ad platforms."""
    GOOGLE = "google"
    META = "meta"
    TIKTOK = "tiktok"
    AMAZON = "amazon"


class MetricSource(str, Enum):
    """Where the metric data comes from."""
    API = "api"
    MANUAL = "manual"
    ESTIMATED = "estimated"


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertChannelType(str, Enum):
    """Types of alert delivery channels."""
    EMAIL = "email"
    SMS = "sms"


class AdAccount(BaseModel):
    """An ad platform account."""
    id: str
    platform: Platform
    name: str
    currency: str = "USD"
    timezone: str = "America/New_York"
    status: str = "active"


class Campaign(BaseModel):
    """A campaign across an ad platform."""
    id: str
    account_id: str
    platform: Platform
    name: str
    status: str = "active"
    daily_budget: Optional[Decimal] = None
    lifetime_budget: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CampaignMetric(BaseModel):
    """Performance metrics for a campaign at a point in time."""
    campaign_id: str
    platform: Platform
    timestamp: datetime
    source: MetricSource = MetricSource.API

    # Spend & delivery
    spend: Decimal = Field(default=Decimal("0"), decimal_places=4)
    impressions: int = 0
    clicks: int = 0
    reach: int = 0
    frequency: float = 0.0

    # Performance
    conversions: int = 0
    ctr: float = 0.0  # Click-through rate
    cpc: Decimal = Field(default=Decimal("0"), decimal_places=4)  # Cost per click
    cpm: Decimal = Field(default=Decimal("0"), decimal_places=4)  # Cost per mille
    cpa: Optional[Decimal] = None  # Cost per acquisition

    # Revenue
    revenue: Optional[Decimal] = None
    roas: Optional[float] = None  # Return on ad spend
    profit: Optional[Decimal] = None

    @property
    def effective_cpc(self) -> Decimal:
        if self.clicks > 0:
            return self.spend / Decimal(str(self.clicks))
        return Decimal("0")

    @property
    def effective_cpm(self) -> Decimal:
        if self.impressions > 0:
            return (self.spend / Decimal(str(self.impressions))) * Decimal("1000")
        return Decimal("0")


class AnomalyAlert(BaseModel):
    """An anomaly detected in campaign performance."""
    id: str
    campaign_id: str
    platform: Platform
    metric: str  # e.g. "spend", "ctr", "cpa"
    severity: AnomalySeverity
    expected_value: float
    actual_value: float
    deviation_pct: float  # Percentage deviation from expected
    detected_at: datetime
    message: str
    acknowledged: bool = False


class BudgetRecommendation(BaseModel):
    """A budget optimization recommendation."""
    campaign_id: str
    platform: Platform
    current_budget: Decimal
    recommended_budget: Decimal
    confidence: float  # 0.0 to 1.0
    reasoning: str
    expected_impact: str
    generated_at: datetime


class ReportConfig(BaseModel):
    """Configuration for an automated report."""
    id: str
    name: str
    campaign_ids: list[str] = []
    platforms: list[Platform] = []
    schedule: str = "daily"  # daily, weekly, monthly
    metrics: list[str] = ["spend", "impressions", "clicks", "conversions", "ctr", "cpc", "roas"]
    format: str = "pdf"
    recipients: list[str] = []


class Report(BaseModel):
    """A generated performance report."""
    id: str
    config_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    format: str
    file_path: Optional[str] = None
    summary: str
    metrics: dict[str, dict] = {}


class AlertChannel(BaseModel):
    """Configuration for an alert delivery channel."""
    id: str
    type: AlertChannelType
    name: str
    enabled: bool = True
    config: dict = {}  # e.g. {"email": "alerts@example.com"} or {"phone": "+15551234567", "provider": "twilio"}