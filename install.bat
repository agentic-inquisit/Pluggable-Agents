@echo off
rem Double-click entry point - runs setup.ps1 without ever hitting
rem PowerShell's execution-policy prompt/error. All real logic lives in
rem setup.ps1; this just launches it safely.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
pause
