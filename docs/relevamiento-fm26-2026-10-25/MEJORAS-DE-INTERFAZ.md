# Touchline: análisis estético, redundancias y propuesta de mejora

## Base y límites de la revisión

Se revisaron `web/index.html`, `web/views.js`, `web/current-view.js`, `web/tactics-view.js`, `web/zones-view.js`, `web/style.css` y el flujo de renderizado de `web/app.js`. Se inspeccionaron capturas existentes de escritorio, Mi táctica y ventana angosta, copiadas en `referencias-interfaz/`.

Las capturas proceden de pruebas con datos sintéticos y pueden ser anteriores a cambios del código. Permiten valorar distribución y densidad, pero no certificar el estado actual de todos los flujos. La ventana nativa se cerró antes del recorrido interactivo. La IA implementadora debe contrastar cada hallazgo con el código vigente y verificar visualmente el resultado.

## Evaluación general

La identidad oscura con acento verde menta funciona como base. Los nombres de jugadores, puntajes y navegación tienen estilos reconocibles. Conviene conservar esa identidad y mejorar la organización de la información.

El problema dominante es la competencia por atención: encabezados, barras de acciones, botones rápidos, avisos, etiquetas, checklist y tarjetas tienen mucho peso antes de llegar a la cancha. En la captura de Propuestas a 1360 × 1000, la cancha empieza cerca del borde inferior. En la ventana de 760 px, el resumen de propuesta llega después de varias barras y controles. Esto retrasa la respuesta a «¿qué equipo propongo y qué debo cambiar?».

## Prioridad 1: mensajes vinculados al análisis real

### Checklist fijo de tres jugadores

En `web/current-view.js`, `renderGroupedAdvice` construye un checklist fijo de Ekitiké, Vušković y Wharton, aunque las recomendaciones agrupadas de abajo usan `result.advice`. El bloque alternativo `captureReview` también conserva recomendaciones históricas de esos jugadores.

La captura de prueba de Mi táctica muestra nombres de prueba en las recomendaciones dinámicas y jugadores de Liverpool en el checklist. Es una inconsistencia concreta, además de una repetición visual.

**Propuesta:** construir checklist, tarjetas, copia y HUD a partir del mismo conjunto de recomendaciones vigente. Cada recomendación necesita identidad estable, jugador o ámbito de equipo, fase, acción, motivo y procedencia. Invalidar las marcas de aplicación cuando cambie la carrera, táctica o recomendación correspondiente. El estado debe decir «Marcado como aplicado por vos» si no se verificó contra FM.

### Mensajes que atribuyen más certeza de la disponible

- «¡Táctica 100% optimizada para este partido!» aparece al completar tres casillas. Cambiar por «3 ajustes marcados como aplicados», con el número real.
- «Próximo Partido» en `overview` muestra nombre y encaje de la primera propuesta, y tres ajustes fijos; no se alimenta de un encuentro en ese bloque. Renombrar a «Resumen táctico» o incorporar datos reales antes de presentarlo como análisis de partido.
- Las órdenes «100% confirmadas» deben distinguir confirmación manual de lectura automática. Mostrar fuente y fecha donde ayuden a decidir.
- El puntaje debe etiquetarse como «Encaje del once» o «Encaje de esta fase». Conservar la metodología en un enlace o ayuda contextual.

### Coherencia del HUD

Revisar antes de cambiar la presentación: `companionView` consulta `currentResult.tactical_advice`, mientras la vista de recomendaciones usa `result.advice`. Además, los metadatos de la cabecera del HUD toman la propuesta seleccionada. Esto requiere comprobar el contrato vigente y el comportamiento completo; no se verificó interactivamente.

**Criterio:** cuando el HUD se abre desde Mi táctica, su título, estilo, contexto y acciones corresponden a esa revisión. Desde Propuestas, corresponden a la propuesta elegida. Si falta un análisis, mostrarlo explícitamente.

## Prioridad 2: reducir duplicaciones

| Hallazgo | Propuesta |
|---|---|
| Mini-HUD en barra global, encabezado y checklist | Un acceso persistente por pantalla; mantener la ventana auxiliar porque sirve en otro contexto de uso |
| «Salir» y «Cerrar Touchline» | Un único acceso de cierre en el menú de aplicación |
| Botones rápidos de formación y desplegable de formación | Un selector completo; puede incluir favoritos y búsqueda, sin otra entrada paralela |
| Campo rápido de idea y textarea avanzado | Una sola entrada y una interpretación aplicada visible; parámetros concretos en ajustes secundarios |
| Ajuste repetido en checklist, tarjeta, chips y párrafo | Una tarjeta o fila por recomendación, con acción visible y motivo desplegable |
| Cifras de cedidos, otros grupos y encaje repetidas en el inicio | Una tarjeta por tema con cantidad, situación y siguiente acción |
| «Propuestas» en el menú y «Tácticas» como título | Usar «Propuestas» en ambos lugares |
| «Companion», «Mini-HUD» y «Mini-HUD Flotante» | Nombre único sugerido: «Guía para FM»; describir que abre una ventana auxiliar |

La repetición entre una vista principal y una herramienta auxiliar puede ser útil. La mejora consiste en compartir datos y evitar repetir controles y explicaciones dentro de una misma pantalla.

## Prioridad 3: estructura propuesta

### Centro del club

Encabezado compacto con club, fecha de partida, última actualización y estado de sincronización. A continuación, hasta tres prioridades reales con acceso al lugar donde se resuelven. Debajo, tarjetas compactas de contratos, plantel, inferiores, cedidos y ojeo cuando existan datos.

