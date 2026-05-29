# Run in PowerShell: Set-ExecutionPolicy -Scope Process Bypass; .\install.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Install Docker Desktop first: https://www.docker.com/products/docker-desktop/"
    exit 1
}

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env - fill SIP and TELEGRAM_BOT_TOKEN"
}

New-Item -ItemType Directory -Force -Path sounds, recordings | Out-Null
docker compose up -d --build
Write-Host "Done. Telegram bot: docker compose logs -f app"
