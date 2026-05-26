# AdCrewOS Setup Guide
### For people who don't code — step by step

This guide walks you through getting the **4 keys** AdCrewOS needs to connect to the real world. Each section is a separate "errand" — do them in any order. Each takes about 10-15 minutes.

---

## Before You Start

You will be:
1. Making several free accounts
2. Copy-pasting secret codes into AdCrewOS
3. Maybe spending $0–$10 (some services need a tiny deposit)

**Rules for the secret codes:**
- Treat them like passwords. Never share them, never email them, never post them online.
- If a code starts with "AC" or "sk-" or "ya29.", that's normal. Copy the whole thing.
- If you mess up and run a command with the wrong code, just run it again with the right one.

---

## 🅰️ Google Ads Tokens
*What this does: lets AdCrewOS see your Google ad campaigns and their performance.*

### Step 1: Log into Google
Go to https://console.cloud.google.com
- Sign in with the same email you use for Google Ads
- If it asks you to pick a "project," click the project dropdown at the top → "New Project" → name it "AdCrewOS" → click "Create"

### Step 2: Turn on the Google Ads API
- At the top, in the search bar, type **"Google Ads API"** and press Enter
- Click the result that says **"Google Ads API"**
- Click the blue **"ENABLE"** button
- Wait 30 seconds for it to turn on

### Step 3: Create your Developer Token
- On the left menu, click **"Credentials"**
- Click the blue **"+ CREATE CREDENTIALS"** button at the top
- Choose **"API Key"**
- A box pops up with a long code like `AIzaSyB234...`. **Copy this code** and save it somewhere. This is your **developer token**.
- Click "Close"

### Step 4: Create OAuth2 Credentials (the harder one)
- Click **"+ CREATE CREDENTIALS"** again
- Choose **"OAuth client ID"**
- If it asks you to "Configure Consent Screen," click "External" → "Create" → fill in just the "App name" (type "AdCrewOS") and your email → click "Save and Continue" (skip everything else) → "Back to Dashboard"
- Try "+ CREATE CREDENTIALS" → "OAuth client ID" again
- For **Application type**, choose **"Desktop app"**
- Name it "AdCrewOS CLI"
- Click **"Create"**
- A box pops up with a **Client ID** and **Client Secret**. Both are long codes. Copy both and save them.

### Step 5: Find your Google Ads Customer ID
- Go to https://ads.google.com
- In the top right, click the little gear icon → "Account settings"
- Look for your **Customer ID** — it looks like `123-456-7890`
- Copy it exactly (dashes and all)

### Step 6: Tell AdCrewOS your codes
Open Termux and type this (replace the fake codes with your real ones):

```
adcrewos config credentials \
  --google-dev-token AIzaSyB234... \
  --google-client-id 123456789-abc.apps.googleusercontent.com \
  --google-client-secret GOCSPX-xxxxx \
  --google-customer-id 123-456-7890
```

If it worked, you'll see: **"Credentials updated."**
Check with: `adcrewos status` — it should show a green check ✓ next to Google Ads.

---

## 🅱️ Meta (Facebook/Instagram) Ads Tokens
*What this does: lets AdCrewOS see your Meta ad campaigns.*

### Step 1: Create a Meta Developer Account
- Go to https://developers.facebook.com
- Click **"Get Started"** (top right)
- Log in with your Facebook/Instagram ad account
- Accept the terms

### Step 2: Create a Meta App
- At the top right, click **"My Apps"** → **"Create App"**
- Choose **"Business"** (the first option)
- Click **"Next"**
- App name: type **"AdCrewOS"**
- Contact email: your email
- Click **"Create App"**

### Step 3: Get your App ID and App Secret
- You're now on your app's dashboard
- On the left menu, click **"Settings"** → **"Basic"**
- You'll see:
  - **App ID** — a long number like `123456789012345`
  - **App Secret** — click "Show" and copy the code
- Copy both and save them

### Step 4: Turn on the Marketing API
- On the left menu, click **"Add Products"**
- Find **"Marketing API"** and click **"Set Up"**
- Accept any terms

### Step 5: Get a Long-Lived Access Token
- On the left menu, click **"Tools"** → **"Graph API Explorer"**
- At the top:
  - **Application**: pick "AdCrewOS"
  - **Token**: click "Get Token" → "Get Access Token"
  - A window pops up asking for permissions. Check these boxes:
    - `ads_read`
    - `ads_management`
    - `business_management`
    - `pages_read_engagement`
- Click "Submit"
- You now have a short-lived token (only lasts 1 hour). We need a **long-lived** one (lasts 60 days):
  - Next to "Access Token," click the little "i" in a circle
  - Click **"Open in Access Token Tool"**
  - Click the blue **"Extend Token"** button
  - Copy the new long code that appears

### Step 6: Tell AdCrewOS your codes
In Termux, type this:

```
adcrewos config credentials \
  --meta-app-id 123456789012345 \
  --meta-app-secret abcdef123456secret \
  --meta-access-token EAAxxx...verylongtoken...
```

Check: `adcrewos status` — should show ✓ next to Meta Ads.

