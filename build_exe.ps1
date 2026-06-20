# build_exe.ps1
# Packages Pacer + mylang into a standalone Windows executable using PyInstaller.
# Run from the project root (where Pacer_mylang.py and requirements.txt live).
#
# Usage:
#   .\build_exe.ps1

# Exit script on first error
$ErrorActionPreference = "Stop"

# Define variables
$EntryPoint = "Pacer_mylang.py"   # Pacer's main entry point
$AppName    = "Pacer"             # Desired name of your final executable (.exe)

# Remove any leftover venv from a previous failed run before starting fresh
if (Test-Path "venv_build") {
    Write-Host "Removing leftover venv_build from a previous run..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .\venv_build
}

# Remove any leftover .spec file, dist/, or build/ from a previous run.
# PyInstaller reuses an existing .spec file's baked-in paths if one is present,
# which silently overrides the --add-data flags below — so a stale .spec from
# an earlier failed attempt can break later builds even after a clean venv.
foreach ($leftover in @(".\dist", ".\build", ".\$AppName.spec")) {
    if (Test-Path $leftover) {
        Write-Host "Removing leftover build artifact: $leftover" -ForegroundColor Yellow
        Remove-Item -Recurse -Force $leftover
    }
}

Write-Host "Creating clean virtual environment..." -ForegroundColor Cyan
python -m venv venv_build
if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment." }
.\venv_build\Scripts\Activate.ps1

Write-Host "Upgrading pip and installing project dependencies..." -ForegroundColor Cyan
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Failed to upgrade pip." }

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "pip install -r requirements.txt failed. See errors above." }
} else {
    Write-Host "Warning: requirements.txt not found. Installing only PyInstaller." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) { throw "Failed to install PyInstaller." }
}

Write-Host "Building standalone Windows executable..." -ForegroundColor Cyan

# Pre-flight check: confirm every --add-data source actually exists before
# invoking PyInstaller, so failures are reported clearly up front instead of
# surfacing as a cryptic "Unable to find ... when adding binary and data files."
$requiredPaths = @("mylang", "MYLANG_DOCS.md", "pacer_logo.png", $EntryPoint)
foreach ($p in $requiredPaths) {
    if (-not (Test-Path $p)) {
        throw "Required file/folder not found: $p (expected in $(Get-Location))"
    }
}

# --onefile:     Bundles everything into a single .exe
# --name:        Names the output file
# --clean:       Cleans PyInstaller cache before building
# --noconsole:   Pacer is a GUI app — suppress the console window
# --add-data:    Bundle the mylang/ engine and docs alongside the exe
#                (Windows uses ';' as the source;dest separator)
pyinstaller --onefile --name="$AppName" --clean --noconsole `
    --add-data "mylang;mylang" `
    --add-data "MYLANG_DOCS.md;." `
    --add-data "pacer_logo.png;." `
    "$EntryPoint"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed. See errors above." }

Write-Host "Cleaning up virtual environment and build folders..." -ForegroundColor Cyan
deactivate
Remove-Item -Recurse -Force .\venv_build
Remove-Item -Recurse -Force .\build
Remove-Item -Force ".\$AppName.spec"

Write-Host "SUCCESS! Your executable is available in the 'dist' directory." -ForegroundColor Green
Get-ChildItem .\dist\
