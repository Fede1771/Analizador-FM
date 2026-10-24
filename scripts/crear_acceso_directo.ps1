# Crea un acceso directo en el Escritorio de Windows para iniciar Touchline Analizador FM26
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$workspace = Split-Path -Parent $PSScriptRoot
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Touchline - Analizador FM26.lnk"
$pythonw = Join-Path $workspace ".venv\Scripts\pythonw.exe"
$appScript = Join-Path $workspace "app_desktop.py"
$iconPath = Join-Path $workspace "web\touchline.ico"
if (-not (Test-Path $iconPath)) {
    $iconPath = Join-Path $workspace "web\app_icon.ico"
}

if (-not (Test-Path $pythonw)) {
    Write-Error "No se encontró el entorno virtual en $pythonw"
    exit 1
}

# Si existía un acceso directo previo, borrarlo para forzar a Windows a leer la nueva definición
if (Test-Path $shortcutPath) {
    try { Remove-Item $shortcutPath -Force -ErrorAction SilentlyContinue } catch {}
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

# Notificar al explorador de Windows para que refresque la caché de íconos del Escritorio
try {
    Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;
    public class WinShellRefresh {
        [DllImport("shell32.dll")]
        public static extern void SHChangeNotify(int eventId, int flags, IntPtr item1, IntPtr item2);
    }
"@ -ErrorAction SilentlyContinue
    [WinShellRefresh]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)
} catch {}

Write-Host "=========================================================="
Write-Host "  ACCESO DIRECTO CREADO CON ÉXITO"
Write-Host "=========================================================="
Write-Host "Ubicación: $shortcutPath"
Write-Host "Ícono: $iconPath (alta resolución con 10 tamaños nativos)"
Write-Host "Ahora podés iniciar Analizador FM con un doble clic en tu Escritorio."
Write-Host "Se abre como ventana nativa sin ninguna consola negra de fondo."
Write-Host "Al cerrar la ventana, la aplicación se detiene automáticamente."
