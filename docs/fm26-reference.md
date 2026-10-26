# Referencia de roles e instrucciones de FM26

Consulta: 24 de octubre de 2026. La partida probada es FM26 26.3.2.

La aplicación conserva hechos del catálogo público de FM Sidekick: nombres originales, fases, posiciones, atributos de referencia, instrucciones del rol y valores posibles. No conserva sus descripciones o análisis editorial. Las explicaciones de Touchline se generan a partir de los atributos reales de cada jugador.

Fuentes consultadas:

- [Catálogo de roles](https://fmsidekick.com/database/roles)
- [Instrucciones individuales](https://fmsidekick.com/database/player_instructions)
- [Instrucciones colectivas](https://fmsidekick.com/database/team_instructions)
- [Role Explorer, comprobaciones declaradas sobre 26.3.2](https://fm.guidetofootball.com/fm26/roles/)
- [Sports Interactive: sistema de fases y nuevos roles, en español](https://www.footballmanager.com/es/fm26/funcionalidades/con-posesion-y-sin-posesion-la-nueva-evolucion-tactica-de-fm26)
- [Sports Interactive: delanteros abiertos y roles defensivos de banda](https://www.footballmanager.com/es/the-dugout/como-dominar-al-delantero-escorado-en-fm26)

## Alcance de la verificación

Los nombres originales y valores recomendados existen en el catálogo consultado. La selección utiliza un subconjunto de sus 74 registros y valida posición/fase. No pretende cubrir todo el catálogo de 82 registros del otro explorador. Se excluye Stopping Centre-Back: las referencias discrepan sobre su presión. No se usan tareas Defender/Apoyar/Atacar del sistema anterior.

Los nombres españoles proceden ahora del archivo **Español latinoamericano** de la instalación Steam del usuario: FM26 **26.3.2**, build **23583635**. Se comprobó visualmente la versión y el idioma seleccionado en Preferencias. No se completó el recorrido visual de todos los menús: el usuario interrumpió el control con Escape. `menu_verified_es` y `runtime_verified` permanecen en `false`; `resource_verified` distingue el texto comprobado en el archivo.

`fm_app/data/fm26_es419.json` conserva las etiquetas seleccionadas para Touchline. El alcance histórico inicial era de 55 registros de rol; la ampliación a 79 roles y las instrucciones colectivas está documentada en `docs/relevamiento-fm26-2026-10-25/`. Cada etiqueta incluye su procedencia y contexto cuando están disponibles. Los hashes SHA-256 identifican los archivos de origen. Los archivos completos del juego no forman parte de la entrega: los extractores pueden generarlos en un área temporal, mientras que los textos seleccionados y las evidencias necesarias se conservan en la documentación.

La selección se realiza por clave y contexto, no mediante un diccionario global inglés/español. Por ejemplo, More Often es «Más a menudo» en la presión individual y «Más insistente» en la colectiva. Standard es «Normal» en entradas individuales y «Estándar» en la línea defensiva. Higher figura literalmente como «Alto» en la clave latinoamericana de línea defensiva, aunque en España esa clave dice «Alta»; no se corrige editorialmente la traducción instalada.

El archivo contiene variantes de un mismo rol: Ball-Playing Goalkeeper es «Portero jugador» (688113, `player_instructions; player role`) y «portero con juego de pies» (696150, posición de portero). La app muestra la primera y conserva la segunda como otra etiqueta del archivo. Deep-Lying Forward corresponde a «delantero sorpresa» (688112), mientras que Second Striker es «Segundo delantero» (688140). Las variantes conservadas no prueban qué vista concreta carga cada clave durante la ejecución.

Se resolvieron vinculaciones que antes eran provisionales: `hold_up_ball_ip` cuenta ahora con las claves verificadas por contexto del traductor `651226` («Sí») y `651227` («No»), con notas específicas para la instrucción individual de aguantar el balón (`binding_status = context_selected`), conservando las claves genéricas como alias. `pass_reception_ip` incorpora el alias contextual `682315` («Equilibrada») junto a `682664`. Los valores estándar genéricos (`682178`) se conservan marcados como provisionales donde el recurso no ofrece una clave unívoca con contexto específico.

Se confirmaron asimismo las categorías reales de plantilla en el fútbol inglés: Grupo 0 corresponde a «Primer equipo», Grupo 1 a «Sub-21» (competición EFL Trophy y reservas) y Grupo 2 a «Sub-18» (UEFA Youth League y juveniles), reflejados automáticamente en la interfaz. La validación del extractor se extendió además a los jugadores cedidos fuera (`loaned_out`). La versión del motor (`ENGINE_VERSION`) se actualizó a **5**.

Para reproducir la extracción sin modificar la instalación:

```powershell
.venv\Scripts\python.exe scripts/extract_fm26_locale.py --archive 'C:\Program Files (x86)\Steam\steamapps\common\Football Manager 26\data\game_simulation\languages.fmf' --template 'C:\Program Files (x86)\Steam\steamapps\common\Football Manager 26\data\game_simulation\templates\user_folder\languages\example.ltf' --build 23583635 --version 26.3.2
```

El script valida las claves contra los nombres ingleses antes de escribir. Una nueva versión puede requerir revisar las selecciones; no se actualizan durante una importación de partida. El análisis de los archivos se realizó con Python y Zstandard; no es una traza de ejecución ni un registro de evidencia generado por REA.

Las instrucciones del rol se distinguen de los ajustes sugeridos y las opciones estándar. El catálogo describe comportamientos; eso no demuestra que todos sean controles independientes ni que estén bloqueados en la interfaz. Si hay una orden propia del rol, no se recomienda la contraria.

## Motor de recomendación

Los atributos de referencia tienen peso uniforme; la puntuación combina 80% atributos del rol con 20% atributos del estilo, y penaliza la falta de familiaridad en la posición concreta. La fórmula es propia, no la del sistema de estrellas de FM. Se evalúan por separado los roles de ambas fases, ponderados 80/20 para armar el once.

En banda, el estilo limita los roles candidatos. Un jugador con pases, decisiones o primer toque por debajo de 12 no recibe Ball-Playing Goalkeeper. Los roles presionantes de lateral/medio solo se consideran en presión alta con sacrificio y resistencia de al menos 13. Los umbrales son reglas propias, no requisitos oficiales del juego.

Cada elección incluye evidencia de atributos, posición, comparación con la siguiente alternativa, riesgos e instrucciones. Los juveniles y cedidos usan el mismo procedimiento. Las fichas abiertas desde la táctica muestran los roles del once; las demás muestran el mejor encaje individual. La descarga TXT permite trasladar manualmente la configuración; no genera archivos `.fmf`.

El análisis persistido se versiona para recalcular resultados antiguos cuando cambia el motor. El script `scripts/update_fm26_catalog.py` actualiza el vocabulario; requiere red, no forma parte de la importación de partidas y no envía datos de usuarios.
