# build_msi.ps1
# Builds a full MSI installer for Pacer + mylang using WiX Toolset v5.
#
# Steps:
#   1. Verify .NET SDK is present (needed by WiX MSBuild SDK)
#   2. Run build_exe.ps1 if dist\Pacer.exe does not already exist
#   3. Stage dist\Pacer.exe + docs into installer\payload\
#   4. Convert pacer_logo.png to pacer_logo.ico for installer shortcuts
#   5. Bundle mylang-vscode\ if present; offer VS Code install if detected
#   6. dotnet restore + dotnet build -> Pacer-Setup.msi
#
# Usage:
#   .\build_msi.ps1
#
# Requirements:
#   .NET SDK 6.0 or later  ->  https://dotnet.microsoft.com/download
#   (WiX itself is restored automatically via NuGet on first build)

$ErrorActionPreference = "Stop"

$ProjectRoot  = $PSScriptRoot
$InstallerDir = Join-Path $ProjectRoot "installer"
$DistDir      = Join-Path $ProjectRoot "dist"
$AppName      = "Pacer"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Pacer + mylang  -  MSI Installer Build"   -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ----------------------------------------------------------------------------
# 1. Verify .NET SDK
# ----------------------------------------------------------------------------
Write-Host "[1/6] Checking for .NET SDK..." -ForegroundColor Cyan

$dotnetVersion = $null
try { $dotnetVersion = (dotnet --version 2>$null) } catch {}

if (-not $dotnetVersion) {
    throw ("The .NET SDK was not found.`n" +
           "WiX Toolset v5 builds via the .NET SDK MSBuild.`n" +
           "Download from: https://dotnet.microsoft.com/download`n" +
           "Any version 6.0 or later works.")
}
Write-Host "      Found .NET SDK $dotnetVersion" -ForegroundColor Green

# ----------------------------------------------------------------------------
# 2. Ensure dist\Pacer.exe exists
# ----------------------------------------------------------------------------
Write-Host ""
Write-Host "[2/6] Checking for built executable..." -ForegroundColor Cyan

$exePath = Join-Path $DistDir "$AppName.exe"

if (-not (Test-Path $exePath)) {
    Write-Host "      dist\$AppName.exe not found -- running build_exe.ps1 first..." -ForegroundColor Yellow
    $buildExeScript = Join-Path $ProjectRoot "build_exe.ps1"
    if (-not (Test-Path $buildExeScript)) {
        throw "build_exe.ps1 not found in $ProjectRoot"
    }
    & $buildExeScript
    if ($LASTEXITCODE -ne 0) { throw "build_exe.ps1 failed. See errors above." }
    if (-not (Test-Path $exePath)) {
        throw "build_exe.ps1 completed but dist\$AppName.exe was still not found."
    }
} else {
    Write-Host "      Found $exePath" -ForegroundColor Green
}

# ----------------------------------------------------------------------------
# 3. Stage installer payload
# ----------------------------------------------------------------------------
Write-Host ""
Write-Host "[3/6] Staging installer payload..." -ForegroundColor Cyan

$PayloadDir = Join-Path $InstallerDir "payload"
if (Test-Path $PayloadDir) {
    Remove-Item -Recurse -Force $PayloadDir
}
New-Item -ItemType Directory -Path $PayloadDir | Out-Null

Copy-Item $exePath -Destination $PayloadDir
Write-Host "      Copied $AppName.exe" -ForegroundColor Green

foreach ($doc in @("MYLANG_DOCS.md", "README.md")) {
    $src = Join-Path $ProjectRoot $doc
    if (Test-Path $src) {
        Copy-Item $src -Destination $PayloadDir
        Write-Host "      Copied $doc" -ForegroundColor Green
    }
}

# ----------------------------------------------------------------------------
# 4. Prepare installer icon
# ----------------------------------------------------------------------------
Write-Host ""
Write-Host "[4/6] Preparing installer icon..." -ForegroundColor Cyan

$logoPng = Join-Path $ProjectRoot "pacer_logo.png"
$logoIco = Join-Path $InstallerDir "pacer_logo.ico"

