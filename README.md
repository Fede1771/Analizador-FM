# Touchline · Analizador FM26

Aplicación local para analizar partidas de Football Manager 2026, revisar el plantel y comparar propuestas tácticas con y sin posesión. Los puntajes y recomendaciones son cálculos propios de Touchline y deben contrastarse en FM.

![Vista de Mi táctica con datos de prueba](docs/capturas-finales/02-mi-tactica-desktop.png)

*Captura generada con datos de prueba. [Ver las demás pantallas](docs/capturas-finales/README.md).*

## Empezar en Windows

1. Instalá Python 3.12 o posterior y ejecutá `Instalar_Analizador_FM.bat`. El instalador crea `.venv/`, instala las versiones de `requirements-lock-windows.txt`, comprueba los componentes y crea un acceso directo.
2. Abrí **Touchline - Analizador FM26** desde el acceso directo o ejecutá `Touchline.bat`.
3. Importá una partida `.fm` de hasta 400 MB o configurá el monitor dentro de Touchline. El archivo original no se modifica.
4. Revisá los grupos detectados y confirmá cuál es el primer equipo antes de comparar jugadores y propuestas.

La ventana usa pywebview y Microsoft Edge WebView2. Para abrir Touchline en el navegador, ejecutá `app_desktop.py --browser-only` con el Python de `.venv/` (comando completo más abajo). Ese modo se elige explícitamente: si falla la ventana nativa, la aplicación muestra un diagnóstico en vez de abrir el navegador. Los errores se guardan en `data/logs/touchline.log`.

## Qué podés hacer

- **Mi táctica:** armá o revisá tu once y los roles de ambas fases, confirmá instrucciones individuales y colectivas, y observá un mapa estimado de cobertura por zonas. El lector recupera algunos datos tácticos de la partida, pero **no identifica automáticamente el once activo ni descifra todos sus roles e instrucciones**. Confirmalos en FM antes de tomar el análisis como referencia.
- **Propuestas:** compará diez estructuras, consultá las tres de mayor encaje o elegí una. Touchline construye once y banco con la misma lógica de evaluación, y permite ajustar estilo e instrucciones de equipo.
- **Idea de juego:** describí lo que buscás y revisá cómo se interpretó el texto. Podés corregir el resultado con controles explícitos.
- **Plantilla y cedidos:** examiná grupos, posibles excedentes, refuerzos y retornos. Las estadísticas ausentes se muestran como «—»; las condiciones de préstamos e inscripción se confirman en FM.

El puntaje del once pondera **80 % con posesión y 20 % sin posesión**. La cancha muestra el puntaje de la fase seleccionada. Estos números sirven para comparar opciones dentro de Touchline; no predicen resultados de partidos.

## Partidas y preferencias

El monitor se configura en pantalla. Por defecto busca `Documents/Sports Interactive/Football Manager 26/games` del usuario actual. Podés seguir la partida más reciente o fijar un archivo.

El monitor espera a que el guardado sea estable antes de copiarlo. Una actualización se registra como exitosa al terminar la extracción y el análisis. Si falla, se conserva el informe anterior y se puede reintentar.

Después de cada importación exitosa se aplica una retención configurable a las **copias administradas por Touchline**: por defecto cinco copias y 2048 MB. Siempre se conserva la copia activa. Esa limpieza no alcanza los archivos `.fm` originales. Las preferencias se guardan por carrera; los autoguardados y copias de una misma carrera comparten configuración.

## Documentación y estructura

| Ruta | Para qué sirve |
|---|---|
| `data/` | Partidas importadas, preferencias, configuración y perfil local; excluidos de Git |
| `fm_app/`, `web/` | Código de Touchline y su interfaz |
| `docs/` | [Índice de documentación](docs/README.md), relevamiento de FM26, ZIP e informes |
| `docs/capturas-finales/` | Capturas de referencia de la interfaz |
| `docs/verificaciones/` | Evidencias conservadas de las revisiones y pruebas |
| `scripts/` | [Instalación, diagnóstico y generación de informes](scripts/README.md) |
| `tools/` | [Herramientas auxiliares vigentes](tools/README.md); scripts antiguos en `tools/historicos/` |
| `tests/` | Pruebas automáticas |
| `.venv/` | Entorno Python instalado, necesario para el acceso directo; excluido de Git |

**Conservá `data/` y `.venv/`** si querés mantener tus datos y el acceso directo funcionando. Las carpetas `.tmp/` y `__pycache__/` son regenerables y pueden reaparecer durante las pruebas o la ejecución.

El [informe integral de FM26](docs/relevamiento-fm26-2026-10-25/INFORME-INTEGRAL.md) documenta los 79 paneles de roles observados, atributos, instrucciones, evidencias y límites. La [revisión de la integración](docs/REVISION-TOUCHLINE-2026-10-26.md) registra las correcciones y pruebas de Touchline.

## Desarrollo y comprobaciones

Desde la carpeta del proyecto, con la instalación ya hecha:

```powershell
.\.venv\Scripts\python.exe -B scripts/diagnostico.py
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
node --test tests/frontend.test.mjs
node tests/browser.test.mjs
```

Las pruebas de navegador requieren Node.js y Chrome, Edge o Chromium. Podés indicar el navegador con `CHROME_BIN` y el intérprete con `PYTHON_BIN`. Los artefactos temporales se guardan en `.tmp/browser-*` o en `TOUCHLINE_TEST_ARTIFACTS`.

Las pruebas generan datos sintéticos y, cuando corresponde, usan **copias aisladas** de datos importados. No deben editar las partidas ni las preferencias originales.

Inicio manual:

```powershell
.\.venv\Scripts\python.exe -B app_desktop.py
.\.venv\Scripts\python.exe -B app_desktop.py --browser-only
.\.venv\Scripts\python.exe -B -m fm_app.server --no-sync --port 8765
```

El servidor escucha en `127.0.0.1`. En modo navegador, usá **Cerrar Touchline** para detener también el servidor.

## Alcance del análisis

Touchline trabaja con los datos accesibles de la partida y con los atributos visibles. No lee capacidad o potencial ocultos, ni verifica por sí solo lesiones, sanciones, inscripción, rival o carga de partidos. El lector valida estructura y rangos, pero eso no certifica que cada valor coincida con la ficha de FM. La disponibilidad de ciertas instrucciones fuera del puesto, costado o ámbito observado sigue **sin verificar**; esas reglas no se inventan.

La exportación general es JSON y el plan individual es texto; no se exportan tácticas `.fmf`. Para detalles de lectura, confirmación manual y mapa de zonas, consultá [Táctica actual y zonas](docs/tactica-actual-y-zonas.md). La [arquitectura](docs/arquitectura.md) describe los contratos y componentes.
