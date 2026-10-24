# Touchline — informe para continuar el proyecto con otra IA

Fecha: 24 de octubre de 2026. Estado del proyecto local al preparar este informe.

## 1. Qué quiere el usuario

Crear una aplicación donde pueda cargar directamente su partida guardada de **Football Manager 26**, elegir el estilo de juego que quiere implementar y recibir un análisis automático de su club:

- Formación, once, roles e instrucciones recomendados.
- Explicaciones concretas para cada jugador basadas en sus atributos.
- Análisis del primer equipo, inferiores y cedidos.
- Orientación para desarrollar juveniles y comparar su nivel actual con el primer equipo.
- Nombres que coincidan con el juego en **Español latinoamericano**, no español de España.

El usuario quiere que la aplicación haga la extracción y el análisis a partir del `.fm`; no quiere preparar CSV ni exportaciones manuales. Prefiere que se avance con el trabajo autorizado sin pedir confirmaciones rutinarias.

**Estado general:** hay un prototipo local funcional que ya lee partidas reales y recomienda tácticas. No es todavía un producto terminado ni una demostración de cuál es la táctica óptima en el motor de FM. El último trabajo se concentró en reemplazar traducciones aproximadas por etiquetas extraídas del juego instalado.

## 2. Ubicación y cómo ejecutarlo

Proyecto:

```text
C:\Users\feder\Documents\Codigos varios y emprendimientos\Analizador FM
```

Sistema: Windows, PowerShell. Entorno existente: `.venv`, con Python 3.14 y `fmsave==0.5.11`. La dependencia principal está fijada en `requirements.txt`.

Para abrirlo: doble clic en `iniciar.cmd`. O, desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe -m fm_app.server --open
```

Dirección: `http://127.0.0.1:8765/`. Si el servidor ya está activo, basta abrir esa dirección. Es una aplicación local; no está desplegada en Internet, no necesita una cuenta ni una API de IA para funcionar.

El servidor se dejó ejecutando en segundo plano. Último PID registrado: **24392**, en `.tmp/server.pid`. Ese número es transitorio: comprobar el proceso y su línea de comandos antes de reiniciar nada. No detener una importación activa. El endpoint `/api/status` informa su estado.

En la última comprobación, esta carpeta no era un repositorio Git. No asumir que existen commits o una rama donde recuperar cambios.

## 3. Partidas y resultados reales

El usuario movió sus partidas a:

```text
C:\Users\feder\Downloads\games\Federico Burgos - Brighton.fm
C:\Users\feder\Downloads\games\Federico Burgos - Liverpool.fm
```

Se confirmó la existencia de ambas. Tamaños: Brighton **171.434.713 bytes**; Liverpool **243.624.533 bytes**. La ubicación antigua en OneDrive ya no debe tomarse como ubicación principal.

Las importaciones reales existentes dieron estos resultados:

| Partida | Fecha dentro del juego | Jugadores en el club | Grupo 0 | Grupo 1 | Grupo 2 | Cedidos fuera |
|---|---|---:|---:|---:|---:|---:|
| Brighton & Hove Albion | 2026-05-31 | 63 | 25 | 24 | 14 | 23 |
| Liverpool | 2028-09-14 | 39 | 22 | 15 | 2 | 23 |

Los reportes de esas importaciones indican build reconocido, sin errores de consistencia y sin advertencias del lector. Esto **no demuestra** que cada atributo extraído coincida con la ficha del juego: ese cotejo visual sigue pendiente.

Grupo 0 corresponde al primer equipo. Grupo 1 corresponde a la división Sub-21 (jugadores de 16–20 años que compiten en el EFL Trophy —competición 1301429—) y Grupo 2 a Sub-18 (jugadores de 15–17 años que disputan la UEFA Youth League —competición 214404—). Ambos nombres fueron confirmados y ahora se reflejan automáticamente en la aplicación sin la etiqueta provisional de «sin confirmar».

La importación seleccionada al redactar este informe es Liverpool:

```text
data/imports/current.json
  folder = 852092479d4c4d86ba646a0a40220fb7
```

Un snapshot de Brighton está en `data/imports/765beec7b2f04971aed2e89a946196df/`. Hay otras importaciones históricas. **Leer siempre `current.json` antes de actuar:** el usuario puede cargar otra partida desde la app y cambiar el estado.

