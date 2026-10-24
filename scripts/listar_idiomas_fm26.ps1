# Run on the Windows PC where Football Manager 26 is installed.
# Reads file names and sizes only. Does not modify the game or send any data.
param([string]$GameFolder)
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($GameFolder)) {
    $GameFolder = Read-Host 'Pega la carpeta de FM26 que abrio Steam (sin agregar comandos)'
}
$GameFolder = $GameFolder.Trim().Trim('"')
$fmFolder = (Resolve-Path -LiteralPath $GameFolder).ProviderPath
if (-not (Test-Path -LiteralPath $fmFolder -PathType Container)) {
    throw 'La ruta debe ser una carpeta.'
}
if (-not (Test-Path -LiteralPath (Join-Path $fmFolder 'fm_Data') -PathType Container)) {
    throw 'No se encontro fm_Data. Selecciona la carpeta principal de Football Manager 26.'
}
$fmItems = @(Get-ChildItem -LiteralPath $fmFolder -File -Recurse -ErrorAction SilentlyContinue)
$fmCandidates = @($fmItems | Where-Object {
    $_.FullName.Substring($fmFolder.Length) -match '(?i)languages?|locali[sz]|locales?|spanish|espanol|latin|es[-_](419|mx|ar)' -or
    $_.Extension -in @('.ltc', '.ltf')
} | Sort-Object FullName)
$fmLines = [System.Collections.Generic.List[string]]::new()
$fmLines.Add('FM26 - Inventario de archivos de idioma')
$fmLines.Add('Idioma que se busca: Espanol (Latinoamerica), es-419.')
$fmLines.Add('Este listado contiene rutas relativas y tamanos, no contenido de archivos.')
$fmLines.Add('')
if ($fmCandidates.Count -gt 0) {
    foreach ($fmItem in $fmCandidates) {
        $fmRelative = $fmItem.FullName.Substring($fmFolder.Length).TrimStart('\', '/')
        $fmLines.Add(('{0} | {1} bytes' -f $fmRelative, $fmItem.Length))
    }
} else {
    $fmLines.Add('No se identificaron candidatos por el nombre. Archivos FMF de la instalacion:')
    foreach ($fmItem in ($fmItems | Where-Object Extension -eq '.fmf' | Sort-Object FullName)) {
        $fmRelative = $fmItem.FullName.Substring($fmFolder.Length).TrimStart('\', '/')
        $fmLines.Add(('{0} | {1} bytes' -f $fmRelative, $fmItem.Length))
    }
}
$fmDesktop = [Environment]::GetFolderPath('Desktop')
$fmOutput = Join-Path $fmDesktop ('FM26-idiomas-{0}.txt' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$fmLines | Set-Content -LiteralPath $fmOutput -Encoding UTF8
Write-Host ''
Write-Host 'Listo. Comparti este archivo en el chat:'
Write-Host $fmOutput
Write-Host 'No hace falta enviar el juego completo.'
Read-Host 'Presiona Enter para cerrar' | Out-Null
