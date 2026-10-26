# Pedido para la IA que va a reconstruir el software

Quiero que reconstruyas/mejores Touchline, mi analizador local de Football Manager 26, usando este relevamiento de mi instalación como referencia táctica. No te pido recrear el motor de partidos de FM.

Primero leé REPORTE.md y catalogo-para-reconstruccion.json. Consultá las capturas y los registros de textos para resolver detalles. El idioma actual es Español latinoamericano y la versión visible es 26.3.2.2329565 (m.e v26.3.0.1). No confundas claves de idioma con IDs de la partida ni textos instalados con comportamiento comprobado.

El catálogo reúne 79 definiciones por fase, 14 familias de puesto y 15 grupos individuales con 45 opciones. Los 79 roles tienen evidencia visual, panel individual registrado y lista de atributos cotejada. Se completaron los 13 paneles de la última tanda y los tres valores ocultos quedaron confirmados en No. Consultá verificacion-adicional-roles.json y matriz-instrucciones-observadas.json para estos datos, y verificacion-adicional-mecanicas.json para los destinos de marca. La matriz completa de disponibilidad por subpuesto, fase y alcance sigue pendiente: respetá la procedencia y los desconocidos. No afirmes que se verificaron todas las combinaciones.

Revisá la arquitectura existente antes de modificarla. Conservá el lector de partidas y los datos reales que ya funcionan. Evitá datos de ejemplo en los análisis de mi equipo. Separá posiciones/subpuestos, roles CP/SP, comportamientos inherentes, instrucciones de posición y personales, y órdenes colectivas.

Contrastá el estado actual del código con los problemas identificados en la revisión: Más directo en passing_directness_ip, seis definiciones ausentes, duplicado de Carrilero organizador, alias de español, restricciones dependientes del puesto y objetivo adicional requerido por las marcas específicas. Corregí lo que siga vigente; el software puede haber cambiado desde la primera inspección. No conviertas valores desconocidos en Normal y no extrapoles candados de una captura a todos los contextos.

Las fórmulas 80/20, umbrales de atributos, riesgos y mapas de zonas son reglas propias de Touchline; explicalas y no las atribuyas a FM. Una descripción de rol no revela pesos internos ni una probabilidad de ganar.

Implementá de extremo a extremo: catálogo y contratos, validación, persistencia, cálculo, interfaz, exportación y pruebas significativas. Preservá la configuración de la carrera y la identidad del mismo jugador en ambas fases. Mostrá qué cambió, por qué, qué quedó pendiente y cómo se verificó.

Cobertura al cierre: 79/79 paneles y 79/79 listas de atributos cotejadas. Leé PENDIENTES.md antes de asumir cobertura completa. Usá matriz-instrucciones-observadas.json como fuente directa de restricciones en el contexto observado. La ficha del Zaguero contradice su panel activo: conservá la discrepancia y priorizá el panel de instrucciones para ese valor.


## Encargo ampliado: interfaz y organización de información

El proyecto local está en `C:\Users\feder\Documents\Codigos varios y emprendimientos\Analizador FM`. La documentación está en `docs/relevamiento-fm26-2026-10-25/` dentro del proyecto. Si recibiste el ZIP en otro equipo, extraelo y usá la carpeta equivalente; el ZIP contiene documentación y evidencias, no todo el repositorio del programa.

Empezá por INFORME-INTEGRAL.md y leé también MEJORAS-DE-INTERFAZ.md. Implementá las mejoras tácticas y de interfaz en el proyecto existente. Contrastá cada hallazgo con el código actual: hay trabajo previo y puede haber correcciones posteriores al análisis. Conservá las modificaciones existentes y resolvé únicamente los problemas que sigan vigentes.

Prioridad 1: recomendaciones vigentes y coherentes entre checklist, tarjetas, copia y HUD; eliminar nombres y cantidades fijas ajenos al resultado; sustituir «100% optimizada» por un estado que describa lo marcado por el usuario; distinguir propuesta y táctica actual. Comprobá que los metadatos y acciones del HUD correspondan al contexto desde donde se abre.

Prioridad 2: integrar las restricciones tácticas documentadas y simplificar el flujo visual. Mostrar antes la cancha y hasta tres prioridades, unificar la entrada de formación y de idea de juego, reducir botones duplicados y abrir explicaciones y ajustes extensos bajo demanda. Conservar la identidad oscura con verde menta, unificar nombres e iconos y separar colores de fase y gravedad. Adaptar las ventanas angostas y verificar teclado, foco y contraste.

Seguí los criterios de aceptación de MEJORAS-DE-INTERFAZ.md. Preservá el lector de partidas, los datos reales, la configuración por carrera, la identidad del jugador entre fases, las órdenes desconocidas y los cambios pendientes al navegar. No presentes las capturas de prueba de referencias-interfaz/ como datos del equipo. No inventes opciones o reglas para cubrir lo que falta: dejá esos contextos explícitos y preparados para incorporar evidencia posterior.

Implementá y validá el flujo completo con pruebas significativas y capturas de escritorio y ventana angosta. Entregá qué cambió, cómo se verificó y qué queda pendiente. Si no tenés acceso al código del programa, usá el paquete para preparar una especificación concreta y señalá que la implementación necesita el repositorio; no afirmes haberlo modificado.

## Actualización: selectores colectivos observados

Se revisaron **27 paneles colectivos únicos (28 dimensiones)** y se confirmaron dos controles compartidos. Leé [ADENDA-COLECTIVAS.md](ADENDA-COLECTIVAS.md) y [verificacion-colectivas.json](verificacion-colectivas.json). Estas pruebas cierran la lista de opciones visibles y las duplicaciones de Regate/Trampa de presión; las combinaciones de contexto y todas las ayudas siguen sin certificarse. El marcaje queda excluido de nuevas investigaciones por pedido del usuario.

Integrá estas opciones y únicamente los bloqueos observados, conservando el trabajo actual. No agregues nuevos requisitos de marcaje. Priorizá estos datos frente a listas históricas de variantes pendientes.
