# Continuación del 26/10/2026: desdobles por costado y distribución del portero

Se cerraron las dos dudas específicas solicitadas. Se incorporaron 17 capturas (309–325). Pruebas en la partida del 14/9/2028 13:15, mentalidad Ofensivo y formación CP 3-2-4-1; estos resultados no certifican todos los contextos posibles.

## Desdobles: matriz completa del selector en el contexto observado

Cada eje elige Equilibrado, Izquierda, Derecha o Ambas bandas. Se seleccionaron las nueve combinaciones compatibles y se observaron las siete incompatibles como botones deshabilitados. Se intentó pulsar Interior derecha con Banda derecha y el caso izquierdo equivalente: no modificaron el estado.

| Doblar por banda | Doblar por dentro | Resultado | Evidencia |
|---|---|---|---|
| Equilibrado | Equilibrado | Seleccionado | [captura](capturas/319-desdobles-equilibrados.jpg) |
| Equilibrado | Izquierda | Seleccionado | [captura](capturas/310-interior-izquierda.jpg) |
| Equilibrado | Derecha | Seleccionado | [captura](capturas/313-interior-derecha.jpg) |
| Equilibrado | Ambas bandas | Seleccionado | [captura](capturas/309-desdobles-inicio-26.jpg) |
| Izquierda | Equilibrado | Seleccionado | [captura](capturas/316-banda-izquierda-interior-equilibrado.jpg) |
| Izquierda | Izquierda | Bloqueado | [captura](capturas/310-interior-izquierda.jpg) |
| Izquierda | Derecha | Seleccionado | [captura](capturas/314-banda-izquierda-interior-derecha.jpg) |
| Izquierda | Ambas bandas | Bloqueado | [captura](capturas/309-desdobles-inicio-26.jpg) |
| Derecha | Equilibrado | Seleccionado | [captura](capturas/317-banda-derecha-interior-equilibrado.jpg) |
| Derecha | Izquierda | Seleccionado | [captura](capturas/311-banda-derecha-interior-izquierda.jpg) |
| Derecha | Derecha | Bloqueado | [captura](capturas/313-interior-derecha.jpg) |
| Derecha | Ambas bandas | Bloqueado | [captura](capturas/309-desdobles-inicio-26.jpg) |
| Ambas bandas | Equilibrado | Seleccionado | [captura](capturas/318-banda-ambas-interior-equilibrado.jpg) |
| Ambas bandas | Izquierda | Bloqueado | [captura](capturas/310-interior-izquierda.jpg) |
| Ambas bandas | Derecha | Bloqueado | [captura](capturas/313-interior-derecha.jpg) |
| Ambas bandas | Ambas bandas | Bloqueado | [captura](capturas/309-desdobles-inicio-26.jpg) |

Los costados opuestos pueden coexistir: banda izquierda + interior derecha, y banda derecha + interior izquierda. En un mismo costado son excluyentes. Ambas bandas en un eje deja al otro únicamente Equilibrado.

Regla de implementación que resume la observación: convertir cada valor en un conjunto de costados (Equilibrado = vacío) y permitir la pareja si su intersección es vacía. No presentar esta fórmula como código extraído del motor ni convertir Equilibrado en ausencia de movimientos espontáneos.

## Distribución del propio portero

Los dos botones Bandas son representaciones del mismo destino global. Los dos Laterales también. Se probaron los cuatro botones cambiando de destino: ambos del mismo nombre se resaltan simultáneamente, muestran el mismo título y descripción y dejan un único valor en el resumen. No son opciones izquierda/derecha.

| Botón pulsado | Valor resultante | Evidencia |
|---|---|---|
| Bandas izquierdo | Bandas | [captura](capturas/321-distribucion-bandas-izquierdo.jpg) |
| Laterales izquierdo | Laterales | [captura](capturas/322-distribucion-laterales-izquierdo.jpg) |
| Bandas derecho | Bandas | [captura](capturas/323-distribucion-bandas-derecho.jpg) |
| Laterales derecho | Laterales | [captura](capturas/324-distribucion-laterales-derecho.jpg) |

Mantener un selector de siete destinos; no agregar Bandas izquierda/derecha ni Laterales izquierda/derecha. Si la interfaz reproduce el dibujo de FM, ambos botones de cada nombre deben reflejar el mismo valor.

## Entrega a la IA que trabaja en Touchline

Integrar incrementalmente sobre el trabajo existente: aplicar la matriz documentada a los dos ejes de Carreras de apoyo y tratar los botones duplicados del portero como alias gráficos de un solo destino. Preservar datos y configuraciones. Si existen selecciones incompatibles, informarlas y permitir corregirlas sin reemplazarlas silenciosamente.

Fuentes estructuradas: verificacion-costados-portero-2026-10-26.json, verificacion-colectivas.json y catálogo actualizado. El archivo nuevo contiene toda la matriz, pruebas de clic bloqueado, contexto y referencias de evidencia.

## Límites no bloqueantes de la verificación

- Disponibilidad en otros contextos de puesto/rol, alcance, formación, mentalidad y personalización no ensayados.
- Ayudas colectivas no abiertas individualmente; los textos de instalación ya están conservados.
- Marcaje excluido por el usuario. Identificadores de partida y pesos del motor permanecen fuera del relevamiento visual.

Estado final: ambos ejes de desdobles Equilibrado y destino del propio portero Laterales. [Captura final](capturas/325-cierre-costados-portero.jpg). No se avanzó fecha ni se guardó la partida.

## Cierre del alcance acordado — 26/10/2026

El relevamiento queda completo para el alcance acordado; no hay identificado un dato indispensable pendiente. Los contextos no ensayados y las ayudas no abiertas individualmente son límites no bloqueantes. No se confirmó que cambiar la mentalidad modifique los candados individuales: no implementar bloqueos por esa hipótesis. La búsqueda web no proporcionó una matriz universal ni certifica los textos exactos de la instalación; se conservan los recursos locales extraídos. Aplicar las restricciones documentadas con su procedencia, mantener desconocidos explícitos y revisar casos nuevos ante discrepancias concretas. El marcaje sigue excluido. Ver [ALCANCE-Y-CIERRE.md](ALCANCE-Y-CIERRE.md) y [PROMPT-ACTUALIZACION-INCREMENTAL.md](PROMPT-ACTUALIZACION-INCREMENTAL.md). Este cierre prevalece sobre listas históricas que parezcan exigir probar todas las combinaciones antes de implementar.
