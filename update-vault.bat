@echo off
cd /d "%~dp0"
echo Updating Tenelis vault...
git fetch origin
git reset --hard origin/master
echo.
echo Vault updated!
pause
