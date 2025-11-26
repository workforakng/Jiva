@echo off
echo [*] Stopping Jiva Health services...

taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo [OK] All services stopped
pause
