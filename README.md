# SignalWire Payment Form Automation

Async Playwright script that restores a SignalWire session from cookies and fills the payment method form.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Configuration

1. Copy `cookies.json.example` to `cookies.json` and paste your authenticated session cookies.
2. Copy `config.json.example` to `config.json` and update form values.

## Run

```bash
python fill_payment_form.py
```

## Behavior

- Launches Chromium and imports cookies before navigation
- Verifies login session; stops with error screenshot if invalid
- Navigates to `/payment_methods/new`
- Auto-detects and fills name, billing address, city, country, and payment fields
- Handles payment iframes (Stripe-style)
- Logs every step to console and `automation.log`
- Saves screenshots in `screenshots/` on errors
- Keeps browser open until you press ENTER
