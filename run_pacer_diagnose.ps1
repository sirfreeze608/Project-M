Param(
	[string]$ProjectRoot = $PSScriptRoot
)

# Ensure we're running from the project root (defaults to script folder)
if (-not $ProjectRoot) { $ProjectRoot = (Split-Path -Parent $MyInvocation.MyCommand.Definition) }
Set-Location -Path $ProjectRoot

$traceFile = Join-Path $ProjectRoot "traceback.txt"
$runLog   = Join-Path $ProjectRoot "run_log.txt"
$pythonInfo = Join-Path $ProjectRoot "python_info.txt"

# Clean old outputs
Remove-Item -Force -ErrorAction SilentlyContinue $traceFile, $runLog, $pythonInfo

# Locate python (try python then py)
$pythonCmd = (Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1).Source
if (-not $pythonCmd) { $pythonCmd = (Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1).Source }
if (-not $pythonCmd) {
	Write-Host "No python executable found in PATH. Install Python or adjust PATH." -ForegroundColor Red
	exit 2
}

# Record python version & path info
& $pythonCmd --version 2>&1 | Out-File -FilePath $pythonInfo -Encoding utf8
where.exe python 2>&1 | Out-File -FilePath $pythonInfo -Append -Encoding utf8

# Run once capturing stdout/stderr to traceback.txt (non-interactive)
Write-Host "Running (captured output): $pythonCmd .\pacer_mylang.pyw"
& $pythonCmd ".\pacer_mylang.pyw" > $traceFile 2>&1
$exitCode = $LASTEXITCODE

# Run again with Start-Transcript to capture a terminal transcript
Write-Host "Running (transcript): $pythonCmd .\pacer_mylang.pyw"
Start-Transcript -Path $runLog -Force
try {
	& $pythonCmd ".\pacer_mylang.pyw"
} catch {
	Write-Error $_
}
Stop-Transcript

# Show last lines of logs for quick inspection
Write-Host "`n=== traceback.txt (last 200 lines) ==="
Get-Content $traceFile -Tail 200 -ErrorAction SilentlyContinue

Write-Host "`n=== run_log.txt (last 200 lines) ==="
Get-Content $runLog -Tail 200 -ErrorAction SilentlyContinue

Write-Host "`n=== python_info.txt ==="
Get-Content $pythonInfo -ErrorAction SilentlyContinue

Write-Host "`nExit code: $exitCode"
exit $exitCode
