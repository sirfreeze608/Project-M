@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

:: ── Try pythonw first (no console window) ────────────────────────────────────
where pythonw >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "" pythonw Pacer_mylang.pyw
    exit /b 0
)

:: ── pythonw not on PATH — find it next to python.exe ─────────────────────────
for /f "delims=" %%i in ('where python 2^>nul') do (
    set "PYDIR=%%~dpi"
    if exist "!PYDIR!pythonw.exe" (
        start "" "!PYDIR!pythonw.exe" "%~dp0Pacer_mylang.pyw"
        exit /b 0
    )
)

:: ── Last resort: use python (will show a console window briefly) ──────────────
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] pythonw.exe not found - launching with python.exe instead.
    echo        A console window will appear. Run fix_pyw_association.bat to fix this.
    python Pacer_mylang.pyw
    exit /b 0
)

:: ── Python not installed at all ───────────────────────────────────────────────
echo [ERROR] Python is not installed or not on PATH.
echo         Download Python from: https://python.org
echo         Make sure to tick "Add Python to PATH" during install.
pause
exit /b 1
