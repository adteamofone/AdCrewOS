"""Campaign Monitoring Module.

Fetches ad performance data from Google Ads and Meta Ads APIs.
Provides a unified interface for campaign metrics regardless of platform.

The actual API integration requires tokens — this module defines the interfaces,
mock data for development, and the provider abstraction layer.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from adcrewos.models.schemas import (
    AdAccount,
    Campaign,
    CampaignMetric,
    MetricSource,
    Platform,
)


# ---------------------------------------------------------------------------
# Configuration paths
# ---------------------------------------------------------------------------

def get_config_dir() -> Path:
    """Get the AdCrewOS config directory."""
    return Path(os.getenv("ADCREWOS_HOME", str(Path.home() / ".adcrewos")))


def get_credentials_path() -> Path:
    """Path where API tokens/credentials are stored."""
    return get_config_dir() / "credentials.json"


# ---------------------------------------------------------------------------
# Abstract provider
# ---------------------------------------------------------------------------

class AdPlatformProvider(ABC):
    """Base class for ad platform API clients."""

    platform: Platform

    @abstractmethod
    async def get_accounts(self) -> list[AdAccount]:
        """Fetch all ad accounts for this platform."""
        ...

    @abstractmethod
    async def get_campaigns(self, account_id: str) -> list[Campaign]:
        """Fetch campaigns for an account."""
        ...

    @abstractmethod
    async def get_metrics(
        self,
        campaign_ids: list[str],
        start_date: datetime,
        end_date: datetime,
    ) -> list[CampaignMetric]:
        """Fetch campaign metrics for a date range."""
        ...


# ---------------------------------------------------------------------------
# Google Ads placeholder provider
# ---------------------------------------------------------------------------

class GoogleAdsProvider(AdPlatformProvider):
    """Google Ads API client.

    Requires a Google Ads developer token, OAuth2 credentials,
    and a customer/client ID. Setup:
      1. Enable Google Ads API in Google Cloud Console
      2. Create OAuth2 credentials (desktop app)
      3. Note your Google Ads customer ID (CCC-XXX-XXXX)

    *Tokens needed from you:* Google Ads developer token + OAuth2 client ID/secret
    """

    platform = Platform.GOOGLE

    def __init__(self, credentials: Optional[dict] = None):
        self.credentials = credentials or {}
        self._authenticated = bool(
            self.credentials.get("developer_token")
            and self.credentials.get("client_id")
            and self.credentials.get("client_secret")
            and self.credentials.get("customer_id")
        )

    async def get_accounts(self) -> list[AdAccount]:
        if not self._authenticated:
            return self._mock_accounts()
        # TODO: Implement Google Ads API integration
        # Requires: google-ads library
        raise NotImplementedError(
            "Google Ads API integration requires: pip install google-ads, "
            "then provide developer_token + OAuth2 credentials"
        )

    async def get_campaigns(self, account_id: str) -> list[Campaign]:
        if not self._authenticated:
            return self._mock_campaigns(account_id)
        raise NotImplementedError("Google Ads API integration pending credentials")

    async def get_metrics(
        self,
        campaign_ids: list[str],
        start_date: datetime,
        end_date: datetime,
    ) -> list[CampaignMetric]:
        if not self._authenticated:
            return self._mock_metrics(campaign_ids, start_date, end_date)
        raise NotImplementedError("Google Ads API integration pending credentials")

    # --- Mock data for development ---

    def _mock_accounts(self) -> list[AdAccount]:
        return [
            AdAccount(id="google-123-456-7890", platform=Platform.GOOGLE, name="Main Search Account"),
            AdAccount(id="google-987-654-3210", platform=Platform.GOOGLE, name="Display Network Account"),
        ]

    def _mock_campaigns(self, account_id: str) -> list[Campaign]:
        return [
            Campaign(id=f"{account_id}-camp-1", account_id=account_id, platform=Platform.GOOGLE, name="Brand Search"),
            Campaign(id=f"{account_id}-camp-2", account_id=account_id, platform=Platform.GOOGLE, name="Generic Search"),
            Campaign(id=f"{account_id}-camp-3", account_id=account_id, platform=Platform.GOOGLE, name="Remarketing Display"),
        ]

    def _mock_metrics(
        self,
        campaign_ids: list[str],
        start_date: datetime,
        end_date: datetime,
    ) -> list[CampaignMetric]:
        import random
        from decimal import Decimal

        metrics = []
        days = (end_date - start_date).days or 1
        for cid in campaign_ids:
            for day_offset in range(days):
                day = start_date + timedelta(days=day_offset)
                impressions = random.randint(1000, 50000)
                clicks = random.randint(10, int(impressions * 0.1))
                spend = Decimal(str(round(random.uniform(10.0, 500.0), 2)))
                conversions = random.randint(0, int(clicks * 0.05))
                metrics.append(CampaignMetric(
                    campaign_id=cid,
                    platform=Platform.GOOGLE,
                    timestamp=day,
                    source=MetricSource.ESTIMATED,
                    impressions=impressions,
                    clicks=clicks,
                    spend=spend,
                    conversions=conversions,
                    ctr=round(clicks / impressions * 100, 4) if impressions else 0.0,
                    revenue=spend * Decimal(str(round(random.uniform(0.5, 5.0), 2))),
                ))
        return metrics


# ---------------------------------------------------------------------------
# Meta Ads placeholder provider
# ---------------------------------------------------------------------------

class MetaAdsProvider(AdPlatformProvider):
    """Meta (Facebook) Ads API client.

    Requires:
      - Meta App ID + App Secret
      - Access token (long-lived, with ads_read permission)
      - Ad account ID(s)

    *Tokens needed from you:* Meta App credentials + long-lived access token
    """

    platform = Platform.META

    def __init__(self, credentials: Optional[dict] = None):
        self.credentials = credentials or {}
        self._authenticated = bool(
            self.credentials.get("access_token")
            and self.credentials.get("app_id")
            and self.credentials.get("app_secret")
        )

    async def get_accounts(self) -> list[AdAccount]:
        if not self._authenticated:
            return self._mock_accounts()
        raise NotImplementedError(
            "Meta Ads API integration requires: pip install facebook-business, "
            "then provide app_id + app_secret + access_token"
        )

    async def get_campaigns(self, account_id: str) -> list[Campaign]:
        if not self._authenticated:
            return self._mock_campaigns(account_id)
        raise NotImplementedError("Meta Ads API integration pending credentials")

    async def get_metrics(
        self,
        campaign_ids: list[str],
        start_date: datetime,
        end_date: datetime,
    ) -> list[CampaignMetric]:
        if not self._authenticated:
            return self._mock_metrics(campaign_ids, start_date, end_date)
        raise NotImplementedError("Meta Ads API integration pending credentials")

    def _mock_accounts(self) -> list[AdAccount]:
        return [
            AdAccount(id="meta-act_123456789", platform=Platform.META, name="Facebook Main Account"),
            AdAccount(id="meta-act_987654321", platform=Platform.META, name="Instagram Shop Account"),
        ]

    def _mock_campaigns(self, account_id: str) -> list[Campaign]:
        return [
            Campaign(id=f"{account_id}-camp-1", account_id=account_id, platform=Platform.META, name="FB News Feed - Conversions"),
            Campaign(id=f"{account_id}-camp-2", account_id=account_id, platform=Platform.META, name="IG Stories - Brand Awareness"),
            Campaign(id=f"{account_id}-camp-3", account_id=account_id, platform=Platform.META, name="FB Retarget - Dynamic Products"),
        ]

    def _mock_metrics(
        self,
        campaign_ids: list[str],
        start_date: datetime,
        end_date: datetime,
    ) -> list[CampaignMetric]:
        import random
        from decimal import Decimal

        metrics = []
        days = (end_date - start_date).days or 1
        for cid in campaign_ids:
            for day_offset in range(days):
                day = start_date + timedelta(days=day_offset)
                impressions = random.randint(5000, 100000)
                clicks = random.randint(50, int(impressions * 0.02))
                spend = Decimal(str(round(random.uniform(20.0, 800.0), 2)))
                conversions = random.randint(0, int(clicks * 0.08))
                metrics.append(CampaignMetric(
                    campaign_id=cid,
                    platform=Platform.META,
                    timestamp=day,
                    source=MetricSource.ESTIMATED,
                    impressions=impressions,
                    clicks=clicks,
                    spend=spend,
                    conversions=conversions,
                    ctr=round(clicks / impressions * 100, 4) if impressions else 0.0,
                    revenue=spend * Decimal(str(round(random.uniform(1.0, 8.0), 2))),
                ))
        return metrics


# ---------------------------------------------------------------------------
# Campaign Monitor — unified orchestrator
# ---------------------------------------------------------------------------

class CampaignMonitor:
    """Unified interface for monitoring campaigns across all platforms.

    Usage:
        monitor = CampaignMonitor()
        # With mock data (no credentials needed):
        metrics = await monitor.fetch_metrics(days_back=7)

        # With credentials, providers switch to real API mode:
        monitor.set_credentials("google", {...})
        monitor.set_credentials("meta", {...})
    """

    def __init__(self):
        self._providers: dict[Platform, AdPlatformProvider] = {
            Platform.GOOGLE: GoogleAdsProvider(),
            Platform.META: MetaAdsProvider(),
        }

    def set_credentials(self, platform: str, credentials: dict):
        """Set API credentials for a platform. Once set, providers use real API calls."""
        plat = Platform(platform.lower())
        if plat == Platform.GOOGLE:
            self._providers[plat] = GoogleAdsProvider(credentials)
        elif plat == Platform.META:
            self._providers[plat] = MetaAdsProvider(credentials)

    def get_provider(self, platform: Platform) -> AdPlatformProvider:
        return self._providers[platform]

    async def fetch_accounts(self, platform: Optional[Platform] = None) -> list[AdAccount]:
        """Fetch all ad accounts, optionally filtered by platform."""
        accounts = []
        platforms = [platform] if platform else list(self._providers)
        for plat in platforms:
            try:
                result = await self._providers[plat].get_accounts()
                accounts.extend(result)
            except NotImplementedError:
                pass  # Will raise when credentials are set but API isn't wired yet
        return accounts

    async def fetch_campaigns(self, platform: Optional[Platform] = None) -> list[Campaign]:
        campaigns = []
        platforms = [platform] if platform else list(self._providers)
        for plat in platforms:
            try:
                accounts = await self._providers[plat].get_accounts()
                for acc in accounts:
                    result = await self._providers[plat].get_campaigns(acc.id)
                    campaigns.extend(result)
            except NotImplementedError:
                pass
        return campaigns

    async def fetch_metrics(
        self,
        days_back: int = 7,
        platform: Optional[Platform] = None,
    ) -> list[CampaignMetric]:
        """Fetch metrics for the last N days across all platforms."""
        end = datetime.now()
        start = end - timedelta(days=days_back)
        all_metrics = []
        platforms = [platform] if platform else list(self._providers)
        for plat in platforms:
            try:
                campaigns = await self.fetch_campaigns(plat)
                if campaigns:
                    cids = [c.id for c in campaigns]
                    result = await self._providers[plat].get_metrics(cids, start, end)
                    all_metrics.extend(result)
            except NotImplementedError:
                pass
        return all_metrics