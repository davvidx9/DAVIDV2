# Windows setup (Docker Desktop)

## Prerequisites

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL2 backend
2. [ngrok](https://ngrok.com/) (optional — only if you need public HTTP to Flask `/health`)
3. SIP account from your provider (username, password, domain)

## Steps

1. Copy `.env.example` to `.env` and fill values.
2. Edit `asterisk/pjsip.conf` with your SIP provider host, user, and password.
3. Set `CALLER_ID_NUMBER` to the number your provider allows (client number).
4. From PowerShell in `sip-ivr-platform`:

```powershell
docker compose up -d --build
```

5. Open Telegram → `/start` → `/redeem` with a key from admin `/genkey`.
6. Test call:

```
/call 12025551234 MyCompany John 4
```

## Notes

- **No spoof:** outbound caller ID comes from `CALLER_ID_NUMBER` and your trunk — configure only numbers you own.
- Telephony events use **ARI WebSocket**, not Telnyx HTTP webhooks.
- Sounds: generated under `sounds/ivr_custom/` (mounted into Asterisk).
- If audio fails, install `ffmpeg` in the container (already in Dockerfile) and check Asterisk logs:

```powershell
docker compose logs -f asterisk
```

## WebRTC (optional)

For browser SIP you need additional Asterisk `pjsip.conf` WebRTC endpoints and TLS — not included in this starter; use a softphone or trunk for first tests.

## Run bot without Docker

1. Install Python 3.11, MongoDB, Asterisk 20 on WSL2.
2. Copy Asterisk configs into `/etc/asterisk/`.
3. `pip install -r requirements.txt`
4. `python telegram_bot.py`
