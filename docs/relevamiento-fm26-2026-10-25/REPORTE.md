# FM26: posiciones, roles e instrucciones para reconstruir Touchline

Relevamiento del 25 de octubre de 2026. Idioma **Español latinoamericano**, comprobado en Preferencias. Versión visible **26.3.2.2329565 (m.e v26.3.0.1)**. Fecha de la partida: 14/9/2028, 13:15. Evidencia: [054](capturas/054-preferencias.jpg), [060](capturas/060-version-juego.jpg).

## 1. Qué contiene y cómo interpretar la evidencia

Este paquete reúne **79 definiciones de rol por fase**, **14 familias de posición**, **15 grupos de instrucciones individuales y sus 45 opciones**, ocho vistas colectivas y 326 capturas actuales. Se adjuntan 1680 registros tácticos seleccionados de la instalación, con claves, contexto del traductor y huellas de los archivos.

**La revisión visual completa de todas las combinaciones puesto × rol × fase × alcance no está terminada.** Los 15 menús individuales sí se abrieron y sus conjuntos de opciones se leyeron. Las descripciones completas de los 79 roles se obtuvieron de los recursos instalados. Las familias de compatibilidad combinan el catálogo previo y los menús observados; no constituyen una matriz oficial de disponibilidad.

Cada ficha distingue `current_ui_evidence` de `description_resource`. Una captura prueba lo mostrado en ese contexto, no todas las variantes del rol. Una cadena instalada prueba que existe ese texto, no que esté habilitado en un menú actual. El anexo conserva textos antiguos y variantes; no deben habilitarse roles solo porque exista su nombre.

Las lecturas de recursos se hicieron con el lector Python local FMF/LTC. No son trazas de ejecución, descompilación del motor ni registros REA. Los IDs de este paquete son IDs de referencia para la aplicación. **Una clave KEY de localización no es el número de rol dentro de la partida.**

La navegación no avanzó la fecha ni guardó la partida. Se creó una copia local de la táctica para el relevamiento. La captura 162 documenta una restauración intermedia; después el usuario autorizó usar esta partida de prueba sin restaurar jugadores ni roles. El último estado observado conserva roles de prueba: CP 3-2-4-1 y SP 4-2-2-2 ancho con mediocampista defensivo. Los cambios de formación renombraron automáticamente la táctica. [062](capturas/062-continuacion-tactica-inicial.jpg), [106](capturas/106-respaldo-guardado.jpg), [162](capturas/162-once-restaurado.jpg), [244](capturas/244-formacion-relevamiento-doble-pivote.jpg), [275](capturas/275-central-dobla-aguantar-confirmado.jpg).

**Actualización de la segunda pasada:** los 79 de 79 roles tienen ahora evidencia visual de menú/ficha. Se cerraron los 24 roles que antes estaban pendientes. Hay 80 observaciones de instrucciones, incluidas restricciones parciales; esto no equivale a todas las combinaciones posibles. Los detalles nuevos están en `verificacion-adicional-roles.json` y `verificacion-adicional-mecanicas.json`.

**Cierre actualizado:** 79/79 roles tienen panel de instrucciones registrado en al menos un contexto; 79/79 tienen lista de atributos clave cotejada en la ficha. Quedan 0 paneles, 0 listas de atributos y 0 valores bloqueados sin transcribir. La última continuación completó los 13 paneles solicitados y confirmó los tres valores antes ocultos. Ver `PENDIENTES.md` y `cobertura-y-pendientes.json` para los límites que siguen abiertos.

## 2. Modelo táctico observado

El mismo jugador tiene una posición y un rol con posesión (CP) y otra posición y otro rol sin posesión (SP). El once conserva la identidad de sus jugadores al cambiar de fase. La vista combina ambas asignaciones, o permite ver CP, SP y ambos dibujos. La táctica actual se anuncia como **4-1-2-3 MD Amplio CP y 4-4-1-1 2MD SP** en la ayuda interna. [056](capturas/056-fmpedia-tacticas.jpg).

Un rol tiene comportamientos inherentes además de las órdenes editables. FMPedia explica que modifica la posición base con el tiempo y entre fases, y da el ejemplo de un extremo abierto que tiende a regatear más. Por eso un rol no se reconstruye únicamente como una colección de selectores de instrucciones. [057](capturas/057-fmpedia-roles.jpg).

Las tarjetas muestran nombre, adecuación en estrellas, rasgos de comportamiento, descripción, atributos clave, órdenes resumidas y una animación. Las estrellas y los números de atributos corresponden al jugador contextual: no son constantes del rol. Al recorrer el selector de puestos, no asumir que la ficha cambió automáticamente al jugador que ocupa ese otro puesto.

Se ofrecen alcances **Posición / Personalizada** en roles y **Posición / Jugador** en instrucciones. El modelo debe guardar el alcance y la identidad del jugador para los ajustes personales. Una captura del alcance Posición no basta para certificar todos los valores efectivos de un jugador con personalización.

### Once de la primera pasada

Asignaciones leídas en la tabla y los dibujos actuales. Las familias de posición son la convención del informe; no IDs decodificados de la partida. [053](capturas/053-tactica-final.jpg), [056](capturas/056-fmpedia-tacticas.jpg).

| Jugador | Puesto CP → SP | Rol CP | Rol SP | Abreviaturas vistas CP / SP |
|---|---|---|---|---|
| Bart Verbruggen | GK → GK | Portero con salida | Portero líbero | PCS / POL |
| Djed Spence | DR → DR | Carrilero | Lateral / Lateral defensivo | CR / LAT |
| Luka Vušković | DC → DC | Central con salida | Central / Defensa central | CCS / DFC |
| Pau Cubarsí | DC → DC | Central con salida | Central / Defensa central | CCS / DFC |
| Miloš Kerkez | DL → DL | Carrilero | Lateral / Lateral defensivo | CR / LAT |
| Aleksandar Pavlović | DM → DM | Organizador defensivo / Organizador retrasado | Mediocentro defensivo | ORD / MD |
| Yasin Ayari | MC → AMC | Organizador adelantado | Mediapunta | OAD / MP |
| Adam Wharton | MC → DM | Mediocampista organizador / Mediocentro organizador | Mediocentro defensivo | MOR / MD |
| Dominik Szoboszlai | AMR → MR | Extremo invertido | Mediocampista abierto | EXI / MA |
| Florian Wirtz | AML → ML | Extremo invertido | Mediocampista abierto | EXI / MA |
| Hugo Ekitiké | STC → STC | Delantero de apoyo | Delantero centro | DDA / DLC |

### Once de la continuación: flick barcelona 26

El usuario tenía otra táctica abierta al retomar. Esta tabla conserva la referencia inicial de la continuación y la restauración intermedia; no representa los roles de prueba del último estado observado. [062](capturas/062-continuacion-tactica-inicial.jpg), [162](capturas/162-once-restaurado.jpg).

| Jugador | Puesto CP y SP | Rol CP | Rol SP |
|---|---|---|---|
| Bart Verbruggen | GK | Portero con salida | Portero líbero |
| Djed Spence | DR | Lateral interior | Lateral / Lateral defensivo |
| Luka Vušković | DC-right | Central con salida | Central / Defensa central |
| Pau Cubarsí | DC-left | Central con salida | Central / Defensa central |
| Miloš Kerkez | DL | Carrilero | Lateral / Lateral defensivo |
| Aleksandar Pavlović | DM | Organizador defensivo / Organizador retrasado | Mediocentro fijo |
| Yasin Ayari | MC-right | Organizador adelantado | Mediocampista presionante |
| Adam Wharton | MC-left | Mediocampista entre líneas | Mediocampista presionante |
| Dominik Szoboszlai | AMR | Delantero interior | Extremo |
| Hugo Ekitiké | AMC | Mediocampista entre líneas | Mediapunta estacionario |
| Florian Wirtz | AML | Delantero interior | Extremo |

## 3. Posiciones y subpuestos

Los siguientes códigos son la convención del programa actual. Las abreviaturas españolas varían entre la ficha del futbolista y el dibujo. No se han descifrado aquí los IDs de puestos del archivo `.fm`.

| Código de referencia | Rótulo de referencia | Posición | Distinción necesaria |
|---|---|---|---|
| GK | POR | Portero | Zona del arco. |
| DL | DF (I) | Defensa izquierdo / lateral | Banda de la línea defensiva. |
| DR | DF (D) | Defensa derecho / lateral | Banda de la línea defensiva. |
| DC | DF (C) | Defensa central | Distinguir puesto central y puestos laterales de una zaga; no perder el subpuesto. |
| WBL | CR (I) | Carrilero izquierdo | Altura de carrilero; no equivale a lateral aunque comparta roles CP. |
| WBR | CR (D) | Carrilero derecho | Altura de carrilero; no equivale a lateral aunque comparta roles CP. |
| DM | MD | Mediocampista defensivo / mediocentro | Distinguir pivote central único y subpuestos de doble/triple pivote. |
| MC | ME (C) | Mediocampista central | Distinguir centro e interiores a sus costados. |
| ML | ME (I) | Mediocampista izquierdo | Banda a altura de mediocampo. |
| MR | ME (D) | Mediocampista derecho | Banda a altura de mediocampo. |
| AMC | MP (C) | Mediapunta central | Distinguir centro y medias puntas en los canales. |
| AML | MP (I) | Mediapunta izquierdo / extremo | Banda adelantada. |
| AMR | MP (D) | Mediapunta derecho / extremo | Banda adelantada. |
| STC | DL (C) | Delantero centro | Distinguir punta central y puntas de los canales. |

La familia central necesita subpuesto: centro, centro-izquierda o centro-derecha, según la línea. Conservar también el dibujo y los vecinos. No representar todo como un simple `DC`, `DM`, `AMC` o `STC` si eso hace perder restricciones reales.

Observaciones actuales de disponibilidad:

- En un central de la línea de dos se ven cuatro roles CP: Central, Central avanzado, Central con salida y Central práctico. No aparecen Central abierto ni Central que dobla en ese contexto. [013](capturas/013-menu-central-cp.jpg).
- En el pivote central único CP se ven Mediocentro defensivo, Organizador defensivo y Medio cierre; el catálogo de referencia incluye además los dos todoterreno para otros subpuestos/contextos. [015](capturas/015-roles-mediocentro-cp.jpg).
- En el doble pivote SP aparecen cinco variantes, incluida cobertura abierta. [038](capturas/038-roles-md-sp.jpg), [039](capturas/039-roles-md-sp-inferiores.jpg).
- En una línea de tres centrales se comprobaron Central abierto y Central que dobla CP, y Central abierto, Zaguero abierto y Central de cobertura abierta SP. [123](capturas/123-central-exterior-cp-menu.jpg), [126](capturas/126-central-dobla.jpg), [134](capturas/134-central-exterior-sp-menu.jpg), [139](capturas/139-central-cobertura-abierta.jpg).
- En doble pivote CP se comprobaron los dos todoterreno que no aparecían en el pivote central único. [128](capturas/128-doble-pivote-cp-menu.jpg), [129](capturas/129-todoterreno-dm.jpg), [131](capturas/131-organizador-todoterreno.jpg).
- Un AMC central SP y un punta central único SP muestran tres roles cada uno. Al pasar a dos jugadores en la línea se comprobaron Mediapunta estacionario con salida y Delantero centro estacionario con salida. Se verificó el caso de pareja; no se deduce de ello una regla para todo dibujo. [037](capturas/037-roles-mediapunta-sp.jpg), [109](capturas/109-mediapunta-estacionario-salida.jpg), [114](capturas/114-delantero-salida.jpg).

## 4. Catálogo de roles por posición y fase

La siguiente tabla es la unión de familias de referencia, **no una orden de habilitar todos los roles en todos los subpuestos**. Los costados se agrupan cuando comparten catálogo; todavía se debe validar la matriz contextual.

| Familia | Con posesión | Sin posesión |
|---|---|---|
| Portero | Portero; Portero con salida; Portero práctico | Portero; Portero líbero; Portero entre palos |
| Centrales | Central / Defensa central; Central avanzado; Central con salida; Central práctico; Central abierto; Central que dobla | Central / Defensa central; Zaguero; Defensa central de cobertura; Central abierto; Central de cobertura abierta; Zaguero abierto |
| Laterales | Lateral; Carrilero; Carrilero interior; Lateral interior; Carrilero organizador | Lateral / Lateral defensivo; Lateral de contención; Lateral presionante |
| Carrileros | Carrilero; Carrilero interior; Carrilero organizador; Carrilero avanzado | Carrilero; Carrilero de contención; Carrilero presionante |
| Mediocentros | Mediocentro defensivo; Organizador defensivo / Organizador retrasado; Medio cierre; Mediocampista todoterreno; Organizador todoterreno | Mediocentro defensivo; Mediocentro de repliegue; Mediocentro presionante; Mediocentro fijo; Mediocampista defensivo de cobertura abierta |
| Mediocampistas centrales | Mediocampista / Centrocampista; Mediocampista abierto; Mediocampista organizador / Mediocentro organizador; Mediapunta; Organizador adelantado; Mediocampista entre líneas | Mediocampista; Mediocampista presionante; Mediocampista fijo; Mediocampista de cobertura abierta |
| Medios de banda | Mediocampista abierto; Extremo; Extremo invertido; Extremo organizador | Mediocampista abierto; Mediocampista abierto con retroceso; Mediocampista abierto estacionario |
| Mediapunta central | Mediapunta; Organizador adelantado; Mediocampista entre líneas; Mediapunta libre; Segundo delantero | Mediapunta; Mediapunta con retroceso; Mediapunta estacionario; Mediapunta de ruptura con salida (nombre de recurso) |
| Extremos / mediapuntas de banda | Extremo; Extremo invertido; Extremo organizador; Delantero interior; Delantero abierto | Extremo; Extremo con retroceso; Extremo de salida invertida; Extremo estacionario |
| Delanteros | Delantero de apoyo; Delantero centro; Delantero torre; Ariete; Delantero entre líneas; Falso nueve | Delantero centro; Delantero centro con retroceso; Delantero centro estacionario; Delantero centro de ruptura con salida (nombre de recurso) |

### Descripciones completas de los 79 roles

Texto de los recursos instalados. Se conserva la traducción del recurso aunque difiera del rótulo del menú. Los nombres de referencia sin captura actual no deben presentarse como transcripción actual verificada. En JSON están también el inglés y las variantes españolas.

#### 1. Portero · CP

ID de referencia: `goalkeeper_ip`. Familias: GK. Nombre inglés: Goalkeeper. Descripción: KEY-690521.

Revisión visual actual: [menú/ficha](capturas/164-portero-cp.jpg).

El Portero puede distribuir el balón de diferentes maneras, dependiendo de la estrategia de juego del equipo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): handling, aerial_reach, command_of_area, communication, positioning, reflexes, agility, concentration.

Rótulo verificado en esta pasada: **Portero**.

Atributos clave leídos en la ficha actual: Blocaje, Alcance aéreo, Mando en el área, Comunicación, Colocación, Reflejos, Agilidad, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: GK, alcance Posición. [Panel](capturas/166-portero-cp-sin-tooltip.jpg).

Controles bloqueados: attacking_width_ip = Standard; dribbling_direction_ip = Standard; forward_runs_ip = Standard; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; shoot_ip = Standard; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: dribbling_frequency_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 2. Portero con salida · CP

ID de referencia: `ball_playing_goalkeeper_ip`. Familias: GK. Nombre inglés: Ball-Playing Goalkeeper. Descripción: KEY-690523.

Revisión visual actual: [menú/ficha](capturas/163-arquero-cp-segunda-pasada.jpg).

El Portero con salida de balón busca desempeñar un papel activo en la construcción del juego de su equipo, moviéndose a menudo fuera de su portería para estar en disposición de recibir el balón.

Alias del recurso KEY-688113: **Portero jugador**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): handling, aerial_reach, command_of_area, communication, kicking, positioning, reflexes, agility.

