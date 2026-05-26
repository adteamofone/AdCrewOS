# AdCrewOS 🤖📊

**Mission:** Give solo advertisers the operational firepower of a full ad team, so one person can outperform agencies that charge ten times more.

AdCrewOS is the AI backbone for independent media buyers and freelance advertisers. Campaign monitoring, budget optimization, anomaly detection, and performance reporting that runs autonomously, 24/7. The strategy stays human. Everything else runs itself.

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.0-blue">
  <img src="https://img.shields.io/badge/tests-45%20passing-brightgreen">
  <img src="https://img.shields.io/badge/license-MIT-green">
  <img src="https://img.shields.io/badge/python-3.10+-orange">
</p>

---

## ✨ Features

| Module | What It Does |
|--------|-------------|
| **Campaign Monitor** | Fetches performance data from Google Ads & Meta Ads — spend, impressions, clicks, conversions, revenue, ROAS |
| **Budget Optimizer** | Statistical ROAS-based scoring engine that recommends how to shift budget between campaigns |
| **Anomaly Detector** | Z-score analysis that catches spend spikes, CTR drops, CPC changes, conversion anomalies, and missing data |
| **Report Generator** | Beautiful HTML + **PDF** performance reports (via weasyprint) with color-coded metrics and summary cards |
| **Alerting Service** | Email alerts via SMTP + SMS alerts via Twilio — critical anomalies are sent immediately, warnings get a daily digest |

## 📦 Quick Start

```bash
# Install
cd AdCrewOS
pip install -e .

# See what's possible
adcrewos --help

# Run with mock data (no accounts needed)
adcrewos monitor --days 7
adcrewos anomalies --days 14
adcrewos report generate --format pdf --days 7

# Check system status
adcrewos status
```

## 🧪 Tests

```bash
pytest tests/ -v    # 45 passing
```

## 🗺️ Project Structure

```
AdCrewOS/
├── src/adcrewos/
│   ├── cli.py                # Click CLI — 18 commands
│   ├── models/schemas.py     # Pydantic models
│   ├── core/
│   │   ├── campaign_monitor.py
│   │   ├── budget_optimizer.py
│   │   └── anomaly_detector.py
│   └── services/
│       ├── reporting.py      # HTML + PDF (weasyprint)
│       └── alerting.py       # SMTP email + Twilio SMS
├── tests/                    # 7 test files, 45 tests
├── docs/
│   └── SETUP_GUIDE.md        # Plain-English setup guide
└── pyproject.toml
```

## 🔑 To Go Live

AdCrewOS runs with mock data immediately. To connect real ad accounts and alerts, you'll need:

| What | How |
|------|-----|
| Google Ads tokens | Google Cloud Console → Google Ads API → developer token + OAuth2 |
| Meta Ads tokens | Meta Developer portal → App → Marketing API → access token |
| Email alerts | Any SMTP server (Gmail works — free app password) |
| SMS alerts | Twilio account (~$1/mo + $0.008/text) |

A full step-by-step guide with screenshots and no jargon is in **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)**.

## 📋 CLI Commands

```
adcrewos                              Show help
adcrewos init                         Initialize config
adcrewos config credentials           Store API tokens
adcrewos monitor                      Fetch campaign data
adcrewos optimize                     Budget recommendations
adcrewos anomalies                    Scan for anomalies
adcrewos report generate              HTML or PDF report
adcrewos alerts config email          Configure SMTP email
adcrewos alerts config sms            Configure Twilio SMS
adcrewos alerts send                  Dispatch anomaly alerts
adcrewos status                       System status
```

## 🕐 Automated Daily Report

A cron job runs every morning at 9:00 AM:

1. Checks yesterday's campaign performance
2. Scans for anomalies over the last 7 days
3. Generates a PDF report
4. Delivers a summary to you

## 📄 License

MIT