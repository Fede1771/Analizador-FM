@echo off
chcp 65001 >nul
title Instalando Acceso Directo - Touchline Analizador FM26

echo ========================================================
echo   INSTALADOR DE ACCESO DIRECTO - ANALIZADOR FM26
echo ========================================================
echo Creando acceso directo en tu Escritorio...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\crear_acceso_directo.ps1"

echo.
echo Presioná cualquier tecla para salir...
pause >nul