Rótulo verificado en esta pasada: **Portero con salida**.

Atributos clave leídos en la ficha actual: Blocaje, Alcance aéreo, Mando en el área, Comunicación, Saques de puerta, Colocación, Reflejos, Agilidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Expresiva; Itinerante.

Resumen de instrucciones en la ficha: Arriesgar más. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: GK, alcance position_panel. [Panel](capturas/004-instrucciones-arquero-cp.jpg).

Controles bloqueados: attacking_width_ip = Standard; dribbling_direction_ip = Standard; forward_runs_ip = Standard; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; shoot_ip = Standard; passing_risk_ip = Take More Risks; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: dribbling_frequency_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 3. Portero práctico · CP

ID de referencia: `no_nonsense_goalkeeper_ip`. Familias: GK. Nombre inglés: No Nonsense Goalkeeper. Descripción: KEY-690522.

Revisión visual actual: [menú/ficha](capturas/167-portero-practico-ficha.jpg).

El Portero con criterio tiene un planteamiento cauto, ya que prefiere quedarse más cerca de su portería y tomar los mínimos riesgos posibles cuando tiene el balón en sus pies y lo presionan.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): handling, aerial_reach, command_of_area, communication, positioning, reflexes, agility, concentration.

Rótulo verificado en esta pasada: **Portero práctico**.

Atributos clave leídos en la ficha actual: Blocaje, Alcance aéreo, Mando en el área, Comunicación, Colocación, Reflejos, Agilidad, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Cuidado; Mantiene la posición.

Resumen de instrucciones en la ficha: Tomar menos riesgos; Regatear con menos frecuencia. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: GK, alcance Posición. [Panel](capturas/169-portero-practico-sin-tooltip.jpg).

Controles bloqueados: attacking_width_ip = Standard; dribbling_direction_ip = Standard; dribbling_frequency_ip = Dribble Less; forward_runs_ip = Standard; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; shoot_ip = Standard; passing_risk_ip = Take Fewer Risks; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 4. Portero · SP

ID de referencia: `goalkeeper_oop`. Familias: GK. Nombre inglés: Goalkeeper. Descripción: KEY-690561.

Revisión visual actual: [menú/ficha](capturas/171-portero-sp-ficha.jpg).

El rol de portero tiene la responsabilidad principal de proteger su portería, deteniendo disparos e interceptando centros. Es la última línea de defensa y en quien se confía para que el equipo pueda mantener la valla invicta.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): handling, aerial_reach, command_of_area, communication, positioning, reflexes, agility, concentration.

Rótulo verificado en esta pasada: **Portero**.

Atributos clave leídos en la ficha actual: Blocaje, Alcance aéreo, Mando en el área, Comunicación, Colocación, Reflejos, Agilidad, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: GK, alcance Posición. [Panel](capturas/172-portero-sp-instrucciones.jpg).

Controles bloqueados: pressing_oop = Standard; marking_oop = Standard; marking_target_oop = Standard.

Controles editables: tackling_oop. No extrapolar a otros subpuestos o alcances.

#### 5. Portero líbero · SP

ID de referencia: `sweeper_keeper_oop`. Familias: GK. Nombre inglés: Sweeper Keeper. Descripción: KEY-690562.

Revisión visual actual: [menú/ficha](capturas/170-portero-libero-ficha.jpg).

El Portero líbero es un guardameta proactivo que sale frecuentemente de su área para intentar interceptar pases en profundidad o anticiparse a los delanteros rivales.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): handling, aerial_reach, command_of_area, communication, anticipation, decisions, one_on_ones, reflexes.

Rótulo verificado en esta pasada: **Portero líbero**.

Atributos clave leídos en la ficha actual: Blocaje, Alcance aéreo, Mando en el área, Comunicación, Anticipación, Decisiones, Uno contra uno, Reflejos. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: No se queda bajo los palos; Proactivo.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: GK, alcance position_panel. [Panel](capturas/010-instrucciones-portero-sp.jpg).

Controles bloqueados: pressing_oop = Standard; marking_oop = Standard; marking_target_oop = Standard.

Controles editables: tackling_oop. No extrapolar a otros subpuestos o alcances.

#### 6. Portero entre palos · SP

ID de referencia: `line_holding_keeper_oop`. Familias: GK. Nombre inglés: Line-Holding Goalkeeper. Descripción: KEY-690560.

Revisión visual actual: [menú/ficha](capturas/173-portero-entre-palos-ficha.jpg).

El Portero bajo palos es un guardameta que se mantiene principalmente dentro de su área, dejando la responsabilidad de defender más arriba a sus compañeros.

Alias del recurso KEY-688069: **Portero de línea**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): handling, aerial_reach, command_of_area, communication, positioning, reflexes, agility, concentration.

Rótulo verificado en esta pasada: **Portero entre palos**.

Atributos clave leídos en la ficha actual: Blocaje, Alcance aéreo, Mando en el área, Comunicación, Colocación, Reflejos, Agilidad, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición; Reactivo.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: GK, alcance Posición. [Panel](capturas/174-portero-entre-palos-instrucciones.jpg).

Controles bloqueados: pressing_oop = Standard; marking_oop = Standard; marking_target_oop = Standard.

Controles editables: tackling_oop. No extrapolar a otros subpuestos o alcances.

#### 7. Central / Defensa central · CP

ID de referencia: `centre_back_ip`. Familias: DC. Nombre inglés: Centre-Back. Descripción: KEY-690525.

Revisión visual actual: [menú/ficha](capturas/177-defensa-central-cp-ficha.jpg).

La tarea principal del central es proteger al equipo, situándose en una posición que le permita reaccionar rápidamente ante amenazas ofensivas cuando se pierde la posesión.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, positioning, strength, jumping_reach.

Rótulo verificado en esta pasada: **Defensa central**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, Anticipación, Colocación, Fuerza, Alcance de salto. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición.

