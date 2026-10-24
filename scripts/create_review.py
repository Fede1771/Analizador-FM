"""Create a readable review from the locally exported data (no save re-read)."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
output = root / "data" / "output"
report = json.loads((output / "validation.json").read_text(encoding="utf-8"))
players = json.loads((output / "brighton_full.json").read_text(encoding="utf-8"))
first = sorted((p for p in players if p["team_slot"] == 0), key=lambda p: p["name"])
lines = [
    "# Prueba de lectura: Brighton",
    "",
    f"Partida: {report['game']}, compilación {report['build']}. Fecha interna: {report['game_date']}.",
    f"Lector: fmsave {report['library']}; compilación reconocida: {report['known_build']}.",
    "",
    f"Se extrajeron {report['brighton_count']} jugadores vinculados al club y {report['loaned_out_count']} cedidos a otros clubes (exportados aparte).",
    "Los grupos almacenados contienen 25, 24 y 14 jugadores. El grupo 0 parece ser el primer equipo; las etiquetas de los otros grupos requieren confirmación en FM.",
    "",
    f"Campos básicos faltantes: {report['missing_required_fields']}. Errores de consistencia: {report['sanity_errors']}. Advertencias del lector: {report['reader_warnings']}.",
    f"Se comprobaron los {report['attributes_per_player']} atributos y las 15 posiciones por jugador: enteros entre 1 y 20; identificadores sin duplicados y edades entre 12 y 65.",
    f"La copia permaneció sin cambios durante la extracción: {report['snapshot_unchanged']}.",
    "",
    "## Grupo 0: probable primer equipo",
    "",
    "Posiciones naturales según el lector. Pases, técnica, velocidad y remate en escala 1–20.",
    "",
    "| Jugador | Edad | Posiciones | Pases | Técnica | Velocidad | Remate |",
    "|---|---:|---|---:|---:|---:|---:|",
]
for p in first:
    a = p["attributes"]
    lines.append(f"| {p['name']} | {p['age']} | {', '.join(p['natural_positions'])} | {a['passing']} | {a['technique']} | {a['pace']} | {a['finishing']} |")
lines += [
    "",
    "## Alcance de la validación",
    "",
    "La extracción y los controles de consistencia finalizaron. Todavía NO se cotejaron estos valores con la interfaz del juego. Un dato plausible no demuestra una interpretación correcta de los bytes.",
    "Para completar esa comprobación, comparar en esta misma fecha de la partida las fichas de Bart Verbruggen, Lewis Dunk y Yankuba Minteh: identidad, edad, posiciones y atributos. Si FM muestra otro día, la edad y los atributos podrían haber cambiado.",
    "El archivo validation.json conserva el estado de verificación declarado por la biblioteca para cada campo. Ese estado proviene del autor del lector y no sustituye una comprobación de esta partida.",
    "",
    "## Archivos",
    "",
    "- brighton_visible.csv: datos básicos y atributos visibles de los 63 jugadores; excluye capacidad actual/potencial, personalidad oculta y los cinco atributos ocultos del conjunto de 52.",
    "- brighton_full.json / brighton_full.csv: extracción completa, incluyendo datos ocultos, valores sin normalizar y contratos. No todos los campos tienen el mismo grado de confirmación.",
    "- brighton_loaned_out.json: jugadores cedidos por Brighton a otros clubes.",
    "- validation.json: conteos, controles, advertencias, estados de campos y huella SHA-256.",
    "",
    "La prueba se ejecutó localmente sobre data/input/brighton.fm; el archivo original no se modificó ni se subió a servicios externos.",
]
(output / "informe_brighton.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
