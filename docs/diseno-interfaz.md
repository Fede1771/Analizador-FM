# Criterios visuales de Touchline

La referencia del video de Donweb Cloud aporta el método: definir criterios antes de construir, usar componentes como referencia y revisar capturas. No se instala Claude Code ni un catálogo de componentes para ejecutar Touchline. La interfaz mantiene HTML, CSS y módulos JavaScript locales, sin fuentes, telemetría o recursos gráficos externos añadidos.

## Identidad

- Base oscura: `--bg`, `--panel` y `--raised` del CSS existente; bordes `--line` para relaciones y separación.
- Menta `--accent` para acción y selección. Ámbar para datos pendientes. Rojo `--lab-negative` para diferencias negativas. Siempre se acompaña el color con signo, texto o número.
- Tipografía del sistema, escala clara de títulos y cifras tabulares. Etiquetas legibles y foco de teclado visible.
- La cancha identifica las pantallas tácticas; las comparaciones de jugadores usan columnas equivalentes y el historial una línea temporal. No repetir tarjetas de estadísticas como estructura de todas las pantallas.

## Reglas de los nuevos gráficos

Los ejes muestran la escala 1–20 y su composición. El historial muestra fechas de juego y el mismo contexto de rol. Las métricas indican denominadores y datos ausentes. Un estado vacío explica qué dato falta y cómo obtenerlo. No se usan animaciones que distraigan de las decisiones.

Las referencias de [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) y [21st](https://github.com/21st-dev/magic-mcp) sirven como orientación de proceso. No se copian sus componentes ni se agrega React/Tailwind: el diseño se adapta al código existente.
