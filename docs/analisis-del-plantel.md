# Análisis del plantel

Disponible en Touchline 1.1.0. Inspirado en las funciones públicas de [FMApp de FMSite](https://www.fmsite.net/app/#/); las fórmulas y el código son propios de Touchline.

## Evolución

Elegí un jugador, un rol, un puesto y un estilo. Las observaciones históricas se recalculan con ese mismo criterio; un cambio de estilo entre sesiones no se presenta como una mejora del futbolista. Las diferencias de atributos son valores observados, no una estimación de potencial. El encaje también depende de la familiaridad.

Los registros viven en `data/imports/history/<identificador de carrera>/`. En la aplicación instalada, `data/` corresponde a `%LOCALAPPDATA%\Touchline\data`. Se escriben de forma atómica y no entran en la retención de partidas. Se recuperan las extracciones previas que aún existan, sin abrir ni modificar el `.fm` original. Las observaciones del mismo día pueden ser distintas; las repetidas se deduplican por contenido. Si abrís un guardado anterior, el gráfico no utiliza datos con fechas de juego futuras.

La identidad de carrera conserva la regla existente de club y manager. Para tablas externas, por defecto se crea una carrera separada. Vincularla con la actual requiere confirmación explícita, el mismo club y manager y los IDs únicos de FM. No uses esa vinculación para una partida diferente aunque tenga los mismos nombres.

## Comparar

Los jugadores del plantel y los cedidos se comparan para el mismo rol, posición y estilo. Se destacan los atributos prioritarios comprobados del catálogo. El signo expresa izquierda menos derecha; un atributo prioritario no representa una ponderación del motor de partidos. Los salarios desconocidos permanecen en «—».

Si una tabla no incluye la familiaridad del puesto elegido, el encaje y la familiaridad permanecen en «—», sin tratarlos como valores observados. Esas observaciones tampoco se dibujan como puntos de encaje en la línea temporal; las diferencias de atributos continúan disponibles.

## Profundidad

Se respeta el grupo elegido y las exclusiones de disponibilidad. Los arqueros se incluyen en cobertura, pero se excluyen del perfil de campo. Se calculan medias sin ponderar de seis conjuntos: velocidad (velocidad y aceleración), físico (fuerza, resistencia, equilibrio y agilidad), defensa (entradas, marcaje, colocación y anticipación), creación (pases, visión y decisiones), técnica (técnica, primer toque y regate) y gol (remate, desmarques y serenidad).

El núcleo son los primeros 16 jugadores de campo según la media de los seis ejes; la rotación es el resto. No representa el once táctico, personalidad psicológica, capacidad oculta ni potencial. La cobertura exige familiaridad mínima de 15/20 y ordena alternativas por encaje para el puesto y estilo. Un mismo jugador puede contar para varios puestos: no son alineaciones simultáneas.

## Minutos y aportes

Se leen las estadísticas de temporada para el club. El lector usa una fila `OVERALL` inequívoca por jugador; si hay varias del mismo club (por ejemplo, equipos de reserva), no las suma. Los datos antiguos necesitan una nueva importación `.fm` para incorporar estos campos.

Los porcentajes requieren datos de todos los jugadores disponibles del grupo, un ámbito y período común y valores de minutos, goles y asistencias conocidos. No se mezclan liga y todas las competiciones. Una fila ausente no equivale a cero. Los denominadores nulos muestran «—».

- Minutos del Top 11: suma de minutos de los once más utilizados / suma del grupo.
- Top 3 y Top 5: suma de goles + asistencias de los mayores aportantes / suma de goles + asistencias del grupo.
- Máximo goleador: goles del mayor goleador / goles de los jugadores del grupo. No incluye automáticamente autogoles ni jugadores que ya salieron del club.
- Edades: minutos de cada rango / minutos del grupo; se omiten los porcentajes si falta alguna edad.
- G+A/90: (goles + asistencias) × 90 / minutos, solo con valores conocidos y minutos positivos.

Estos datos describen participación y concentración, sin atribuir causas ni demostrar la eficacia de una táctica.

## Importar CSV, TSV o HTML

Desde la bienvenida o **Análisis del plantel → Importar tabla**, descargá la plantilla, exportá los datos visibles de FM y cotejá los encabezados. No se instala un exportador ni se accede a una cuenta de FMSite. No se garantiza cualquier vista o abreviatura de terceros: se muestran las columnas que faltan o se ignoran.

Obligatorios: ID único (`uid`, `ID único`, `Unique ID`), nombre, los 47 atributos con nombres completos en español o claves inglesas y familiaridades. Podés usar:

- `positions`: JSON, por ejemplo `{"mc":20,"dm":15}`.
- Columnas numéricas `pos_gk`, `pos_dc`, `pos_mc`, etc., con valores 1–20.
- `Posiciones naturales` con códigos `GK DL DC DR DM ML MC MR AML AMC AMR STC WBL WBR`, solo si confirmás explícitamente que son naturales (20/20). Una columna genérica `Posición` no demuestra familiaridad.

Opcionales: edad, valor numérico, `wage_weekly` o `Salario semanal`, fin de contrato (AAAA-MM-DD), minutos, goles, asistencias, apariciones y media. Los salarios son semanales en euros; no se interpretan cantidades abreviadas ni unidades anuales. Para estadísticas, indicá el ámbito y la temporada del archivo. Se aceptan UTF-8, UTF-16 y Windows-1252, con límite de 6 MB y 2000 jugadores.

La vista previa no cambia la partida activa. La confirmación crea una importación normalizada, activa el plantel y conserva el análisis anterior si falla. No se fusionan filas con datos de otra importación. Una tabla no aporta táctica, roles activos, instrucciones, rivales ni reglas nuevas de disponibilidad de FM26. Las preferencias de una carrera vinculada se conservan; sin vinculación se usa una carrera de tablas separada.

La vista previa avisa cuántos jugadores tienen familiaridades incompletas. En el motor existente de Propuestas, los puestos sin familiaridad aportada reciben su penalización mínima; no es una observación de FM. Para evitar esa limitación, completá todas las columnas pos_* con los valores del juego. En Comparar y Evolución, esos encajes permanecen desconocidos.

La fila de la plantilla es un **ejemplo ficticio**: reemplazala con tus jugadores y datos antes de confirmar.
