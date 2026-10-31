# Pluggable Agents / anime-companion automation layer — Windows setup
# Run from PowerShell in the repo root: .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Checking Python ===" -ForegroundColor Cyan
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python not found on PATH. Install Python 3.12+ from python.org first."
    exit 1
}

Write-Host "=== Creating virtual environment (.venv) ===" -ForegroundColor Cyan
python -m venv .venv

Write-Host "=== Activating virtual environment ===" -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

Write-Host "=== Upgrading pip ===" -ForegroundColor Cyan
python -m pip install --upgrade pip

Write-Host "=== Installing requirements.txt ===" -ForegroundColor Cyan
python -m pip install -r requirements.txt

Write-Host "=== Smoke test: import automation driver (Windows-only guard + pyautogui/pygetwindow) ===" -ForegroundColor Cyan
python -c "from src.automation import AutomationDriver; from src.automation.driver import list_open_windows; print('Import OK. Open windows:'); [print(' -', t) for t in list_open_windows()]"

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "Next: pick an exact title from the list above and construct:"
Write-Host "  driver = AutomationDriver(app_title='<exact title from the list>')"
Write-Host "  driver.attach_or_launch()"
