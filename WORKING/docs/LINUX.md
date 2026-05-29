# Linux setup

Same as Windows but use native Docker:

```bash
cp .env.example .env
# edit .env and asterisk/pjsip.conf
docker compose up -d --build
docker compose logs -f app
```

## Native Asterisk (no Docker)

```bash
sudo apt install asterisk ffmpeg
sudo cp asterisk/*.conf /etc/asterisk/
sudo systemctl restart asterisk
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)
python telegram_bot.py
```

## SIP → ARI mapping (replaces Telnyx)

| Telnyx | This project |
|--------|----------------|
| `Call.create` | `AriCallManager.originate()` |
| `Call.retrieve` | Channel id from originate / StasisStart |
| `gather_using_speak` | `synthesize()` + play + DTMF events |
| `speak` | `synthesize()` + `speak_tts_file()` |
| `record_start` | `start_recording()` |
| `hangup` | `hangup()` |
| HTTP webhooks | ARI WebSocket + `call_flows.py` |
