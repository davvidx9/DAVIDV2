# SignalWire Payment Form Automation

**Double-click `run.bat` on Windows** — installs everything, opens browser, logs in, and goes to billing.

## Quick start (Windows)

1. Download this repo (branch `cursor/signalwire-form-fill-eb58`)
2. Edit `config.json` → put your **email** and **password**
3. Double-click **`run.bat`**
4. Browser opens → login → billing page → form filled → review → press ENTER

Full Darija guide: **[KIFACH_NTESTI.md](KIFACH_NTESTI.md)**

## What run.bat does

| Step | Action |
|------|--------|
| 1 | `pip install -r requirements.txt` |
| 2 | `playwright install chromium` |
| 3 | Create `config.json` if missing |
| 4 | Launch browser tab |
| 5 | Login with email/password |
| 6 | Navigate to `/payment_methods/new` |
| 7 | Fill billing + payment fields |
| 8 | Keep browser open until ENTER |

## Config files

| File | Purpose |
|------|---------|
| `config.json` | Email, password, form data (auto-created, **not in git**) |
| `cookies.json` | Optional — saved after login for faster next run |
| `config.json.example` | Template |

## Manual run (Linux/Mac)

```bash
pip install -r requirements.txt
python3 -m playwright install chromium
cp config.json.example config.json
# edit config.json
python fill_payment_form.py
```

## Cookies (optional)

If you prefer cookies instead of login: **[COOKIES_HNA.md](COOKIES_HNA.md)**

## GitHub

- Repo: https://github.com/davvidx9/DAVIDV2
- Branch: https://github.com/davvidx9/DAVIDV2/tree/cursor/signalwire-form-fill-eb58
- PR: https://github.com/davvidx9/DAVIDV2/pull/9
