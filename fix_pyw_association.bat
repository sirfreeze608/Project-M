@echo off
setlocal EnableDelayedExpansion
echo.
echo ============================================
echo   Fix .pyw File Association
echo   Links .pyw files to pythonw.exe so
echo   double-clicking them shows no console.
echo ============================================
echo.

:: ── Find pythonw.exe ──────────────────────────────────────────────────────────
set "PYTHONW="

:: Check if pythonw is already on PATH
for /f "delims=" %%i in ('where pythonw 2^>nul') do (
    if not defined PYTHONW set "PYTHONW=%%i"
)

:: If not on PATH, look next to python.exe
if not defined PYTHONW (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        set "PYDIR=%%~dpi"
        if exist "!PYDIR!pythonw.exe" (
            set "PYTHONW=!PYDIR!pythonw.exe"
        )
    )
)

:: Check common install locations
if not defined PYTHONW (
    for %%p in (
        "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe"
        "C:\Python312\pythonw.exe"
        "C:\Python311\pythonw.exe"
        "C:\Python310\pythonw.exe"
        "C:\Program Files\Python312\pythonw.exe"
        "C:\Program Files\Python311\pythonw.exe"
        "C:\Program Files\Python310\pythonw.exe"
    ) do (
        if not defined PYTHONW (
            if exist %%p set "PYTHONW=%%~p"
        )
    )
)

if not defined PYTHONW (
    echo [ERROR] pythonw.exe not found on this machine.
    echo         Install Python from https://python.org
    echo         Then re-run this script.
    pause
    exit /b 1
)

echo [OK] Found pythonw.exe at: %PYTHONW%
echo.

:: ── Register the .pyw file association ───────────────────────────────────────
echo Registering .pyw file association...

:: File type definition
reg add "HKCU\Software\Classes\.pyw" /ve /d "Python.NoConFile" /f >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Could not write to registry. Try running as Administrator.
    pause
    exit /b 1
)

:: Open command using pythonw.exe
reg add "HKCU\Software\Classes\Python.NoConFile\shell\open\command" ^
    /ve /d "\"!PYTHONW!\" \"%%1\" %%*" /f >nul 2>&1

:: Icon (use pythonw.exe icon)
reg add "HKCU\Software\Classes\Python.NoConFile\DefaultIcon" ^
    /ve /d "\"!PYTHONW!\",0" /f >nul 2>&1

:: Tell Windows Explorer the association changed
ie4uinit.exe -show >nul 2>&1
ftype Python.NoConFile="!PYTHONW!" "%%1" %%* >nul 2>&1

echo.
echo ============================================
echo   Done!
echo.
echo   .pyw files are now linked to:
echo   %PYTHONW%
echo.
echo   Double-clicking any .pyw file will now
echo   launch it with NO console window.
echo ============================================
echo.
pause
