@echo off
setlocal
cd /d "%~dp0.."

echo ==========================================================
echo    Touchline - Creador de Instalador MSI para Windows
echo ==========================================================
echo.

if not exist "%~dp0..\.venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual en .venv.
    echo Ejecuta primero scripts\Instalar_Analizador_FM.bat
    pause
    exit /b 1
)

echo [1/3] Verificando dependencias de empaquetado...
"%~dp0..\.venv\Scripts\python.exe" -c "import PyInstaller" 2>nul
if %ERRORLEVEL% neq 0 (
    echo Instalando PyInstaller en el entorno virtual...
    "%~dp0..\.venv\Scripts\python.exe" -m pip install pyinstaller
)

echo.
echo [2/3] Generando ejecutable standalone y paquete instalador .MSI...
"%~dp0..\.venv\Scripts\python.exe" "%~dp0..\tools\build_installer.py" %*

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==========================================================
    echo    INSTALADOR MSI CREADO CON EXITO
    echo ==========================================================
    echo El archivo listo para compartir se encuentra en:
    echo   dist\Touchline-Analizador-FM26.msi
    echo.
    echo Solo tenes que enviarle este archivo .msi a cualquier persona.
    echo El destinatario solo le hace doble clic y se instala solo!
    echo ==========================================================
) else (
    echo.
    echo [ERROR] Ocurrio un problema durante la construccion del instalador.
)

pause
