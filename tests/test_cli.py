"""Basic tests for AdCrewOS."""
import subprocess
import sys


def test_cli_version():
    """Test that the CLI reports the correct version."""
    result = subprocess.run(
        [sys.executable, "-m", "adcrewos", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_cli_help():
    """Test that the CLI help is displayed."""
    result = subprocess.run(
        [sys.executable, "-m", "adcrewos", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "AdCrewOS" in result.stdout
    assert "init" in result.stdout


def test_alerts_config_sms_help():
    """Test SMS config help displays."""
    result = subprocess.run(
        [sys.executable, "-m", "adcrewos", "alerts", "config", "sms", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "account-sid" in result.stdout
    assert "from-number" in result.stdout


def test_alerts_config_email_help():
    """Test email config help displays."""
    result = subprocess.run(
        [sys.executable, "-m", "adcrewos", "alerts", "config", "email", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "smtp-server" in result.stdout


def test_monitor_works_with_mock():
    """Test monitor runs without errors using mock data."""
    result = subprocess.run(
        [sys.executable, "-m", "adcrewos", "monitor", "--days", "3"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "Total Spend" in result.stdout
