"""AdCrewOS CLI entry point."""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click

from adcrewos import __version__
from adcrewos.core.campaign_monitor import CampaignMonitor
from adcrewos.core.budget_optimizer import BudgetOptimizer
from adcrewos.core.anomaly_detector import AnomalyDetector
from adcrewos.services.reporting import ReportGenerator
from adcrewos.services.alerting import AlertManager, EmailAlert, SMSAlert


# ---------------------------------------------------------------------------
# Shared configuration
# ---------------------------------------------------------------------------

CONFIG_DIR = Path.home() / ".adcrewos"
CREDENTIALS_PATH = CONFIG_DIR / "credentials.json"


def load_credentials() -> dict:
    if CREDENTIALS_PATH.exists():
        return json.loads(CREDENTIALS_PATH.read_text())
    return {}


def save_credentials(creds: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(json.dumps(creds, indent=2))


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------


@click.group(invoke_without_command=True)
@click.version_option(package_name="adcrewos")
@click.pass_context
def main(ctx):
    """AdCrewOS — AI backbone for independent media buyers.

    Campaign monitoring, budget optimization, anomaly detection,
    and automated reporting for solo advertisers.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        sys.exit(0)


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


@main.command()
@click.option("--force", is_flag=True, help="Overwrite existing config")
def init(force: bool):
    """Initialize a new AdCrewOS project."""
    if CONFIG_DIR.exists() and not force:
        click.echo(f"AdCrewOS already initialized at {CONFIG_DIR}")
        click.echo("Use --force to reinitialize.")
        return

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text("{}")
    click.echo(f"AdCrewOS initialized at {CONFIG_DIR}")
    click.echo("Next: configure your ad platform credentials")
    click.echo("  adcrewos config credentials --help")


# ---------------------------------------------------------------------------
# config credentials
# ---------------------------------------------------------------------------


@main.group()
def config():
    """Manage AdCrewOS configuration."""


@config.command()
@click.option("--google-dev-token", default="", help="Google Ads developer token")
@click.option("--google-client-id", default="", help="Google OAuth2 client ID")
@click.option("--google-client-secret", default="", help="Google OAuth2 client secret")
@click.option("--google-customer-id", default="", help="Google Ads customer ID (XXX-XXX-XXXX)")
@click.option("--meta-app-id", default="", help="Meta App ID")
@click.option("--meta-app-secret", default="", help="Meta App Secret")
@click.option("--meta-access-token", default="", help="Meta long-lived access token")
@click.option("--show", is_flag=True, help="Show all stored credentials")
def credentials(
    google_dev_token: str,
    google_client_id: str,
    google_client_secret: str,
    google_customer_id: str,
    meta_app_id: str,
    meta_app_secret: str,
    meta_access_token: str,
    show: bool,
):
    """Store ad platform API credentials."""
    if show:
        creds = load_credentials()
        for k, v in creds.items():
            masked = v[:4] + "****" + v[-4:] if len(v) > 8 else "****"
            click.echo(f"  {k}: {masked}")
        return

    creds = load_credentials()
    updated = False

    for key, val in [
        ("google_developer_token", google_dev_token),
        ("google_client_id", google_client_id),
        ("google_client_secret", google_client_secret),
        ("google_customer_id", google_customer_id),
        ("meta_app_id", meta_app_id),
        ("meta_app_secret", meta_app_secret),
        ("meta_access_token", meta_access_token),
    ]:
        if val:
            creds[key] = val
            updated = True

    if updated:
        save_credentials(creds)
        click.echo("Credentials updated.")
    else:
        click.echo("No credentials provided. Use --help to see options.")
        click.echo("Use --show to view stored credentials.")


# ---------------------------------------------------------------------------
# monitor
# ---------------------------------------------------------------------------


@main.command()
@click.option("--platform", type=click.Choice(["google", "meta", "all"]), default="all")
@click.option("--days", default=7, help="Days of history to fetch")
def monitor(platform: str, days: int):
    """Fetch and display campaign performance metrics."""
    click.echo(f"Fetching campaign data for last {days} days...")

    async def run():
        monitor = CampaignMonitor()

        # Wire credentials if available
        creds = load_credentials()
        if creds.get("google_developer_token"):
            monitor.set_credentials("google", {
                "developer_token": creds["google_developer_token"],
                "client_id": creds.get("google_client_id", ""),
                "client_secret": creds.get("google_client_secret", ""),
                "customer_id": creds.get("google_customer_id", ""),
            })
        if creds.get("meta_access_token"):
            monitor.set_credentials("meta", {
                "access_token": creds["meta_access_token"],
                "app_id": creds.get("meta_app_id", ""),
                "app_secret": creds.get("meta_app_secret", ""),
            })

        from adcrewos.models.schemas import Platform as PlatEnum
        plat = None if platform == "all" else PlatEnum(platform)

        accounts = await monitor.fetch_accounts(platform=plat)
        campaigns = await monitor.fetch_campaigns(platform=plat)
        metrics = await monitor.fetch_metrics(days_back=days, platform=plat)

        if not campaigns:
            click.echo("No campaigns found. Are your credentials configured?")
            click.echo("  adcrewos config credentials --help")
            return

        # Aggregation
        from collections import defaultdict
        by_campaign = defaultdict(list)
        for m in metrics:
            by_campaign[m.campaign_id].append(m)

        campaign_names = {c.id: c.name for c in campaigns}

        click.echo(f"\n{'Platform':<10} {'Campaign':<35} {'Spend':>12} {'Imp':>10} {'Clicks':>8} {'Conv':>6} {'ROAS':>8}")
        click.echo("-" * 90)
        total_spend = 0
        for camp in campaigns:
            camp_m = by_campaign.get(camp.id, [])
            if not camp_m:
                continue
            spend = sum(m.spend for m in camp_m)
            imp = sum(m.impressions for m in camp_m)
            clicks = sum(m.clicks for m in camp_m)
            convs = sum(m.conversions for m in camp_m)
            rev = sum((m.revenue or 0) for m in camp_m)
            roas = float(rev / spend) if spend > 0 else 0.0
            total_spend += spend
            click.echo(
                f"{camp.platform.value:<10} "
                f"{camp.name:<35} "
                f"${float(spend):>8.2f}  "
                f"{imp:>8,d}  "
                f"{clicks:>6,d}  "
                f"{convs:>4,d}  "
                f"{roas:>6.2f}x"
            )

        click.echo("-" * 90)
        click.echo(f"{'Total Spend:':>57} ${float(total_spend):>8.2f}")

    asyncio.run(run())


# ---------------------------------------------------------------------------
# optimize
# ---------------------------------------------------------------------------


@main.command()
@click.option("--days", default=7, help="Analysis window in days")
@click.option("--budget", default=None, type=float, help="Total daily budget to allocate")
@click.option("--min-confidence", default=0.5, type=float, help="Minimum confidence threshold")
def optimize(days: int, budget: Optional[float], min_confidence: float):
    """Analyze campaign performance and recommend budget allocation."""
    click.echo(f"Analyzing campaign performance over last {days} days...")

    async def run():
        monitor = CampaignMonitor()
        campaigns = await monitor.fetch_campaigns()
        metrics = await monitor.fetch_metrics(days_back=days)

        if not campaigns or not metrics:
            click.echo("Insufficient data to generate recommendations.")
            click.echo("Use 'adcrewos monitor' to verify data availability.")
            return

        from decimal import Decimal
        optimizer = BudgetOptimizer(min_confidence=min_confidence)
        total = Decimal(str(budget)) if budget else None
        recs = optimizer.analyze(campaigns, metrics, total_budget=total)

        if not recs:
            click.echo("No budget recommendations at this time. Performance may be stable or data insufficient.")
            return

        click.echo(f"\n{'Campaign':<40} {'Current':>10} {'Recommended':>12} {'Conf.':>7} {'Impact'}")
        click.echo("-" * 100)
        for r in recs:
            direction = "▲" if r.recommended_budget > r.current_budget else "▼"
            click.echo(
                f"{r.campaign_id[:38]:<40} "
                f"${float(r.current_budget):>8.2f}  "
                f"{direction} ${float(r.recommended_budget):>8.2f}  "
                f"{r.confidence:>5.0%}  "
                f"{r.reasoning[:40]}"
            )

        click.echo("")
        click.echo("Apply recommendations: adcrewos optimize apply (coming soon)")

    asyncio.run(run())


# ---------------------------------------------------------------------------
# anomalies
# ---------------------------------------------------------------------------


@main.command()
@click.option("--days", default=14, help="Analysis window in days")
@click.option("--threshold", default=2.5, type=float, help="Z-score threshold for anomaly detection")
def anomalies(days: int, threshold: float):
    """Scan for performance anomalies."""
    click.echo(f"Scanning for anomalies over last {days} days (z-score threshold: {threshold})...")

    async def run():
        monitor = CampaignMonitor()
        metrics = await monitor.fetch_metrics(days_back=days)

        if not metrics:
            click.echo("No metrics data available to analyze.")
            return

        detector = AnomalyDetector(z_score_threshold=threshold)
        alerts = detector.analyze(metrics)

        if not alerts:
            click.echo("No anomalies detected. Performance looks normal.")
            return

        # Group by severity
        from adcrewos.models.schemas import AnomalySeverity
        critical = [a for a in alerts if a.severity == AnomalySeverity.CRITICAL]
        warnings = [a for a in alerts if a.severity == AnomalySeverity.WARNING]
        info = [a for a in alerts if a.severity == AnomalySeverity.INFO]

        if critical:
            click.echo(f"\n🔥 CRITICAL ({len(critical)}):")
            for a in critical:
                click.echo(f"  [{a.metric}] {a.message}")

        if warnings:
            click.echo(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for a in warnings[:10]:
                click.echo(f"  [{a.metric}] {a.message}")

        if info:
            click.echo(f"\nℹ️  INFO ({len(info)}):")
            for a in info[:5]:
                click.echo(f"  [{a.metric}] {a.message}")

        if len(alerts) > 15:
            click.echo(f"\n... and {len(alerts) - 15} more alerts.")

        click.echo("\nSend alerts: adcrewos alerts send")
        click.echo("Configure alerts: adcrewos alerts config --help")

    asyncio.run(run())


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------


@main.group()
def report():
    """Generate performance reports."""


@report.command()
@click.option("--days", default=7, help="Report period in days")
@click.option("--format", "fmt", type=click.Choice(["html", "pdf"]), default="html", help="Output format")
@click.option("--output", default=None, help="Custom output path")
def generate(days: int, fmt: str, output: Optional[str]):
    """Generate a campaign performance report."""
    click.echo(f"Generating {fmt.upper()} report for last {days} days...")

    async def run():
        monitor = CampaignMonitor()
        campaigns = await monitor.fetch_campaigns()
        metrics = await monitor.fetch_metrics(days_back=days)
        campaign_names = {c.id: c.name for c in campaigns}

        if not metrics:
            click.echo("No metrics available for report generation.")
            return

        gen = ReportGenerator()
        path = gen.export_html(
            metrics,
            campaign_names,
            output_path=output,
            period_label=f"Last {days} days",
        )
        click.echo(f"\nReport generated: {path}")
        click.echo("Open the HTML file in your browser to view.")

        if fmt == "pdf":
            pdf_path = gen.export_pdf(
                metrics,
                campaign_names,
                output_path=output.replace(".html", ".pdf") if output else None,
                period_label=f"Last {days} days",
            )
            click.echo(f"PDF: {pdf_path}")

    asyncio.run(run())


# ---------------------------------------------------------------------------
# alerts
# ---------------------------------------------------------------------------


@main.group()
def alerts():
    """Manage anomaly alerting configuration."""


# ---------------------------------------------------------------------------
# alerts config (group)
# ---------------------------------------------------------------------------


@alerts.group(invoke_without_command=True)
@click.pass_context
def config(ctx):
    """Configure alert delivery channels."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@config.command()
@click.option("--smtp-server", default="", help="SMTP server (e.g. smtp.gmail.com)")
@click.option("--smtp-port", default=587, type=int, help="SMTP port")
@click.option("--username", default="", help="SMTP username")
@click.option("--password", default="", help="SMTP password/app-password")
@click.option("--from-addr", default="", help="From email address")
@click.option("--to", "recipients", multiple=True, help="Recipient email address (repeatable)")
def email(
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    from_addr: str,
    recipients: tuple[str],
):
    """Configure email alerts via SMTP.

    Example:
        adcrewos alerts config email \\
            --smtp-server smtp.gmail.com \\
            --smtp-port 587 \\
            --username your@gmail.com \\
            --password "app-password" \\
            --to alerts@example.com
    """
    if smtp_server:
        AlertManager.configure_email(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            username=username,
            password=password,
            from_addr=from_addr or None,
            recipients=list(recipients) or None,
        )
        click.echo(f"Email alerts configured: {smtp_server}:{smtp_port}")
        click.echo("  Recipients: " + (", ".join(recipients) if recipients else "(none)"))
    else:
        click.echo("No configuration provided. See: adcrewos alerts config email --help")


@config.command()
@click.option("--provider", default="twilio", help="SMS provider (default: twilio)")
@click.option("--account-sid", default="", help="Twilio Account SID (ACxxx)")
@click.option("--auth-token", default="", help="Twilio Auth Token")
@click.option("--from-number", default="", help="Twilio phone number to send from")
@click.option("--to", "to_number", default="", help="Phone number to receive alerts")
def sms(
    provider: str,
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str,
):
    """Configure SMS alerts via Twilio.

    Example:
        adcrewos alerts config sms \\
            --provider twilio \\
            --account-sid ACxxxxxxxxxxxx \\
            --auth-token xxxxxxxxxxxxxxx \\
            --from-number +15551234567 \\
            --to +15557654321
    """
    if account_sid and auth_token and from_number and to_number:
        AlertManager.configure_sms(
            provider=provider,
            to_number=to_number,
            account_sid=account_sid,
            auth_token=auth_token,
            **{"from": from_number},
        )
        click.echo(f"SMS alerts configured: {provider.upper()}")
        click.echo(f"  From: {from_number}")
        click.echo(f"  To:   {to_number}")
    else:
        click.echo("Missing required fields. See: adcrewos alerts config sms --help")
        click.echo("Requires: --account-sid, --auth-token, --from-number, --to")


@alerts.command()
@click.option("--dry-run", is_flag=True, help="Show what would be sent without sending")
def send(dry_run: bool):
    """Scan for anomalies and dispatch alerts."""
    click.echo("Scanning for anomalies and dispatching alerts...")

    async def run():
        monitor = CampaignMonitor()
        metrics = await monitor.fetch_metrics(days_back=14)
        if not metrics:
            click.echo("No metrics data available.")
            return

        detector = AnomalyDetector()
        alerts_ = detector.analyze(metrics)

        if not alerts_:
            click.echo("No anomalies found. Nothing to alert on.")
            return

        click.echo(f"Found {len(alerts_)} anomalies")

        if dry_run:
            click.echo("\nWould send:")
            from adcrewos.models.schemas import AnomalySeverity
            for a in alerts_:
                if a.severity in (AnomalySeverity.CRITICAL, AnomalySeverity.WARNING):
                    click.echo(f"  [{a.severity.value}] {a.message}")
            return

        mgr = AlertManager()
        if not mgr.email.is_ready() and not mgr.sms.is_ready():
            click.echo("\nNo alert channels configured!")
            click.echo("Configure email: adcrewos alerts config email --help")
            click.echo("Configure SMS:   adcrewos alerts config sms --help")
            click.echo("Or set environment variables:")
            click.echo("  ADCREWOS_SMTP_SERVER / ADCREWOS_SMTP_USERNAME / ADCREWOS_SMTP_PASSWORD")
            click.echo("  ADCREWOS_TWILIO_ACCOUNT_SID / ADCREWOS_TWILIO_AUTH_TOKEN / ADCREWOS_TWILIO_FROM")
            return

        result = mgr.dispatch(alerts_)
        click.echo(f"Sent: {result['email_sent']} email(s), {result['sms_sent']} SMS")

    asyncio.run(run())


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


@main.command()
def status():
    """Show AdCrewOS system status and configuration."""
    creds = load_credentials()
    config_dir = CONFIG_DIR

    click.echo(f"AdCrewOS v{__version__}")
    click.echo(f"Config dir: {config_dir}")
    click.echo("")

    # Credentials
    has_google = bool(creds.get("google_developer_token"))
    has_meta = bool(creds.get("meta_access_token"))

    click.echo("Platform Credentials:")
    click.echo(f"  Google Ads:      {'✓' if has_google else '✗ (needs setup)'}")
    click.echo(f"  Meta Ads:        {'✓' if has_meta else '✗ (needs setup)'}")
    click.echo("")

    # Alert channels
    from adcrewos.services.alerting import EmailAlert, SMSAlert
    email = EmailAlert()
    sms = SMSAlert()
    click.echo("Alert Channels:")
    click.echo(f"  Email:           {'✓ ready' if email.is_ready() else '✗ not configured'}")
    click.echo(f"  SMS:             {'✓ ready' if sms.is_ready() else '✗ not configured'}")
    click.echo("")

    click.echo("Quick commands:")
    click.echo("  adcrewos monitor        Fetch campaign performance")
    click.echo("  adcrewos optimize       Get budget recommendations")
    click.echo("  adcrewos anomalies      Scan for performance anomalies")
    click.echo("  adcrewos report generate  Generate performance report")

    if not has_google or not has_meta:
        click.echo("\nTo connect ad platforms:")
        click.echo("  adcrewos config credentials --help")


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()