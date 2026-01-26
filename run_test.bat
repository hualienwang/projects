@echo off
chcp 65001 > nul
echo ========================================
echo Dashboard API Test Tool
echo ========================================
echo.
powershell -ExecutionPolicy Bypass -NoProfile -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $OutputEncoding = [System.Text.Encoding]::UTF8; & '%~dp0test_dashboard_api.ps1'"
echo.
echo Test completed!
pause
