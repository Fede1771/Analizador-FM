# Táctica actual, instrucciones individuales y cobertura por zonas

Actualización: 29/10/2026. Lectura táctica v2, instalador 1.0.1.

## Datos leídos y datos confirmados

`fmsave 0.5.11` recupera las copias tácticas por equipo. Touchline añade un adaptador para las máscaras de posición y las tablas de roles de FM26, extraídas de los enums `PositionMask`, `InPossessionRole` y `OutOfPossessionRole` de los recursos de Unity del juego. `scripts/generate_tactic_codes.py` permite regenerar la tabla incluida en `fm_app/data/tactic_codes.json`. No requiere tener FM instalado para utilizar el instalador resultante.

El lector recupera los primeros once selectores de la selección guardada del equipo y los resuelve contra el índice de jugadores de esa misma partida. Conserva los huecos y los costados de los puestos centrales. Vincula las fases por `out_of_possession_position_index`, comprobando que sea una permutación completa. Ni el nombre del club ni el nombre de la táctica determinan el esquema o los jugadores. El archivo de Brighton del 31/05/2026 devuelve 11 seleccionados, 4-2-3-1 con balón y 4-1-4-1 sin balón.

Las traducciones de rol se aplican solamente si el código existe y el rol es compatible con el puesto. Los códigos incompatibles quedan pendientes; no se sustituyen por roles recomendados. Las instrucciones individuales y colectivas continúan sin descifrar y requieren carga manual. Si hay varias copias del primer equipo, el lector no puede distinguir cuál está activa: se ofrece elegirla explícitamente. Una sola copia se selecciona automáticamente. La vinculación y los códigos recuperados deben cotejarse en FM antes de confirmar el análisis.

El extractor escribe `output/tactics.json` con `schema_version: 2` y conserva el detalle bruto para diagnóstico. Si un bloque no es compatible, se conserva la extracción de jugadores y se permite cargar la táctica manualmente. «Cargar táctica de la partida» actualiza las importaciones anteriores a partir de su copia local `.fm`, en segundo plano y sin depender de la carpeta monitoreada ni de otro guardado en FM. Se conserva el último análisis si la actualización falla.

En «Mi táctica» se eligen los jugadores y las posiciones y roles de ambas fases. El análisis mantiene exactamente ese once. Los roles alternativos y los posibles suplentes se presentan como cambios separados, con la misma fórmula de atributos y familiaridad que se usa en las propuestas. El puntaje del once pondera 80% con balón y 20% sin balón; no es una medición de resultados, de calidad colectiva ni una probabilidad de ganar.

El perfil nativo persistente se guarda en `data/webview/`, excluido de Git. El borrador se conserva por carrera en el almacenamiento local, se reconcilia al cambiar la plantilla y pierde la confirmación al modificar datos o cargar un nuevo guardado. El servidor exige once jugadores distintos del club, un arquero por fase y roles compatibles con cada posición. También rechaza órdenes que contradigan los bloqueos relevados. Los resultados de solicitudes anteriores se descartan si cambia el borrador o la partida.

Una orden sin confirmar se mantiene desconocida. No se sustituye por una instrucción generada ni por «Normal». La revisión informa cuántas instrucciones quedan pendientes y compara solo las órdenes aportadas o los valores bloqueados comprobados. Los menús de arquero están completamente relevados e incorporados al igual que los de jugadores de campo.

## Referencia confirmada de Liverpool

A partir de las 30 capturas de FM26 aportadas por el usuario (22 de jugadores Captura de pantalla 2026-10-24 204016.png a 204125.png y 8 de instrucciones de equipo Captura de pantalla 2026-10-24 211110.png a 211131.png), tanto el once titular, sus roles en ambas fases y sus 165 instrucciones individuales, como la totalidad de las 26 órdenes colectivas del equipo están relevados y cotejados al 100%:

