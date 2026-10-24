# Obtener la referencia de FM26 en Español (Latinoamérica)

**Actualización del 24 de octubre de 2026:** ya se instaló FM26 en esta notebook y se extrajeron sus etiquetas latinoamericanas. No hace falta enviar archivos de otra PC. El procedimiento reproducible, las variantes de nombre y lo pendiente de cotejo visual figuran en [fm26-reference.md](fm26-reference.md).

Se conserva a continuación el procedimiento de inventario para futuras instalaciones. No se deben confirmar textos de España como si fueran los del menú LATAM.

Para localizar el archivo correcto sin enviar el juego completo:

1. En la PC de juego, abrir Steam → Biblioteca → clic derecho sobre FM26 → Administrar → Ver archivos locales.
2. Copiar la ruta de la carpeta que se abre.
3. Ejecutar `scripts/listar_idiomas_fm26.ps1` en PowerShell y pegar esa ruta cuando la pida. El script consulta nombres y tamaños, sin leer el contenido ni modificar el juego.
4. Compartir el archivo `FM26-idiomas-*.txt` creado en el Escritorio. Con el inventario se podrá pedir únicamente el archivo de localización necesario.

Si una política de Windows impide ejecutar el script, no es necesario cambiarla: se puede abrir el archivo en Bloc de notas, copiar su contenido a una consola de PowerShell y ejecutarlo allí, o enviar capturas de los nombres de los archivos de idioma desde el Explorador.

El inventario solo guarda rutas relativas a FM26 y tamaños. No incluye la ruta de usuario, partidas, credenciales ni contenido de los archivos. Los idiomas de la instalación actual están empaquetados en `languages.fmf`; se analizó una copia sin modificar el juego.
