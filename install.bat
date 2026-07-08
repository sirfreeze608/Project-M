@echo off
setlocal EnableDelayedExpansion

echo.
echo ============================================
echo   Pacer + mylang  v0.5.1  ^|  Windows Setup
echo ============================================
echo.

:: ── Check Python ──────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Download from https://python.org
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] Python %PYVER% found.

:: ── Install Python packages ───────────────────────────────────────────────────
echo.
echo [1/3] Installing Python packages...
python -m pip install --upgrade pip --quiet
python -m pip install PyQt5 anthropic --quiet
if errorlevel 1 (
    echo [ERROR] pip install failed. Check your internet connection.
    pause
    exit /b 1
)
echo [OK] Packages installed.

:: ── Install mylang CLI ────────────────────────────────────────────────────────
echo.
echo [2/3] Installing mylang CLI...
cd /d "%~dp0mylang"
python -m pip install -e . --quiet
if errorlevel 1 (
    echo [WARN] mylang CLI install had issues - you can still run via python main.py
) else (
    echo [OK] mylang CLI installed. Run: mylang yourfile.ml
)
cd /d "%~dp0"

:: ── API key setup ─────────────────────────────────────────────────────────────
echo.
echo [3/3] API Key Setup
echo.
echo To use AI features, set your Anthropic API key.
echo You can do this now, or later via Settings ^(Ctrl+,^) inside Pacer.
echo.
set /p APIKEY="Enter your Anthropic API key (or press Enter to skip): "
if not "!APIKEY!"=="" (
    setx ANTHROPIC_API_KEY "!APIKEY!" >nul 2>&1
    echo [OK] API key saved to ANTHROPIC_API_KEY environment variable.
    echo      (Restart your terminal / Pacer for it to take effect)
) else (
    echo [SKIP] No key entered. Add it later via Pacer Settings.
)

:: ── Done ──────────────────────────────────────────────────────────────────────
echo.
echo ============================================
echo   Setup complete!
echo.
echo   Launch Pacer (no console window):
echo     run_pacer.bat
echo     -- or --
echo     pythonw Pacer_mylang.pyw
echo.
echo   Run a mylang file:
echo     mylang mylang\examples\hello.ml
echo.
echo   Open the REPL:
echo     mylang --repl
echo ============================================
echo.
pause
