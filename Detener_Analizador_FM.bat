@echo off
chcp 65001 >nul
echo Deteniendo procesos de Touchline Analizador FM...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*app_desktop.py*' -or $_.CommandLine -like '*fm_app.server*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host ('Proceso cerrado: ' + $_.ProcessId) }"
echo.
echo Operación completada.
timeout /t 2 >nul
