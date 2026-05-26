"""Reporting Dashboard Module.

Generates performance reports in HTML and PDF formats.
Uses Jinja2 for HTML templates, and can export to PDF via weasyprint
(when available) or fallback HTML-only.

Also provides a text summary suitable for CLI display.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional

from adcrewos.models.schemas import (
    CampaignMetric,
    Platform,
    Report,
    ReportConfig,
)

try:
    from jinja2 import Environment, PackageLoader, select_autoescape
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

try:
    import weasyprint
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False


class ReportGenerator:
    """Generate campaign performance reports.

    Usage:
        gen = ReportGenerator()
        report = gen.generate_report(metrics, campaigns, config)
        pdf_path = gen.export_pdf(report)
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or self._default_output_dir())
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _default_output_dir() -> str:
        return os.getenv("ADCREWOS_REPORTS_DIR", str(Path.home() / ".adcrewos" / "reports"))

    def generate_report(
        self,
        metrics: list[CampaignMetric],
        campaign_names: dict[str, str],
        config: Optional[ReportConfig] = None,
        period_label: str = "Last 7 days",
    ) -> Report:
        """Generate a performance report from metrics data."""
        now = datetime.now()
        period_start = now - timedelta(days=7)
        period_end = now

        if metrics:
            period_start = min(m.timestamp for m in metrics)
            period_end = max(m.timestamp for m in metrics)

        # Aggregate metrics by campaign
        campaign_data = self._aggregate_by_campaign(metrics, campaign_names)

        # Build summary
        total_spend = sum(m.spend for m in metrics)
        total_impressions = sum(m.impressions for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        total_revenue = sum((m.revenue or Decimal("0")) for m in metrics)
        total_roas = float(total_revenue / total_spend) if total_spend > 0 else 0.0

        summary = (
            f"Period: {period_start.strftime('%b %d')} - {period_end.strftime('%b %d, %Y')}\n"
            f"Total Spend: ${float(total_spend):,.2f}\n"
            f"Total Impressions: {total_impressions:,}\n"
            f"Total Clicks: {total_clicks:,}\n"
            f"Total Conversions: {total_conversions:,}\n"
            f"Total Revenue: ${float(total_revenue):,.2f}\n"
            f"Overall ROAS: {total_roas:.2f}x\n"
            f"Campaigns: {len(campaign_data)}"
        )

        metrics_dict = {}
        for cid, data in campaign_data.items():
            metrics_dict[cid] = {
                "name": data["name"],
                "spend": float(data["spend"]),
                "impressions": data["impressions"],
                "clicks": data["clicks"],
                "conversions": data["conversions"],
                "revenue": float(data["revenue"]),
                "roas": data["roas"],
                "ctr": data["ctr"],
            }

        report_id = str(uuid.uuid4())[:8]
        fmt = config.format if config else "html"

        # Generate the file
        if fmt == "pdf":
            file_path = self.export_pdf(
                metrics, campaign_names,
                output_path=str(self.output_dir / f"report_{report_id}.pdf"),
                period_label=period_label,
            )
        else:
            file_path = self.export_html(
                metrics, campaign_names,
                output_path=str(self.output_dir / f"report_{report_id}.html"),
                period_label=period_label,
            )

        return Report(
            id=report_id,
            config_id=config.id if config else "manual",
            generated_at=now,
            period_start=period_start,
            period_end=period_end,
            format=fmt,
            file_path=file_path,
            summary=summary,
            metrics=metrics_dict,
        )

    def _aggregate_by_campaign(
        self,
        metrics: list[CampaignMetric],
        campaign_names: dict[str, str],
    ) -> dict:
        """Group and aggregate metrics by campaign."""
        from collections import defaultdict

        agg: dict[str, dict] = defaultdict(lambda: {
            "name": "",
            "spend": Decimal("0"),
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "revenue": Decimal("0"),
            "days": set(),
        })

        for m in metrics:
            d = agg[m.campaign_id]
            d["name"] = campaign_names.get(m.campaign_id, m.campaign_id)
            d["spend"] += m.spend
            d["impressions"] += m.impressions
            d["clicks"] += m.clicks
            d["conversions"] += m.conversions
            d["revenue"] += m.revenue or Decimal("0")
            d["days"].add(m.timestamp.date())

        result = {}
        for cid, data in agg.items():
            roas = float(data["revenue"] / data["spend"]) if data["spend"] > 0 else 0.0
            ctr = (data["clicks"] / data["impressions"] * 100) if data["impressions"] > 0 else 0.0
            data["roas"] = round(roas, 2)
            data["ctr"] = round(ctr, 4)
            data["days"] = len(data["days"])
            result[cid] = dict(data)

        return result

    def export_html(
        self,
        metrics: list[CampaignMetric],
        campaign_names: dict[str, str],
        output_path: Optional[str] = None,
        period_label: str = "Last 7 days",
    ) -> str:
        """Generate an HTML report file."""
        now = datetime.now()
        campaign_data = self._aggregate_by_campaign(metrics, campaign_names)

        total_spend = sum(m.spend for m in metrics)
        total_impressions = sum(m.impressions for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        total_revenue = sum((m.revenue or Decimal("0")) for m in metrics)
        total_roas = float(total_revenue / total_spend) if total_spend > 0 else 0.0

        # Build rows
        rows_html = ""
        for cid, data in campaign_data.items():
            roas_color = "#22c55e" if data["roas"] >= 2 else ("#eab308" if data["roas"] >= 1 else "#ef4444")
            rows_html += f"""
            <tr>
                <td>{data['name']}</td>
                <td style="text-align:right">${data['spend']:,.2f}</td>
                <td style="text-align:right">{data['impressions']:,}</td>
                <td style="text-align:right">{data['clicks']:,}</td>
                <td style="text-align:right">{data['conversions']}</td>
                <td style="text-align:right">${data['revenue']:,.2f}</td>
                <td style="text-align:right; color:{roas_color}; font-weight:bold">{data['roas']}x</td>
                <td style="text-align:right">{data['ctr']}%</td>
                <td style="text-align:right">{data['days']}d</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AdCrewOS Performance Report - {now.strftime('%b %d, %Y')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1a1a2e; background: #f8fafc; padding: 40px; }}
        .header {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; padding: 32px; border-radius: 12px; margin-bottom: 32px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
        .header p {{ color: #94a3b8; font-size: 14px; }}
        .summary-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-bottom: 32px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; }}
        .metric-card .value {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; }}
        .metric-card .label {{ font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
        .green {{ color: #22c55e; }} .yellow {{ color: #eab308; }} .red {{ color: #ef4444; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th {{ background: #f1f5f9; text-align: left; padding: 12px 16px; font-size: 12px; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px; }}
        td {{ padding: 12px 16px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
        tr:last-child td {{ border-bottom: none; }}
        .footer {{ text-align: center; margin-top: 32px; color: #94a3b8; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AdCrewOS Performance Report</h1>
        <p>{period_label}  |  Generated {now.strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>

    <div class="summary-row">
        <div class="metric-card"><div class="value {'red' if total_roas < 1 else ('yellow' if total_roas < 2 else 'green')}">${float(total_spend):,.2f}</div><div class="label">Total Spend</div></div>
        <div class="metric-card"><div class="value">{total_impressions:,}</div><div class="label">Impressions</div></div>
        <div class="metric-card"><div class="value">{total_clicks:,}</div><div class="label">Clicks</div></div>
        <div class="metric-card"><div class="value">{total_conversions}</div><div class="label">Conversions</div></div>
        <div class="metric-card"><div class="value green">${float(total_revenue):,.2f}</div><div class="label">Revenue</div></div>
        <div class="metric-card"><div class="value {'red' if total_roas < 1 else ('yellow' if total_roas < 2 else 'green')}">{total_roas:.2f}x</div><div class="label">ROAS</div></div>
    </div>

    <table>
        <thead>
            <tr><th>Campaign</th><th style="text-align:right">Spend</th><th style="text-align:right">Impressions</th><th style="text-align:right">Clicks</th><th style="text-align:right">Conv.</th><th style="text-align:right">Revenue</th><th style="text-align:right">ROAS</th><th style="text-align:right">CTR</th><th style="text-align:right">Days</th></tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    <div class="footer">Generated by AdCrewOS  |  Data provided by connected ad platforms</div>
</body>
</html>"""

        path = output_path or str(self.output_dir / f"report_{uuid.uuid4().hex[:8]}.html")
        with open(path, "w") as f:
            f.write(html)

        return path

    def export_pdf(
        self,
        metrics: list[CampaignMetric],
        campaign_names: dict[str, str],
        output_path: Optional[str] = None,
        period_label: str = "Last 7 days",
    ) -> str:
        """Generate a PDF report.

        Falls back to HTML if weasyprint is not available.
        """
        if not HAS_WEASYPRINT:
            # PDF export requires weasyprint: pip install weasyprint
            # For now, generate HTML (which most browsers can convert to PDF)
            return self.export_html(metrics, campaign_names, output_path, period_label)

        path = output_path or str(self.output_dir / f"report_{uuid.uuid4().hex[:8]}.pdf")
        html_path = self.export_html(metrics, campaign_names, period_label=period_label)
        weasyprint.HTML(filename=html_path).write_pdf(path)
        return path