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

### Cookies dyal account (IMPORTANT)

**Blasa:** `cookies.json` — f nafs dossier dyal script.

Talimt kamla b Darija: **[COOKIES_HNA.md](COOKIES_HNA.md)**

```bash
# Ila cookies.json ma kaynach, script kaycreyih automatiquement
# Men ba3d, fta7 cookies.json w paste cookies dyalek f "value"
```

1. Connecté f `https://us11111111.signalwire.com` f Chrome
2. F12 → Application → Cookies
3. Copier cookies → paste f **`cookies.json`**
4. Copy `config.json.example` to `config.json` and update form values

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
