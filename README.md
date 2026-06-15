# SignalWire Automation — Cookies Only

**Ghir cookies. Bla email. Bla password.**

Double-click **`run.bat`** → browser ytftah → account yconnecta → billing page → form.

## Quick start

1. Download branch: https://github.com/davvidx9/DAVIDV2/tree/cursor/signalwire-form-fill-eb58
2. Paste your session cookies in **`cookies.json`**
3. Double-click **`run.bat`**

## What you edit

| File | Edit? |
|------|-------|
| **`cookies.json`** | **YES** — paste cookies hna |
| `config.json` | No (auto-created, URLs pre-configured) |
| `run.bat` | No — just double-click |

## Flow

```
run.bat
  → install deps + Chromium
  → load cookies.json
  → open browser
  → restore session (cookies)
  → go to payment_methods/new
  → fill form
  → wait for ENTER
```

## Guides

- [KIFACH_NTESTI.md](KIFACH_NTESTI.md) — Darija
- [COOKIES_HNA.md](COOKIES_HNA.md) — kifach tjib cookies

## GitHub

- Branch: https://github.com/davvidx9/DAVIDV2/tree/cursor/signalwire-form-fill-eb58
- PR: https://github.com/davvidx9/DAVIDV2/pull/9
