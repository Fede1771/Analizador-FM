# Scripts de Touchline

Se ejecutan desde la carpeta principal del proyecto.

## Instalación y mantenimiento

- `instalar.ps1` y `crear_acceso_directo.ps1`: utilizados por el instalador de la carpeta principal.
- `diagnostico.py`: comprueba Python, dependencias y recursos sin iniciar el servidor ni modificar partidas.
- `check_http.py`: comprobaciones auxiliares del servicio HTTP.

## Relevamiento y referencias de FM26

- `relevar_textos_fm26.py`, `extract_fm26_locale.py` y `listar_idiomas_fm26.ps1`: extracción y localización.
- `crear_reporte_relevamiento_fm26.py` y `actualizar_colectivas_fm26.py`: informe, catálogo documental y ZIP.
- `update_fm26_catalog.py`: actualización explícita del vocabulario; no pertenece a la importación normal.
- `extract_brighton.py` y `create_review.py`: utilidades de la prueba histórica de lectura.
- `generate_touchline_icon.py`: generación de recursos gráficos.

Sus rutas se mantienen para conservar el instalador y las referencias existentes. El uso normal de Touchline no requiere ejecutar los extractores o generadores.
