# Touchline · Analizador FM26

Aplicación local para leer una partida de Football Manager 26, analizar primer equipo, otros grupos y cedidos, y comparar diez estructuras con y sin posesión. Los índices y recomendaciones son propios de Touchline y deben probarse en FM.

## Instalación en Windows

1. Instalá Python 3.12 o superior.
2. Ejecutá `Instalar_Analizador_FM.bat`. El instalador crea `.venv` si hace falta, instala las versiones de `requirements-lock-windows.txt`, realiza un diagnóstico y crea el acceso directo.
3. Abrí el acceso directo **Touchline - Analizador FM26** o `Touchline.bat`.

La ventana nativa usa pywebview y el runtime WebView2 de Microsoft Edge. Si no puede abrirse, se usa el navegador. En ese modo, elegí **Cerrar Touchline** para detener también el servidor. Los errores de inicio se guardan en `data/logs/touchline.log` y se muestran en una ventana de diagnóstico.

## Uso

- Importá un archivo `.fm` de hasta 400 MB. Se conserva la partida original y se publica el nuevo análisis cuando termina correctamente.
- Confirmá en **Grupos** cuál es el primer equipo y nombrá reservas y juveniles.
- En **Tácticas**, compará las tres propuestas de mayor encaje entre diez esquemas o elegí uno específico. La misma lógica construye el once, el banco y la evaluación de refuerzos.
- Podés describir una idea de juego. Se usan reglas explícitas con negaciones y prioridades, y se muestra la interpretación. Corregila con el estilo, la formación y los ajustes de equipo.
- El puntaje del once combina 80 % función con posesión y 20 % función sin posesión. La cancha muestra el puntaje individual de la fase seleccionada.
- Las estadísticas ausentes de cedidos se muestran como “—”, no como cero. Las propuestas de regreso requieren confirmar cláusulas, fechas, costos e inscripción en FM.
- Las preferencias se conservan por club e identificador del manager; los autoguardados y las copias de la misma carrera comparten configuración. Los resultados se invalidan al cambiar datos o parámetros.

## Sincronización y almacenamiento

El monitor se configura en pantalla. Por defecto busca `Documents/Sports Interactive/Football Manager 26/games` del usuario actual. Podés seguir el último archivo o fijar una partida.

El monitor espera estabilidad antes de copiar. Una actualización se registra como exitosa al terminar la extracción y el análisis. Los errores conservan el informe anterior y permiten reintentar; los fallos automáticos tienen una espera antes del siguiente intento. Podés consultar el último informe durante la importación.

Después de cada importación exitosa se aplica una retención configurable: por defecto cinco copias y 2048 MB. La copia activa se conserva incluso si supera el límite. Solo se limpian carpetas de importación administradas por Touchline; las partidas originales quedan fuera de esa limpieza. Cambiar los límites no ejecuta una limpieza inmediata.

## Desarrollo y verificación

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
node --test tests/frontend.test.mjs
node tests/browser.test.mjs
.\.venv\Scripts\python.exe -B scripts/diagnostico.py
```

La prueba de navegador requiere Chrome, Edge o Chromium; podés indicar su ejecutable con `CHROME_BIN` y Python con `PYTHON_BIN`. Guarda capturas en `.tmp/browser-*` o en la carpeta indicada por `TOUCHLINE_TEST_ARTIFACTS`.

Las pruebas usan clubes sintéticos, puertos dinámicos y directorios temporales. No necesitan partidas personales ni modifican la configuración de sincronización real.

Inicio manual:

```powershell
.\.venv\Scripts\python.exe -B app_desktop.py
.\.venv\Scripts\python.exe -B app_desktop.py --browser-only
.\.venv\Scripts\python.exe -B -m fm_app.server --no-sync --port 8765
```

El servidor escucha únicamente en `127.0.0.1` y comprueba host, origen y cabecera de aplicación para las operaciones de escritura. El cierre cancela la extracción activa, finaliza los trabajos y detiene el monitor y el servidor.

## Alcance

El lector realiza controles de estructura y rangos; eso no certifica la coincidencia de cada dato con la ficha de FM. Se usan atributos visibles para recomendar, sin capacidad actual/potencial ni personalidad oculta. La selección no verifica lesiones, sanciones, inscripción, rival ni carga de partidos. Los grupos distintos del principal pueden incluir reservas adultos. No se exportan tácticas `.fmf`.

La exportación general es JSON y el plan individual es texto. La arquitectura y los contratos se describen en [docs/arquitectura.md](docs/arquitectura.md).
