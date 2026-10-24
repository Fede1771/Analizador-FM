# Crea un acceso directo en el Escritorio de Windows para iniciar Touchline Analizador FM26
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$workspace = Split-Path -Parent $PSScriptRoot
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Touchline - Analizador FM26.lnk"
$pythonw = Join-Path $workspace ".venv\Scripts\pythonw.exe"
$appScript = Join-Path $workspace "app_desktop.py"
$iconPath = Join-Path $workspace "web\app_icon.ico"

if (-not (Test-Path $pythonw)) {
    Write-Error "No se encontró el entorno virtual en $pythonw"
    exit 1
}

$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = "`"$appScript`""
$shortcut.WorkingDirectory = $workspace
if (Test-Path $iconPath) {
    $shortcut.IconLocation = "$iconPath,0"
}
$shortcut.Description = "Touchline · Analizador Football Manager 26"
$shortcut.Save()

Write-Host "=========================================================="
Write-Host "  ACCESO DIRECTO CREADO CON ÉXITO"
Write-Host "=========================================================="
Write-Host "Ubicación: $shortcutPath"
Write-Host "Ahora podés iniciar Analizador FM con un doble clic en tu Escritorio."
Write-Host "Se abre como ventana nativa sin ninguna consola negra de fondo."
Write-Host "Al cerrar la ventana, la aplicación se detiene automáticamente."
