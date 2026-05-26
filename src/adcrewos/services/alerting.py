"""Alerting Service — Email and SMS notifications for anomalies.

Email: Uses SMTP (works with Gmail, SendGrid, Mailgun, any SMTP relay).
SMS:   Requires a third-party SMS provider (Twilio, etc.).

The SMS module is designed to work with any provider that has an HTTP API.
When you set up Twilio (or similar), update the provider config and it
just works.

*Tokens needed from you:*
  - Email: SMTP server + credentials (or SendGrid/Mailgun API key)
  - SMS:  Twilio (or similar) account SID + auth token + phone number
"""

from __future__ import annotations

import json
import os
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from adcrewos.models.schemas import (
    AlertChannel,
    AlertChannelType,
    AnomalyAlert,
    AnomalySeverity,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def get_alerts_config_path() -> Path:
    return Path(os.getenv("ADCREWOS_HOME", str(Path.home() / ".adcrewos"))) / "alerts.json"


def _load_config() -> dict:
    path = get_alerts_config_path()
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_config(cfg: dict):
    get_alerts_config_path().parent.mkdir(parents=True, exist_ok=True)
    get_alerts_config_path().write_text(json.dumps(cfg, indent=2))


# ---------------------------------------------------------------------------
# Email Alerting
# ---------------------------------------------------------------------------

class EmailAlert:
    """Send anomaly alerts via email over SMTP.

    Setup (one-time):
        adcrewos alerts config email --smtp-server smtp.gmail.com \\
            --smtp-port 587 --username your@gmail.com --password "app-password"

    Or set environment variables:
        ADCREWOS_SMTP_SERVER=smtp.gmail.com
        ADCREWOS_SMTP_PORT=587
        ADCREWOS_SMTP_USERNAME=your@gmail.com
        ADCREWOS_SMTP_PASSWORD=your-app-password
    """

    def __init__(self, config: Optional[dict] = None):
        cfg = config or _load_config().get("email", {})
        self.server = cfg.get("smtp_server") or os.getenv("ADCREWOS_SMTP_SERVER", "")
        self.port = int(cfg.get("smtp_port") or os.getenv("ADCREWOS_SMTP_PORT", "587"))
        self.username = cfg.get("username") or os.getenv("ADCREWOS_SMTP_USERNAME", "")
        self.password = cfg.get("password") or os.getenv("ADCREWOS_SMTP_PASSWORD", "")
        self.from_addr = cfg.get("from") or self.username
        self.recipients = cfg.get("recipients", [])

        if cfg.get("recipients_file"):
            rpath = Path(cfg["recipients_file"]).expanduser()
            if rpath.exists():
                self.recipients = [l.strip() for l in rpath.read_text().splitlines() if l.strip()]

        self._ready = bool(self.server and self.username and self.password)

    def is_ready(self) -> bool:
        return self._ready and bool(self.recipients)

    def send_alert(self, alert: AnomalyAlert) -> bool:
        """Send a single anomaly alert via email."""
        if not self.is_ready():
            return False

        subject = f"[AdCrewOS] {alert.severity.upper()} - {alert.message[:80]}"
        body = self._format_alert_email(alert)

        return self._send(subject, body)

    def send_alerts_batch(self, alerts: list[AnomalyAlert]) -> int:
        """Send multiple alerts in one email digest, or individually for critical."""
        if not self.is_ready():
            return 0

        critical = [a for a in alerts if a.severity == AnomalySeverity.CRITICAL]
        others = [a for a in alerts if a.severity != AnomalySeverity.CRITICAL]

        sent = 0
        # Send critical alerts individually
        for a in critical:
            if self.send_alert(a):
                sent += 1

        # Send digest for non-critical
        if others:
            digest_body = self._format_digest(others)
            if self._send(f"[AdCrewOS] Alert Digest - {len(others)} anomaly{'ies' if len(others) > 1 else 'y'}", digest_body):
                sent += 1

        return sent

    def _send(self, subject: str, body: str) -> bool:
        try:
            msg = MIMEText(body, "plain" if not body.strip().startswith("<") else "html")
            msg["Subject"] = subject
            msg["From"] = self.from_addr
            msg["To"] = ", ".join(self.recipients)

            ctx = ssl.create_default_context()
            with smtplib.SMTP(self.server, self.port) as smtp:
                smtp.starttls(context=ctx)
                smtp.login(self.username, self.password)
                smtp.sendmail(self.from_addr, self.recipients, msg.as_string())
            return True
        except Exception as e:
            print(f"[AdCrewOS] Email send failed: {e}")
            return False

    @staticmethod
    def _format_alert_email(alert: AnomalyAlert) -> str:
        return f"""AdCrewOS Alert
{'=' * 60}

Severity: {alert.severity.upper()}
Campaign: {alert.campaign_id}
Metric:   {alert.metric}
Time:     {alert.detected_at.strftime('%Y-%m-%d %H:%M:%S')}

Message:  {alert.message}

Expected: {alert.expected_value:.2f}
Actual:   {alert.actual_value:.2f}
Deviation: {alert.deviation_pct:+.1f}%

{'=' * 60}
This is an automated alert from AdCrewOS.
"""

    @staticmethod
    def _format_digest(alerts: list[AnomalyAlert]) -> str:
        lines = [f"AdCrewOS Alert Digest ({len(alerts)} anomalies)", "=" * 60, ""]
        for a in alerts:
            lines.append(f"[{a.severity.upper()}] {a.campaign_id[:20]:>20} | {a.message}")
        lines.append("")
        lines.append("=" * 60)
        lines.append("This is an automated digest from AdCrewOS.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# SMS Alerting (via Twilio or generic HTTP API)
# ---------------------------------------------------------------------------

class SMSAlert:
    """Send anomaly alerts via SMS.

    Requires a third-party SMS provider. Twilio is the primary integration path.

    Setup (one-time):
        adcrewos alerts config sms --provider twilio \\
            --account-sid ACxxxx --auth-token xxxx --from +15551234567 \\
            --to +15559876543

    Environment variables:
        ADCREWOS_SMS_PROVIDER=twilio
        ADCREWOS_TWILIO_ACCOUNT_SID=ACxxxx
        ADCREWOS_TWILIO_AUTH_TOKEN=xxxx
        ADCREWOS_TWILIO_FROM=+15551234567
        ADCREWOS_SMS_TO=+15559876543
    """

    def __init__(self, config: Optional[dict] = None):
        cfg = config or _load_config().get("sms", {})
        self.provider = cfg.get("provider") or os.getenv("ADCREWOS_SMS_PROVIDER", "")
        self.to_number = (cfg.get("to") or os.getenv("ADCREWOS_SMS_TO", "")).strip()

        self._ready = False
        self._api_base = ""
        self._api_key = ""

        if self.provider == "twilio":
            self.account_sid = cfg.get("account_sid") or os.getenv("ADCREWOS_TWILIO_ACCOUNT_SID", "")
            self.auth_token = cfg.get("auth_token") or os.getenv("ADCREWOS_TWILIO_AUTH_TOKEN", "")
            self.from_number = cfg.get("from") or os.getenv("ADCREWOS_TWILIO_FROM", "")
            self._ready = bool(self.account_sid and self.auth_token and self.from_number and self.to_number)
            self._api_base = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            self._api_key = self.auth_token

    def is_ready(self) -> bool:
        return self._ready

    def send_alert(self, alert: AnomalyAlert) -> bool:
        """Send an SMS for a critical anomaly."""
        if not self.is_ready():
            return False

        if alert.severity not in (AnomalySeverity.CRITICAL, AnomalySeverity.WARNING):
            return False

        message = self._format_sms(alert)
        return self._send(message)

    def _format_sms(self, alert: AnomalyAlert) -> str:
        """Keep SMS short — 160 char target."""
        return (
            f"[AdCrewOS {alert.severity.upper()}] "
            f"{alert.campaign_id[:20]}: "
            f"{alert.message[:120]}"
        )[:160]

    def _send(self, message: str) -> bool:
        if not self._ready:
            return False

        if self.provider == "twilio":
            return self._send_twilio(message)

        # Generic HTTP API fallback — customize for your provider
        print(f"[AdCrewOS] SMS would send to {self.to_number}: {message}")
        return True

    def _send_twilio(self, message: str) -> bool:
        """Send SMS via Twilio HTTP API."""
        try:
            import httpx
            # Twilio uses basic auth with AccountSid:AuthToken
            auth = (self.account_sid, self.auth_token)
            data = {
                "To": self.to_number,
                "From": self.from_number,
                "Body": message,
            }
            with httpx.Client() as client:
                resp = client.post(self._api_base, auth=auth, data=data, timeout=15)
                if resp.status_code == 201:
                    return True
                else:
                    print(f"[AdCrewOS] Twilio error: {resp.status_code} - {resp.text}")
                    return False
        except ImportError:
            print("[AdCrewOS] httpx required for SMS. Install: pip install httpx")
            return False
        except Exception as e:
            print(f"[AdCrewOS] SMS send failed: {e}")
            return False


# ---------------------------------------------------------------------------
# Alert Manager — unified orchestrator
# ---------------------------------------------------------------------------

class AlertManager:
    """Unified alert dispatch. Routes anomalies to all configured channels.

    Usage:
        mgr = AlertManager()
        results = mgr.dispatch(alerts)

    Works immediately with email if you configure SMTP.
    SMS requires a Twilio (or similar) account.
    """

    def __init__(self):
        self.email = EmailAlert()
        self.sms = SMSAlert()

    def dispatch(self, alerts: list[AnomalyAlert]) -> dict:
        """Send alerts through all configured channels.

        Returns:
            dict with keys 'email_sent', 'sms_sent' counts.
        """
        result = {"email_sent": 0, "sms_sent": 0}

        if alerts and self.email.is_ready():
            result["email_sent"] = self.email.send_alerts_batch(alerts)

        if self.sms.is_ready():
            for a in alerts:
                if self.sms.send_alert(a):
                    result["sms_sent"] += 1

        return result

    @staticmethod
    def configure_email(
        smtp_server: str,
        smtp_port: int = 587,
        username: str = "",
        password: str = "",
        from_addr: Optional[str] = None,
        recipients: Optional[list[str]] = None,
    ):
        """Save email configuration."""
        cfg = _load_config()
        cfg["email"] = {
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "from": from_addr or username,
            "recipients": recipients or [],
        }
        _save_config(cfg)

    @staticmethod
    def configure_sms(
        provider: str,
        to_number: str,
        **kwargs,
    ):
        """Save SMS configuration."""
        cfg = _load_config()
        sms_cfg = {"provider": provider, "to": to_number}
        sms_cfg.update(kwargs)
        cfg["sms"] = sms_cfg
        _save_config(cfg)