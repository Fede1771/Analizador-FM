# Guía de Desarrollo y Pruebas · Touchline

Documento interno para desarrolladores y mantenimiento de Touchline.

## Requisitos de Desarrollo
- Python 3.12 o 3.14
- Node.js 18+ (para pruebas de frontend e integración de navegador)
- WiX Toolset v7 (`dotnet tool install --global wix`) y extensión `WixToolset.UI.wixext`

## Ejecución de Pruebas

```powershell
# Pruebas unitarias de Python (96 tests)
.\.venv\Scripts\python.exe -m unittest discover -s tests

# Pruebas unitarias de Frontend (6 tests)
node tests/frontend.test.mjs

# Pruebas de integración en navegador (27 tests)
node tests/browser.test.mjs

# Diagnóstico de entorno
.\.venv\Scripts\python.exe scripts/diagnostico.py
```

## Construcción del Instalador Standalone (.msi)

Para compilar el ejecutable y generar el instalador MSI para usuarios finales:

```powershell
# Usando el script batch
.\Construir_Instalador_MSI.bat

# O directamente vía Python
.\.venv\Scripts\python.exe tools/build_installer.py
```

El instalador resultante se genera en `dist/Touchline-Analizador-FM26.msi`.

## Ejecución en Modo Desarrollo

```powershell
# Ventana nativa de escritorio
.\.venv\Scripts\python.exe app_desktop.py

# Modo solo navegador
.\.venv\Scripts\python.exe app_desktop.py --browser-only --port 8765
```
