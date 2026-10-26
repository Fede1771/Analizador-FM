# Revisión de la integración del relevamiento FM26 en Touchline

## Estado después de las correcciones

Los tres hallazgos de esta revisión y el fallo adicional de caché quedaron corregidos el 26/10/2026:

- Se valida la pareja efectiva de desdobles después de combinar estilo, pedido y ajustes, tanto en solicitudes y preferencias como en el generador de propuestas.
- Las preferencias antiguas incompatibles muestran controles de recuperación sin necesitar un resultado válido. Se puede corregir un eje, conservar ritmo y demás ajustes, guardar y reabrir la aplicación.
- Los candados y etiquetas de disponibilidad comprueban puesto, costado, cantidad de jugadores del mismo puesto cuando está especificada y ámbito. Fuera del contexto observado, el valor suministrado por el usuario se conserva y su disponibilidad queda no verificada. No se incorporan órdenes faltantes por extrapolación.
- Se normalizan los identificadores de los mapas de excedentes al restaurar la caché. La versión del análisis pasa a 12 para no reutilizar resultados con las certificaciones anteriores.

Verificación final: **96/96 pruebas Python, 6/6 pruebas de frontend y 27/27 recorridos de navegador**, sin errores inesperados de ejecución. Incluyen rechazo del ajuste parcial, recuperación selectiva de preferencias antiguas, cambios de puesto/ámbito y reapertura del borrador personalizado. Las pruebas usan almacenamiento aislado y copias de datos reales; no se modificaron partidas ni configuraciones originales. Los apartados siguientes conservan la revisión histórica que motivó estos cambios.

Revisado el 26/10/2026 sobre el commit `f7c0c80`, comparado con `63ec93e`. La integración incorpora correctamente el catálogo y buena parte de los controles nuevos, pero no queda cerrada: se reprodujeron tres defectos en los casos de validación, recuperación y contexto. No se modificaron archivos de producción ni las configuraciones reales durante esta revisión.

## Hallazgos reproducidos

### 1. P2 — Validar el resultado de mezclar ajustes con el estilo, no solo los ajustes enviados

`validate_overrides` comprueba únicamente las dos claves que estén presentes en el objeto enviado (`fm_app/contracts.py:104`). Después `team_instructions` mezcla ese objeto con `TEAM_PLANS` sin volver a comprobar la pareja (`fm_app/fm26.py:529` y `533`).

Reproducción: solicitar una simulación 4-3-3 con estilo `press` y solo `underlap_ip = Underlap - Left`. La API responde HTTP 200 y devuelve `overlap_ip = Overlap - Both Flanks` junto a `underlap_ip = Underlap - Left`: una de las siete combinaciones documentadas como prohibidas. La función aislada de compatibilidad la identifica como incompatible.

Corregir la validación de la configuración efectiva después de combinar estilo, interpretación y ajustes. No corregirlo sustituyendo silenciosamente una selección del usuario. Añadir una prueba con un único eje enviado; las pruebas actuales de la matriz suministran los dos ejes y no detectan este caso.

### 2. P2 — Una combinación antigua incompatible deja al usuario sin controles para corregirla

La versión anterior permitía izquierda + izquierda y derecha + derecha. Al recuperar unas preferencias así, la nueva validación falla antes de disponer de resultados. `refresh` borra los resultados (`web/app.js:93`), y la página de propuestas solo muestra los selectores de instrucciones dentro de un resultado válido (`web/views.js:190`).

Reproducción en un servidor y perfil de navegador temporales: recuperar preferencias con ambos ejes Left. Se muestra el error de incompatibilidad y además el mensaje engañoso «No hay un once completo». No existen los selectores `#override-overlap_ip`, `#override-underlap_ip` ni el botón `clear-overrides`. Reintentar repite el error. Cambiar el estilo recupera la pantalla, pero borra todos los ajustes manuales, incluido el ritmo que se había guardado.

Las preferencias originales no se borran al cargar: el defecto es la falta de una vía de corrección selectiva. Conservar los valores incompatibles, mostrarlos con el aviso y permitir corregir un eje antes de recalcular. Mantener el resto de los ajustes. Añadir una prueba de actualización desde preferencias válidas para la versión anterior.

### 3. P2 — Se generalizan candados comprobados a contextos que no se verificaron

El editor obtiene la evidencia solo por `roleId` (`web/current-view.js:421`) y aplica los candados sin comparar el puesto ni el ámbito (`428–430`). El backend también aplica `SCREENSHOT_LOCKS[role_id]` al auditar, sin comprobar ese contexto (`fm_app/current_tactic.py:108–110`). Las recomendaciones asignan los estados `locked_verified` y `editable_verified` por rol (`fm_app/fm26.py:359–386`).

