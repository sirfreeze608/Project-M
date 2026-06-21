@echo off
cd /d "%~dp0"

:: .pyw runs via pythonw.exe — no console window ever appears
:: pythonw is included with every standard Python install on Windows
pythonw Pacer_mylang.pyw

if errorlevel 1 (
    echo.
    echo [ERROR] Pacer failed to start.
    echo.
    echo Possible causes:
    echo   1. Python is not installed - download from https://python.org
    echo   2. Dependencies not installed - run install.bat first
    echo   3. pythonw.exe not on PATH - try: python Pacer_mylang.pyw
    echo.
    pause
)
