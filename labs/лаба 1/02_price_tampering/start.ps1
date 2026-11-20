$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"
if (!(Test-Path $python)) {
    Write-Error "Run setup.cmd first."
    exit 1
}
Write-Host "Open http://127.0.0.1:5051 in your browser. Stop: Ctrl+C."
& $python app.py
exit $LASTEXITCODE