La comparación completa de tres formaciones puede quedar en Propuestas, con un resumen y enlace desde el inicio. «Importar partida» conserva acceso, pero una vez cargada la carrera pasa a acción secundaria; no debería competir siempre con el siguiente paso táctico.

### Mi táctica

1. Encabezado: nombre, encaje general y estado resumido de confirmación.
2. Área principal: cancha con selector CP/SP y columna con hasta tres ajustes prioritarios. En una ventana angosta, apilar cancha y prioridades en el mismo orden de lectura.
3. Vistas secundarias: «Jugadores», «Instrucciones» y «Zonas». Mostrar el resto de recomendaciones bajo «Ver todas».
4. Seleccionar un jugador en la cancha o lista abre su panel de detalle: rol CP/SP, órdenes, atributos relevantes, alternativas y motivo de la recomendación.
5. Mantener un editor completo disponible para configurar el once, con resumen por fila; evitar desplegar once formularios extensos como superficie principal.

Conservar los estados de edición y las órdenes no confirmadas al cambiar de fase, pestaña o jugador. Las pestañas no deben perder información que ya funciona.

### Propuestas

Un bloque compacto para idea de juego, estilo y formación. Debajo, resultado seleccionado con cancha, encaje y cambios respecto de Mi táctica, cuando se pueda comparar. La comparación de las tres mejores puede abrirse bajo demanda.

Distinguir el encaje total, el individual por fase y la diferencia frente a otra propuesta. Acompañar cada cifra con su significado; evitar múltiples puntajes grandes sin un contexto claro.

### Plantilla, contratos, ojeo y cedidos

Usar filtros y tablas consistentes. Mantener visibles las columnas útiles para la decisión de esa pantalla, con detalles adicionales al abrir un jugador. Permitir elegir columnas cuando la tabla sea extensa. Diferenciar sin datos, cero y no aplicable. Estas son propuestas a verificar en las pantallas finales; no se completó su auditoría visual individual.

## Prioridad 4: sistema visual

- **Color:** verde menta para selección/acción; rojo para problemas graves y amarillo para atención. CP/SP deben ser etiquetas neutras y explícitas: rojo para toda la fase sin posesión confunde fase con gravedad.
- **Iconografía:** sustituir el uso generalizado de emojis por un conjunto coherente de iconos. Mantener texto en las acciones principales y nombres accesibles.
- **Jerarquía:** una acción principal por contexto; acciones de exportación, cierre y configuración con menor prominencia. Reducir paneles anidados, bordes y etiquetas repetitivas.
- **Tipografía:** limitar tamaños y pesos; números alineados y tabulares. Mantener las explicaciones legibles sin reducir globalmente la letra para ganar espacio.
- **Espaciado:** compactar encabezados, controles y checklist; conservar aire entre bloques con propósitos distintos.
- **Ventanas angostas:** sustituir varias filas de acciones y navegación horizontal extensa por menú compacto y acciones secundarias agrupadas. A 760 px debe poder verse el resumen del resultado sin atravesar dos barras de herramientas completas.
- **Accesibilidad:** foco visible, navegación por teclado, etiquetas de formulario, contraste comprobado y estados expresados también con texto/iconos. El cambio de pestañas y paneles debe anunciar el contexto y conservar el foco de forma previsible.
- **Ayuda:** pasar el bloque permanente «¿Dónde dar a Continuar?» a ayuda contextual o primera utilización. Conservar «Cómo se calcula» como referencia central y mostrar límites específicos cuando afecten una decisión.

## Criterios de aceptación

1. La revisión usa el mismo conjunto vigente de recomendaciones para lista, checklist, HUD y copia; sin nombres ni cantidades fijas ajenas al análisis.
2. Marcar casillas no promete optimización ni una validación automática en FM.
3. Existe un solo punto principal para formación y uno para idea de juego; editar cualquiera mantiene el resultado coherente.
4. El acceso al HUD y al cierre no se repite dentro de una misma pantalla sin una razón de uso clara.
5. A 1360 × 920 el área de cancha comienza dentro de la primera pantalla, sin exigir recorrer formularios largos; verificar con una revisión completa y con avisos activos.
6. A 760 px las barras se compactan; a 720 px se respeta el tamaño mínimo actual de la ventana. No hay desplazamiento horizontal global. Las tablas extensas pueden desplazarse dentro de su propio contenedor.
7. Seleccionar fase o jugador no borra ajustes pendientes, ni cambia la identidad del futbolista entre CP y SP.
8. Cada alerta muestra acción y fase; el motivo y la evidencia se consultan sin repetir el mensaje en cuatro lugares.
9. Confirmación manual, lectura de partida, recurso instalado, estimación y desconocido se distinguen sin volcar detalles técnicos innecesarios en el flujo principal.
10. Se entregan capturas finales de inicio, Mi táctica, Propuestas y ventana angosta, y se verifican sus acciones principales con pruebas de flujo.

## Evidencia gráfica de referencia

- [Propuestas en escritorio](referencias-interfaz/propuestas-escritorio-prueba.png).
- [Mi táctica: checklist y recomendaciones](referencias-interfaz/mi-tactica-prueba.png).
- [Propuestas en ventana angosta](referencias-interfaz/propuestas-ventana-angosta-prueba.png).

Estas imágenes contienen datos sintéticos. Los problemas de datos se deben contrastar con el análisis real y el código vigente, no con los valores de los jugadores ficticios.