Reproducción: Carrilero organizador CP en WBL, ámbito Personalizada. «Aguantar el balón» queda deshabilitado y marcado «Bloqueado comprobado», aunque el registro de este rol corresponde a DR y ámbito Posición. No se afirma que FM permita modificarlo en WBL; el problema es que la aplicación presenta como probado un contexto no acreditado y lo bloquea apoyándose en otra observación.

Comprobar contexto antes de aplicar y etiquetar restricciones. Fuera del contexto documentado, conservar la disponibilidad como no verificada y evitar restricciones hipotéticas, según ALCANCE-Y-CIERRE.md. Corregir frontend y backend de manera consistente y probar cambio de puesto y ámbito.

## Incidencia adicional de verificación: restauración de caché

La suite Python termina con un fallo: `test_import_precomputes_and_restores_the_exact_cache_keys` (`tests/test_import.py:41`). Se reprodujo por separado: las claves de jugador de `surplus_players` son `int` antes de guardar y `str` después de restaurar. `_restore` normaliza `profiles`, pero no esos nuevos mapas (`fm_app/jobs.py:50`).

No se observó pérdida de partidas ni de configuraciones por este cambio de tipos. Sí se incumple la equivalencia de caché exigida por la prueba. Normalizar de forma consistente los mapas nuevos, tanto los generales como los incluidos en propuestas, y verificar de nuevo la restauración.

## Qué se comprobó correctamente

- Los 79 IDs de rol del relevamiento están presentes; las listas de atributos de los 79 coinciden tras normalizar sus nombres.
- Los tres valores confirmados de Aguantar el balón permanecen en No para Central abierto CP, Central que dobla CP y Mediocampista todoterreno CP.
- Las opciones traducidas de las 28 dimensiones colectivas coinciden con el JSON observado, incluidos ambos ejes de desdobles.
- La función de compatibilidad y la validación con ambos ejes implementan las nueve combinaciones permitidas y las siete bloqueadas.
- El portero tiene siete destinos únicos; Bandas y Laterales no se duplican por costado.
- Regate y Trampa de presión usan una clave de estado cada uno y muestran sus subfases compartidas.
- Se conserva la eliminación del restablecimiento automático del otro eje al cambiar una selección.

## Verificación de las mejoras anteriores

Se ejecutaron los tests del proyecto con almacenamiento temporal aislado. Las restricciones iniciales de temporales y sockets del entorno se resolvieron repitiendo las pruebas con un directorio temporal del proyecto y ejecución autorizada para servidores locales. Los errores de permisos iniciales no se contabilizan como defectos de Touchline.

- Python: **91 pruebas, 90 correctas y un fallo de restauración de caché**; sin errores ni omisiones en la ejecución final.
- Frontend unitario: **4/4 correctas**.
- Navegador: **24/24 recorridos correctos, sin errores de ejecución registrados**. Cubren navegación, edición pendiente entre fases, persistencia por carrera, interpretación de pedidos, contratos, ojeo, plantilla, mini HUD, once con identidad conservada, mapa de 25 zonas, disposición de escritorio y ventana de 760 px.
- Pruebas adicionales de esta revisión: reproducciones HTTP y de navegador de los tres hallazgos anteriores.
- Se inspeccionaron las capturas de escritorio y de Mi táctica a 760 px generadas por el test. La organización visual anterior permanece en esos flujos; esto no certifica todas las pantallas ni todas las configuraciones personales.

Los tests con datos reales usan copias temporales de los datos importados de Liverpool. El test de guardado de táctica real serializa el resultado de auditoría en un JSON temporal; eso no sustituye una prueba completa de migración del perfil nativo y de todos sus borradores. Las partidas y preferencias reales no se alteraron.

## Evidencia disponible en esta carpeta del proyecto

- `.tmp/revision-2026-10-26/python-tests.log`: ejecución final de la suite Python.
- `.tmp/revision-2026-10-26/browser-tests.log`: 24 recorridos de navegador.
- `.tmp/revision-2026-10-26/browser-audit/audit-observations.json`: resultados de las reproducciones.
- `.tmp/revision-2026-10-26/browser-audit/legacy-conflict.png`: pantalla sin controles de recuperación.
- `.tmp/browser-spXiiG/`: capturas de los flujos habituales con datos sintéticos.
- `.tmp/revision-2026-10-26/prepare_browser_audit.py`: preparación del recorrido adicional, sin modificar los tests ni el código de producción.

La conclusión es conservar la integración y las mejoras actuales, corregir estos casos puntuales y volver a ejecutar las comprobaciones afectadas. El cierre del relevamiento de FM no significa que estos defectos de implementación estén resueltos.
