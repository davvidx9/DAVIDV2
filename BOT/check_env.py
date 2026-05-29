"""Run: python check_env.py — verifies .env and token (does not print full token)."""

from pathlib import Path

BASE = Path(__file__).resolve().parent
env_path = BASE / ".env"

print("Folder:", BASE)
print(".env exists:", env_path.is_file())

if not env_path.is_file():
    print("\nFIX: copy .env.example to .env")
    print("  copy .env.example .env")
    raise SystemExit(1)

try:
    from dotenv import load_dotenv

    load_dotenv(env_path)
except ImportError:
    print("\nFIX: pip install python-dotenv")
    raise SystemExit(1)

import os

token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not token:
    print("\nFIX: open .env and set:")
    print("  TELEGRAM_BOT_TOKEN=your_token_from_BotFather")
    raise SystemExit(1)

print("TELEGRAM_BOT_TOKEN: OK (length", len(token), ")")
print("Ready. Run: python run.py")