if (Test-Path $logoIco) {
    Write-Host "      Using existing installer\pacer_logo.ico" -ForegroundColor Green
} elseif (Test-Path $logoPng) {
    Write-Host "      Converting pacer_logo.png -> pacer_logo.ico ..." -ForegroundColor Yellow
    Add-Type -AssemblyName System.Drawing
    $bitmap     = [System.Drawing.Bitmap]::FromFile($logoPng)
    $iconHandle = $bitmap.GetHicon()
    $icon       = [System.Drawing.Icon]::FromHandle($iconHandle)
    $stream     = [System.IO.File]::Create($logoIco)
    $icon.Save($stream)
    $stream.Close()
    $bitmap.Dispose()
    Write-Host "      Created installer\pacer_logo.ico" -ForegroundColor Green
} else {
    throw ("pacer_logo.png not found in $ProjectRoot and installer\pacer_logo.ico does not exist.`n" +
           "Place pacer_logo.png next to build_msi.ps1, or drop your own pacer_logo.ico into the installer\ folder.")
}

# ----------------------------------------------------------------------------
# 5. Bundle mylang VS Code extension (optional)
# ----------------------------------------------------------------------------
Write-Host ""
Write-Host "[5/6] Checking for mylang VS Code extension..." -ForegroundColor Cyan

$VscodeExtDir  = Join-Path $ProjectRoot "mylang-vscode"
$VscodeStaged  = $false

if (Test-Path $VscodeExtDir) {
    $VscodePayload = Join-Path $PayloadDir "mylang-vscode"
    Copy-Item -Recurse $VscodeExtDir -Destination $VscodePayload
    $VscodeStaged = $true
    Write-Host "      Bundled mylang-vscode\ into installer payload." -ForegroundColor Green

    $codeCmd = Get-Command code -ErrorAction SilentlyContinue
    if ($codeCmd) {
        Write-Host "      VS Code is installed on this machine." -ForegroundColor Yellow
        $reply = Read-Host "      Install the mylang extension into VS Code right now? (y/N)"
        if ($reply -ieq "y") {
            $target = Join-Path $env:USERPROFILE ".vscode\extensions\mylang-vscode"
            if (Test-Path $target) { Remove-Item -Recurse -Force $target }
            Copy-Item -Recurse $VscodeExtDir -Destination $target
            Write-Host "      Installed to $target -- reload VS Code to activate." -ForegroundColor Green
        }
    }
} else {
    Write-Host "      mylang-vscode\ not found -- skipping (MSI will still install Pacer)." -ForegroundColor Yellow
}

# ----------------------------------------------------------------------------
# 6. Build the MSI
# ----------------------------------------------------------------------------
Write-Host ""
Write-Host "[6/6] Building Pacer-Setup.msi..." -ForegroundColor Cyan

Push-Location $InstallerDir
try {
    Write-Host "      Restoring WiX NuGet packages (first run may take ~20s) ..." -ForegroundColor Cyan
    dotnet restore Pacer.wixproj
    if ($LASTEXITCODE -ne 0) { throw "dotnet restore failed. See errors above." }

    Write-Host "      Compiling MSI ..." -ForegroundColor Cyan
    dotnet build Pacer.wixproj -c Release
    if ($LASTEXITCODE -ne 0) { throw "MSI build failed. See errors above." }
} finally {
    Pop-Location
}

# ----------------------------------------------------------------------------
# Done
# ----------------------------------------------------------------------------
$msiFile = Get-ChildItem -Path $InstallerDir -Filter "Pacer-Setup.msi" -Recurse |
           Select-Object -First 1

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  SUCCESS!" -ForegroundColor Green

if ($msiFile) {
    Write-Host "  MSI: $($msiFile.FullName)" -ForegroundColor Green
} else {
    Write-Host "  Check installer\bin\Release\ for Pacer-Setup.msi" -ForegroundColor Yellow
}

if ($VscodeStaged) {
    Write-Host "  VS Code extension: bundled inside the installer" -ForegroundColor Green
}

Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Double-click the MSI to install Pacer with:" -ForegroundColor Cyan
Write-Host "  - Start Menu shortcut" -ForegroundColor Cyan
Write-Host "  - Desktop shortcut" -ForegroundColor Cyan
Write-Host "  - Entry in Add/Remove Programs with a working uninstaller" -ForegroundColor Cyan
Write-Host ""