Resumen de instrucciones en la ficha: Mantener la posición. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right, alcance Posición. [Panel](capturas/178-defensa-central-cp-instrucciones.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; forward_runs_ip = Make Fewer Runs; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_frequency_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 8. Central avanzado · CP

ID de referencia: `advanced_centre_back_ip`. Familias: DC. Nombre inglés: Advanced Centre-Back. Descripción: KEY-690527.

Revisión visual actual: [menú/ficha](capturas/179-central-avanzado-ficha.jpg).

La primera tarea del central avanzado es proteger al equipo, colocándose en una posición que le permita reaccionar rápidamente ante amenazas ofensivas cuando se pierde la posesión.

Alias del recurso KEY-688115: **Central ofensivo**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, passing, tackling, anticipation, decisions, positioning, technique.

Rótulo verificado en esta pasada: **Central avanzado**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Pases, Entradas, Anticipación, Decisiones, Colocación, Técnica. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se adelanta a posición de mediocampista defensivo; Expresiva.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right, alcance Posición. [Panel](capturas/181-central-avanzado-carreras.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; forward_runs_ip = Make Fewer Runs; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_frequency_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 9. Central con salida · CP

ID de referencia: `ball_playing_centre_back_ip`. Familias: DC. Nombre inglés: Ball-Playing Centre-Back. Descripción: KEY-690524.

Revisión visual actual: [menú/ficha](capturas/175-central-salida-ficha.jpg).

Las dos tareas principales del central con buen juego de pies son proteger al equipo y realizar pases que rompan líneas y pases al hueco desde zonas profundas para subir el balón en el campo.

Alias del recurso KEY-688116: **Central jugador**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, passing, tackling, anticipation, positioning, strength, jumping_reach.

Rótulo verificado en esta pasada: **Central con salida**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Pases, Entradas, Anticipación, Colocación, Fuerza, Alcance de salto. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Expresiva; Mantiene la posición.

Resumen de instrucciones en la ficha: Mantener la posición; Arriesgar más. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right, alcance Posición. [Panel](capturas/176-central-salida-instrucciones.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; forward_runs_ip = Make Fewer Runs; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; passing_risk_ip = Take More Risks; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_frequency_ip, shoot_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 10. Central práctico · CP

ID de referencia: `no_nonsense_center_back_ip`. Familias: DC. Nombre inglés: No-Nonsense Centre-Back. Descripción: KEY-690526.

Revisión visual actual: [menú/ficha](capturas/182-central-practico-ficha.jpg).

El central práctico trata de ser la última línea de protección del equipo, colocándose para estar listo para defender en cualquier momento, mientras procura minimizar los riesgos al manejar el balón.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, positioning, strength, jumping_reach.

Rótulo verificado en esta pasada: **Central práctico**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, Anticipación, Colocación, Fuerza, Alcance de salto. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición; Cuidado.

Resumen de instrucciones en la ficha: Tomar menos riesgos; Regatear con menos frecuencia; Mantener la posición. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right, alcance Posición. [Panel](capturas/183-central-practico-instrucciones.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; dribbling_frequency_ip = Dribble Less; forward_runs_ip = Make Fewer Runs; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; passing_risk_ip = Take Fewer Risks; passing_directness_ip = More Direct; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, shoot_ip. No extrapolar a otros subpuestos o alcances.

#### 11. Central abierto · CP

ID de referencia: `wide_centre_back_ip`. Familias: DC. Nombre inglés: Wide Centre-Back. Descripción: KEY-690528.

Revisión visual actual: [menú/ficha](capturas/124-central-abierto-cp.jpg).

Además de brindar protección defensiva al equipo, al central lateral se le anima a aportar amplitud en la posesión y a apoyar a sus compañeros atacantes por banda, ofreciendo con frecuencia una opción de pase para reciclar el balón desde posiciones profundas.

Alias del recurso KEY-688117: **Central escorado**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, positioning, strength, jumping_reach.

Rótulo verificado en esta pasada: **Central abierto**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, AnticipaciÃ³n, ColocaciÃ³n, Fuerza, Alcance de salto. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posiciÃ³n; Mantenerse abierto.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right-of-three, alcance PosiciÃ³n. [Panel](capturas/274-central-abierto-aguantar-confirmado.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No.

Controles editables: attacking_width_ip, dribbling_frequency_ip, forward_runs_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 12. Central que dobla · CP

ID de referencia: `overlapping_centre_back_ip`. Familias: DC. Nombre inglés: Overlapping Centre-Back. Descripción: KEY-690529.

Revisión visual actual: [menú/ficha](capturas/126-central-dobla.jpg).

El central que dobla combina las responsabilidades de un central y un extremo, buscando proteger al equipo durante las fases iniciales del ataque, mientras se incorpora a posiciones para realizar centros mediante desdoblamientos en el último tercio del campo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): crossing, heading, marking, tackling, anticipation, work_rate, strength, stamina.

Rótulo verificado en esta pasada: **Central que dobla**.

Atributos clave leídos en la ficha actual: Centros, Cabeceo, Marca, Entradas, AnticipaciÃ³n, Sacrificio, Fuerza, Resistencia. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Sube mÃ¡s arriba; Mantenerse abierto.

Resumen de instrucciones en la ficha: Subir mÃ¡s. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right-of-three, alcance PosiciÃ³n. [Panel](capturas/275-central-dobla-aguantar-confirmado.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; forward_runs_ip = Make More Runs; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_frequency_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip. No extrapolar a otros subpuestos o alcances.

#### 13. Central / Defensa central · SP

ID de referencia: `centre_back_oop`. Familias: DC. Nombre inglés: Centre-Back. Descripción: KEY-690563.

Revisión visual actual: [menú/ficha](capturas/184-central-sp-ficha.jpg).

El principal trabajo del Central es tratar de evitar que los delanteros rivales puedan jugar el balón e impedir que puedan generar peligro cuando sea necesario.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, positioning, strength, jumping_reach.

Rótulo verificado en esta pasada: **Defensa central**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, Anticipación, Colocación, Fuerza, Alcance de salto. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right, alcance Posición. [Panel](capturas/185-central-sp-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 14. Zaguero · SP

ID de referencia: `stopping_centre_back_oop`. Familias: DC. Nombre inglés: Stopping Centre-Back. Descripción: KEY-696068.

Revisión visual actual: [menú/ficha](capturas/186-zaguero-ficha.jpg).

Como Tapón, se pide al Central que salga más de su posición para incomodar y enfrentarse a los delanteros rivales, con el objetivo de cortar los ataques desde su origen.

Alias del recurso KEY-688073: **Central marcador**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, positioning, strength, jumping_reach, bravery.

Rótulo verificado en esta pasada: **Zaguero**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, Anticipación, Colocación, Fuerza, Alcance de salto, Valentía. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Sale al encuentro; Con autoridad.

Resumen de instrucciones en la ficha: Presionar con menos insistencia. Este resumen no sustituye el panel de candados.

**Discrepancia observada:** La ficha 186 mostraba resumen Presionar con menos insistencia; el panel activo 187 confirma Más a menudo bloqueado. Priorizar panel, conservar discrepancia.

Contexto de instrucciones comprobado: DC-right, alcance Posición. [Panel](capturas/187-zaguero-instrucciones.jpg).

Controles bloqueados: pressing_oop = More Often.

Controles editables: marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 15. Defensa central de cobertura · SP

ID de referencia: `covering_centre_back_oop`. Familias: DC. Nombre inglés: Covering Centre-Back. Descripción: KEY-690564.

Revisión visual actual: [menú/ficha](capturas/188-central-cobertura-ficha.jpg).

Como cobertura, se le pide al central que adopte un planteamiento más cauto, guardando su posición y esperando para reaccionar a los movimientos ofensivos del rival.

Alias del recurso KEY-688072: **Defensa central con cobertura**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, decisions, positioning, strength, pace.

Rótulo verificado en esta pasada: **Defensa central de cobertura**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, Anticipación, Decisiones, Colocación, Fuerza, Velocidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición; Prudente.

Resumen de instrucciones en la ficha: Presionar con menos insistencia. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right, alcance Posición. [Panel](capturas/189-central-cobertura-instrucciones.jpg).

Controles bloqueados: pressing_oop = Less Often.

Controles editables: marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 16. Central abierto · SP

ID de referencia: `wide_centre_back_oop`. Familias: DC. Nombre inglés: Wide Centre-Back. Descripción: KEY-690513.

Revisión visual actual: [menú/ficha](capturas/135-central-abierto-sp.jpg).

La principal tarea del central lateral es evitar que los atacantes rivales generen ocasiones y marquen goles.

Alias del recurso KEY-688076: **Central escorado**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, positioning, strength, jumping_reach.

Rótulo verificado en esta pasada: **Central abierto**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, AnticipaciÃ³n, ColocaciÃ³n, Fuerza, Alcance de salto. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right-of-three, alcance PosiciÃ³n. [Panel](capturas/136-central-abierto-sp-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 17. Central de cobertura abierta · SP

ID de referencia: `covering_wide_centre_back_oop`. Familias: DC. Nombre inglés: Covering Wide Centre-Back. Descripción: KEY-690511.

Revisión visual actual: [menú/ficha](capturas/139-central-cobertura-abierta.jpg).

Como Cobertura, se le pide al central lateral que adopte un planteamiento más cauto, guardando su posición y esperando para reaccionar a los movimientos ofensivos del rival.

Alias del recurso KEY-688074: **Central de cobertura por banda**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, decisions, positioning, strength, pace.

Rótulo verificado en esta pasada: **Central de cobertura abierta**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, AnticipaciÃ³n, Decisiones, ColocaciÃ³n, Fuerza, Velocidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posiciÃ³n; Cuidadoso.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right-of-three, alcance PosiciÃ³n. [Panel](capturas/140-central-cobertura-abierta-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 18. Zaguero abierto · SP

ID de referencia: `stopping_wide_centre_back_oop`. Familias: DC. Nombre inglés: Stopping Wide Centre-Back. Descripción: KEY-696071.

Revisión visual actual: [menú/ficha](capturas/137-zaguero-abierto.jpg).

Como tapón, se pide al central que salga más de su posición para incomodar y enfrentarse a los delanteros rivales, con el objetivo de cortar los ataques desde su origen.

Alias del recurso KEY-688075: **Central defensivo de banda**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, positioning, strength, jumping_reach, bravery.

Rótulo verificado en esta pasada: **Zaguero abierto**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, AnticipaciÃ³n, ColocaciÃ³n, Fuerza, Alcance de salto, ValentÃ­a. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Sale al encuentro; Con autoridad.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DC-right-of-three, alcance PosiciÃ³n. [Panel](capturas/138-zaguero-abierto-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 19. Lateral · CP

ID de referencia: `full_back_ip`. Familias: DL, DR. Nombre inglés: Full-Back. Descripción: KEY-690530.

Revisión visual actual: [menú/ficha](capturas/192-lateral-defensivo-ficha.jpg).

El lateral es un jugador clave en el fútbol moderno, ya que debe complementar sus funciones defensivas tradicionales con desdoblamientos por la banda para apoyar el juego ofensivo y ayudar a sobrecargar el último tercio del campo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, anticipation, positioning, teamwork, acceleration, concentration.

Rótulo verificado en esta pasada: **Lateral defensivo**.

Atributos clave leídos en la ficha actual: Marca, Entradas, Anticipación, Colocación, Juego en equipo, Aceleración, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición; Mantenerse abierto.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DR, alcance Posición. [Panel](capturas/193-lateral-defensivo-instrucciones.jpg).

Controles bloqueados: freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 20. Carrilero · CP

ID de referencia: `wing_back_ip`. Familias: DL, DR, WBL, WBR. Nombre inglés: Wing-Back. Descripción: KEY-690534.

Revisión visual actual: [menú/ficha](capturas/194-lateral-ofensivo-cp-ficha.jpg).

El carrilero combina las responsabilidades de un lateral y un extremo, proporcionando amplitud al equipo durante el ataque.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): crossing, marking, tackling, teamwork, work_rate, acceleration, stamina, pace.

Rótulo verificado en esta pasada: **Lateral ofensivo**.

Atributos clave leídos en la ficha actual: Centros, Marca, Entradas, Juego en equipo, Sacrificio, Aceleración, Resistencia, Velocidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Sube más arriba; Mantenerse abierto.

Resumen de instrucciones en la ficha: Subir más. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DR, alcance Posición. [Panel](capturas/195-lateral-ofensivo-cp-instrucciones.jpg).

Controles bloqueados: forward_runs_ip = Make More Runs; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 21. Carrilero interior · CP

ID de referencia: `inside_wing_back_ip`. Familias: DL, DR, WBL, WBR. Nombre inglés: Inside Wing-Back. Descripción: KEY-690532.

Revisión visual actual: [menú/ficha](capturas/196-carrilero-interior-ficha.jpg).

Buscando desplazarse hacia zonas centrales del campo a medida que su equipo progresa con el balón, el carrilero por dentro apoya las redes de pase en el centro, además de proporcionar una protección vital contra los contraataques centrales cuando se pierde la posesión.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): passing, tackling, anticipation, decisions, positioning, teamwork, acceleration, composure.

Rótulo verificado en esta pasada: **Carrilero interior**.

Atributos clave leídos en la ficha actual: Pases, Entradas, Anticipación, Decisiones, Colocación, Juego en equipo, Aceleración, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición; Se mueve hacia dentro a posición de mediocampista defensivo.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DR, alcance Posición. [Panel](capturas/197-carrilero-interior-instrucciones.jpg).

Controles bloqueados: hold_up_ball_ip = No; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip. No extrapolar a otros subpuestos o alcances.

#### 22. Lateral interior · CP

ID de referencia: `inside_full_back_ip`. Familias: DL, DR. Nombre inglés: Inside Full-Back. Descripción: KEY-690531.

Revisión visual actual: [menú/ficha](capturas/190-lateral-interior-ficha.jpg).

El lateral por dentro es un jugador cuyo rol especializado implica desplazarse hacia el centro para convertirse en un defensor central adicional durante el ataque.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, positioning, strength.

Rótulo verificado en esta pasada: **Lateral interior**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, Anticipación, Colocación, Fuerza. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición; Se mueve hacia dentro a posición de central.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DR, alcance Posición. [Panel](capturas/191-lateral-interior-instrucciones.jpg).

Controles bloqueados: freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 23. Carrilero organizador · CP

ID de referencia: `playmaking_wing_back_ip`. Familias: DL, DR, WBL, WBR. Nombre inglés: Playmaking Wing-Back. Descripción: KEY-690533.

Revisión visual actual: [menú/ficha](capturas/198-carrilero-organizador-ficha.jpg).

De manera similar al carrilero inverso, el carrilero organizador intentará desplazarse hacia zonas centrales del campo para apoyar las redes de pase centrales y ofrecer una protección vital contra los contraataques por el centro.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): passing, tackling, vision, decisions, first_touch, technique, teamwork, acceleration.

Rótulo verificado en esta pasada: **Carrilero organizador**.

Atributos clave leídos en la ficha actual: Pases, Entradas, Visión, Decisiones, Control, Técnica, Juego en equipo, Aceleración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se mueve hacia dentro a posición de mediocampista defensivo; Expresiva.

Resumen de instrucciones en la ficha: Variar la posición. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DR, alcance Posición. [Panel](capturas/199-carrilero-organizador-instrucciones.jpg).

Controles bloqueados: freedom_of_movement_ip = Roam From Position; hold_up_ball_ip = No.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 24. Carrilero avanzado · CP

ID de referencia: `advanced_wing_back_ip`. Familias: WBL, WBR. Nombre inglés: Advanced Wing-Back. Descripción: KEY-690535.

Revisión visual actual: [menú/ficha](capturas/150-carrilero-avanzado.jpg).

Con un posicionamiento más agresivo que el de un carrilero tradicional, el carrilero avanzado busca jugar lo más arriba y abierto posible.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): crossing, dribbling, off_the_ball, technique, teamwork, work_rate, acceleration, stamina.

Rótulo verificado en esta pasada: **Carrilero avanzado**.

Atributos clave leídos en la ficha actual: Centros, Regate, Desmarques, TÃ©cnica, Juego en equipo, Sacrificio, AceleraciÃ³n, Resistencia. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Sube mÃ¡s arriba; Mantenerse abierto.

Resumen de instrucciones en la ficha: Subir mÃ¡s. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: WBR, alcance PosiciÃ³n. [Panel](capturas/152-carrilero-avanzado-sin-tooltip.jpg).

Controles bloqueados: forward_runs_ip = Make More Runs; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 25. Lateral / Lateral defensivo · SP

ID de referencia: `full_back_oop`. Familias: DL, DR. Nombre inglés: Full-Back. Descripción: KEY-690514.

Revisión visual actual: [menú/ficha](capturas/200-lateral-sp-ficha.jpg).

La principal tarea de un Lateral es defender las bandas como parte de la línea defensiva del equipo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, anticipation, positioning, teamwork, acceleration.

Rótulo verificado en esta pasada: **Lateral defensivo**.

Atributos clave leídos en la ficha actual: Marca, Entradas, Anticipación, Colocación, Juego en equipo, Aceleración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DR, alcance Posición. [Panel](capturas/201-lateral-sp-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 26. Lateral de contención · SP

ID de referencia: `holding_full_back_oop`. Familias: DL, DR. Nombre inglés: Holding Full-Back. Descripción: KEY-690515.

Revisión visual actual: [menú/ficha](capturas/204-lateral-contencion-ficha.jpg).

Como Contención, al Lateral se le pide mantener una posición más retrasada mientras su equipo defiende en zonas más adelantadas del campo, con el fin de proporcionar protección adicional contra ataques directos.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, anticipation, decisions, positioning, acceleration, concentration.

Rótulo verificado en esta pasada: **Lateral de contención**.

Atributos clave leídos en la ficha actual: Marca, Entradas, Anticipación, Decisiones, Colocación, Aceleración, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición; Cuidadoso.

Resumen de instrucciones en la ficha: Presionar con menos insistencia. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DR, alcance Posición. [Panel](capturas/205-lateral-contencion-instrucciones.jpg).

Controles bloqueados: pressing_oop = Less Often.

Controles editables: marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 27. Lateral presionante · SP

ID de referencia: `pressing_full_back_oop`. Familias: DL, DR. Nombre inglés: Pressing Full-Back. Descripción: KEY-690516.

Revisión visual actual: [menú/ficha](capturas/202-lateral-presionante-ficha.jpg).

Como Presionante, al Lateral se le pide presionar arriba a los jugadores de banda rivales para apoyar la presión alta del equipo.

Alias del recurso KEY-688079: **Lateral presionador**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, anticipation, positioning, teamwork, work_rate, acceleration, aggression.

Rótulo verificado en esta pasada: **Lateral presionante**.

Atributos clave leídos en la ficha actual: Marca, Entradas, Anticipación, Colocación, Juego en equipo, Sacrificio, Aceleración, Agresividad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Sube; Con autoridad.

Resumen de instrucciones en la ficha: Presionar con más insistencia. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DR, alcance Posición. [Panel](capturas/203-lateral-presionante-instrucciones.jpg).

Controles bloqueados: pressing_oop = More Often.

Controles editables: marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 28. Carrilero · SP

ID de referencia: `wing_back_oop`. Familias: WBL, WBR. Nombre inglés: Wing-Back. Descripción: KEY-690518.

Revisión visual actual: [menú/ficha](capturas/141-carrilero-sp.jpg).

Se espera que el Carrilero defienda las zonas exteriores para su equipo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, anticipation, positioning, teamwork, acceleration, stamina.

Rótulo verificado en esta pasada: **Lateral ofensivo**.

Atributos clave leídos en la ficha actual: Marca, Entradas, AnticipaciÃ³n, ColocaciÃ³n, Juego en equipo, AceleraciÃ³n, Resistencia. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: WBR, alcance PosiciÃ³n. [Panel](capturas/142-carrilero-sp-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 29. Carrilero de contención · SP

ID de referencia: `holding_wing_back_oop`. Familias: WBL, WBR. Nombre inglés: Holding Wing-Back. Descripción: KEY-690517.

Revisión visual actual: [menú/ficha](capturas/146-carrilero-contencion.jpg).

Como Contención, al Carrilero se le pide mantener una posición más retrasada mientras su equipo defiende en zonas más adelantadas del campo, con el fin de proporcionar protección adicional contra ataques directos.

Alias del recurso KEY-688081: **Carrilero defensivo**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, anticipation, decisions, positioning, acceleration, concentration.

Rótulo verificado en esta pasada: **Carrilero de contenciÃ³n**.

Atributos clave leídos en la ficha actual: Marca, Entradas, AnticipaciÃ³n, Decisiones, ColocaciÃ³n, AceleraciÃ³n, ConcentraciÃ³n. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posiciÃ³n; Cuidadoso.

Resumen de instrucciones en la ficha: Presionar con menos insistencia. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: WBR, alcance PosiciÃ³n. [Panel](capturas/147-carrilero-contencion-instrucciones.jpg).

Controles bloqueados: pressing_oop = Less Often.

Controles editables: marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 30. Carrilero presionante · SP

ID de referencia: `pressing_wing_back_oop`. Familias: WBL, WBR. Nombre inglés: Pressing Wing-Back. Descripción: KEY-690519.

Revisión visual actual: [menú/ficha](capturas/143-carrilero-presionante.jpg).

Como Presionante, al Carrilero se le pide presionar arriba de forma agresiva a los jugadores de banda rivales para apoyar la presión alta del equipo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, anticipation, positioning, teamwork, work_rate, acceleration, stamina.

Rótulo verificado en esta pasada: **Carrilero presionante**.

Atributos clave leídos en la ficha actual: Marca, Entradas, AnticipaciÃ³n, ColocaciÃ³n, Juego en equipo, Sacrificio, AceleraciÃ³n, Resistencia. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Sube; Con autoridad.

Resumen de instrucciones en la ficha: Presionar con mÃ¡s insistencia. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: WBR, alcance PosiciÃ³n. [Panel](capturas/145-carrilero-presionante-instrucciones.jpg).

Controles bloqueados: pressing_oop = More Often.

Controles editables: marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 31. Mediocentro defensivo · CP

ID de referencia: `defensive_midfielder_ip`. Familias: DM. Nombre inglés: Defensive Midfielder. Descripción: KEY-690536.

Revisión visual actual: [menú/ficha](capturas/208-mediocentro-defensivo-cp-ficha.jpg).

La principal responsabilidad del mediocampista es colocarse delante de la defensa del equipo y ayudar a protegerse de los contrataques rivales.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): tackling, anticipation, positioning, teamwork, concentration.

Rótulo verificado en esta pasada: **Mediocentro defensivo**.

Atributos clave leídos en la ficha actual: Entradas, Anticipación, Colocación, Juego en equipo, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición; Cuidado.

Resumen de instrucciones en la ficha: Mantener la posición. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DM-single, alcance Posición. [Panel](capturas/209-mediocentro-defensivo-cp-instrucciones.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; dribbling_frequency_ip = Dribble Less; forward_runs_ip = Make Fewer Runs; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 32. Organizador defensivo / Organizador retrasado · CP

ID de referencia: `deep_lying_playmaker_ip`. Familias: DM. Nombre inglés: Deep Lying Playmaker. Descripción: KEY-690540.

Revisión visual actual: [menú/ficha](capturas/206-organizador-retrasado-ficha.jpg).

El Pivote organizador opera en el espacio entre la defensa y el centro del campo, con el objetivo de iniciar las jugadas ofensivas mediante pases precisos hacia compañeros situados en zonas más avanzadas del campo.

Alias del recurso KEY-688119: **pivote organizador**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): passing, vision, decisions, first_touch, technique, teamwork, composure.

Rótulo verificado en esta pasada: **Organizador defensivo**.

Atributos clave leídos en la ficha actual: Pases, Visión, Decisiones, Control, Técnica, Juego en equipo, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición; Expresiva.

Resumen de instrucciones en la ficha: Arriesgar más. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DM-single, alcance Posición. [Panel](capturas/207-organizador-defensivo-instrucciones.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; forward_runs_ip = Make Fewer Runs; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; passing_risk_ip = Take More Risks; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_frequency_ip, shoot_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 33. Medio cierre · CP

ID de referencia: `half_back_ip`. Familias: DM. Nombre inglés: Half Back. Descripción: KEY-690537.

Revisión visual actual: [menú/ficha](capturas/210-medio-cierre-ficha.jpg).

Un mediocampista que busca retrasarse e integrarse en la línea defensiva de su equipo a medida que se progresa con el balón, el mediocampista retrasado actúa como un defensa central adicional.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): heading, marking, tackling, anticipation, positioning, teamwork, strength, jumping_reach.

Rótulo verificado en esta pasada: **Medio cierre**.

Atributos clave leídos en la ficha actual: Cabeceo, Marca, Entradas, Anticipación, Colocación, Juego en equipo, Fuerza, Alcance de salto. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se retrasa a posición de central; Cuidado.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DM-single, alcance Posición. [Panel](capturas/211-medio-cierre-instrucciones.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; forward_runs_ip = Make Fewer Runs; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_frequency_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 34. Mediocampista todoterreno · CP

ID de referencia: `box_to_box_midfielder_ip`. Familias: DM. Nombre inglés: Box To Box Midfielder. Descripción: KEY-690538.

Revisión visual actual: [menú/ficha](capturas/129-todoterreno-dm.jpg).

El dinamismo constante del mediocampista todoterreno le permite contribuir significativamente tanto en la fase ofensiva como en la defensiva, desde la construcción del juego hasta la zona de finalización.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, passing, tackling, teamwork, work_rate, stamina.

Rótulo verificado en esta pasada: **Mediocampista todoterreno**.

Atributos clave leídos en la ficha actual: Desmarques, Pases, Entradas, Juego en equipo, Sacrificio, Resistencia. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Adelanta su posiciÃ³n a mediocampista defensivo; Amenaza de gol.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DM-right-double-pivot, alcance PosiciÃ³n. [Panel](capturas/273-todoterreno-aguantar-confirmado.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; hold_up_ball_ip = No; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 35. Organizador todoterreno · CP

ID de referencia: `box_to_box_playmaker_ip`. Familias: DM. Nombre inglés: Box To Box Playmaker. Descripción: KEY-690539.

Revisión visual actual: [menú/ficha](capturas/131-organizador-todoterreno.jpg).

El Organizador todoterreno es el motor creativo del equipo, actuando como un canal de generación de juego tanto desde atrás como en posiciones más avanzadas del campo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, passing, vision, decisions, first_touch, technique, teamwork, work_rate.

Rótulo verificado en esta pasada: **Organizador todoterreno**.

Atributos clave leídos en la ficha actual: Desmarques, Pases, VisiÃ³n, Decisiones, Control, TÃ©cnica, Juego en equipo, Sacrificio. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Adelanta su posiciÃ³n a mediocampista defensivo; Amenaza creativa.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DM-right-double-pivot, alcance PosiciÃ³n. [Panel](capturas/132-organizador-todoterreno-instrucciones.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; freedom_of_movement_ip = Follow Tactical Position; hold_up_ball_ip = No; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_frequency_ip, forward_runs_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 36. Mediocentro defensivo · SP

ID de referencia: `defensive_midfielder_oop`. Familias: DM. Nombre inglés: Defensive Midfielder. Descripción: KEY-690493.

Revisión visual actual: [menú/ficha](capturas/214-mediocentro-defensivo-sp-ficha.jpg).

La principal responsabilidad del mediocampista defensivo cuando no tiene el balón es colocarse delante de la defensa del equipo y ayudar a protegerse de los ataques rivales.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): tackling, anticipation, decisions, positioning, teamwork, work_rate.

Rótulo verificado en esta pasada: **Mediocentro defensivo**.

Atributos clave leídos en la ficha actual: Entradas, Anticipación, Decisiones, Colocación, Juego en equipo, Sacrificio. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DM-single, alcance Posición. [Panel](capturas/215-mediocentro-defensivo-sp-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 37. Mediocentro de repliegue · SP

ID de referencia: `dropping_defensive_midfielder_oop`. Familias: DM. Nombre inglés: Dropping Defensive Midfielder. Descripción: KEY-690494.

Revisión visual actual: [menú/ficha](capturas/216-mediocentro-repliegue-ficha.jpg).

Como Incrustado, el mediocampista defensivo buscará retroceder e incrustarse en la línea defensiva cuando su equipo se vea replegado en el tercio defensivo propio, actuando como un defensor central adicional.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, anticipation, decisions, positioning, teamwork, work_rate, strength.

Rótulo verificado en esta pasada: **Mediocentro de repliegue**.

Atributos clave leídos en la ficha actual: Marca, Entradas, Anticipación, Decisiones, Colocación, Juego en equipo, Sacrificio, Fuerza. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se retrasa a posición de central.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DM-single, alcance Posición. [Panel](capturas/217-mediocentro-repliegue-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 38. Mediocentro presionante · SP

ID de referencia: `pressing_defensive_midfielder_oop`. Familias: DM. Nombre inglés: Pressing Defensive Midfielder. Descripción: KEY-690497.

Revisión visual actual: [menú/ficha](capturas/245-mediocentro-presionante-ficha.jpg).

Como Presionante, al mediocampista defensivo se le asigna la tarea de adelantarse desde su posición para apoyar la presión alta del equipo.

Alias del recurso KEY-688085: **Mediocentro presionador**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): tackling, anticipation, decisions, positioning, teamwork, work_rate, stamina, aggression.

Rótulo verificado en esta pasada: **Mediocentro presionante**.

Atributos clave leídos en la ficha actual: Entradas, Anticipación, Decisiones, Colocación, Juego en equipo, Sacrificio, Resistencia, Agresividad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Sube; Con autoridad.

Resumen de instrucciones en la ficha: Presionar con más insistencia. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DM (derecha, doble pivote), alcance Posición. [Panel](capturas/246-mediocentro-presionante-instrucciones.jpg).

Controles bloqueados: pressing_oop = More Often.

Controles editables: marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 39. Mediocentro fijo · SP

ID de referencia: `screening_defensive_midfielder_oop`. Familias: DM. Nombre inglés: Screening Defensive Midfielder. Descripción: KEY-690495.

Revisión visual actual: [menú/ficha](capturas/212-mediocentro-fijo-ficha.jpg).

Como Pantalla, la principal responsabilidad del mediocampista defensivo es proteger el espacio por delante de los defensores centrales.

Alias del recurso KEY-688086: **mediocentro de pantalla**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, anticipation, decisions, positioning, concentration.

Rótulo verificado en esta pasada: **Mediocentro fijo**.

Atributos clave leídos en la ficha actual: Marca, Entradas, Anticipación, Decisiones, Colocación, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posición; Cuidadoso.

Resumen de instrucciones en la ficha: Presionar con menos insistencia. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DM-single, alcance Posición. [Panel](capturas/213-mediocentro-fijo-instrucciones.jpg).

Controles bloqueados: pressing_oop = Less Often.

Controles editables: marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 40. Mediocampista defensivo de cobertura abierta · SP

ID de referencia: `wide_covering_defensive_midfielder_oop`. Familias: DM. Nombre inglés: Wide Covering Defensive Midfielder. Descripción: KEY-690496.

Revisión visual actual: [menú/ficha](capturas/247-mediocentro-cobertura-abierta-ficha.jpg).

Como Cobertura por banda, se pide al mediocampista defensivo que brinde apoyo defensivo en las bandas, desplazándose desde su posición habitual para ayudar al equipo a defender ante amenazas por los costados.

Alias del recurso KEY-688087: **Mediocampista defensivo escorado de cobertura**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, anticipation, decisions, positioning, teamwork, work_rate, stamina.

Rótulo verificado en esta pasada: **Mediocampista defensivo de cobertura abierta**.

Atributos clave leídos en la ficha actual: Marca, Entradas, Anticipación, Decisiones, Colocación, Juego en equipo, Sacrificio, Resistencia. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Cubre la banda.

Resumen de instrucciones en la ficha: Defiende los flancos. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: DM (derecha, doble pivote), alcance Posición. [Panel](capturas/248-cobertura-abierta-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 41. Mediocampista / Centrocampista · CP

ID de referencia: `central_midfielder_ip`. Familias: MC. Nombre inglés: Central Midfielder. Descripción: KEY-690541.

Revisión visual actual: [menú/ficha](capturas/218-centrocampista-cp-ficha.jpg).

Responsable de ofrecer un vínculo trabajador y versátil entre la defensa y el ataque, el mediocampista debe desempeñar una amplia variedad de tareas en la zona media del campo. Este rol exige inteligencia táctica y calidad técnica para poder apoyar tanto en las labores defensivas como en las ofensivas, adaptándose a las necesidades del juego en cada momento.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): passing, tackling, decisions, first_touch, teamwork.

Rótulo verificado en esta pasada: **Centrocampista**.

Atributos clave leídos en la ficha actual: Pases, Entradas, Decisiones, Control, Juego en equipo. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MC-left, alcance Posición. [Panel](capturas/219-centrocampista-cp-instrucciones.jpg).

Controles bloqueados: hold_up_ball_ip = No; cross_from_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_risk_ip, passing_directness_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 42. Mediocampista abierto · CP

ID de referencia: `wide_central_midfielder_ip`. Familias: MC. Nombre inglés: Wide Central Midfielder. Descripción: KEY-690543.

Revisión visual actual: [menú/ficha](capturas/223-mediocampista-abierto-central-ficha.jpg).

Normalmente utilizado en uno de los costados de un doble pivote o de un trío en el centro del campo, el Mediocampista escorado tiene como responsabilidad ofrecer un vínculo trabajador y versátil entre la defensa y el ataque.

Alias del recurso KEY-688123: **Centrocampista abierto**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): passing, tackling, decisions, first_touch, teamwork.

Rótulo verificado en esta pasada: **Mediocampista abierto**.

Atributos clave leídos en la ficha actual: Pases, Entradas, Decisiones, Control, Juego en equipo. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Cae a banda.

Resumen de instrucciones en la ficha: Abrirse a banda. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MC-left, alcance Posición. [Panel](capturas/224-mediocampista-abierto-central-instrucciones.jpg).

Controles bloqueados: attacking_width_ip = Stay Wider; hold_up_ball_ip = No; cross_from_ip = Standard.

Controles editables: dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_risk_ip, passing_directness_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 43. Mediocampista organizador / Mediocentro organizador · CP

ID de referencia: `midfield_playmaker_ip`. Familias: MC. Nombre inglés: Midfield Playmaker. Descripción: KEY-690542.

Revisión visual actual: [menú/ficha](capturas/225-mediocampista-organizador-ficha.jpg).

El mediocampista organizador actúa como un vínculo creativo entre la defensa y el ataque, buscando realizar pases progresivos y pases definitivos a sus compañeros ofensivos para iniciar las jugadas de ataque de su equipo.

Alias del recurso KEY-688146: **centrocampista organizador**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, passing, vision, decisions, first_touch, technique, teamwork, composure.

Rótulo verificado en esta pasada: **Mediocampista organizador**.

Atributos clave leídos en la ficha actual: Desmarques, Pases, Visión, Decisiones, Control, Técnica, Juego en equipo, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Expresiva; Amenaza creativa.

Resumen de instrucciones en la ficha: Arriesgar más. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MC-left, alcance Posición. [Panel](capturas/226-mediocampista-organizador-instrucciones.jpg).

Controles bloqueados: hold_up_ball_ip = No; passing_risk_ip = Take More Risks; cross_from_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_directness_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 44. Mediapunta · CP

ID de referencia: `attacking_midfielder_ip`. Familias: MC, AMC. Nombre inglés: Attacking Midfielder. Descripción: KEY-690544.

Revisión visual actual: [menú/ficha](capturas/220-mediapunta-cp-ficha.jpg).

Un rol ofensivo que busca operar entre la línea defensiva y la línea de mediocampistas del rival, el mediapunta intenta recibir pases en espacios reducidos tan a menudo como sea posible.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): long_shots, off_the_ball, passing, first_touch, technique, flair, composure.

Rótulo verificado en esta pasada: **Mediapunta**.

Atributos clave leídos en la ficha actual: Remates lejanos, Desmarques, Pases, Control, Técnica, Talento, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Encuentra espacios entre líneas; Amenaza de gol.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MC-left, alcance Posición. [Panel](capturas/221-mediapunta-cp-instrucciones.jpg).

Controles bloqueados: hold_up_ball_ip = No; cross_from_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_risk_ip, passing_directness_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 45. Organizador adelantado · CP

ID de referencia: `advanced_playmaker_ip`. Familias: MC, AMC. Nombre inglés: Advanced Playmaker. Descripción: KEY-696046.

Revisión visual actual: [menú/ficha](capturas/016-roles-mc-cp.jpg).

El organizador adelantado es un rol creativo que busca operar en zonas avanzadas del terreno de juego, entre el centro del campo y la defensa del equipo rival, tratando de recibir pases en espacios reducidos siempre que sea posible.

La principal función del organizador adelantado es crear oportunidades para que sus compañeros marquen goles, realizando pases definitivos en el último tercio del campo con la mayor frecuencia posible.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, passing, vision, decisions, first_touch, technique, teamwork, composure.

Atributos clave leídos en la ficha actual: Desmarques, Pases, Visión, Decisiones, Control, Técnica, Juego en equipo, Serenidad. No se registran los valores personales como constantes del rol.

Contexto de instrucciones comprobado: MC-left, alcance Posición. [Panel](capturas/222-organizador-adelantado-sin-tooltip.jpg).

Controles bloqueados: hold_up_ball_ip = No; passing_risk_ip = Take More Risks; cross_from_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_directness_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 46. Mediocampista entre líneas · CP

ID de referencia: `channel_midfielder_ip`. Familias: MC, AMC. Nombre inglés: Channel Midfielder. Descripción: KEY-690549.

Revisión visual actual: [menú/ficha](capturas/082-amc-cp-libre.jpg).

El mediocampista entre líneas busca hacer desmarques de apoyo hacia las zonas laterales, conectando frecuentemente con los delanteros por banda de su equipo.

Alias del recurso KEY-688111: **centrocampista de canal**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): crossing, off_the_ball, passing, first_touch, technique, work_rate, acceleration, composure.

Rótulo verificado en esta pasada: **Mediocampista entre lÃ­neas**.

Atributos clave leídos en la ficha actual: Centros, Desmarques, Pases, Control, TÃ©cnica, Sacrificio, AceleraciÃ³n, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se abre a las bandas; Amenaza creativa.

Resumen de instrucciones en la ficha: Moverse entre lÃ­neas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMC, alcance PosiciÃ³n. [Panel](capturas/110-canal-amc-instrucciones.jpg).

Controles bloqueados: attacking_width_ip = Move Into Channels; dribbling_direction_ip = Standard; cross_from_ip = Standard.

Controles editables: dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, hold_up_ball_ip, shoot_ip, passing_risk_ip, passing_directness_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 47. Mediocampista · SP

ID de referencia: `central_midfielder_oop`. Familias: MC. Nombre inglés: Central Midfielder. Descripción: KEY-690499.

Revisión visual actual: [menú/ficha](capturas/068-mc-sp-centrocampista.jpg).

El mediocampista central trata de ofrecer protección en el centro del campo, intentando encontrar un equilibrio entre apoyar la presión y bloquear los pases por el medio.

Alias del recurso KEY-688088: **Centrocampista**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): tackling, decisions, teamwork, work_rate.

Rótulo verificado en esta pasada: **Centrocampista**.

Atributos clave leídos en la ficha actual: Entradas, Decisiones, Juego en equipo, Sacrificio. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MC, alcance PosiciÃ³n. [Panel](capturas/080-centrocampista-sp-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 48. Mediocampista presionante · SP

ID de referencia: `pressing_central_midfielder_oop`. Familias: MC. Nombre inglés: Pressing Central Midfielder. Descripción: KEY-690501.

Revisión visual actual: [menú/ficha](capturas/065-mc-sp-entrada.jpg).

Como Presionante, al mediocampista se le anima a adelantarse desde su posición para apoyar la presión alta del equipo.

Alias del recurso KEY-688089: **centrocampista presionador**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): tackling, anticipation, decisions, teamwork, work_rate, stamina, aggression.

Rótulo verificado en esta pasada: **Mediocampista presionante**.

Atributos clave leídos en la ficha actual: Entradas, AnticipaciÃ³n, Decisiones, Juego en equipo, Sacrificio, Resistencia, Agresividad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Sube; Con autoridad.

Resumen de instrucciones en la ficha: Presionar con mÃ¡s insistencia. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MC, alcance PosiciÃ³n. [Panel](capturas/067-mcp-sp-instrucciones.jpg).

Controles bloqueados: pressing_oop = More Often.

Controles editables: marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 49. Mediocampista fijo · SP

ID de referencia: `screening_central_midfielder_oop`. Familias: MC. Nombre inglés: Screening Central Midfielder. Descripción: KEY-690498.

Revisión visual actual: [menú/ficha](capturas/071-mc-sp-fijo.jpg).

Como Pantalla, el mediocampista central trata de no alejarse demasiado de su posición, centrándose en bloquear las líneas de pase por el centro del campo.

Alias del recurso KEY-688090: **centrocampista de pantalla**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, decisions, positioning, concentration.

Rótulo verificado en esta pasada: **Mediocampista fijo**.

Atributos clave leídos en la ficha actual: Marca, Entradas, Decisiones, ColocaciÃ³n, ConcentraciÃ³n. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posiciÃ³n; Cuidadoso.

Resumen de instrucciones en la ficha: Presionar con menos insistencia. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MC, alcance PosiciÃ³n. [Panel](capturas/074-mc-fijo-sp-instrucciones.jpg).

Controles bloqueados: pressing_oop = Less Often.

Controles editables: marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 50. Mediocampista de cobertura abierta · SP

ID de referencia: `wide_covering_central_midfielder_oop`. Familias: MC. Nombre inglés: Wide Covering Central Midfielder. Descripción: KEY-690500.

Revisión visual actual: [menú/ficha](capturas/075-mc-sp-cobertura.jpg).

Como Cobertura por banda, se pide al mediocampista que brinde apoyo defensivo en las bandas, desplazándose desde su posición habitual para ayudar al equipo a defender ante amenazas por los costados.

Alias del recurso KEY-688091: **centrocampista de cobertura por banda**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): marking, tackling, decisions, teamwork, work_rate, stamina, agility.

Rótulo verificado en esta pasada: **Mediocampista de cobertura abierta**.

Atributos clave leídos en la ficha actual: Marca, Entradas, Decisiones, Juego en equipo, Sacrificio, Resistencia, Agilidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Cubre la banda.

Resumen de instrucciones en la ficha: Defiende los flancos. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MC, alcance PosiciÃ³n. [Panel](capturas/077-mc-cobertura-sp-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 51. Mediocampista abierto · CP

ID de referencia: `wide_midfielder_ip`. Familias: ML, MR. Nombre inglés: Wide Midfielder. Descripción: KEY-690545.

Revisión visual actual: [menú/ficha](capturas/155-mediocampista-abierto-cp.jpg).

Un jugador de banda que suele apoyar el ataque desde zonas más retrasadas que un extremo tradicional, el mediocampista de banda prefiere realizar pases peligrosos y centros desde atrás en lugar de intentar desbordar al lateral rival, confiando más en su capacidad técnica que en el regate o la velocidad.

Alias del recurso KEY-688108: **Mediocampista escorado**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): crossing, passing, decisions, technique, teamwork, work_rate, stamina, pace.

Rótulo verificado en esta pasada: **Mediocampista abierto**.

Atributos clave leídos en la ficha actual: Centros, Pases, Decisiones, TÃ©cnica, Juego en equipo, Sacrificio, Resistencia, Velocidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantiene la posiciÃ³n; Mantenerse abierto.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MR, alcance PosiciÃ³n. [Panel](capturas/157-mediocampista-abierto-sin-tooltip.jpg).

Controles bloqueados: hold_up_ball_ip = No.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 52. Extremo · CP

ID de referencia: `winger_ip`. Familias: ML, MR, AML, AMR. Nombre inglés: Winger. Descripción: KEY-690548.

Revisión visual actual: [menú/ficha](capturas/229-extremo-cp-ficha.jpg).

Aportando amplitud durante todo el ataque, el extremo estira la defensa rival atacando desde cerca de la línea de banda. Su función principal es apoyar a los delanteros del equipo, realizando pases y centros peligrosos en el último tercio para generar ocasiones de gol.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): crossing, dribbling, technique, teamwork, acceleration, pace, agility.

Rótulo verificado en esta pasada: **Extremo**.

Atributos clave leídos en la ficha actual: Centros, Regate, Técnica, Juego en equipo, Aceleración, Velocidad, Agilidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantenerse abierto; Amenaza creativa.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMR, alcance Posición. [Panel](capturas/230-extremo-cp-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, hold_up_ball_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 53. Extremo invertido · CP

ID de referencia: `inside_winger_ip`. Familias: ML, MR, AML, AMR. Nombre inglés: Inside Winger. Descripción: KEY-690546.

Revisión visual actual: [menú/ficha](capturas/235-extremo-invertido-ficha.jpg).

Con la tendencia habitual de meterse hacia dentro y ocupar los interiores durante las fases ofensivas, el extremo por dentro busca recibir el balón en zonas más centrales del campo, al mismo tiempo que genera espacio para que los compañeros doblen por banda. Este rol suele estar acompañado de un lateral ofensivo o un extremo que se pegue a la banda, lo que permite que ambos jugadores operen sin estorbarse.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): dribbling, first_touch, technique, teamwork, acceleration, agility, composure.

Rótulo verificado en esta pasada: **Extremo invertido**.

Atributos clave leídos en la ficha actual: Regate, Control, Técnica, Juego en equipo, Aceleración, Agilidad, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se mueve hacia adentro; Amenaza creativa.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMR, alcance Posición. [Panel](capturas/236-extremo-invertido-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, hold_up_ball_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 54. Extremo organizador · CP

ID de referencia: `playmaking_winger_ip`. Familias: ML, MR, AML, AMR. Nombre inglés: Playmaking Winger. Descripción: KEY-690547.

Revisión visual actual: [menú/ficha](capturas/231-extremo-organizador-ficha.jpg).

El extremo organizador actúa como la principal fuente de creatividad del equipo, comenzando en una posición abierta durante la fase de construcción y luego metiéndose hacia dentro para encontrar espacios desde donde realizar pases definitivos y generar ocasiones.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): crossing, dribbling, off_the_ball, passing, vision, decisions, first_touch, technique.

Rótulo verificado en esta pasada: **Extremo organizador**.

Atributos clave leídos en la ficha actual: Centros, Regate, Desmarques, Pases, Visión, Decisiones, Control, Técnica. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se mueve hacia adentro; Expresiva.

Resumen de instrucciones en la ficha: Arriesgar más. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMR, alcance Posición. [Panel](capturas/232-extremo-organizador-instrucciones.jpg).

Controles bloqueados: attacking_width_ip = Sit Narrower; forward_runs_ip = Standard; freedom_of_movement_ip = Roam From Position; passing_risk_ip = Take More Risks; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: dribbling_direction_ip, dribbling_frequency_ip, hold_up_ball_ip, shoot_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 55. Mediocampista abierto · SP

ID de referencia: `wide_midfielder_oop`. Familias: ML, MR. Nombre inglés: Wide Midfielder. Descripción: KEY-690503.

Revisión visual actual: [menú/ficha](capturas/249-medio-abierto-ficha.jpg).

El mediocampista de banda ofrece un equilibrio entre la protección defensiva frente a las amenazas por banda y estar bien posicionado para lanzar un contraataque en caso de recuperar el balón.

Alias del recurso KEY-688093: **Mediocampista escorado**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): decisions, teamwork, work_rate, acceleration.

Rótulo verificado en esta pasada: **Mediocampista abierto**.

Atributos clave leídos en la ficha actual: Decisiones, Juego en equipo, Sacrificio, Aceleración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MR, alcance Posición. [Panel](capturas/250-medio-abierto-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 56. Mediocampista abierto con retroceso · SP

ID de referencia: `tracking_wide_midfielder_oop`. Familias: ML, MR. Nombre inglés: Tracking Wide Midfielder. Descripción: KEY-690502.

Revisión visual actual: [menú/ficha](capturas/251-medio-abierto-retroceso-ficha.jpg).

Como Rastreador, al mediocampista de banda se le indica que retroceda defensivamente cuando el equipo rival avanza hacia el tercio defensivo propio, con el fin de apoyar a los defensores que tiene por detrás, incluso incrustándose a veces atrás como un defensor más.

Alias del recurso KEY-688092: **Mediocampista de banda itinerante**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): anticipation, decisions, teamwork, work_rate, acceleration, stamina, aggression.

Rótulo verificado en esta pasada: **Mediocampista abierto con retroceso**.

Atributos clave leídos en la ficha actual: Anticipación, Decisiones, Juego en equipo, Sacrificio, Aceleración, Resistencia, Agresividad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Retrocede; Apoya a la defensa.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MR, alcance Posición. [Panel](capturas/252-medio-abierto-retroceso-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 57. Mediocampista abierto estacionario · SP

ID de referencia: `wide_outlet_wide_midfielder_oop`. Familias: ML, MR. Nombre inglés: Wide Outlet Wide Midfielder. Descripción: KEY-690504.

Revisión visual actual: [menú/ficha](capturas/253-medio-abierto-estacionario-ficha.jpg).

Como recurso ofensivo por banda, se le pide al mediocampista de banda que evite bajar para ayudar al lateral que tiene detrás en la mayor medida posible, prefiriendo mantener su posición para estar en una posición amenazante para un contrataque cuando se produzca una pérdida del balón.

Alias del recurso KEY-688094: **Mediocampista abierto con salida**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, anticipation, decisions, teamwork, pace, concentration.

Rótulo verificado en esta pasada: **Mediocampista abierto estacionario**.

Atributos clave leídos en la ficha actual: Desmarques, Anticipación, Decisiones, Juego en equipo, Velocidad, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se queda arriba; Contraataques.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: MR, alcance Posición. [Panel](capturas/254-medio-abierto-estacionario-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 58. Mediapunta libre · CP

ID de referencia: `free_role_ip`. Familias: AMC. Nombre inglés: Free Role. Descripción: KEY-690550.

Revisión visual actual: [menú/ficha](capturas/083-amc-libre.jpg).

Un jugador con libertad de movimientos tiene licencia creativa total, lo que le permite moverse con libertad desde su posición original para generar oportunidades ofensivas para su equipo. Se le anima a asumir más riesgos con el balón, tanto para crear como para finalizar jugadas.

Alias del recurso KEY-688131: **Libertad de movimientos**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): dribbling, long_shots, off_the_ball, passing, vision, first_touch, technique, flair.

Rótulo verificado en esta pasada: **Mediapunta libre**.

Atributos clave leídos en la ficha actual: Regate, Remates lejanos, Desmarques, Pases, VisiÃ³n, Control, TÃ©cnica, Talento. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Expresiva; Amenaza creativa.

Resumen de instrucciones en la ficha: Regatear con mÃ¡s frecuencia; Arriesgar mÃ¡s. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMC, alcance PosiciÃ³n. [Panel](capturas/084-amc-libre-instrucciones.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; dribbling_frequency_ip = Dribble More; passing_risk_ip = Take More Risks; cross_from_ip = Standard.

Controles editables: attacking_width_ip, forward_runs_ip, freedom_of_movement_ip, hold_up_ball_ip, shoot_ip, passing_directness_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 59. Segundo delantero · CP

ID de referencia: `second_striker_ip`. Familias: AMC. Nombre inglés: Second Striker. Descripción: KEY-690551.

Revisión visual actual: [menú/ficha](capturas/085-amc-segundo-delantero.jpg).

El segundo delantero actúa como una de las principales amenazas ofensivas del equipo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): finishing, off_the_ball, anticipation, first_touch, acceleration, composure.

Rótulo verificado en esta pasada: **Segundo delantero**.

Atributos clave leídos en la ficha actual: Remate, Desmarques, AnticipaciÃ³n, Control, AceleraciÃ³n, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Adelanta su posiciÃ³n al lateral izquierdo; Amenaza de gol.

Resumen de instrucciones en la ficha: Subir mÃ¡s. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMC, alcance PosiciÃ³n. [Panel](capturas/086-amc-segundo-instrucciones.jpg).

Controles bloqueados: dribbling_direction_ip = Standard; forward_runs_ip = Make More Runs; cross_from_ip = Standard.

Controles editables: attacking_width_ip, dribbling_frequency_ip, freedom_of_movement_ip, hold_up_ball_ip, shoot_ip, passing_risk_ip, passing_directness_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 60. Mediapunta · SP

ID de referencia: `attacking_midfielder_oop`. Familias: AMC. Nombre inglés: Attacking Midfielder. Descripción: KEY-690506.

Revisión visual actual: [menú/ficha](capturas/239-mediapunta-ficha.jpg).

El mediapunta se encarga de defender las zonas centrales del campo y, a menudo, tiene la tarea de impedir el acceso a los mediocampistas del equipo rival.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): anticipation, decisions, work_rate.

Rótulo verificado en esta pasada: **Mediapunta**.

Atributos clave leídos en la ficha actual: Anticipación, Decisiones, Sacrificio. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMC, alcance Posición. [Panel](capturas/240-mediapunta-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 61. Mediapunta con retroceso · SP

ID de referencia: `tracking_attacking_midfielder_oop`. Familias: AMC. Nombre inglés: Tracking Attacking Midfielder. Descripción: KEY-690505.

Revisión visual actual: [menú/ficha](capturas/241-mediapunta-retroceso-ficha.jpg).

Como rastreador, se le indica al mediapunta que retroceda defensivamente cuando el equipo rival avanza hacia el tercio defensivo propio, con el fin de apoyar a los defensores que tiene por detrás, replegándose a una posición defensiva más profunda.

Alias del recurso KEY-688098: **Mediapunta itinerante**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): anticipation, decisions, teamwork, work_rate, stamina, aggression.

Rótulo verificado en esta pasada: **Mediapunta con retroceso**.

Atributos clave leídos en la ficha actual: Anticipación, Decisiones, Juego en equipo, Sacrificio, Resistencia, Agresividad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Retrocede; Apoya a la defensa.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMC, alcance Posición. [Panel](capturas/242-mediapunta-retroceso-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 62. Mediapunta estacionario · SP

ID de referencia: `central_outlet_attacking_midfielder_oop`. Familias: AMC. Nombre inglés: Central Outlet Attacking Midfielder. Descripción: KEY-690507.

Revisión visual actual: [menú/ficha](capturas/237-mediapunta-estacionario-ficha.jpg).

Como salida central, se le pide al mediapunta que no retroceda tanto para ayudar a los defensores que tiene detrás, sino que mantenga su posición para situarse en una zona peligrosa de cara a un posible contraataque tras una pérdida del rival.

Alias del recurso KEY-688096: **Mediapunta central con salida**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, anticipation, decisions, teamwork, balance, concentration.

Rótulo verificado en esta pasada: **Mediapunta estacionario**.

Atributos clave leídos en la ficha actual: Desmarques, Anticipación, Decisiones, Juego en equipo, Equilibrio, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se queda arriba; Contraataques.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMC, alcance Posición. [Panel](capturas/238-mediapunta-estacionario-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 63. Mediapunta de ruptura con salida (nombre de recurso) · SP

ID de referencia: `splitting_outlet_attacking_midfielder_oop`. Familias: AMC. Nombre inglés: Splitting Outlet Attacking Midfielder. Descripción: KEY-690508.

Revisión visual actual: [menú/ficha](capturas/109-mediapunta-estacionario-salida.jpg).

Con Ruptura con salida, se solicita al mediapunta que evite bajar para ayudar a los defensores que tiene detrás en la mayor medida posible, prefiriendo adelantar su posición para estar en una posición amenazante para un contrataque cuando se produzca una pérdida de balón.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, anticipation, decisions, teamwork, pace, concentration.

Rótulo verificado en esta pasada: **Mediapunta estacionario con salida**.

Atributos clave leídos en la ficha actual: Desmarques, AnticipaciÃ³n, Decisiones, Juego en equipo, Velocidad, ConcentraciÃ³n. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se queda arriba; Contraataques.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMC-right, alcance PosiciÃ³n. [Panel](capturas/111-amc-salida-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 64. Delantero interior · CP

ID de referencia: `inside_forward_ip`. Familias: AML, AMR. Nombre inglés: Inside Forward. Descripción: KEY-690552.

Revisión visual actual: [menú/ficha](capturas/227-delantero-interior-ficha.jpg).

El delantero por dentro es un rol de banda cuya función principal es cerrarse hacia las zonas interiores cuando su equipo ataca para dar espacios a un lateral que lo doble, además de estar en disposición de recibir el balón en zonas más centrales del campo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): dribbling, off_the_ball, anticipation, first_touch, technique, acceleration, agility, composure.

Rótulo verificado en esta pasada: **Delantero interior**.

Atributos clave leídos en la ficha actual: Regate, Desmarques, Anticipación, Control, Técnica, Aceleración, Agilidad, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se mueve hacia adentro; Amenaza de gol.

Resumen de instrucciones en la ficha: Subir más. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMR, alcance Posición. [Panel](capturas/228-delantero-interior-instrucciones.jpg).

Controles bloqueados: forward_runs_ip = Make More Runs.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, freedom_of_movement_ip, hold_up_ball_ip, shoot_ip, passing_risk_ip, passing_directness_ip, cross_from_ip, crossing_strategy_ip. No extrapolar a otros subpuestos o alcances.

#### 65. Delantero abierto · CP

ID de referencia: `wide_forward_ip`. Familias: AML, AMR. Nombre inglés: Wide Forward. Descripción: KEY-690553.

Revisión visual actual: [menú/ficha](capturas/233-delantero-abierto-ficha.jpg).

Al igual que el extremo, el delantero escorado tiene la responsabilidad de dar amplitud al ataque, posicionándose cerca de la línea de banda para estirar la defensa rival.

Alias del recurso KEY-696156: **Delantero escorado**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): dribbling, off_the_ball, anticipation, first_touch, technique, acceleration, pace, agility.

Rótulo verificado en esta pasada: **Delantero abierto**.

Atributos clave leídos en la ficha actual: Regate, Desmarques, Anticipación, Control, Técnica, Aceleración, Velocidad, Agilidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Mantenerse abierto; Amenaza de gol.

Resumen de instrucciones en la ficha: Subir más. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMR, alcance Posición. [Panel](capturas/234-delantero-abierto-instrucciones.jpg).

Controles bloqueados: forward_runs_ip = Make More Runs; passing_directness_ip = Shorter; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, freedom_of_movement_ip, hold_up_ball_ip, shoot_ip, passing_risk_ip, cross_from_ip. No extrapolar a otros subpuestos o alcances.

#### 66. Extremo · SP

ID de referencia: `winger_oop`. Familias: AML, AMR. Nombre inglés: Winger. Descripción: KEY-690492.

Revisión visual actual: [menú/ficha](capturas/088-extremo-sp.jpg).

El Extremo se centra principalmente en defender las zonas laterales del campo, buscando encontrar un equilibrio entre apoyar la presión en zonas adelantadas y retroceder cuando sea necesario para ayudar al defensor lateral que tiene detrás.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): anticipation, decisions, teamwork, work_rate, acceleration.

Rótulo verificado en esta pasada: **Extremo**.

Atributos clave leídos en la ficha actual: AnticipaciÃ³n, Decisiones, Juego en equipo, Sacrificio, AceleraciÃ³n. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMR, alcance PosiciÃ³n. [Panel](capturas/089-extremo-sp-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 67. Extremo con retroceso · SP

ID de referencia: `tracking_winger_oop`. Familias: AML, AMR. Nombre inglés: Tracking Winger. Descripción: KEY-690509.

Revisión visual actual: [menú/ficha](capturas/090-extremo-retroceso.jpg).

Como Rastreador, se le indica al extremo que retroceda defensivamente cuando el equipo rival avanza hacia el tercio defensivo propio, con el fin de apoyar a los defensores que tiene por detrás, incluso incrustándose a veces atrás como un defensor más.

Alias del recurso KEY-688100: **extremo de seguimiento**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): anticipation, decisions, teamwork, work_rate, acceleration, stamina, aggression.

Rótulo verificado en esta pasada: **Extremo con retroceso**.

Atributos clave leídos en la ficha actual: AnticipaciÃ³n, Decisiones, Juego en equipo, Sacrificio, AceleraciÃ³n, Resistencia, Agresividad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Retrocede; Apoya a la defensa.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMR, alcance PosiciÃ³n. [Panel](capturas/091-extremo-retroceso-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 68. Extremo de salida invertida · SP

ID de referencia: `inside_outlet_winger_oop`. Familias: AML, AMR. Nombre inglés: Inside Outlet Winger. Descripción: KEY-696094.

Revisión visual actual: [menú/ficha](capturas/092-extremo-salida-invertida.jpg).

Como Extremo por dentro con salida, se solicita al extremo que evite bajar para ayudar a la lateral que tiene detrás en la medida de lo posible, prefiriendo adelantar su posición para estar en una posición amenazante para un contrataque cuando se produzca una pérdida de balón.

A medida que el equipo rival avanza en el juego, el extremo por dentro con salida también busca moverse hacia la zona central. Esto le permite iniciar contrataques desde zonas con espacios, generalmente con el objetivo de recibir pases directos entre líneas.

Alias del recurso KEY-696138: **Extremo por dentro con salida**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, anticipation, decisions, teamwork, balance, concentration.

Rótulo verificado en esta pasada: **Extremo de salida invertida**.

Atributos clave leídos en la ficha actual: Desmarques, AnticipaciÃ³n, Decisiones, Juego en equipo, Equilibrio, ConcentraciÃ³n. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se queda arriba; Contraataques.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMR, alcance PosiciÃ³n. [Panel](capturas/093-extremo-salida-invertida-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 69. Extremo estacionario · SP

ID de referencia: `wide_outlet_winger_oop`. Familias: AML, AMR. Nombre inglés: Wide Outlet Winger. Descripción: KEY-696097.

Revisión visual actual: [menú/ficha](capturas/094-extremo-estacionario.jpg).

Siendo Escorado con salida, se le solicita al Extremo que evite bajar para ayudar al Lateral que tiene detrás en la medida de lo posible, prefiriendo mantener su posición para estar en una posición amenazante para un contrataque cuando se produzca una pérdida de balón.

Ya que no realiza tanta labor defensiva, a menudo es crucial asegurarse de que el equipo no sufra en su banda, por ejemplo, pidiéndole a los mediocampistas cercanos que desempeñen un rol de Cobertura Amplia para cubrirle.

Alias del recurso KEY-688101: **extremo de salida por banda**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, anticipation, decisions, teamwork, pace, concentration.

Rótulo verificado en esta pasada: **Extremo estacionario**.

Atributos clave leídos en la ficha actual: Desmarques, AnticipaciÃ³n, Decisiones, Juego en equipo, Velocidad, ConcentraciÃ³n. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se queda arriba; Contraataques.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: AMR, alcance PosiciÃ³n. [Panel](capturas/095-extremo-estacionario-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 70. Delantero de apoyo · CP

ID de referencia: `deep_lying_forward_ip`. Familias: STC. Nombre inglés: Deep Lying Forward. Descripción: KEY-690556.

Revisión visual actual: [menú/ficha](capturas/261-delantero-apoyo-ficha.jpg).

La función principal del Delantero de apoyo es conectar el ataque con el mediocampo. Busca posicionarse entre líneas para recibir pases desde zonas profundas y luego distribuir el balón a sus compañeros de diversas maneras: devolviendo el balón hacia el mediocampo para buscar apoyo, abriendo el juego hacia las bandas o, si tiene tiempo para girarse, habilitando a su compañero de ataque.

Alias del recurso KEY-688112: **delantero sorpresa**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): finishing, off_the_ball, first_touch, technique, strength, composure.

Rótulo verificado en esta pasada: **Delantero de apoyo**.

Atributos clave leídos en la ficha actual: Remate, Desmarques, Control, Técnica, Fuerza, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Retrocede al espacio; Conecta el juego.

Resumen de instrucciones en la ficha: Mantener el balón. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: ST (derecha, pareja), alcance Posición. [Panel](capturas/262-delantero-apoyo-instrucciones.jpg).

Controles bloqueados: hold_up_ball_ip = Yes; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 71. Delantero centro · CP

ID de referencia: `centre_forward_ip`. Familias: STC. Nombre inglés: Centre-Forward. Descripción: KEY-690554.

Revisión visual actual: [menú/ficha](capturas/263-delantero-centro-cp-ficha.jpg).

El Delantero centro, también conocido como el clásico 'número 9', es el encargado de liderar la línea de ataque y ser el referente ofensivo del equipo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): finishing, heading, off_the_ball, first_touch, technique, acceleration, strength, composure.

Rótulo verificado en esta pasada: **Delantero centro**.

Atributos clave leídos en la ficha actual: Remate, Cabeceo, Desmarques, Control, Técnica, Aceleración, Fuerza, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Amenaza de gol.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: ST (derecha, pareja), alcance Posición. [Panel](capturas/264-delantero-centro-cp-instrucciones.jpg).

Controles bloqueados: cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, hold_up_ball_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 72. Delantero torre · CP

ID de referencia: `target_forward_ip`. Familias: STC. Nombre inglés: Target Forward. Descripción: KEY-690559.

Revisión visual actual: [menú/ficha](capturas/265-delantero-torre-ficha.jpg).

El Delantero objetivo es un jugador que aprovecha su físico y altura para molestar a la defensa rival y generar ocasiones de gol para su equipo. Durante la fase de construcción, suele ser el principal punto de apoyo en ataque, siendo el objetivo de balones largos o despejes que intenta bajar, prolongar o descargar hacia compañeros cercanos.

Alias del recurso KEY-688126: **Delantero objetivo**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): finishing, heading, off_the_ball, strength, jumping_reach, balance, bravery, aggression.

Rótulo verificado en esta pasada: **Delantero torre**.

Atributos clave leídos en la ficha actual: Remate, Cabeceo, Desmarques, Fuerza, Alcance de salto, Equilibrio, Valentía, Agresividad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Juega en la última línea; Conecta el juego.

Resumen de instrucciones en la ficha: Mantener la posición. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: ST (derecha, pareja), alcance Posición. [Panel](capturas/266-delantero-torre-instrucciones.jpg).

Controles bloqueados: hold_up_ball_ip = Yes; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 73. Ariete · CP

ID de referencia: `poacher_ip`. Familias: STC. Nombre inglés: Poacher. Descripción: KEY-690558.

Revisión visual actual: [menú/ficha](capturas/267-ariete-ficha.jpg).

El Ariete juega al límite de la línea defensiva rival, buscando constantemente romper el fuera de juego y recibir pases definitivos del mediocampo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): finishing, heading, off_the_ball, anticipation, acceleration, composure, concentration.

Rótulo verificado en esta pasada: **Ariete**.

Atributos clave leídos en la ficha actual: Remate, Cabeceo, Desmarques, Anticipación, Aceleración, Serenidad, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Juega en la última línea; Amenaza de gol.

Resumen de instrucciones en la ficha: Mantener la posición. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: ST (derecha, pareja), alcance Posición. [Panel](capturas/268-ariete-instrucciones.jpg).

Controles bloqueados: freedom_of_movement_ip = Follow Tactical Position; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, hold_up_ball_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 74. Delantero entre líneas · CP

ID de referencia: `channel_forward_ip`. Familias: STC. Nombre inglés: Channel Forward. Descripción: KEY-690555.

Revisión visual actual: [menú/ficha](capturas/269-delantero-entre-lineas-ficha.jpg).

Un rol de alta intensidad, el Delantero entre líneas busca ser una molestia constante para los defensores rivales, realizando de forma habitual desmarques de apoyo hacia las zonas laterales para su equipo.

Alias del recurso KEY-688635: **delantero de canal**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): dribbling, finishing, off_the_ball, first_touch, technique, work_rate, acceleration, composure.