---

## 📧 Email Setup (for Anomaly Alerts)
*What this does: lets AdCrewOS email you when something goes wrong with your ads.*

### Option A: Gmail (easiest, free)

**Step 1: Make a Gmail App Password**
- Go to https://myaccount.google.com
- Click **"Security"** on the left
- Turn on **"2-Step Verification"** if it's not already on (you need this for app passwords)
- After turning it on, go back to Security → scroll down to **"App passwords"** and click it
- At the bottom, click the dropdown that says "Select app" → choose **"Other (Custom name)"**
- Type **"AdCrewOS"** and click "Generate"
- A yellow box appears with a **16-character password** (looks like `abcd efgh ijkl mnop`). **Copy it right now** — you won't see it again.
- The spaces in it are fine, type them as-is.

**Step 2: Decide who should get alert emails**
- Pick one or more email addresses. Could be your own Gmail, could be a team member's.

**Step 3: Tell AdCrewOS**
In Termux:

```
adcrewos alerts config email \
  --smtp-server smtp.gmail.com \
  --smtp-port 587 \
  --username yourname@gmail.com \
  --password "abcd efgh ijkl mnop" \
  --to you@gmail.com
```

If you want to send to multiple people, add more `--to` flags:
```
  --to you@gmail.com --to partner@gmail.com
```

Check: `adcrewos status` — should show ✓ ready next to Email.

---

### Option B: Other email providers
If you use Outlook, Yahoo, or a custom business email, the codes are slightly different:

| Provider | SMTP Server | SMTP Port | Password Type |
|----------|-------------|-----------|---------------|
| Outlook / Hotmail | `smtp-mail.outlook.com` | 587 | Your normal password (or app password if 2FA is on) |
| Yahoo Mail | `smtp.mail.yahoo.com` | 587 | App password (from Yahoo security settings) |
| SendGrid (business) | `smtp.sendgrid.net` | 587 | SendGrid API key |
| Mailgun (business) | `smtp.mailgun.org` | 587 | Mailgun SMTP password |

Same command format, just change the server:

```
adcrewos alerts config email \
  --smtp-server smtp-mail.outlook.com \
  --smtp-port 587 \
  --username you@outlook.com \
  --password "your-app-password" \
  --to you@outlook.com
```

---

## 📱 SMS Setup (Twilio — Text Message Alerts)
*What this does: sends a text to your phone when something urgent happens with your ads.*

### Step 1: Create a Twilio Account
- Go to https://twilio.com
- Click **"Sign up"** (top right)
- Enter your email, password, and full name
- Verify your phone number (they'll text you a code)
- They'll ask you a few questions — you can skip or answer quickly

### Step 2: Get a Phone Number
- After signup, Twilio asks "Get a phone number to start" — click **"Get my first Twilio phone number"**
- They'll show you a number. Click **"Choose this number"**
- **Cost:** About $1/month for the number, plus about $0.0079 per text sent ($0.79 for 100 texts)

### Step 3: Find your Account SID and Auth Token
- On your Twilio dashboard (console.twilio.com), look for a box that says **"Account SID"** and **"Auth Token"**
- **Account SID** — starts with `AC` followed by 32 letters/numbers
- **Auth Token** — long secret code. Click the eye icon 👁 to see it
- Copy both and save them

### Step 4: Know your Personal Phone Number
- The number where you want to receive alert texts
- Include the country code: US numbers start with `+1`, UK with `+44`, etc.
- Example: `+15551234567`

### Step 5: Tell AdCrewOS
In Termux:

```
adcrewos alerts config sms \
  --account-sid ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --auth-token xxxxxxxxxxxxxxxxxxxxxxxxxx \
  --from-number +15551234567 \
  --to +15557654321
```

Where `--from-number` is the Twilio number you bought, and `--to` is your personal phone.

Check: `adcrewos status` — should show ✓ ready next to SMS.

---

## ✅ How to Check Everything

At any time, run:

```
adcrewos status
```

You'll see:

```
AdCrewOS v0.2.0

Platform Credentials:
  Google Ads:      ✓
  Meta Ads:        ✓

Alert Channels:
  Email:           ✓ ready
  SMS:             ✓ ready
```

If something shows ✗, go back to that section and follow the steps again.

---

## 🚀 Test It Out

Once you have at least Google or Meta set up, run:

```
adcrewos monitor --days 7
```

This fetches your actual campaign data and shows a table. If you see numbers, it's working!

Run:

```
adcrewos anomalies --days 14
```

This scans for anything unusual in your last 2 weeks of data.

Run:

```
adcrewos alerts send --dry-run
```

This shows what alerts *would* be sent (without actually sending). Remove `--dry-run` when you're ready for real alerts.

---

## ❓ Help

For any command:

```
adcrewos COMMAND --help
```

Example: `adcrewos alerts config email --help`

---

## 📁 Where Things Are Saved

- Your API tokens live at: `~/.adcrewos/credentials.json`
- Alert settings live at: `~/.adcrewos/alerts.json`
- Generated reports go to: `~/.adcrewos/reports/`
- These files never leave your phone