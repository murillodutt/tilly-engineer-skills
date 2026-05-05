param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $InstallerArgs
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($null -ne $Python) {
  & $Python.Source -c "import sys; raise SystemExit(0 if sys.version_info[0] >= 3 else 1)"
  if ($LASTEXITCODE -eq 0) {
    & $Python.Source "$ScriptDir/scripts/install_adapter.py" @InstallerArgs
    exit $LASTEXITCODE
  }
}

$Py = Get-Command py -ErrorAction SilentlyContinue
if ($null -ne $Py) {
  & $Py.Source -3 "$ScriptDir/scripts/install_adapter.py" @InstallerArgs
  exit $LASTEXITCODE
}

Write-Error "Python 3 is required to run the Tilly installer."
exit 1
