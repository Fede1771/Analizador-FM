# Verificación de Touchline 1.1.0

Fecha: 4 de noviembre de 2026.

## Código y flujos

- Suite Python: 125/125 aprobadas, con datos sintéticos y copias temporales de extracciones reales.
- Frontend: 14/14 aprobadas, incluido el escape de nombres y encabezados externos en la vista previa.
- Navegador: 33/33 recorridos aprobados, sin errores inesperados. Incluyen táctica guardada, fases, candados por contexto, preferencias, historial tras recarga, comparación a 420 px, profundidad, minutos e importación CSV UTF-16 con confirmación y preferencias vinculadas conservadas.
- Las capturas actualizadas y las cinco pantallas nuevas están en [la galería](../../capturas-finales/README.md). Se usan datos sintéticos.

El test real anterior asumía que cualquier guardado de Liverpool coincidía con unas capturas antiguas y tenía todas las instrucciones y titulares completos. Se reprodujeron las mismas instrucciones parciales con el código anterior a estos cambios. El test ahora valida los datos disponibles y el rechazo de un once incompleto. Un cotejo exacto con capturas requiere identificar su archivo por hash; esa huella no está documentada en la referencia actual. Las pruebas de máscaras de decodificación conocidas se mantienen.

## Copia de Arsenal aportada para la prueba

Se ejecutó el flujo de importación de producción en un almacenamiento temporal, con una copia interna `.fm`. Se verificó el hash del archivo aportado antes y después, sin alteraciones:

- Fecha del juego: 30/08/2026.
- 54 jugadores y 10 cedidos.
- Dos tácticas leídas; una permitió auditar los 11 titulares con cero instrucciones individuales y colectivas pendientes.
- Cuatro estilos analizados y precalculados correctamente.
- Estadísticas de temporada disponibles y comparables para 22/22 jugadores del grupo principal.
- Comparación y primera observación histórica generadas correctamente.
- Advertencias del lector: ninguna.

No se adjuntan la partida, su extracción, nombres de manager ni perfiles personales a este informe ni a la distribución.

## Distribución

MSI compilado con WiX 7.0.0 y PyInstaller 6.22.3:

- ProductVersion: `1.1.0`.
- UpgradeCode: `{4E565251-5443-4C4E-8765-202610260001}` (conservado).
- 293 archivos y accesos directos de Escritorio y Menú Inicio.
- Recursos de `web/` empaquetados: todos coinciden con el código fuente final.
- Prueba del ejecutable compilado: restauración de una carrera sintética, API de análisis, comparación, historial, vista previa CSV sin cambiar el plantel activo y cierre limpio; correcta.
- SHA-256 del MSI: `e4479e90f389140d6df815cef20afd757d60426598d684a06b5a19024928f3da`.

No se instaló el MSI sobre el perfil personal del usuario. La prueba del ejecutable se hizo con `--server-only --no-sync` y un directorio de datos aislado. No se modificó la configuración de sincronización ni el perfil WebView del usuario.
