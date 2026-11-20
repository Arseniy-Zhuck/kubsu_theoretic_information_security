$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
try {
    if ([Environment]::OSVersion.Version.Major -lt 10) { throw "Windows 10/11 required." }
    $runtime = Join-Path $PSScriptRoot ".runtime"
    $python = Join-Path $runtime "python/python.exe"
    New-Item -ItemType Directory -Force $runtime | Out-Null
    if (!(Test-Path $python)) {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $arch = if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64" -or $env:PROCESSOR_ARCHITEW6432 -eq "ARM64") { "arm64" } elseif ([Environment]::Is64BitOperatingSystem) { "amd64" } else { "win32" }
        $suffix = if ($arch -eq "win32") { "" } else { "-$arch" }
        $installer = Join-Path $runtime "python-installer.exe"
        Write-Host "Downloading Python from python.org..."
        Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/3.13.17/python-3.13.17$suffix.exe" -OutFile $installer -TimeoutSec 180
        $sig = Get-AuthenticodeSignature $installer
        if ($sig.Status -ne "Valid" -or $sig.SignerCertificate.Subject -notmatch "Python Software Foundation") {
            throw "Python installer signature verification failed."
        }
        $target = Join-Path $runtime "python"
        $arguments = '/quiet InstallAllUsers=0 Include_pip=1 Include_launcher=0 Include_test=0 Include_doc=0 Include_tcltk=0 Shortcuts=0 AssociateFiles=0 PrependPath=0 TargetDir="' + $target + '"'
        Write-Host "Installing private Python (no administrator rights required)..."
        $process = Start-Process -FilePath $installer -ArgumentList $arguments -Wait -PassThru
        if ($process.ExitCode -notin @(0,3010)) { throw "Python installer exit code: $($process.ExitCode)" }
        if (!(Test-Path $python)) { throw "Python installation not found." }
        Remove-Item $installer
    }
    & $python -m venv --clear .venv
    if ($LASTEXITCODE -ne 0) { throw "Cannot create virtual environment." }
    $venv = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"
    & $venv -m pip install --disable-pip-version-check -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
    & $venv -m unittest -v
    if ($LASTEXITCODE -ne 0) { throw "Self-test failed." }
    Write-Host "Ready. Run start.cmd."
} catch {
    Write-Error $_
    exit 1
}
