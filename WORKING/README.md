# SIP IVR Platform

Legitimate **Flask + Telegram + MongoDB + Asterisk (PJSIP + ARI)** starter for outbound IVR on **your own SIP trunk**.

This is **not** a copy of fraud/OTP bots. It intentionally:

- Uses **your** `CALLER_ID_NUMBER` (no caller-ID spoofing)
- Uses **neutral** prompts (reference numbers, not “fraud prevention OTP”)
- Does **not** implement Accept/Deny loops to validate stolen codes with callees
- Does **not** post captured digits to public “OTP” channels

## Structure

```
sip-ivr-platform/
  telegram_bot.py      # Telegram commands (/call, /recall, …)
  api.py               # Flask health + ARI init
  sip_call_manager.py  # ARI WebSocket + originate/playback/DTMF/record
  call_flows.py        # IVR logic per route (voice, pin, bank, custom, …)
  tts.py               # gTTS / pyttsx3 → Asterisk sounds
  db.py                # MongoDB
  asterisk/            # pjsip.conf, extensions.conf, ari.conf
  docker-compose.yml
  docs/WINDOWS.md
  docs/LINUX.md
```

## Quick start

```bash
cp .env.example .env
# Edit .env and asterisk/pjsip.conf
docker compose up -d --build
```

Telegram: `/genkey` (admin) → `/redeem` → `/call <number> <company> <name> <digits>`

## Routes (compatibility names)

| Route | Purpose |
|-------|---------|
| `voice` | Generic 2-step IVR |
| `pin` | Same with PIN wording |
| `bank` | Uses bank name as company label |
| `email` | Recorded message flow |
| `custom` | 3-part script from MongoDB |

Legacy Flask paths like `/voice/...` return **410** — use ARI instead of Telnyx webhooks.

## Environment

See `.env.example` for `SIP_*`, `ARI_*`, `MONGO_URI`, `TELEGRAM_BOT_TOKEN`, `NGROK_URL`.

## License / use

For lawful IVR and systems you are authorized to operate. You are responsible for compliance with telecom and privacy laws.
