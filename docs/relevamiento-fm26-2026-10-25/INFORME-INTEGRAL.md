# Entrega integral: FM26 y mejoras de Touchline

Este es el punto de entrada al paquete para la IA que continuará el trabajo. Incluye el relevamiento táctico de Football Manager 26 y una propuesta de reorganización visual y de información de Touchline. El análisis de interfaz es una propuesta de producto; no constituye una regla observada en FM.

## Orden de lectura

1. Este documento, para entender alcance y prioridades.
2. [REPORTE.md](REPORTE.md): informe táctico completo, con las fichas, descripciones, instrucciones, observaciones y referencias a capturas.
3. [MEJORAS-DE-INTERFAZ.md](MEJORAS-DE-INTERFAZ.md): hallazgos estéticos, redundancias, estructura propuesta y criterios de aceptación.
4. [catalogo-para-reconstruccion.json](catalogo-para-reconstruccion.json) y [matriz-instrucciones-observadas.json](matriz-instrucciones-observadas.json), para implementar los datos y las restricciones documentadas.
5. [PENDIENTES.md](PENDIENTES.md), antes de asumir que se verificaron todas las variantes.
6. [PROMPT-PARA-OTRA-IA.md](PROMPT-PARA-OTRA-IA.md): encargo completo de implementación táctica y visual.

## Qué está relevado de FM26

Instalación observada: versión 26.3.2.2329565, motor v26.3.0.1; idioma Español latinoamericano. El alcance es reconstruir/mejorar el analizador, no recrear el motor de partidos.

| Contenido | Cobertura comprobada |
|---|---|
| Roles por fase | 79 definiciones y descripciones completas de recursos instalados |
| Paneles individuales | 79/79, cada uno en al menos un contexto |
| Listas de atributos clave | 79/79 cotejadas visualmente |
| Familias de posición | 14 documentadas; disponibilidad contextual, no matriz universal |
| Instrucciones individuales | 15 grupos y 45 opciones documentadas |
| Instrucciones colectivas | Ocho vistas, 29 apariciones, 27 selectores únicos con sus opciones; 28 dimensiones y dos estados compartidos confirmados |
| Evidencia visual FM | 326 registros de capturas |
| Recursos tácticos seleccionados | 1680 registros con contexto y huellas de origen |

La última revisión cerró los 13 paneles pendientes. Los tres valores antes tapados por ayudas quedaron confirmados visualmente: **Aguantar el balón = No, con candado**, para Central abierto CP, Central que dobla CP y Mediocampista todoterreno CP. Las capturas 273, 274 y 275 documentan la confirmación.

En el Zaguero SP existe una discrepancia entre la ficha y el panel activo de instrucciones. Debe conservarse como discrepancia y usarse el panel activo como evidencia del valor observado, sin inventar una conciliación.

## Qué todavía falta verificar

- Todas las combinaciones de subpuesto, costado, formación y alcance Posición/Jugador.
- Combinaciones de contexto y ayudas colectivas aún no abiertas: ver ADENDA-COLECTIVAS.md. Los estados compartidos de Regate y Trampa de presión ya están confirmados.
- El marcaje queda excluido de nuevas verificaciones por pedido del usuario.
- Los identificadores de roles/posiciones/instrucciones dentro de la partida, si se necesita automatizar su lectura. Las claves de localización no sirven como sustituto.

Los atributos clave no revelan pesos internos del motor. El índice 80/20, los umbrales, recomendaciones y mapas de cobertura son métodos propios de Touchline. Un índice sobre 100 no es una probabilidad de ganar.

## Diagnóstico de la interfaz

La paleta oscura y verde menta, la navegación lateral y la separación entre táctica actual y propuestas ofrecen una base consistente. La mayor mejora está en la jerarquía: demasiados accesos, avisos, tarjetas y controles aparecen antes del once.

Se detectaron selectores duplicados de formación e idea de juego, accesos reiterados al Mini-HUD y al cierre, información repetida entre tarjetas y estadísticas, y recomendaciones presentadas varias veces. Además hay texto fijo de jugadores en el checklist, un bloque «Próximo partido» alimentado por una propuesta y una promesa de «100% optimizada» al marcar casillas. Estos últimos puntos afectan la interpretación del análisis y deben resolverse primero.

