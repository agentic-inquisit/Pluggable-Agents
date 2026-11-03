# Pluggable Agents / anime-companion automation layer - Windows setup
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
if ($LASTEXITCODE -ne 0) { Write-Error "python -m venv .venv failed (exit $LASTEXITCODE)."; exit 1 }

Write-Host "=== Activating virtual environment ===" -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1
Write-Host "Using interpreter: $(Get-Command python | Select-Object -ExpandProperty Source)"

Write-Host "=== Upgrading pip ===" -ForegroundColor Cyan
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { Write-Error "pip upgrade failed (exit $LASTEXITCODE)."; exit 1 }

Write-Host "=== Installing requirements-automation.txt (Phase 1 only - not the full project stack) ===" -ForegroundColor Cyan
python -m pip install -r requirements-automation.txt
if ($LASTEXITCODE -ne 0) { Write-Error "pip install -r requirements-automation.txt failed (exit $LASTEXITCODE). See the pip output above for the real cause."; exit 1 }

Write-Host "=== Verifying pyautogui/pygetwindow landed in THIS venv ===" -ForegroundColor Cyan
python -m pip show pyautogui pygetwindow
if ($LASTEXITCODE -ne 0) { Write-Error "pyautogui/pygetwindow not found via pip show in this venv - install step above did not actually succeed."; exit 1 }

Write-Host "=== Smoke test: import automation driver (Windows-only guard + pyautogui/pygetwindow) ===" -ForegroundColor Cyan
python -c "from src.automation import AutomationDriver; from src.automation.driver import list_open_windows; print('Import OK. Open windows:'); [print(' -', t) for t in list_open_windows()]"
if ($LASTEXITCODE -ne 0) { Write-Error "Smoke test failed (exit $LASTEXITCODE)."; exit 1 }

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "Next: pick an exact title from the list above and construct:"
Write-Host "  driver = AutomationDriver(app_title='<exact title from the list>')"
Write-Host "  driver.attach_or_launch()"
