"""Configuration from environment variables."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# SIP trunk / PJSIP endpoint (outbound caller ID = your client's number, no spoof)
SIP_USERNAME = os.getenv("SIP_USERNAME", "")
SIP_PASSWORD = os.getenv("SIP_PASSWORD", "")
SIP_DOMAIN = os.getenv("SIP_DOMAIN", "")
SIP_PORT = os.getenv("SIP_PORT", "5060")
SIP_TRANSPORT = os.getenv("SIP_TRANSPORT", "udp")  # udp | tcp | tls
SIP_ENDPOINT = os.getenv("SIP_ENDPOINT", "trunk")  # pjsip endpoint name in pjsip.conf
CALLER_ID_NUMBER = os.getenv("CALLER_ID_NUMBER", "")  # client's published number
CALLER_ID_NAME = os.getenv("CALLER_ID_NAME", "IVR")

# Asterisk ARI
ARI_URL = os.getenv("ARI_URL", "http://127.0.0.1:8088/ari")
ARI_USERNAME = os.getenv("ARI_USERNAME", "ivr")
ARI_PASSWORD = os.getenv("ARI_PASSWORD", "ivr_secret")
ARI_APP = os.getenv("ARI_APP", "ivr-platform")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "ivr_platform")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Public URL for optional HTTP callbacks (ngrok)
NGROK_URL = os.getenv("NGROK_URL", "").rstrip("/")

# Paths
SOUNDS_DIR = Path(os.getenv("SOUNDS_DIR", BASE_DIR / "sounds"))
RECORDINGS_DIR = Path(os.getenv("RECORDINGS_DIR", BASE_DIR / "recordings"))
SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

# Call limits
CALL_TIMEOUT_SEC = int(os.getenv("CALL_TIMEOUT_SEC", "240"))
ADMINS = [
    int(x.strip())
    for x in os.getenv("ADMINS", "").split(",")
    if x.strip().isdigit()
]

# TTS
TTS_ENGINE = os.getenv("TTS_ENGINE", "gtts")  # gtts | pyttsx3
DEFAULT_TTS_LANG = os.getenv("DEFAULT_TTS_LANG", "en")
