$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
  Write-Host "Python virtual environment not found at .venv. Create it first: py -3 -m venv .venv" -ForegroundColor Yellow
  exit 1
}

& .\.venv\Scripts\python.exe backend\scripts\preflight_check.py