## 4. Qué está implementado

### Carga y extracción

- Pantalla inicial para elegir o arrastrar un archivo `.fm` de hasta 400 MB.
- Copia local del archivo importado y extracción automática con `fmsave` en un subproceso.
- Detección del club gestionado. Actualmente exige encontrar **un único club gestionado**; no se implementó un selector para carreras con varios mánagers/clubes.
- Extracción de jugadores del club y de cedidos fuera de él.
- Validación de estructura, campos requeridos, atributos/posiciones en rangos, IDs duplicados y estabilidad del archivo mediante SHA-256 antes/después.
- Progreso de importación, consulta del trabajo en segundo plano y recuperación del seguimiento al recargar la página.
- Cálculo de los cuatro estilos antes de dar la importación por terminada.
- Una importación fallida conserva el último análisis válido.
- Persistencia y restauración de la última partida y de sus análisis.

No se modifican las partidas originales ni se envían sus datos a un servicio externo. Las exportaciones completas del lector **sí contienen datos ocultos**, pero la API que alimenta la aplicación filtra capacidad actual/potencial, personalidad y atributos ocultos. El motor de recomendaciones utiliza atributos visibles.

### Interfaz y recomendaciones

- Centro del club, laboratorio táctico, plantilla, inferiores, cedidos y explicación del método.
- Buscador, filtros, fichas de jugador y atributos.
- Cuatro estilos: posesión, presión alta, transiciones y bandas.
- Comparación de tres estructuras: 4-3-3, 4-2-3-1 y 4-4-2, con estructura defensiva por fase.
- Asignación de once jugadores únicos mediante optimización de la suma de encajes.
- Exclusión manual de jugadores y preferencias por partida guardadas en el navegador.
- Roles diferenciados con posesión y sin posesión, válidos para la posición según el catálogo utilizado.
- Explicaciones por atributos, familiaridad posicional, comparación con la siguiente alternativa y puntos débiles.
- Instrucciones individuales y colectivas, distinguiendo comportamiento del rol, mantener opciones estándar y ajustes sugeridos.
- Ficha abierta desde una táctica: muestra los roles asignados en ese once. Ficha desde plantilla: muestra el mejor encaje individual.
- Mismo procedimiento para juveniles y cedidos.
- Comparación de juveniles con opciones del primer equipo, focos de entrenamiento y recomendación orientativa de prueba/promoción.
- Exportación JSON y descarga TXT de la configuración de cada jugador.

No se generan archivos de táctica `.fmf`; las indicaciones se trasladan manualmente al juego.

### Cómo calcula el encaje

Es una heurística propia, no el sistema interno de FM:

```text
encaje = (80% promedio de atributos del rol + 20% promedio de atributos del estilo)
         × (0,25 + 0,75 × familiaridad posicional / 20)
```

Los promedios se llevan a escala 0–100. Los atributos de referencia de cada rol tienen igual peso. Para armar el once se ponderan las funciones con y sin balón 80/20.

Hay restricciones propias: limitar ciertos roles de banda según el estilo, evitar un portero con salida arriesgada si faltan atributos técnicos, exigir sacrificio/resistencia para algunos roles presionantes y moderar ciertas instrucciones según el plantel.

La referencia juvenil es la tercera opción disponible del primer equipo con familiaridad de al menos 15/20 en una posición de la función. Con menos opciones se usa la última; sin opciones no se recomienda promoción. Una diferencia de hasta −3 puntos permite sugerir una prueba. Los focos de entrenamiento son atributos relevantes de menor valor. **No se predicen potencial ni crecimiento.**

## 5. Trabajo de nombres exactos de FM26: qué se comprobó y qué falta

### Instalación encontrada

```text
C:\Program Files (x86)\Steam\steamapps\common\Football Manager 26
```

Steam App ID: **3551340**. Build instalado identificado: **23583635**. Se vio **FM26 26.3.2** en el menú y se confirmó visualmente **Español latinoamericano** en Preferencias. No se cambiaron esos ajustes.

Se copiaron para análisis, sin modificar la instalación:

```text
data/game_simulation/languages.fmf
data/game_simulation/templates/user_folder/languages/example.ltf
```

Las copias y resultados exploratorios están en `.tmp/fm26-localization/`.

### Extracción realizada

