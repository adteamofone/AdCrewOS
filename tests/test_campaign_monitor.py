"""Tests for Campaign Monitoring Module."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from adcrewos.core.campaign_monitor import CampaignMonitor, GoogleAdsProvider, MetaAdsProvider
from adcrewos.models.schemas import Platform, CampaignMetric


class TestGoogleAdsProvider:
    """Provider works with mock data when no credentials are set."""

    @pytest.mark.asyncio
    async def test_get_accounts_returns_mock(self):
        p = GoogleAdsProvider()
        accounts = await p.get_accounts()
        assert len(accounts) >= 1
        assert accounts[0].platform == Platform.GOOGLE

    @pytest.mark.asyncio
    async def test_get_campaigns_returns_mock(self):
        p = GoogleAdsProvider()
        camps = await p.get_campaigns("test-account")
        assert len(camps) >= 1
        assert camps[0].platform == Platform.GOOGLE

    @pytest.mark.asyncio
    async def test_get_metrics_returns_data(self):
        p = GoogleAdsProvider()
        now = datetime.now()
        metrics = await p.get_metrics(["camp-1"], now - timedelta(days=3), now)
        assert len(metrics) >= 1
        assert isinstance(metrics[0], CampaignMetric)


class TestMetaAdsProvider:
    @pytest.mark.asyncio
    async def test_get_accounts_returns_mock(self):
        p = MetaAdsProvider()
        accounts = await p.get_accounts()
        assert len(accounts) >= 1
        assert accounts[0].platform == Platform.META

    @pytest.mark.asyncio
    async def test_get_campaigns_returns_mock(self):
        p = MetaAdsProvider()
        camps = await p.get_campaigns("test-account")
        assert len(camps) >= 1
        assert camps[0].platform == Platform.META


class TestCampaignMonitor:
    @pytest.mark.asyncio
    async def test_fetch_accounts_returns_all(self):
        m = CampaignMonitor()
        accounts = await m.fetch_accounts()
        assert len(accounts) >= 2

    @pytest.mark.asyncio
    async def test_fetch_campaigns_returns_all(self):
        m = CampaignMonitor()
        camps = await m.fetch_campaigns()
        assert len(camps) >= 4

    @pytest.mark.asyncio
    async def test_fetch_metrics_returns_data(self):
        m = CampaignMonitor()
        metrics = await m.fetch_metrics(days_back=3)
        assert len(metrics) > 0
        assert all(isinstance(m, CampaignMetric) for m in metrics)

    def test_set_google_credentials(self):
        m = CampaignMonitor()
        m.set_credentials("google", {"developer_token": "test"})
        # After setting creds, provider changes but still uses mock (no real API)
        # This just verifies the credential path doesn't error

    def test_set_meta_credentials(self):
        m = CampaignMonitor()
        m.set_credentials("meta", {"access_token": "test"})


class TestCampaignMetric:
    def test_effective_cpc_calculation(self):
        m = CampaignMetric(
            campaign_id="test",
            platform=Platform.GOOGLE,
            timestamp=datetime.now(),
            spend=Decimal("100"),
            clicks=50,
        )
        assert m.effective_cpc == Decimal("2")

    def test_effective_cpm_calculation(self):
        m = CampaignMetric(
            campaign_id="test",
            platform=Platform.GOOGLE,
            timestamp=datetime.now(),
            spend=Decimal("100"),
            impressions=10000,
        )
        assert m.effective_cpm == Decimal("10")

    def test_zero_clicks_no_error(self):
        m = CampaignMetric(
            campaign_id="test",
            platform=Platform.GOOGLE,
            timestamp=datetime.now(),
            spend=Decimal("0"),
            clicks=0,
        )
        assert m.effective_cpc == Decimal("0")