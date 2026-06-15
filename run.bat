@echo off
chcp 65001 >nul
title SignalWire Automation
cd /d "%~dp0"

echo.
echo ============================================================
echo   SignalWire - Run Automation (double-click)
echo ============================================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python ma kaynach. Installi Python 3.10+ mn python.org
    echo         https://www.python.org/downloads/
    echo         W activi "Add Python to PATH" f install.
    pause
    exit /b 1
)

echo [1/5] Installing Python packages...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Pip install failed.
    pause
    exit /b 1
)

echo [2/5] Installing Chromium browser (Playwright)...
python -m playwright install chromium
if errorlevel 1 (
    echo [ERROR] Playwright install failed.
    pause
    exit /b 1
)

echo [3/5] Preparing config files...
if not exist "config.json" (
    copy /Y "config.json.example" "config.json" >nul
    echo        Created config.json - 3mer email/password dyalek fih!
)

if not exist "cookies.json" (
    if exist "cookies.template.json" (
        copy /Y "cookies.template.json" "cookies.json" >nul
    )
)

echo [4/5] Launching browser automation...
echo.
python fill_payment_form.py
set EXIT_CODE=%ERRORLEVEL%

echo.
echo [5/5] Done. Exit code: %EXIT_CODE%
echo.
if %EXIT_CODE% neq 0 (
    echo Chi haja ma mchatch. Chouf automation.log w screenshots\
)

pause
exit /b %EXIT_CODE%