Rótulo verificado en esta pasada: **Delantero entre líneas**.

Atributos clave leídos en la ficha actual: Regate, Remate, Desmarques, Control, Técnica, Sacrificio, Aceleración, Serenidad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se abre a las bandas; Amenaza de gol.

Resumen de instrucciones en la ficha: Moverse entre líneas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: ST (derecha, pareja), alcance Posición. [Panel](capturas/270-delantero-entre-lineas-instrucciones.jpg).

Controles bloqueados: hold_up_ball_ip = No; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, forward_runs_ip, freedom_of_movement_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 75. Falso nueve · CP

ID de referencia: `false_nine_ip`. Familias: STC. Nombre inglés: False Nine. Descripción: KEY-690557.

Revisión visual actual: [menú/ficha](capturas/271-falso-nueve-ficha.jpg).

Un delantero centro poco convencional, el Falso Nueve suele estar entre las líneas de la defensa y el mediocampo del equipo rival, buscando actuar de manera similar a un Organizador avanzado para su equipo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): dribbling, off_the_ball, passing, vision, decisions, first_touch, technique, teamwork.

Rótulo verificado en esta pasada: **Falso nueve**.

Atributos clave leídos en la ficha actual: Regate, Desmarques, Pases, Visión, Decisiones, Control, Técnica, Juego en equipo. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Retrasa su posición para ser mediapunta; Conecta el juego.

