param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $InstallerArgs
)

$ErrorActionPreference = "Stop"
$BootstrapDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path (Join-Path $BootstrapDir "..\..")).Path

$Python = Get-Command python -ErrorAction SilentlyContinue
if ($null -ne $Python) {
  & $Python.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
  if ($LASTEXITCODE -eq 0) {
    & $Python.Source (Join-Path $RepoRoot "scripts\install_adapter.py") @InstallerArgs
    exit $LASTEXITCODE
  }
}

$Py = Get-Command py -ErrorAction SilentlyContinue
if ($null -ne $Py) {
  & $Py.Source -3.11 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
  if ($LASTEXITCODE -eq 0) {
    & $Py.Source -3.11 (Join-Path $RepoRoot "scripts\install_adapter.py") @InstallerArgs
    exit $LASTEXITCODE
  }
}

Write-Error "Python 3.11+ is required to run the Tilly installer."
exit 1