Se interpretó el contenedor FMF y los archivos LTC del idioma. Se emparejaron inglés, latinoamericano y España por token numérico, no por semejanza de texto.

Se creó `scripts/extract_fm26_locale.py`, que reproduce la extracción y valida las claves seleccionadas contra sus nombres ingleses. Genera `fm_app/data/fm26_es419.json`, de aproximadamente 83 KB, con las etiquetas necesarias:

- **45 nombres base** que cubren los **55 registros de rol por fase** usados por el motor.
- **8 grupos** de instrucciones individuales y **9 colectivos**.
- Clave, token, desplazamiento en LTC, formas originales, texto sin marcas de formato y contexto del traductor cuando existe.
- Alias cuando el recurso contiene distintas etiquetas para el mismo rol.
- Hashes SHA-256 de los recursos usados y número de build.

Los archivos completos de idioma no se incorporaron al catálogo distribuible. La extracción no requiere tener el juego abierto. El procedimiento exacto está en `docs/fm26-reference.md`.

Ejemplos corregidos:

| Concepto | Etiqueta extraída / diferencia relevante |
|---|---|
| Ball-Playing Goalkeeper | «Portero jugador» en clave 688113; alias «portero con juego de pies» en 696150 |
| Deep-Lying Forward | «delantero sorpresa», distinto de Second Striker |
| Second Striker | «Segundo delantero» |
| Passing Risk | «Riesgo en los pases» |
| Forward Runs | «Carreras hacia adelante» |
| More Often individual | «Más a menudo» |
| More Often colectivo, presión | «Más insistente» |
| Standard, entradas individuales | «Normal» |
| Standard, línea defensiva | «Estándar» |

Se conservaron las mayúsculas y los textos literales, incluso traducciones extrañas del recurso: por ejemplo, la clave latinoamericana 394442 para Higher en línea defensiva dice «Alto»; la misma clave española dice «Alta».

`ENGINE_VERSION` pasó a **5**, para incorporar las claves específicas de contexto para Sí/No en «Aguantar el balón» (claves 651226 y 651227 con contexto del traductor), los alias de recepción equilibrada y las etiquetas confirmadas de categorías. Se actualizaron el extractor, el backend, la interfaz, las pruebas y la documentación.

### Límite importante: archivo verificado no equivale a menú completo verificado

El recurso conserva etiquetas de distintas vistas y posiblemente de interfaces anteriores. Por eso no basta encontrar un texto para asegurar cuál muestra un control concreto durante la ejecución.

- `resource_verified = true`: se comprobó la etiqueta en el archivo instalado.
- `runtime_verified = false` y `menu_verified_es = false`: no se completó la comprobación de cada control en ejecución.
- Algunas opciones llevan `binding_status = provisional`, especialmente claves genéricas sin contexto específico, Sí/No y otros casos documentados.
- Los alias se muestran como otras etiquetas del archivo; no se afirma qué vista concreta usa cada uno sin evidencia adicional.

El control visual del juego **se interrumpió cuando el usuario pulsó Escape**. Se detuvieron las acciones de mouse/teclado y se continuó solo con archivos y código. No se cargó, avanzó ni guardó una partida desde esa sesión visual. Una IA que continúe debe tratar esa interrupción como contexto, no continuar automáticamente aquella sesión de control.

También se exploraron dos bundles de Unity con `UnityPy==1.25.4`. Produjeron datos de UI en `.tmp/fm26-localization/unity/`, pero no una vinculación estática concluyente entre todos los controles y las claves de idioma. No conviene repetir búsquedas masivas que impriman esos archivos completos. UnityPy fue una herramienta exploratoria; la aplicación y el extractor final de idioma no dependen de ella.

Se consultó una guía de ingeniería inversa, pero no se instalaron/configuraron motores REA ni se modificó la configuración de Codex. Los resultados descritos son análisis propios con Python/Zstandard, no evidencia emitida por herramientas REA.

## 6. Archivos principales