Resumen de instrucciones en la ficha: Variar la posición. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: ST (derecha, pareja), alcance Posición. [Panel](capturas/272-falso-nueve-instrucciones.jpg).

Controles bloqueados: forward_runs_ip = Standard; freedom_of_movement_ip = Roam From Position; cross_from_ip = Standard; crossing_strategy_ip = Standard.

Controles editables: attacking_width_ip, dribbling_direction_ip, dribbling_frequency_ip, hold_up_ball_ip, shoot_ip, passing_risk_ip, passing_directness_ip. No extrapolar a otros subpuestos o alcances.

#### 76. Delantero centro · SP

ID de referencia: `centre_forward_oop`. Familias: STC. Nombre inglés: Centre-Forward. Descripción: KEY-690489.

Revisión visual actual: [menú/ficha](capturas/257-delantero-centro-sp-ficha.jpg).

El Delantero centro marca el tono de la estrategia defensiva de su equipo, y generalmente es quien empieza a presionar, o tapando pases en el centro del campo.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): anticipation, decisions, work_rate.

Rótulo verificado en esta pasada: **Delantero centro**.

Atributos clave leídos en la ficha actual: Anticipación, Decisiones, Sacrificio. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: sin etiquetas.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: ST (derecha, pareja), alcance Posición. [Panel](capturas/258-delantero-centro-sp-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 77. Delantero centro con retroceso · SP

ID de referencia: `tracking_centre_forward_oop`. Familias: STC. Nombre inglés: Tracking Centre-Forward. Descripción: KEY-690490.

Revisión visual actual: [menú/ficha](capturas/255-delantero-retroceso-ficha.jpg).

Como Rastreador, al Delantero centro se le indica que retroceda defensivamente cuando el equipo rival avanza hacia el tercio defensivo propio, con el fin de apoyar a los mediocampistas que tiene por detrás, replegándose a una posición defensiva más profunda.

Alias del recurso KEY-688104: **delantero centro de seguimiento**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): anticipation, decisions, teamwork, work_rate, stamina, aggression.

