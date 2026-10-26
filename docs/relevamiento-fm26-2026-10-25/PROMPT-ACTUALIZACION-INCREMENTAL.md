# Actualización incremental para la IA que ya trabaja en Touchline

Continuá desde tu implementación actual de Touchline e incorporá las últimas evidencias de FM26. Conservá todo lo que ya hiciste y resolvé únicamente diferencias vigentes; no reinicies el proyecto ni reemplaces archivos completos por versiones históricas.

Proyecto:
`C:\Users\feder\Documents\Codigos varios y emprendimientos\Analizador FM`

Documentación actualizada disponible directamente en:
`C:\Users\feder\Documents\Codigos varios y emprendimientos\Analizador FM\docs\relevamiento-fm26-2026-10-25`

No necesitás extraer el ZIP. Leé primero ALCANCE-Y-CIERRE.md, después ADENDA-COSTADOS-PORTERO-2026-10-26.md y ADENDA-COLECTIVAS.md. Contrastá verificacion-costados-portero-2026-10-26.json, verificacion-colectivas.json, catalogo-para-reconstruccion.json y matriz-instrucciones-observadas.json. Usá INFORME-INTEGRAL.md y MEJORAS-DE-INTERFAZ.md para las prioridades tácticas y visuales que todavía sigan vigentes.

Novedades para integrar:

- Carreras de apoyo tiene dos ejes: Doblar por banda y Doblar por dentro. La matriz de 16 combinaciones documenta nueve seleccionadas y siete bloqueadas: exterior e interior coexisten en costados opuestos y se excluyen en el mismo. Ambas bandas en un eje deja al otro únicamente Equilibrado. Conservá la procedencia de esta regla en el contexto observado.
- Los dos botones Bandas de distribución del propio portero son equivalentes; también los dos Laterales. Son siete destinos únicos; no agregues destinos izquierda/derecha.
- Regate comparte estado entre Avance y Último tercio. Trampa de presión comparte estado entre Presión adelantada y Bloque medio. Evitá persistir valores independientes para representaciones del mismo control.
- Respetá los conjuntos y etiquetas reales de los 27 selectores colectivos. Distinguí el destino/velocidad del propio portero de impedir la distribución corta del portero rival.

El relevamiento está completo para el alcance acordado. Los contextos no ensayados son límites de evidencia, no faltantes indispensables conocidos. No se confirmó que cambiar la mentalidad modifique candados individuales: no inventes bloqueos por mentalidad, formación o personalización. Diferenciá editable comprobado, bloqueado comprobado y disponibilidad desconocida. Conservá los textos extraídos de la instalación para las ayudas; no hace falta abrir cada explicación para implementar. El marcaje queda excluido de esta ampliación.

Revisá primero el estado actual y tus cambios existentes. Adaptá los datos al modelo y contratos del proyecto; no importes el catálogo sobre producción a ciegas. Preservá jugadores, carreras, archivos importados y configuraciones. Si hay selecciones antiguas incompatibles, informalas y permití corregirlas sin sustituirlas silenciosamente. Incorporá migraciones compatibles si cambia la persistencia.

Integrá lo que corresponda en validación, cálculo, interfaz, persistencia y exportación. Validá los flujos afectados con pruebas significativas: costados opuestos admitidos, mismo costado bloqueado, Ambas bandas, sincronización de controles compartidos y guardado/reapertura. Complementá los datos sintéticos con copias de archivos y configuraciones reales disponibles, sin sobrescribir originales. Si alguna comprobación no puede hacerse, indicá cuál.

Entregá qué cambió, qué ya estaba implementado, cómo lo verificaste y los límites restantes. Mantené las mejoras gráficas y funcionales actuales y aportá capturas finales de los flujos modificados.
