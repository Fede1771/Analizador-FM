# Herramientas auxiliares

Herramientas vigentes, ejecutadas desde la carpeta principal:

- `check_translations.py`: contrasta etiquetas con el relevamiento.
- `compare_controls.py` e `inspect_colectivas.py`: inspeccionan instrucciones colectivas.
- `take_final_screenshots.mjs`: genera las capturas de referencia en `docs/capturas-finales/` usando un servidor y datos de prueba aislados.

`historicos/` conserva los 23 scripts de migración, parches y reorganizaciones utilizados durante el desarrollo. No se ejecutan al iniciar o instalar Touchline. Son registros de cambios puntuales sobre versiones anteriores, no un procedimiento para actualizar la versión actual; las correcciones vigentes están en el código y en `tests/`.

Los scripts históricos que calculaban la raíz desde su ubicación fueron ajustados a la nueva carpeta. Las herramientas, el instalador y la aplicación mantienen sus puntos de entrada habituales.
