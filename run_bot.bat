@echo off
chcp 65001 >nul
title SignalWire Telegram Bot
cd /d "%~dp0"

echo.
echo ============================================================
echo   SignalWire Telegram Bot
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python ma kaynach.
    pause
    exit /b 1
)

echo [1/3] Installing packages...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt

echo [2/3] Installing Chromium...
python -m playwright install chromium

if not exist "bot_config.json" (
    copy /Y "bot_config.json.example" "bot_config.json" >nul
    echo.
    echo   IMPORTANT: 3mer telegram_bot_token f bot_config.json
    echo   Jib token mn @BotFather f Telegram
    echo.
    pause
)

if not exist "cookies.json" (
    echo.
    echo   IMPORTANT: cookies.json ma kaynach — paste cookies dyalek!
    echo.
    pause
)

echo [3/3] Starting Telegram bot...
python telegram_bot.py

pause