| Jugador | Posición CP / SP | Rol con posesión | Rol sin posesión | Capturas CP / SP |
|---|---|---|---|---|
| Bart Verbruggen | POR / POR (GK) | Portero con salida (PCS) | Portero líbero (POL) | 204123 / 204125 |
| Miloš Kerkez | LTI / LTI (DL) | Carrilero (CR) | Lateral (LAT) | 204059 / 204101 |
| Pau Cubarsí | DFC / DFC (DC) | Central con salida (CCS) | Central (DFC) | 204105 / 204108 |
| Luka Vušković | DFC / DFC (DC) | Central (DFC) | Central (DFC) | 204111 / 204113 |
| Djed Spence | LTD / LTD (DR) | Carrilero (CR) | Lateral (LAT) | 204117 / 204120 |
| Aleksandar Pavlović | MCD / MCD (DM) | Organizador retrasado (ORD) | Mediocentro defensivo (MD) | 204053 / 204055 |
| Yasin Ayari | MC / MCD (MC→DM) | Organizador adelantado (OAD) | Mediocentro defensivo (MD) | 204046 / 204049 |
| Adam Wharton | MC / MP (MC→AMC) | Mediocentro organizador (MOR) | Mediapunta (MP) | 204038 / 204040 |
| Florian Wirtz | EXI / MI (AML→ML) | Extremo invertido (EXI) | Volante abierto (MI) | 204024 / 204026 |
| Hugo Ekitiké | DLC / DLC (STC) | Delantero de apoyo (DLA) | Delantero centro (DLC) | 204016 / 204019 |
| Dominik Szoboszlai | EXD / MD (AMR→MR) | Extremo invertido (EXI) | Volante abierto (MD) | 204030 / 204033 |

### Instrucciones colectivas de equipo confirmadas

Las 8 capturas de equipo (211110.png a 211131.png) relevan las órdenes tácticas colectivas en ambas fases:

#### Con posesión (Capturas 211110, 211113, 211117, 211119)
- **Vista general (211110.png):**
  - Pases directos: Mucho más corto (Much Shorter)
  - Ritmo de juego: Mucho más bajo (Much Lower)
  - Amplitud del ataque: Más estrecho (Narrower)
  - Transición ofensiva: Normal (Standard)
  - Libertad creativa: Equilibrado (Balanced)
  - Perder tiempo: Menos a menudo (Less Often)
  - Jugar buscando el balón parado: Buscar jugadas de balón parado (Play for Set Pieces)
- **Área de creación de oportunidades (211119.png):**
  - Estrategia previa: Jugar superando la presión (Play Through Press)
  - Saques de meta: En corto (Short)
  - Distribución del portero (velocidad): Distribuir con rapidez (Distribute Quickly)
  - Distribución del portero: Equilibrado (Balanced)
- **Avance (211117.png):**
  - Carreras de apoyo: Equilibrado (Overlap - Balanced / Underlap - Balanced)
  - Regate: Animar (Encourage)
  - Avance: Izquierda (Left)
  - Recepción de pase: Pase al pie (Pass to Feet)
- **Último tercio (211113.png):**
  - Regate: Animar (Encourage)
  - Paciencia: Intentar llevar el balón hasta el área (Work Ball Into Box)
  - Disparos lejanos: Alentar (Encourage)
  - Estilo de centros: Centros rasos (Low Crosses)

#### Sin posesión (Capturas 211123, 211126, 211129, 211131)
- **Vista general (211123.png):**
  - Línea de presión: Presión adelantada (High Press)
  - Línea defensiva: Más adelantada (Higher / Alto)
  - Comportamiento de la línea defensiva: Presionar más arriba (Step Up More)
  - Activar presión: Más insistente (More Often)
  - Transición defensiva: Contrapresión (Counter-Press)
  - Realizando una entrada: Ser agresivos (Get Stuck In / Tackle Harder)
- **Presión adelantada (211126.png):**
  - Trampa de presión: Equilibrado (Balanced)
  - Distribución del portero en corto: Sí (Yes - Impedir saques cortos rivales)
- **Bloque medio (211129.png):**
  - Trampa de presión: Equilibrado (Balanced)
- **Bloque bajo (211131.png):**
  - Compromiso de centros: Evitar centros (Stop Crosses)


