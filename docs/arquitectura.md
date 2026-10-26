# Arquitectura de Touchline

## Componentes

| Componente | Responsabilidad |
|---|---|
| `app_desktop.py` | Ventana/navegador, logs, instancia local y cierre coordinado |
| `fm_app/server.py` | HTTP local, autorización de origen y transporte JSON/archivos |
| `fm_app/contracts.py` | Validación de jugadores, estadísticas, solicitudes y preferencias; claves canónicas de caché |
| `fm_app/dataset.py` | Dataset visible validado y metadatos de metodología |
| `fm_app/jobs.py` | Reserva de trabajos, copia, extracción, análisis, publicación y cancelación |
| `fm_app/storage.py` | JSON atómico, puntero de importación y retención acotada |
| `fm_app/watcher.py` | Detección estable, seguimiento por trabajo, confirmación de éxito y reintentos |
| `fm_app/tactics.py` | Catálogo único de puestos/fases/coordenadas, estilos e interpretación de pedidos |
| `fm_app/recommendations.py` | Puntuación, asignación global, constructor compartido, cobertura y desarrollo |
| `fm_app/fm26.py` | Catálogo de roles, localización e instrucciones |
| `fm_app/instruction_rules.py` | Compatibilidad de desdobles y correspondencia entre contexto actual y evidencia de instrucciones |
| `web/api.js` | HTTP con timeout/cancelación y control de respuestas anteriores |
| `web/session.js` | Preferencias, reconciliación de jugadores/grupos y filtros |
| `web/instruction-context.js` | Correspondencia de puesto, costado y ámbito en el editor individual |
| `web/views.js`, `web/tactics-view.js` | Presentación del club y de las propuestas tácticas |
| `web/app.js` | Eventos, navegación y coordinación de actualizaciones |

## Invariantes

- Un puesto tiene identidad estable, posición y coordenadas propias en ambas fases. El orden del array conserva la identidad del jugador; nunca representa un ordenamiento independiente de la línea defensiva.
- La calidad individual es 80 % atributos del rol y 20 % atributos del estilo, llevados a 0–100 y multiplicados por `0,25 + 0,75 × familiaridad/20`.
- El puesto combina 80 % fase con posesión y 20 % fase defensiva. Titulares, suplentes y cedidos usan la misma evaluación del puesto. El once maximiza la suma global sin repetir jugadores.
- El banco reserva una alternativa de arquero cuando existe y luego prioriza cobertura de puestos y encaje. Esa cobertura es una heurística de planificación, no una predicción de rendimiento.
- Los avisos de calidad se calculan respecto de la media del once menos ocho puntos; las faltas de recambio y de familiaridad se informan por separado.
- Los candidatos cedidos se cuentan por identificador único. Una misma persona puede ser alternativa para varios puestos, pero no resolverlos a la vez. Las condiciones de regreso no se verifican.
- Las estadísticas desconocidas conservan `null`, mientras que cero representa un dato conocido. La extracción filtra por jugador y club de destino.
- La caché usa dataset, estilo, grupo, exclusiones ordenadas, pedido, ajustes ordenados y formación. La versión del motor invalida los bundles anteriores.
- La compatibilidad de los desdobles se valida sobre la combinación efectiva de estilo, pedido y ajustes. Un ajuste parcial no puede producir una pareja incompatible con el valor base del otro eje.
- Las restricciones observadas solo se aplican cuando coincide el puesto, costado y ámbito documentados, incluida la cantidad de jugadores del mismo puesto si la evidencia la especifica. Los contextos desconocidos conservan su estado no verificado.

## Ciclo de importación

`uploading/copying → reading → analyzing → done/error/cancelled`

La reserva es exclusiva. Cualquier fallo, incluso durante creación de carpetas o copia, finaliza el trabajo. La extracción se ejecuta en un proceso controlado con tiempo máximo. La publicación escribe primero el bundle y después cambia atómicamente el puntero; el informe anterior permanece activo ante errores.

El monitor identifica un archivo por ruta resuelta, tiempo de modificación en nanosegundos y tamaño. Confirma la firma únicamente cuando el trabajo termina en `done`. La firma restaurada procede de la copia importada, no del estado actual del archivo original.

El transporte captura el estado y libera su bloqueo antes de consultar el monitor. El monitor también libera su bloqueo antes de leer los trabajos o enviar una importación. El cierre interrumpe la espera del monitor y termina el proceso de extracción antes de esperar al ejecutor.

## Persistencia

La identidad de preferencias deriva del UID del club y el UID del manager. Las copias y autoguardados de esa combinación comparten preferencias. El identificador del dataset deriva del contenido de un guardado y separa resultados entre versiones.

Las preferencias se guardan en el servicio local y también en almacenamiento del navegador como respaldo. Se reconcilian los grupos y los identificadores de jugadores antes de reutilizarlas. Todos los resultados se descartan al cambiar dataset o parámetros. Las solicitudes anteriores se cancelan y sus respuestas no se publican.

Una pareja antigua de desdobles incompatible se conserva para permitir su corrección selectiva desde Propuestas, incluso sin un análisis calculado. Solo se persisten las modificaciones después de validar el resultado; no se restablecen otras instrucciones para resolver el conflicto. Los mapas por UID de la caché se normalizan al restaurarlos desde JSON, incluidos los mapas anidados en propuestas.

La retención se ejecuta después de un éxito y protege siempre la copia activa. Solo procesa nombres UUID válidos contenidos en la raíz de importaciones; ignora carpetas ajenas y enlaces simbólicos. Sus límites se configuran sin ejecutar una eliminación inmediata.

## Verificación

Las pruebas Python usan fixtures sintéticos y directorios temporales. Cubren coherencia de fases, ranking completo, puntuación de reemplazos, negaciones, estadísticas, conservación de datos ante fallos, caché, retención, concurrencia HTTP y confirmación del monitor. Las pruebas Node cubren persistencia, filtros, formato y rechazo de respuestas anteriores.
