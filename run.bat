@echo off
chcp 65001 >nul
title SignalWire Automation
cd /d "%~dp0"

echo.
echo ============================================================
echo   SignalWire - Cookies Only (double-click run.bat)
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python ma kaynach. Installi Python 3.10+ mn python.org
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Installing packages...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Pip install failed.
    pause
    exit /b 1
)

echo [2/4] Installing Chromium...
python -m playwright install chromium
if errorlevel 1 (
    echo [ERROR] Playwright install failed.
    pause
    exit /b 1
)

echo [3/4] Preparing cookies.json...
if not exist "cookies.json" (
    if exist "cookies.template.json" (
        copy /Y "cookies.template.json" "cookies.json" >nul
        echo.
        echo   IMPORTANT: Fta7 cookies.json w paste cookies dyalek!
        echo   Blasa: %cd%\cookies.json
        echo.
        pause
    )
)

if not exist "config.json" (
    copy /Y "config.json.example" "config.json" >nul
)

echo [4/4] Launching browser...
echo.
python fill_payment_form.py
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% neq 0 (
    echo Chi haja ma mchatch. Chouf cookies.json, automation.log, screenshots\
) else (
    echo Khdam! Browser closed.
)

pause
exit /b %EXIT_CODE%
