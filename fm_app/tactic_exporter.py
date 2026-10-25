"""Tactic exporter generating .fmf and JSON presets directly into FM26 tactics folder."""
import json
from pathlib import Path
import os


def export_tactic_file(dataset, params):
    formation = params.get('formation', '433')
    club = dataset.get('club', 'Club')
    tactic_name = params.get('name') or f"Touchline_{club}_{formation}"
    safe_name = "".join(c for c in tactic_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')

    # Path to Sports Interactive tactics directory
    documents_dir = Path.home() / 'Documents'
    tactics_dir = documents_dir / 'Sports Interactive' / 'Football Manager 26' / 'tactics'
    tactics_dir.mkdir(parents=True, exist_ok=True)

    tactic_payload = {
        'name': tactic_name,
        'club': dataset.get('club'),
        'date': dataset.get('date'),
        'formation': formation,
        'style': params.get('style'),
        'mentality': params.get('mentality', 'Positiva'),
        'team_instructions': params.get('team', {}),
        'lineup': params.get('lineup', [])
    }

    # Write formatted json descriptor
    json_path = tactics_dir / f"{safe_name}.json"
    json_path.write_text(json.dumps(tactic_payload, indent=2, ensure_ascii=False), encoding='utf-8')

    # Write .fmf archive preset
    fmf_path = tactics_dir / f"{safe_name}.fmf"
    fmf_header = b'\x02\x01fmf.\x08\x00\x00\x00\x00\x00\x00'
    fmf_data = json.dumps(tactic_payload, ensure_ascii=False).encode('utf-8')
    fmf_path.write_bytes(fmf_header + fmf_data)

    # Generate summary instructions formatted for clipboard
    summary_lines = [
        f"⚽ TÁCTICA TOUCHLINE FM26: {tactic_name}",
        f"Esquema: {formation} · Estilo: {params.get('style_name', params.get('style', 'Posesión'))} · Mentalidad: {params.get('mentality', 'Positiva')}",
        "",
        "📋 AJUSTES DEL PARTIDO EN FM:"
    ]
    actions = params.get('actions') or []
    if actions:
        for idx, item in enumerate(actions, 1):
            summary_lines.append(f"{idx}. {item}")
    else:
        summary_lines.append("• Confirmá el once titular y los roles específicos por fase.")

    summary_lines.extend([
        "",
        "📂 ARCHIVO GENERADO EN TU PC:",
        str(fmf_path),
        "En FM: Pantalla Táctica ➔ Menú superior 'Tácticas' ➔ 'Cargar' ➔ Seleccionar archivo."
    ])
    clipboard_text = "\n".join(summary_lines)

    return {
        'success': True,
        'filename': f"{safe_name}.fmf",
        'json_filename': f"{safe_name}.json",
        'path': str(fmf_path),
        'tactics_dir': str(tactics_dir),
        'clipboard_summary': clipboard_text,
        'message': f"¡Táctica exportada con éxito! Guardada en Documentos\\Sports Interactive\\Football Manager 26\\tactics\\{safe_name}.fmf"
    }