La revisión visual utilizó capturas de prueba ya guardadas en el proyecto, contrastadas con el código fuente actual. La ventana nativa no permaneció disponible para completar un recorrido interactivo. Las imágenes de `referencias-interfaz/` contienen datos de prueba: son referencias de presentación, no evidencia del plantel ni del motor de FM. No se certificó visualmente cada pantalla o resolución.

## Orden recomendado de implementación

1. **Coherencia de datos y mensajes.** Sustituir recomendaciones fijas por resultados vigentes y distinguir propuesta, táctica confirmada y verificación pendiente. Revisar la correspondencia del contenido del HUD.
2. **Modelo táctico.** Integrar catálogo, alias, fases, alcance, destinos de marca y restricciones por contexto. Mantener desconocidos explícitos.
3. **Flujo principal.** Mostrar cancha y prioridades antes del detalle; eliminar entradas duplicadas y organizar el resto en vistas secundarias.
4. **Consistencia visual y adaptación.** Unificar iconos, nombres, colores de estado, espaciado y navegación en ventanas angostas.
5. **Verificación.** Comprobar flujos completos, persistencia, accesibilidad, coherencia de datos y capturas de la interfaz final.

El repositorio puede contener cambios de otra IA posteriores al análisis. Inspeccionar el estado actual y conservar el trabajo existente; los problemas históricos son una lista para contrastar, no una orden para revertir correcciones.

Esta entrega incorpora documentación y evidencias. No implementa las propuestas gráficas ni modifica el software de producción.

## Actualización: selectores colectivos observados

Se revisaron **27 paneles colectivos únicos (28 dimensiones)** y se confirmaron dos controles compartidos. Leé [ADENDA-COLECTIVAS.md](ADENDA-COLECTIVAS.md) y [verificacion-colectivas.json](verificacion-colectivas.json). Estas pruebas cierran la lista de opciones visibles y las duplicaciones de Regate/Trampa de presión; las combinaciones de contexto y todas las ayudas siguen sin certificarse. El marcaje queda excluido de nuevas investigaciones por pedido del usuario.

## Actualización del 26/10/2026: costados y portero

Quedaron cerrados los desdobles por costado y los botones duplicados del portero. La matriz 4×4 tiene nueve combinaciones seleccionadas y siete bloqueadas en el contexto observado: exterior e interior coexisten en lados opuestos y se excluyen en el mismo lado. Los dos botones Bandas son equivalentes entre sí; también los dos Laterales. Leé [ADENDA-COSTADOS-PORTERO-2026-10-26.md](ADENDA-COSTADOS-PORTERO-2026-10-26.md) y [verificacion-costados-portero-2026-10-26.json](verificacion-costados-portero-2026-10-26.json). Se incorporaron 17 capturas nuevas. Persisten únicamente los contextos no ensayados y las ayudas no abiertas; no extrapolar reglas universales.

## Cierre del alcance acordado — 26/10/2026

El relevamiento queda completo para el alcance acordado; no hay identificado un dato indispensable pendiente. Los contextos no ensayados y las ayudas no abiertas individualmente son límites no bloqueantes. No se confirmó que cambiar la mentalidad modifique los candados individuales: no implementar bloqueos por esa hipótesis. La búsqueda web no proporcionó una matriz universal ni certifica los textos exactos de la instalación; se conservan los recursos locales extraídos. Aplicar las restricciones documentadas con su procedencia, mantener desconocidos explícitos y revisar casos nuevos ante discrepancias concretas. El marcaje sigue excluido. Ver [ALCANCE-Y-CIERRE.md](ALCANCE-Y-CIERRE.md) y [PROMPT-ACTUALIZACION-INCREMENTAL.md](PROMPT-ACTUALIZACION-INCREMENTAL.md). Este cierre prevalece sobre listas históricas que parezcan exigir probar todas las combinaciones antes de implementar.
