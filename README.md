# SignalWire Automation

## Files mohimmin

| File | Ash dir |
|------|---------|
| `run.bat` | Test browser + cookies (double-click) |
| `run_bot.bat` | Lancer Telegram bot (double-click) |
| `cookies.json` | **Paste cookies hna** |
| `bot_config.json` | Token Telegram (@BotFather) |
| `config.json` | Auto-created men `config.json.example` |

## Setup (marra wa7da)

1. **Python 3.10+** installé
2. Paste cookies f `cookies.json`
3. Bot: copy `bot_config.json.example` → `bot_config.json` + token

## run.bat

Double-click → install auto → browser → cookies → payment page

## run_bot.bat

Double-click → bot ytlauncha → sift f Telegram:

```
/chk card: 5294153155207609
month: 4
year: 2027
cvc2: 896
```

- **Lmarra l-ula:** tab jdid + login cookies
- **Jaya:** nfs tab, redirect ghir l payment page

## Billing (dima fix)

- name: david alaba
- address: New York
- city: New York
- country: United States
- postal: 10080

## Cookies format

```json
[
  {
    "name": "cookie_name",
    "value": "VALUE_HNA",
    "domain": ".signalwire.com",
    "path": "/"
  }
]
```

## GitHub

https://github.com/davvidx9/DAVIDV2/tree/cursor/signalwire-form-fill-eb58
