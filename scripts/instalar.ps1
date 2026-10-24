$ErrorActionPreference = "Stop"
$workspace = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $workspace ".venv\Scripts\python.exe"
$requirements = Join-Path $workspace "requirements-lock-windows.txt"
if (-not (Test-Path -LiteralPath $venvPython)) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        & $launcher.Source -3 -m venv (Join-Path $workspace ".venv")
    } else {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $python) { throw "Instalá Python 3.12 o superior y volvé a ejecutar el instalador." }
        & $python.Source -m venv (Join-Path $workspace ".venv")
    }
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el entorno Python." }
}
& $venvPython -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)"
if ($LASTEXITCODE -ne 0) { throw "Touchline requiere Python 3.12 o superior." }
& $venvPython -m pip install --disable-pip-version-check -r $requirements
if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias. Revisá tu conexión y volvé a intentar." }
& $venvPython -B (Join-Path $PSScriptRoot "diagnostico.py")
if ($LASTEXITCODE -ne 0) { throw "El diagnóstico detectó dependencias faltantes." }
& (Join-Path $PSScriptRoot "crear_acceso_directo.ps1")
Write-Host "Touchline está listo. Abrí el acceso directo del Escritorio."