Las observaciones tácticas analizan hipótesis de coordinación colectiva basadas en las órdenes asignadas:
1. **Zaga central (Vušković y Cubarsí):** ambos tienen presión alta, marca de cerca y entradas fuertes. Con entradas 17 y 16 sobre 20 son muy seguros en el duelo directo, pero si ambos salen a encimar a la vez pueden dejar la espalda desprotegida; probar la presión en Normal en uno de ellos mantiene la cobertura.
2. **Tres organizadores en el medio (Pavlović, Ayari y Wharton):** Pavlović inicia en el pivote, Ayari conecta con libertad y Wharton actúa como mediocentro organizador. Al tener tres futbolistas que prefieren el balón al pie, la profundidad del equipo descansa en las rupturas al espacio de Szoboszlai (quien tiene la orden expresa de más desmarques hacia adelante) y los apoyos de Ekitiké.
3. **Bandas y amplitud:** Wirtz se cierra hacia adentro y Kerkez ataca la banda con desmarques y pases cortos. En la derecha, Szoboszlai encara y rompe al espacio mientras Spence acompaña con pases de apoyo.
4. **Entradas de Ekitiké:** con entradas 7/20 y agresividad 12/20 en «entrar más fuerte», se recomienda evaluar la orden en Normal para evitar faltas evitables y tarjetas tempranas, conservando por separado su presión alta.
5. **Arco:** Verbruggen actúa como Portero con salida (PCS) asumiendo riesgos en la distribución, y como Portero líbero (POL) sin balón para barrer balones largos a espaldas de la defensa adelantada.

## Menú de instrucciones

Se muestran las once propiedades con posesión (amplitud, dirección y frecuencia del regate, carreras hacia adelante, libertad de movimientos, aguantar el balón, disparos, riesgo en pases, longitud de entrega, origen y estrategia de centros) y las cuatro propiedades sin posesión (presión, marca, entradas y objetivo de marca).

Los 79 roles tienen un panel observado. Cada candado o control editable se considera comprobado únicamente cuando el puesto, costado y ámbito coinciden con esa evidencia; también se contrasta la cantidad de jugadores del mismo puesto si está documentada (por ejemplo, el costado derecho de tres centrales o de un doble pivote). Los contextos distintos mantienen disponibilidad no verificada y no reciben candados ni valores automáticos por extrapolación. Los valores que confirme el usuario se conservan, aunque su disponibilidad no esté verificada.

## Modelo del mapa

Cada fase divide el terreno en 25 zonas y conserva la identidad del jugador entre fases. Las posiciones fijan las anclas iniciales. El modelo aproxima desplazamientos de los roles y de las instrucciones de amplitud, conducción y desmarques confirmadas. Cuando falta una orden, puede utilizar el comportamiento típico del rol; esa suposición se declara en la vista.

Para la fase defensiva, una línea más alta o más baja mueve el ancla de los defensores cinco unidades por nivel; un bloque alto/bajo mueve la de los restantes jugadores seis unidades. Estos ajustes se aplican si la instrucción está presente; no se infieren de códigos brutos ni de la mentalidad.

El índice de apoyo de un jugador en una celda es:

`media de tres atributos × 5 × (0,25 + 0,75 × familiaridad/20) × exp(−0,5 × (distancia/24)²)`

Con balón se usan desmarques, decisiones y anticipación. Sin balón se usan colocación, anticipación y sacrificio. Se muestran los tres mayores apoyos de cada zona; el color depende del mayor índice: verde ≥50, amarillo ≥25, rojo <25. El arquero se excluye de los apoyos de campo. Las distancias usan el sistema porcentual de la cancha; son parámetros del modelo, no metros medidos.

Es una estimación estática propia. No reproduce estrellas ni el motor de FM; tampoco incorpora rival, balón, mentalidad, rasgos, fatiga o movimientos de un partido. La suma de los índices no expresa probabilidad de ocupación. El modelo no convierte órdenes de tiro o entradas en desplazamientos ficticios.

## Inicio de escritorio

Una segunda ejecución solicita `/api/activate` a la instancia existente para restaurar y mostrar su ventana. Un mutex por puerto evita que dos lanzadores simultáneos creen dos instancias. La petición utiliza las mismas restricciones de origen local y cabecera de aplicación que el resto de escrituras. El navegador se abre únicamente cuando se solicita `--browser-only`; un error de WebView termina con diagnóstico, sin lanzar otra interfaz automáticamente.

## Verificación

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
node --test tests/frontend.test.mjs
node tests/browser.test.mjs
```

## Referencias

- [Modelo de tácticas de fmsave](https://rhiever.github.io/fmsave/reference/save.html) y código instalado de `fmsave.models.tactics` 0.5.11: capacidades y campos sin identificar.
- [Evolución táctica oficial de FM26](https://www.footballmanager.com/fm26/features/possession-out-possession-fm26s-new-tactical-evolution): separación de fases y visualizador del juego. El modelo de Touchline es independiente.
- Las 22 capturas `docs/screenshots/Captura de pantalla 2026-10-24 204016.png` a `204125.png` aportadas por el usuario.
