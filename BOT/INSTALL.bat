@echo off
cd /d "%~dp0"
echo === BOT SIP IVR Install ===
if not exist .env (
  copy /Y .env.example .env
  echo Created .env - EDIT TELEGRAM_BOT_TOKEN now!
  notepad .env
  pause
)
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
python check_env.py
echo.
echo If OK: python run.py
pause