| Archivo | Responsabilidad |
|---|---|
| `fm_app/server.py` | Servidor HTTP local, importaciones, estado, persistencia, API y caché |
| `fm_app/extraction.py` | Lector genérico de la partida y reportes de validación |
| `fm_app/recommendations.py` | Puntuación, selección de roles, asignación del once, explicaciones y juveniles |
| `fm_app/fm26.py` | Catálogo de roles usados, instrucciones, selección contextual de idioma y versión del motor |
| `fm_app/tactics.py` | Atributos, estilos y estructuras de formación |
| `fm_app/analysis.py` | Punto de entrada/reexportación del análisis |
| `fm_app/data/fm26_catalog.json` | Referencia factual externa: 74 registros de roles y opciones de instrucciones |
| `fm_app/data/fm26_es419.json` | Etiquetas seleccionadas del idioma instalado y su procedencia |
| `web/app.js`, `web/style.css`, `web/index.html` | Interfaz sin proceso de compilación |
| `scripts/extract_fm26_locale.py` | Extracción reproducible del vocabulario LATAM |
| `scripts/update_fm26_catalog.py` | Actualización externa del catálogo, requiere red; no participa en importar partidas |
| `scripts/check_http.py` | Comprobación del servidor y carga completa opcional |
| `tests/test_analysis.py`, `tests/test_import.py`, `tests/test_fm26_roles.py` | Pruebas de análisis, importación y localización |
| `README.md` | Uso, instalación y límites generales |
| `docs/fm26-reference.md` | Fuentes, claves, alcance y procedimiento de idioma |
| `data/imports/current.json` | Puntero a la última importación válida |
| `data/imports/<id>/output/validation.json` | Reporte real de extracción |
| `data/imports/<id>/output/analysis_bundle.json` | Análisis persistido versionado |

`scripts/extract_brighton.py`, `scripts/create_review.py` y ciertos archivos de `data/output/` pertenecen a la prueba inicial. La aplicación actual usa el extractor genérico; no debe volver a depender de Brighton fijo.

API principal: `GET /api/data`, `GET /api/status`, `GET /api/jobs/<id>`, `POST /api/analyze`, `PUT /api/import`. El script HTTP muestra los encabezados y payloads que exige el servidor.

## 7. Qué se probó

