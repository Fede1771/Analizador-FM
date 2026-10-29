# Herramientas auxiliares

Herramientas vigentes, ejecutadas desde la carpeta principal:

- `check_translations.py`: contrasta etiquetas con el relevamiento.
- `compare_controls.py` e `inspect_colectivas.py`: inspeccionan instrucciones colectivas.
- `take_final_screenshots.mjs`: genera las capturas de referencia en `docs/capturas-finales/` usando un servidor y datos de prueba aislados.
- `build_installer.py --version 1.0.3`: compila el ejecutable con PyInstaller y genera un MSI que actualiza la versión anterior. Requiere WiX y `WixToolset.UI.wixext`; se puede configurar el ejecutable con `WIX_EXE`. La compilación de esta versión se verifica con WiX 4.0.6 y su extensión 4.0.6.
- `verify_msi.ps1`: inspecciona las propiedades, los accesos directos y los archivos del instalador generado.

`historicos/` conserva los 23 scripts de migración, parches y reorganizaciones utilizados durante el desarrollo. No se ejecutan al iniciar o instalar Touchline. Son registros de cambios puntuales sobre versiones anteriores, no un procedimiento para actualizar la versión actual; las correcciones vigentes están en el código y en `tests/`.

Los scripts históricos que calculaban la raíz desde su ubicación fueron ajustados a la nueva carpeta. Las herramientas, el instalador y la aplicación mantienen sus puntos de entrada habituales.
