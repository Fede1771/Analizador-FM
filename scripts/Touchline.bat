@echo off
cd /d "%~dp0.."
if not exist "%~dp0..\.venv\Scripts\pythonw.exe" (
  echo Ejecuta primero scripts\Instalar_Analizador_FM.bat
  pause
  exit /b 1
)
start "" "%~dp0..\.venv\Scripts\pythonw.exe" "%~dp0..\app_desktop.py"
