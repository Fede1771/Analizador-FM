# Touchline · Analizador FM26

> **Finalidad de la aplicación:**
> *"Le pasás tu partida de Football Manager 26 y, mientras vas jugando y guardando con el software abierto, va leyendo automáticamente tu archivo de guardado en vivo. En base a los jugadores que tenés (titulares, suplentes, jóvenes prospectos e inferiores, y cedidos), te recomienda el mejor jugador para cada puesto en las mejores formaciones tanto con posesión como sin posesión. Y si le escribís con tus propias palabras pidiéndole jugar de otra forma, adapta todo el análisis, los roles y las 26 instrucciones de equipo al instante."*

---

Aplicación de escritorio local e instalable para Football Manager 26. Procesa todo en tu equipo, sin enviar tus datos a servidores externos y sin consolas abiertas.

---

## 🚀 Inicio rápido (Aplicación de escritorio instalable)

### 1. Crear el acceso directo en tu Escritorio
Hacé doble clic en:
**`Instalar_Analizador_FM.bat`**

Esto crea un acceso directo en tu Escritorio de Windows llamado:
**`Touchline - Analizador FM26`** con su propio ícono táctico.

### 2. Iniciar la aplicación
- Hacé **doble clic en el acceso directo de tu Escritorio** (o en `Touchline.bat` dentro de la carpeta).
- La aplicación arranca de inmediato en una **ventana nativa de escritorio**.
- **Sin consolas negras de fondo**: Se ejecuta limpiamente con `pythonw.exe`.
- **Apagado automático al cerrar**: En el instante en que cerrás la ventana, la aplicación, el servidor local y el monitor de partidas se detienen y cierran por completo. No queda ningún proceso en segundo plano.

---

## ⚡ Sincronización automática en vivo con FM26 (Auto-Sync)

La aplicación monitorea de forma nativa tu carpeta de guardados de FM26:
`C:\Users\feder\Documents\Sports Interactive\Football Manager 26\games`

- **Mientras jugás a FM26 y guardás** (manual o autoguardado rotativo), la aplicación detecta el guardado finalizado, extrae tu plantilla y actualiza todos los informes, alineaciones y tácticas en tiempo real.
- **Detección segura**: Espera a que FM26 complete la escritura del archivo para evitar bloqueos o lecturas corruptas.
- **Configuración en pantalla**: Desde el botón de la barra superior (**🟢 FM26: En vivo**) podés:
  - Ver el archivo monitoreado y la fecha del último guardado.
  - Elegir el **Modo Automático** (detecta siempre la última partida guardada) o fijar una partida específica (ej. `Liverpool.fm`).
  - Cambiar la ruta si tenés tus partidas en otra carpeta o disco.
  - Forzar una sincronización manual con el botón **⚡ Sincronizar ahora**.

---

## 🧠 Laboratorio Táctico Inteligente (FM26 Oficial)

- **Planteo en lenguaje natural**: Escribí cómo querés que juegue tu equipo (ej.: *"Quiero jugar con mucha posesión e intentar tener muchas chances de gol y evitar que me rematen mucho al arco"*). El motor interpreta tu idea, asigna el estilo FM26 oficial y optimiza las instrucciones.
- **Top 3 de mejores formaciones**: Comparación con y sin posesión (`4-3-3`, `4-2-3-1`, `4-4-2`, etc.), con puntuación de encaje sobre 100 y alineación titular óptima.
- **Banco de suplentes y mejores recambios**: Debajo de la cancha táctica, indica para cada suplente a qué titular reemplaza con mejor nivel táctico y la diferencia de encaje.
- **Roles actuales vs. recomendados**: Comparación de la función natural del jugador y la función táctica recomendada.
- **Instrucciones completas de equipo**: 26 instrucciones oficiales divididas en Con posesión (Creación de oportunidades, Avance, Último tercio) y Sin posesión (Líneas y bloque, Presión y recuperación, Trampas y centros).
- **Estilos y Mentalidades oficiales FM26**: Escala oficial de 7 mentalidades (*Muy defensiva*, *Defensivo*, *Cauta*, *Equilibrada*, *Positiva*, *Ofensivo*, *Muy ofensiva*) y 10 estilos tácticos.

---

## 🛠️ Ejecución y Pruebas

- **`Touchline.bat`**: Inicia la aplicación de escritorio directamente.
- **`Instalar_Analizador_FM.bat`**: Crea el acceso directo en el Escritorio.

### Validación y pruebas
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --check web\app.js
```
