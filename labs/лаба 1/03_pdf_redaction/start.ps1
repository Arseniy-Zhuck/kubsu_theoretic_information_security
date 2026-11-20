$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"
if (!(Test-Path $python)) { Write-Error "Run setup.cmd first."; exit 1 }
& $python create_pdf.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Open data/document.pdf in your browser. Then run extract.cmd."
Start-Process (Join-Path $PSScriptRoot "data/document.pdf")
