"""Tests for Reporting Module."""
import pytest
import os
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from adcrewos.services.reporting import ReportGenerator
from adcrewos.models.schemas import CampaignMetric, Platform


def _metric(cid: str, name: str = "Test Campaign", spend: float = 100,
            impressions: int = 10000, clicks: int = 100, conversions: int = 5,
            revenue: float = 300, days_ago: int = 0):
    return CampaignMetric(
        campaign_id=cid,
        platform=Platform.GOOGLE,
        timestamp=datetime.now() - timedelta(days=days_ago),
        spend=Decimal(str(spend)),
        impressions=impressions,
        clicks=clicks,
        conversions=conversions,
        revenue=Decimal(str(revenue)),
    )


class TestReportGenerator:
    def test_generate_html_report(self, tmp_path):
        gen = ReportGenerator(output_dir=str(tmp_path))
        metrics = [_metric("c1", days_ago=i) for i in range(7)]
        names = {"c1": "Test Campaign"}
        path = gen.export_html(metrics, names, output_path=str(tmp_path / "report.html"))
        assert os.path.exists(path)
        content = Path(path).read_text()
        assert "AdCrewOS Performance Report" in content
        assert "Test Campaign" in content

    def test_empty_metrics_generates(self, tmp_path):
        gen = ReportGenerator(output_dir=str(tmp_path))
        path = gen.export_html([], {}, output_path=str(tmp_path / "empty.html"))
        assert os.path.exists(path)

    def test_report_object_created(self, tmp_path):
        gen = ReportGenerator(output_dir=str(tmp_path))
        metrics = [_metric("c1", days_ago=i) for i in range(7)]
        names = {"c1": "Test"}
        report = gen.generate_report(metrics, names)
        assert report.id
        assert report.summary
        assert "Campaigns: 1" in report.summary

    def test_aggregation_by_campaign(self):
        gen = ReportGenerator()
        metrics = [
            _metric("c1", spend=100, clicks=50, days_ago=i) for i in range(3)
        ] + [
            _metric("c2", spend=200, clicks=100, days_ago=i) for i in range(3)
        ]
        names = {"c1": "Camp A", "c2": "Camp B"}
        agg = gen._aggregate_by_campaign(metrics, names)
        assert "c1" in agg
        assert "c2" in agg
        assert float(agg["c1"]["spend"]) == 300  # 3 days * 100
        assert float(agg["c2"]["spend"]) == 600  # 3 days * 200

    def test_pdf_generation(self, tmp_path):
        """Test PDF generation with weasyprint."""
        from adcrewos.services.reporting import HAS_WEASYPRINT
        if not HAS_WEASYPRINT:
            pytest.skip("weasyprint not installed")
        gen = ReportGenerator(output_dir=str(tmp_path))
        metrics = [_metric("c1", days_ago=i) for i in range(5)]
        names = {"c1": "Test Campaign"}
        path = gen.export_pdf(metrics, names, output_path=str(tmp_path / "report.pdf"))
        import os
        assert os.path.exists(path)
        assert path.endswith(".pdf")
        assert os.path.getsize(path) > 1000