Última ejecución al terminar la implementación: **20 pruebas aprobadas**.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --check web/app.js
.\.venv\Scripts\python.exe -m py_compile fm_app/fm26.py fm_app/recommendations.py fm_app/server.py scripts/extract_fm26_locale.py
# Con el servidor funcionando:
.\.venv\Scripts\python.exe scripts/check_http.py
```

Cobertura relevante:

- Asignación global contrastada con fuerza bruta y once sin duplicados.
- Exclusiones, inferiores, comparación por posición y filtrado de datos ocultos.
- Roles por fase/posición e instrucciones válidas según el catálogo.
- Explicaciones para jugadores reales en los cuatro estilos, incluidos juveniles y cedidos.
- Separación de nombres latinoamericanos por contexto y conservación de alias.
- Importación sin exports previos, conservación del análisis ante fallos, restauración de estilos e invalidación de caché por versión de motor.
- HTTP: datos y análisis válidos, etiquetas nuevas presentes, rechazo de una carga inválida sin perder la partida anterior y rechazo de un origen ajeno.

Algunas pruebas de integración usan los exports reales de `data/output/`. Esos archivos están excluidos por `.gitignore`: al mover solo el código a otra máquina hay que proporcionar/regenerar esa fixture o adaptar las pruebas. La aplicación no necesita esa fixture para importar una partida nueva.

La última comprobación de esta actualización no incluyó un recorrido visual nuevo de la app ni todos los menús del juego. No presentar las pruebas automatizadas como evidencia de coincidencia visual total.

## 8. Qué queda por hacer, en orden sugerido

### A. Cerrar la solicitud actual: coincidencia exacta con los menús LATAM

1. **Completado:** Se resolvieron vinculaciones que antes eran provisionales: `hold_up_ball_ip` vincula ahora las claves 651226 («Sí») y 651227 («No») con notas de contexto del traductor específicas de instrucciones individuales de táctica, eliminando su estado provisional. Se añadieron alias contextuales para `pass_reception_ip` (clave 682315).
2. **Completado:** `ENGINE_VERSION` se actualizó a **5**, regenerando la localización y la caché persistida.
3. Confirmar en las vistas del juego la concordancia de las variantes largas/cortas de instrucciones y las opciones Standard genéricas.
4. Confirmar qué comportamientos vienen fijados por el rol y cuáles son ajustes editables en la UI de FM26.
5. Revisar visualmente interfaz y descargas TXT con jugadores reales del primer equipo y juveniles en ambas fases (comprobado programáticamente con Szoboszlai y Neuendorff).

### B. Confirmar la fidelidad de la lectura de partidas

1. **Completado:** Se identificaron y mapearon los nombres reales de los grupos: Grupo 0 = «Primer equipo», Grupo 1 = «Sub-21» (EFL Trophy) y Grupo 2 = «Sub-18» (UEFA Youth League), eliminando la etiqueta de «sin confirmar» y mostrándolos en centro del club, filtros y configuración.
2. **Completado:** Se extendió la validación de consistencia y rangos (atributos y posiciones 1-20, edades 12-65, campos requeridos) a todos los jugadores cedidos fuera (`loaned_out`), comprobando 0 errores en Brighton y Liverpool.
3. Contrastar visualmente fichas reales de jugadores en la interfaz del juego frente a las exportadas.
4. Probar otros guardados/versiones antes de afirmar compatibilidad general con cualquier FM26.

### C. Mejorar la calidad táctica y de desarrollo

- Evaluar recomendaciones en situaciones reales del juego. Los índices actuales no garantizan rendimiento ni una táctica óptima.
- Incorporar, si se decide ampliar el producto, disponibilidad, sanciones, pie preferido por banda, familiaridad táctica, calendario/carga y contexto del rival. Actualmente no se verifican para decidir el once.
- Ampliar cobertura de roles solo con datos coherentes. `Stopping Centre-Back` está excluido por discrepancias entre referencias sobre sus instrucciones.
- Afinar planes juveniles de minutos, cesiones y entrenamiento con contexto real; el estado actual prioriza encaje presente y atributos bajos, no potencial futuro.

### D. Trabajo de producto opcional, no completado ni requerido para la prueba local

Distribución/instalador, historial cómodo de múltiples partidas, selección entre varios clubes gestionados, compatibilidad con otros FM y exportación de tácticas. No se implementaron y no deben confundirse con funciones existentes.

## 9. Fuentes y límites de acceso para continuar

Referencias utilizadas, detalladas en la documentación:

- `https://github.com/rhiever/fmsave`
- `https://fmsidekick.com/database/roles`
- `https://fmsidekick.com/database/player_instructions`
- `https://fmsidekick.com/database/team_instructions`
- `https://fm.guidetofootball.com/fm26/roles/`
- Publicaciones oficiales de Football Manager sobre roles y fases.
- Los recursos instalados del propio juego para el texto latinoamericano.

Las fuentes web se consultaron durante el desarrollo anterior; no sustituyen la evidencia del menú instalado. Si se actualiza el catálogo externo hay que revisar compatibilidad con las selecciones locales.

En este entorno algunas lecturas del juego y llamadas al servidor local requirieron ejecución fuera del sandbox porque la vista restringida no detectaba la instalación nueva. Eso no significa que el juego no esté instalado. Las escrituras de implementación se hicieron en el proyecto; no se modificaron binarios, archivos del juego ni partidas originales.

Para compartir con otra IA, adjuntar este informe y el código si se espera que lo edite. Las rutas locales no serán accesibles para una IA que no tenga acceso a esta computadora. `.venv/`, `.tmp/`, `data/input/`, `data/output/` y `data/imports/` están excluidos por `.gitignore`; un envío de solo código no lleva los guardados ni las pruebas reales. Los recursos completos de idioma no son necesarios para entender la arquitectura: el JSON pequeño conserva las etiquetas seleccionadas y su procedencia.

## 10. Texto breve para iniciar la próxima conversación

> Estoy continuando Touchline, una aplicación local para analizar partidas de FM26 y recomendar tácticas, roles e instrucciones para primer equipo, inferiores y cedidos. Adjunto un informe del estado real y el código. Ya lee `.fm` con fmsave y funciona con Brighton y Liverpool. Mi idioma es Español latinoamericano. La prioridad es terminar de comprobar que los nombres de roles e instrucciones coincidan exactamente con las vistas de mi juego: ya se extrajeron los textos, pero hay variantes y bindings pendientes. Revisá primero el informe, `fm_app/fm26.py`, `fm_app/data/fm26_es419.json` y `docs/fm26-reference.md`. Quiero continuar desde lo implementado y distinguir lo comprobado de las heurísticas o pendientes.
