# Verificación de Touchline 1.1.1

Fecha: 5 de noviembre de 2026.

## Versión aprobada

Base funcional de 1.0.5 con el menú compacto agrupado en Juego, Plantel, Gestión y Ayuda. Se conservan las nueve secciones, los iconos, el colapsado, su preferencia y el panel móvil. No se incorporan el resto del rediseño ni las funciones de Análisis del plantel de 1.1.0.

La normalización de saltos de línea de `fm_app/dataset.py` se verificó mediante igualdad del AST respecto de 1.0.5: no cambia su lógica.

## Pruebas

- **114/114 pruebas Python aprobadas**, incluidas las pruebas con copias temporales de extracciones reales disponibles.
- **13/13 pruebas de frontend aprobadas.**
- **30/30 recorridos de navegador aprobados**, sin errores inesperados. Incluyen navegación agrupada, colapsado y área recuperada, teclado y panel de 420 px, preferencias al cambiar de guardado, desdobles incompatibles, instrucciones manuales, candados por contexto, once y roles en ambas fases, contratos, ojeo, plantillas y guía.
- **11 capturas actualizadas**, generadas con datos sintéticos en [la galería](../../capturas-finales/README.md).
- **Ejecutable compilado comprobado:** restauración de carrera sintética, análisis de tres propuestas, simulación con once jugadores, recursos del menú idénticos a los fuentes, plantel activo conservado y cierre limpio.

Las pruebas automatizadas usan directorios temporales y perfiles aislados. No se importan planteles sintéticos en el perfil personal. La actualización no elimina partidas, preferencias ni el historial almacenado por 1.1.0, aunque este último no se muestra en esta versión.

## Distribución

- MSI compilado con WiX 7.0.0 y PyInstaller 6.22.3.
- ProductVersion: `1.1.1`, superior a 1.1.0 para permitir su actualización normal.
- UpgradeCode conservado: `{4E565251-5443-4C4E-8765-202610260001}`.
- 293 archivos; accesos directos de Escritorio y Menú Inicio verificados.
- Todos los recursos web empaquetados coinciden con los fuentes.
- SHA-256: `88602b598b59bf063e8f3d7509bfd024b1f21ca8c4d338a2a6efe8a44ff101e1`.

No se instaló el MSI sobre el perfil personal para esta verificación. Se ejecutó la aplicación compilada con una carrera temporal y sincronización desactivada únicamente en ese proceso de prueba. El release incluye el MSI y su checksum; no incluye partidas personales ni extracciones.
