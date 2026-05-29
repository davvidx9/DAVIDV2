@echo off
cd /d "%~dp0"
if not exist .env (
  copy .env.example .env
  echo Created .env - edit it before calls.
)
docker compose up -d --build
echo.
echo Logs: docker compose logs -f app
pause
