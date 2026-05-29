"""
Main entry — starts Telegram bot + ARI (SIP).

Usage (from WORKING folder):
  pip install -r requirements.txt
  copy .env.example .env   # then edit .env
  python run.py

Docker (recommended on Windows):
  START_WINDOWS.bat
"""

from telegram_bot import main

if __name__ == "__main__":
    main()