Rótulo verificado en esta pasada: **Delantero centro con retroceso**.

Atributos clave leídos en la ficha actual: Anticipación, Decisiones, Juego en equipo, Sacrificio, Resistencia, Agresividad. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Retrocede; Apoya a la defensa.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: ST (derecha, pareja), alcance Posición. [Panel](capturas/256-delantero-retroceso-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 78. Delantero centro estacionario · SP

ID de referencia: `central_outlet_centre_forward_oop`. Familias: STC. Nombre inglés: Central Outlet Centre-Forward. Descripción: KEY-690488.

Revisión visual actual: [menú/ficha](capturas/259-delantero-estacionario-ficha.jpg).

Cuando tiene salida central, se solicita al Delantero centro que evite bajar para ayudar a los mediocampistas que tiene detrás en la mayor medida posible, prefiriendo mantener su posición para estar en una posición amenazante para un contrataque cuando se produzca una pérdida de balón.

Alias del recurso KEY-688105: **Delantero centro con salida**. No reemplazar automáticamente el rótulo visto en el menú.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, anticipation, decisions, teamwork, balance, concentration.

Rótulo verificado en esta pasada: **Delantero centro estacionario**.

Atributos clave leídos en la ficha actual: Desmarques, Anticipación, Decisiones, Juego en equipo, Equilibrio, Concentración. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se queda arriba; Contraataques.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: ST (derecha, pareja), alcance Posición. [Panel](capturas/260-delantero-estacionario-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

#### 79. Delantero centro de ruptura con salida (nombre de recurso) · SP

ID de referencia: `splitting_outlet_centre_forward_oop`. Familias: STC. Nombre inglés: Splitting Outlet Centre-Forward. Descripción: KEY-690487.

Revisión visual actual: [menú/ficha](capturas/114-delantero-salida.jpg).

Con Ruptura con salida, se solicita al Delantero centro que evite bajar para ayudar a los mediocampistas que tiene detrás en la mayor medida posible, prefiriendo adelantar su posición para estar en una posición amenazante para un contrataque cuando se produzca una pérdida de balón.

Atributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): off_the_ball, anticipation, decisions, teamwork, pace, concentration.

Rótulo verificado en esta pasada: **Delantero centro estacionario con salida**.

Atributos clave leídos en la ficha actual: Desmarques, AnticipaciÃ³n, Decisiones, Juego en equipo, Velocidad, ConcentraciÃ³n. No se registran los valores personales como constantes del rol.

Comportamientos mostrados: Se queda arriba; Contraataques.

Resumen de instrucciones en la ficha: sin órdenes listadas. Este resumen no sustituye el panel de candados.

Contexto de instrucciones comprobado: ST-right, alcance PosiciÃ³n. [Panel](capturas/115-delantero-salida-instrucciones.jpg).

Controles bloqueados: ninguno.

Controles editables: pressing_oop, marking_oop, tackling_oop, marking_target_oop. No extrapolar a otros subpuestos o alcances.

## 5. Instrucciones individuales: los 15 grupos y sus 45 opciones

Los nombres siguientes se leyeron en los menús actuales. Las explicaciones largas se vinculan con claves del recurso instalado; estas vinculaciones son por significado/contexto, no identificadores extraídos de la partida. La app debe permitir una sola opción por grupo y conservar los valores desconocidos como desconocidos.

Algunas claves nuevas no tienen traducción en el LTC instalado o todavía devuelven inglés. En esos casos se incluye una explicación en español escrita para este informe y se conserva el original inglés por separado. Esa explicación no es una transcripción oficial del juego.

`Estándar` aparece en amplitud, regate y carreras. `Normal` aparece en disparos, pases, centros y SP. No normalizar indiscriminadamente los rótulos españoles. Un valor estándar sigue dependiendo del rol, estrategia colectiva y preferencias personales; no equivale a apagar el comportamiento.

### Amplitud del ataque · CP

ID de referencia: `attacking_width_ip`. [Menú actual](capturas/020-menu-amplitud-cp.jpg).

**Abrirse a banda** (`Stay Wider`; KEY-703124).

Anima a ocupar una posición más escorada durante los ataques para intentar estirar más el juego.

**Situarse más cerrado** (`Sit Narrower`; KEY-706686).

Explicación en español (redacción del informe): Ocupar una posición más estrecha al atacar para acortar las distancias de pase con los compañeros.

Original de referencia en inglés: Encourage the player to take up a narrower position during attacks in order to create a smaller passing distance between them and the rest of the team.

**Moverse entre líneas** (`Move Into Channels`; KEY-703125).

Se le anima a realizar más desmarques hacia los espacios detrás de la defensa rival, entre el central y el lateral.

**Estándar** (`Standard`; KEY-683095).

La amplitud de ataque del jugador se basará en su rol de posesión y la estrategia de juego del equipo. No se darán instrucciones específicas al jugador.

### Dirección del regate · CP

ID de referencia: `dribbling_direction_ip`. [Menú actual](capturas/026-menu-direccion-regate-cp.jpg).

**Abrirse con el balón** (`Run Wide With Ball`; KEY-706661).

Explicación en español (redacción del informe): Conducir hacia las bandas para ensanchar la jugada y estirar al rival.

Original de referencia en inglés: Ask the player to dribble into wide areas with the ball when possible, in an attempt to stretch the opposition.

**Recortar hacia dentro** (`Cut Inside With Ball`; KEY-706660).

Explicación en español (redacción del informe): Conducir hacia zonas centrales, entrando por dentro del defensor y orientándose hacia el arco.

Original de referencia en inglés: Ask the player to dribble into central areas when they receive the ball, driving inside their opponent and towards goal.

**Estándar** (`Standard`; KEY-683096).

La dirección del regate de un jugador se basará en su pierna buena y las preferencias personales. No se darán instrucciones específicas al jugador.

### Frecuencia del regate · CP

ID de referencia: `dribbling_frequency_ip`. [Menú actual](capturas/005-regate-arquero-cp.jpg).

**Regatear más** (`Dribble More`; KEY-703139).

Anima a los jugadores a ser más individualistas con el balón e intentar regatear a sus rivales en vez de pasar el balón a un compañero.

**Regatear menos** (`Dribble Less`; KEY-703138).

Prefiere participar en combinaciones de pases para superar a su marcador, en vez de hacerlo regateando.

**Estándar** (`Standard`; KEY-683097).

La frecuencia de regates de un jugador se basará en su rol, la estrategia de juego del equipo y sus propias preferencias personales.

### Carreras hacia adelante · CP

ID de referencia: `forward_runs_ip`. [Menú actual](capturas/021-menu-carreras-cp.jpg).

**Hacer más desmarques** (`Make More Runs`; KEY-706566).

Explicación en español (redacción del informe): Hacer más desmarques ofensivos al espacio para sumar amenazas y sobrecargar a la defensa rival.

Original de referencia en inglés: Encourages the player to make more forward runs into space in an attempt to overload the opposition defence.

**Estándar** (`Standard`; KEY-703134).

El número de desmarques que realicen los delanteros se determinarán por el rol y las preferencias personales.

**Hacer menos carreras** (`Make Fewer Runs`; KEY-683145).

Hace que el jugador no intente hacer tantos desmarques, en vez de quedarse en su posición esperada.

### Libertad de movimientos · CP

ID de referencia: `freedom_of_movement_ip`. [Menú actual](capturas/022-menu-libertad-cp.jpg).

**Variar la posición** (`Roam From Position`; KEY-683144).

Da libertad al jugador para abandonar la posición que tenía fijada dentro de la estructura ofensiva del equipo y así encontrar huecos en donde cree que puede ser más efectivo.

**Sigue posición táctica** (`Follow Tactical Position`; KEY-683143).

Ordena a los jugadores que permanezcan preferentemente en su posición asignada dentro de la estructura ofensiva del equipo y rara vez se desviarán de eso.

### Aguantar el balón · CP

ID de referencia: `hold_up_ball_ip`. [Menú actual](capturas/027-menu-aguantar-cp.jpg).

**Sí** (`Yes`; KEY-683166).

Pide al jugador que juegue de espaldas a la portería y mantenga el balón un poco más de lo que haría habitualmente, ralentizando algo el juego para que sus compañeros puedan subir al ataque para apoyar.

**No** (`No`; KEY-683167).

Al jugador no se le pedirá que juegue de espaldas a la portería ni que aguante el balón; en su lugar, intentará recibir el balón de la forma que sea más natural para él.

### Disparos · CP

ID de referencia: `shoot_ip`. [Menú actual](capturas/025-menu-disparos-cp.jpg).

**Disparar con más frecuencia** (`Shoot More Often`; KEY-704617).

Explicación en español (redacción del informe): Aumentar los intentos de remate cuando surge una oportunidad, en lugar de priorizar otro pase.

Original de referencia en inglés: Encourages the player to attempt a greater number of shots when posed with a potential opportunity, rather than looking for a pass.

**Disparar con menos frecuencia** (`Shoot Less Often`; KEY-706455).

Explicación en español (redacción del informe): Conservar la pelota y esperar una ocasión clara antes de rematar.

Original de referencia en inglés: Asks to retain possession and remain patient, only shooting when they are presented with a clear-cut goalscoring opportunity.

**Normal** (`Standard`; KEY-703157).

La tendencia a disparar se determinará por el estilo de juego y las preferencias personales

### Riesgo en los pases · CP

ID de referencia: `passing_risk_ip`. [Menú actual](capturas/024-menu-riesgo-pases-cp.jpg).

**Tomar más riesgos** (`Take More Risks`; KEY-706523).

Explicación en español (redacción del informe): Intentar más pases difíciles y pases al espacio, aceptando fallos a cambio de la posibilidad de romper la defensa.

Original de referencia en inglés: Encourages the player to play more low-percentage passes and through balls in the hope that one or two of them will unlock the opposition defence in a potentially decisive manner.

**Tomar menos riesgos** (`Take Fewer Risks`; KEY-703155).

Exige a los jugadores que mantengan la posesión ante todo, jugando de forma sensata y paciente sin perder el balón innecesariamente

**Normal** (`Standard`; KEY-703151).

El riesgo en los pases del jugador estará determinado por la estrategia de pases del equipo, su rol y sus preferencias personales

### Estrategia de pase · CP

ID de referencia: `passing_directness_ip`. [Menú actual](capturas/006-pases-arquero-cp.jpg).

**Más corto** (`Shorter`; KEY-706457).

Explicación en español (redacción del informe): Jugar pases más cortos que los del resto del equipo y simplificar el uso del balón.

Original de referencia en inglés: Asks to play shorter passes than the rest of the team, looking to keep things simple when they have the ball.

**Más directo** (`More Direct`; KEY-706456).

Explicación en español (redacción del informe): Jugar pases más largos que los del resto del equipo para llevar la pelota hacia adelante con mayor rapidez.

Original de referencia en inglés: Asks to play longer passes than the rest of the team in an attempt to get the ball from back to front more quickly.

**Normal** (`Standard`; KEY-703169).

Lo directos que sean los pases se determinarán por la estrategia de pases del equipo, el rol y las preferencias personales

### Centro desde · CP

ID de referencia: `cross_from_ip`. [Menú actual](capturas/023-menu-centro-desde-cp.jpg).

**Centro desde atrás** (`Cross From Deep`; KEY-706459).

Explicación en español (redacción del informe): Centrar en cuanto aparezca la ocasión, sin esperar a llegar a una zona más avanzada.

Original de referencia en inglés: Asks to cross the ball into the box as soon as they get the opportunity to do so, rather than try to work the ball into a better area beforehand.

**Línea de fondo** (`Byline`; KEY-706453).

Explicación en español (redacción del informe): Avanzar con el balón por la banda antes de intentar el centro al área.

Original de referencia en inglés: Asks to get the ball as high up the pitch as possible in wide areas before attempting to cross the ball into the penalty area.

**Normal** (`Standard`; KEY-703144).

La frecuencia con que se realizan centros se determinará por el estilo de juego y las preferencias personales.

### Estrategia de centros · CP

ID de referencia: `crossing_strategy_ip`. [Menú actual](capturas/028-menu-estrategia-centros-cp.jpg).

**Segundo palo** (`Far Post`; KEY-706448).

Explicación en español (redacción del informe): Dirigir los centros al segundo palo cuando sea posible.

Original de referencia en inglés: Asks to deliver crosses towards the far post when possible.

**Centro** (`Centre`; KEY-706446).

Explicación en español (redacción del informe): Dirigir los centros hacia la zona central del área cuando sea posible.

Original de referencia en inglés: Asks to deliver crosses towards the middle of the box when possible.

**Primer poste** (`Near Post`; KEY-706447).

Explicación en español (redacción del informe): Dirigir los centros al primer palo cuando sea posible.

Original de referencia en inglés: Asks to deliver crosses towards the near post when possible.

**Delantero torre** (`Target Forward`; KEY-703166).

Pide al jugador que intente centrar el balón hacia el delantero objetivo, si es que hay uno

**Normal** (`Standard`; KEY-703163).

Libertad para elegir la mejor zona para centrar el balón dependiendo de la situación

### Presión alta · SP

ID de referencia: `pressing_oop`. [Menú actual](capturas/031-menu-presion-sp.jpg).

**Más a menudo** (`More Often`; KEY-703077).

Pide al jugador que sea más proactivo en relación a la presión, intentando enfrentarse al rival con más frecuencia siempre que se presente la oportunidad.

**Menos a menudo** (`Less Often`; KEY-706458).

Explicación en español (redacción del informe): Presionar con más paciencia y esperar una oportunidad adecuada para entrar al rival.

Original de referencia en inglés: Asks to be more patient when it comes to pressing, waiting more for the right opportunity to engage with the opponent.

**Normal** (`Standard`; KEY-703084).

El jugador seguirá más la estrategia de presión del equipo.

### Marca · SP

ID de referencia: `marking_oop`. [Menú actual](capturas/032-menu-marca-sp.jpg).

**Marca más férrea** (`Mark Tighter`; KEY-703086).

Pide al jugador que se mantenga fijo en su marca en situaciones defensivas para limitar los espacios que tengan cuando ataquen con el balón.

**Normal** (`Standard`; KEY-703094).

La distancia a la que marque un jugador dependerá de la estrategia defensiva del equipo, del rol que tenga y de sus propias preferencias.

### Entradas · SP

ID de referencia: `tackling_oop`. [Menú actual](capturas/033-menu-entradas-sp.jpg).

**Entrar más fuerte** (`Tackle Harder`; KEY-706568).

Explicación en español (redacción del informe): Disputar el balón de forma más agresiva y usar el físico y las entradas para recuperarlo.

Original de referencia en inglés: Encourages the player to be aggressive and engage their mark as much as possible, using their physicality and putting in tackles in order to win the ball back.

**No entrar fuerte** (`Ease Off Tackles`; KEY-706567).

Explicación en español (redacción del informe): Mantenerse firme, por el lado del arco propio, y orientar al rival lejos del peligro en vez de lanzarse a la entrada.

Original de referencia en inglés: Encourages the player to stand their ground more when their mark receives the ball, instead looking to stay goal side and shield them away from danger.

**Normal** (`Standard`; KEY-703095).

El compromiso defensivo y la forma de entrar a los balones del jugador estarán determinados por la estrategia defensiva del equipo, su rol y sus preferencias personales.

### Objetivo de marca · SP

ID de referencia: `marking_target_oop`. [Menú actual](capturas/034-menu-objetivo-marca-sp.jpg).

**Marca específica** (`Mark Specific`; KEY-706460).

Explicación en español (redacción del informe): Seguir a un jugador rival concreto para limitar su participación. Esta instrucción se refiere al juego abierto y no cambia el marcaje en jugadas de balón parado.

Original de referencia en inglés: Asks to closely follow a specific opposition player around the pitch, in an effort to mark them out of the game.  This instruction only applies to open play situations, so does not affect how the player marks during set pieces.

**Marcar posición** (`Mark Position`; KEY-706454).

Explicación en español (redacción del informe): Seguir al rival que ocupe el puesto seleccionado. Esta instrucción se refiere al juego abierto y no cambia el marcaje en jugadas de balón parado.

Original de referencia en inglés: Asks to closely follow any opposition player playing in the selected position, in an effort to mark them out of the game.  This instruction only applies to open play situations, so does not affect how the player marks during set pieces.

**Normal** (`Standard`; KEY-703115).

El jugador marcará de la forma que mejor encaje con la estrategia defensiva general del equipo

### Distinciones que afectan al software

- **Amplitud** modifica dónde se ofrece sin balón; **dirección del regate** modifica la conducción con balón. Pueden combinarse; no son el mismo control.
- **Carreras hacia adelante** y **libertad de movimientos** son dimensiones distintas.
- **Riesgo en los pases** es distinto de **Estrategia de pase**. Arriesgar más no equivale a jugar más largo.
- **Centro desde** define el origen de los centros. **Estrategia de centros** define su destino: segundo palo, centro, primer poste o delantero torre. No es un selector de frecuencia. El **estilo** de centro —raso, alto, etc.— aparece entre las instrucciones colectivas.
- **Marca** establece proximidad. **Objetivo de marca** agrega una referencia a un jugador o puesto rival. Guardar solo el enum “Marca específica” pierde el objetivo necesario.
- “Sí” en **Distribución del portero en corto**, dentro de la presión colectiva SP, pide impedir la salida corta del **arquero rival**. No ordenar al propio arquero distribuir corto por esa casilla.

### Disponibilidad, bloqueos y modificaciones

El icono de candado se explica como **Instrucción no disponible**. El indicador turquesa se explica como **Instrucción modificada**. Un bloqueo puede deberse al rol o al puesto; no asumir una sola causa universal.

En el extremo izquierdo CP, “Moverse entre líneas” está deshabilitado y el panel dice expresamente que es incompatible con la posición del jugador. [020](capturas/020-menu-amplitud-cp.jpg).

En Portero con salida CP se ven candados en amplitud, dirección del regate, carreras, libertad, aguantar, disparos, riesgo en pases, centro desde y estrategia de centros. Frecuencia del regate y estrategia de pase quedan editables en la vista inspeccionada. Riesgo muestra Tomar más riesgos. [004](capturas/004-instrucciones-arquero-cp.jpg).

En Portero líbero SP, presión, marca y objetivo tienen candado y muestran Normal. **Entradas no tiene candado**. La pantalla no muestra que el rol obligue a “Más a menudo” en presión individual; esa inferencia sería incorrecta. [010](capturas/010-instrucciones-portero-sp.jpg).

Para el resto, mantener `unknown` donde no haya captura del bloqueo en ese contexto. No convertir una orden resumida en una prueba de bloqueo. Para certificar el estado efectivo de un jugador, relevar también el alcance Jugador y sus personalizaciones.

## 6. Instrucciones de equipo: ocho vistas revisadas

Valores de la táctica actual; no son recomendaciones universales. Hay 29 apariciones de controles en estas ocho vistas: Regate aparece en dos subfases CP y Trampa de presión aparece en dos bloques SP. No contar cada aparición como un parámetro independiente sin verificar cómo comparte estado.

| Fase | Área | Instrucción | Valor visto | Captura |
|---|---|---|---|---|
| CP | Vista general | Pases directos | Mucho más corto | [044](capturas/044-equipo-cp-general.jpg) |
| CP | Vista general | Ritmo de juego | Mucho más bajo | [044](capturas/044-equipo-cp-general.jpg) |
| CP | Vista general | Amplitud del ataque | Más estrecho | [044](capturas/044-equipo-cp-general.jpg) |
| CP | Vista general | Transición ofensiva | Normal | [044](capturas/044-equipo-cp-general.jpg) |
| CP | Vista general | Libertad creativa | Equilibrado | [044](capturas/044-equipo-cp-general.jpg) |
| CP | Vista general | Perder tiempo | Menos a menudo | [044](capturas/044-equipo-cp-general.jpg) |
| CP | Vista general | Jugar buscando el balón parado | Buscar jugadas de balón parado | [044](capturas/044-equipo-cp-general.jpg) |
| CP | Último tercio | Regate | Animar | [045](capturas/045-equipo-cp-ultimo-tercio.jpg) |
| CP | Último tercio | Paciencia | Intentar llevar el balón hasta el área | [045](capturas/045-equipo-cp-ultimo-tercio.jpg) |
| CP | Último tercio | Disparos lejanos | Alentar | [045](capturas/045-equipo-cp-ultimo-tercio.jpg) |
| CP | Último tercio | Estilo de centros | Centros rasos | [045](capturas/045-equipo-cp-ultimo-tercio.jpg) |
| CP | Avance | Carreras de apoyo | Equilibrado | [046](capturas/046-equipo-cp-avance.jpg) |
| CP | Avance | Regate | Animar | [046](capturas/046-equipo-cp-avance.jpg) |
| CP | Avance | Avance | Izquierda | [046](capturas/046-equipo-cp-avance.jpg) |
| CP | Avance | Recepción de pase | Pase al pie | [046](capturas/046-equipo-cp-avance.jpg) |
| CP | Área de creación de oportunidades | Estrategia previa | Jugar superando la presión | [047](capturas/047-equipo-cp-creacion.jpg) |
| CP | Área de creación de oportunidades | Saques de meta | En corto | [047](capturas/047-equipo-cp-creacion.jpg) |
| CP | Área de creación de oportunidades | Distribución del portero (velocidad) | Distribuir con rapidez | [047](capturas/047-equipo-cp-creacion.jpg) |
| CP | Área de creación de oportunidades | Distribución del portero | Equilibrado | [047](capturas/047-equipo-cp-creacion.jpg) |
| SP | Vista general | Línea de presión | Presión adelantada | [049](capturas/049-equipo-sp-general.jpg) |
| SP | Vista general | Línea defensiva | Más adelantada | [049](capturas/049-equipo-sp-general.jpg) |
| SP | Vista general | Comportamiento de la línea defensiva | Presionar más arriba | [049](capturas/049-equipo-sp-general.jpg) |
| SP | Vista general | Activar presión | Más insistente | [049](capturas/049-equipo-sp-general.jpg) |
| SP | Vista general | Transición defensiva | Contrapresión | [049](capturas/049-equipo-sp-general.jpg) |
| SP | Vista general | Realizando una entrada | Ser agresivos | [049](capturas/049-equipo-sp-general.jpg) |
| SP | Presión adelantada | Trampa de presión | Equilibrado | [050](capturas/050-equipo-sp-presion-alta.jpg) |
| SP | Presión adelantada | Distribución del portero en corto | Sí | [050](capturas/050-equipo-sp-presion-alta.jpg) |
| SP | Bloque medio | Trampa de presión | Equilibrado | [051](capturas/051-equipo-sp-bloque-medio.jpg) |
| SP | Bloque bajo | Compromiso de centros | Evitar centros | [052](capturas/052-equipo-sp-bloque-bajo.jpg) |

El anexo de recursos conserva opciones, descripciones y reacciones del cuerpo técnico de las instrucciones colectivas. En esta sesión se revisaron sus ocho vistas; **actualización: se abrieron los 27 paneles únicos y se transcribieron sus opciones; no todas las combinaciones ni ayudas**. No elevar el contenido del archivo a una matriz de controles confirmados.

## 7. Diferencias concretas con el programa actual

1. `fm_app/data/fm26_catalog.json` tiene 74 registros de rol. Hay un registro específico de Carrilero organizador para laterales además del general. Al unificar ese duplicado quedan 73 definiciones; este paquete agrega seis ausentes y llega a **79**: Central abierto CP, Central que dobla CP, Central abierto SP, Central de cobertura abierta SP, Zaguero abierto SP y Mediocentro presionante SP. Su inclusión final debe respetar los subpuestos y la evidencia.
2. `passing_directness_ip` solo declara `Standard` y `Shorter` en el catálogo actual. El menú muestra también **Más directo**; la descripción de instalación está en KEY-706456. Hay que incorporarlo al contrato, validación, UI, persistencia y análisis, no solo al rótulo.
3. La aplicación guarda 14 familias de puesto. Esa estructura necesita conservar subpuesto o contexto para no ofrecer roles que el menú no permite en un pivote central único o un punta central único.
4. El español de `fm26_es419.json` no garantiza el rótulo de cada superficie del juego. Por ejemplo KEY-688113 dice “Portero jugador”, mientras el menú muestra “Portero con salida”; KEY-688119 y algunos textos dicen “pivote organizador”, pero las pantallas usan Organizador defensivo y ORD. Guardar alias por clave/superficie/idioma; no reemplazar globalmente por una traducción.
5. `SCREENSHOT_LOCKS` conserva bloqueos del relevamiento previo. Debe evolucionar hacia reglas con puesto, fase y alcance. Una clave vacía no prueba por sí sola disponibilidad en todas las posiciones posibles.
6. El código pondera roles CP/SP con **80/20** y añade reglas propias de atributos y zonas. Son decisiones de Touchline. Nada de esta revisión prueba que sean pesos del motor de FM ni probabilidades de éxito.
7. La referencia histórica de Liverpool no coincide íntegramente con la táctica abierta: ahora ambos centrales muestran CCS CP; Ayari pasa de OAD CP a MP SP y Wharton de MOR CP a MD SP. No usar capturas históricas como estado actual automático.

## 8. Especificación de reconstrucción propuesta

Esta sección propone diseño de software; no atribuye estas estructuras al código interno de FM.

### Entidades y procedencia

- `RoleDefinition`: id de referencia estable, fase, nombre base y alias por idioma/superficie, descripción, comportamientos inherentes, atributos de referencia y procedencia.
- `PositionSlot`: familia, lado/subpuesto, coordenada base por fase, identidad de puesto en el dibujo y contexto de vecinos. Los códigos de archivo aún desconocidos se conservan aparte.
- `InstructionDefinition`: grupo, fase, opciones válidas, descripción por opción y objetivos adicionales cuando correspondan.
- `InstructionSetting`: opción explícita o valor desconocido, alcance posición/jugador, target rival cuando exista, fuente, estado de modificación y disponibilidad conocida/desconocida.
- `AvailabilityRule`: fase + puesto/subpuesto + rol + contexto + alcance, estado permitido/no disponible/desconocido, causa y evidencia.
- `Tactic`: mismo once con dos asignaciones de fase; instrucciones colectivas y personales separadas; versión y huellas de la referencia.

No representar un desconocido como `Normal`, `No`, cero o un candado. No reemplazar una selección del usuario al recalcular sugerencias. Mantener claramente separados valor observado, restricción observada e interpretación del analizador.

### Comportamiento de interfaz esperado

Seleccionar fase → puesto concreto → rol compatible → instrucciones. Mostrar por qué una opción está deshabilitada, incluyendo “aún no verificada” si no hay evidencia. Permitir alternar alcance Posición/Jugador. Mostrar el movimiento entre las dos fases manteniendo el mismo futbolista. Describir cambios de forma verificable y no prometer resultados deportivos.

### Pruebas de aceptación significativas

1. El catálogo mantiene un único Carrilero organizador CP con varias familias compatibles, evitando duplicados por rótulo.
2. El mismo jugador puede ser MC CP y AMC SP, o AML CP y ML SP, sin duplicar su identidad.
3. La longitud Más directo se conserva y valida de extremo a extremo.
4. Una asignación desconocida sigue desconocida al guardar, recargar y recomendar.
5. Marca específica requiere rival identificado; Marcar posición requiere puesto rival identificado.
6. Un control modificado permanece distinto de un control bloqueado. Las restricciones no se extienden a contextos no comprobados.
7. El menú de Portero con salida permite las dos dimensiones editables observadas y conserva las restricciones documentadas. El de Portero líbero no bloquea Entradas por inferencia.
8. Centro desde, destino de centros y estilo colectivo de centros son tres conceptos separados.
9. La UI conserva los alias españoles sin usar la etiqueta traducida como clave de datos.
10. La evaluación explica qué viene de atributos, qué viene de la táctica y qué es una regla propia. Cambiar un dato de entrada invalida los resultados dependientes.

## 9. Pendientes explícitos de verificación

- La reapertura visual de los 24 roles antes pendientes quedó cerrada: los 79 roles tienen captura de menú/ficha. Esto acredita presencia en al menos un contexto, no selección individual de todas las fichas de la primera pasada.
- Hay paneles registrados para 79 roles y listas de atributos cotejadas para 79. La lista exacta de los 0 paneles y 0 listas pendientes está en `PENDIENTES.md`; los IDs están también en `cobertura-y-pendientes.json`.
- Los tres valores antes tapados de Aguantar el balón quedaron confirmados visualmente en **No**, con candado: Central abierto CP, Central que dobla CP y Mediocampista todoterreno CP. [273](capturas/273-todoterreno-aguantar-confirmado.jpg), [274](capturas/274-central-abierto-aguantar-confirmado.jpg), [275](capturas/275-central-dobla-aguantar-confirmado.jpg).
- La matriz completa de subpuesto, rol, fase y alcance Posición/Jugador sigue sin certificarse. Priorizar únicamente los contextos que necesite la reconstrucción; la partida de prueba puede modificarse con autorización del usuario.
- Los destinos de Marca específica y Marcar posición ya se abrieron: 25 puestos de campo más Ninguna, o lista dinámica de 10 rivales de campo más Ninguna en el prepartido observado. La investigación adicional de marcaje queda excluida por pedido del usuario. [118](capturas/118-marcar-posicion-destinos.jpg), [120](capturas/120-marca-jugador-destinos.jpg).
- Consultar ADENDA-COLECTIVAS.md: conjuntos de opciones y dos controles compartidos confirmados; las combinaciones de contexto y ayudas no abiertas son límites no bloqueantes del alcance acordado.
- Las 79 listas de atributos fueron cotejadas visualmente. Ninguna lista observada revela pesos numéricos del motor.
- Decodificar, si se desea automatizar la lectura, posiciones, roles e instrucciones de la partida y cotejarlos contra estos menús. Las cadenas de traducción no proporcionan ese mapeo.

## 10. Archivos para la otra IA

- `REPORTE.md`: este informe, con todas las fichas y opciones.
- `catalogo-para-reconstruccion.json`: catálogo normalizado, descripciones, nombres, procedencia y límites.
- `textos-instalacion.json`: registros originales seleccionados y huellas de instalación.
- `ANEXO-TEXTOS-INSTRUCCIONES.md`: textos de ayuda, opciones y reacciones con sus contextos, conservando variantes y ambigüedades.
- `observaciones-ui.json` y `capturas/`: evidencia visual actual, con SHA-256.
- `verificacion-adicional-roles.json`: fichas, atributos, comportamientos y controles comprobados en la continuación.
- `verificacion-adicional-mecanicas.json`: destinos de marcaje y otras mecánicas comprobadas.
- `PROMPT-PARA-OTRA-IA.md`: pedido de implementación listo para adjuntar.
- `matriz-instrucciones-observadas.json`: un panel representativo por cada rol comprobado, con valores bloqueados y grupos editables.
- `PENDIENTES.md` y `cobertura-y-pendientes.json`: cobertura final y faltantes exactos.

Fuentes del proyecto consultadas: `README.md`, `docs/fm26-reference.md`, `docs/tactica-actual-y-zonas.md`, `docs/screenshots/Guia de roles FM - capturas.md`, `fm_app/data/fm26_catalog.json`, `fm_app/data/fm26_es419.json`, `fm_app/fm26.py` y `fm_app/current_tactic.py`. El reporte histórico no se trató como comprobación actual.

## Actualización: selectores colectivos observados

Se revisaron **27 paneles colectivos únicos (28 dimensiones)** y se confirmaron dos controles compartidos. Leé [ADENDA-COLECTIVAS.md](ADENDA-COLECTIVAS.md) y [verificacion-colectivas.json](verificacion-colectivas.json). Estas pruebas cierran la lista de opciones visibles y las duplicaciones de Regate/Trampa de presión; las combinaciones de contexto y todas las ayudas siguen sin certificarse. El marcaje queda excluido de nuevas investigaciones por pedido del usuario.

## Actualización del 26/10/2026: costados y portero

Quedaron cerrados los desdobles por costado y los botones duplicados del portero. La matriz 4×4 tiene nueve combinaciones seleccionadas y siete bloqueadas en el contexto observado: exterior e interior coexisten en lados opuestos y se excluyen en el mismo lado. Los dos botones Bandas son equivalentes entre sí; también los dos Laterales. Leé [ADENDA-COSTADOS-PORTERO-2026-10-26.md](ADENDA-COSTADOS-PORTERO-2026-10-26.md) y [verificacion-costados-portero-2026-10-26.json](verificacion-costados-portero-2026-10-26.json). Se incorporaron 17 capturas nuevas. Persisten únicamente los contextos no ensayados y las ayudas no abiertas; no extrapolar reglas universales.

## Cierre del alcance acordado — 26/10/2026

El relevamiento queda completo para el alcance acordado; no hay identificado un dato indispensable pendiente. Los contextos no ensayados y las ayudas no abiertas individualmente son límites no bloqueantes. No se confirmó que cambiar la mentalidad modifique los candados individuales: no implementar bloqueos por esa hipótesis. La búsqueda web no proporcionó una matriz universal ni certifica los textos exactos de la instalación; se conservan los recursos locales extraídos. Aplicar las restricciones documentadas con su procedencia, mantener desconocidos explícitos y revisar casos nuevos ante discrepancias concretas. El marcaje sigue excluido. Ver [ALCANCE-Y-CIERRE.md](ALCANCE-Y-CIERRE.md) y [PROMPT-ACTUALIZACION-INCREMENTAL.md](PROMPT-ACTUALIZACION-INCREMENTAL.md). Este cierre prevalece sobre listas históricas que parezcan exigir probar todas las combinaciones antes de implementar.
