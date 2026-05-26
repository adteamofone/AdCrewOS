"""Tests for Alerting Module."""
import pytest
from adcrewos.services.alerting import EmailAlert, SMSAlert, AlertManager
from adcrewos.models.schemas import AnomalyAlert, AnomalySeverity, Platform
from datetime import datetime


def _alert(severity: AnomalySeverity = AnomalySeverity.WARNING):
    return AnomalyAlert(
        id="test-1",
        campaign_id="camp-1",
        platform=Platform.GOOGLE,
        metric="ctr",
        severity=severity,
        expected_value=2.5,
        actual_value=0.5,
        deviation_pct=-80.0,
        detected_at=datetime.now(),
        message="CTR dropped significantly",
    )


class TestEmailAlert:
    def test_not_ready_without_config(self):
        email = EmailAlert(config={})
        assert not email.is_ready()

    def test_ready_with_config(self):
        email = EmailAlert(config={
            "smtp_server": "smtp.test.com",
            "username": "test",
            "password": "pass",
            "recipients": ["test@test.com"],
        })
        assert email.is_ready()

    def test_send_fails_when_not_ready(self):
        email = EmailAlert(config={})
        assert not email.send_alert(_alert())

    def test_format_alert_email(self):
        body = EmailAlert._format_alert_email(_alert(AnomalySeverity.CRITICAL))
        assert "CRITICAL" in body
        assert "CTR dropped" in body

    def test_format_digest(self):
        alerts = [_alert(AnomalySeverity.WARNING), _alert(AnomalySeverity.INFO)]
        body = EmailAlert._format_digest(alerts)
        assert "2 anomalies" in body or "Alert Digest" in body


class TestSMSAlert:
    def test_not_ready_without_config(self):
        sms = SMSAlert(config={})
        assert not sms.is_ready()

    def test_not_ready_with_partial_config(self):
        sms = SMSAlert(config={"provider": "twilio"})
        assert not sms.is_ready()

    def test_send_skips_info_alerts(self):
        sms = SMSAlert(config={
            "provider": "twilio",
            "account_sid": "ACtest",
            "auth_token": "token",
            "from": "+15551234567",
            "to": "+15559876543",
        })
        assert sms.is_ready()
        assert not sms.send_alert(_alert(AnomalySeverity.INFO))

    def test_send_critical_fails_with_fake_creds(self, monkeypatch):
        """Sending to real Twilio with fake creds returns False (401 error)."""
        import adcrewos.services.alerting as alerting_mod
        sms = SMSAlert(config={
            "provider": "twilio",
            "account_sid": "ACtest",
            "auth_token": "bad_token",
            "from": "+15551234567",
            "to": "+15559876543",
        })
        assert sms.is_ready()
        # Should return False because Twilio rejects fake credentials
        result = sms.send_alert(_alert(AnomalySeverity.CRITICAL))
        assert result is False


class TestAlertManager:
    def test_dispatch_without_config(self):
        mgr = AlertManager()
        result = mgr.dispatch([_alert(AnomalySeverity.CRITICAL)])
        assert result == {"email_sent": 0, "sms_sent": 0}

    def test_configure_email(self):
        AlertManager.configure_email(
            smtp_server="smtp.test.com",
            username="test@test.com",
            password="secret",
            recipients=["me@test.com"],
        )
        import json
        from adcrewos.services.alerting import get_alerts_config_path
        cfg = json.loads(get_alerts_config_path().read_text())
        assert cfg["email"]["smtp_server"] == "smtp.test.com"
        # Clean up test file
        get_alerts_config_path().unlink(missing_ok=True)