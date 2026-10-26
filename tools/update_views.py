from pathlib import Path

p = Path("web/views.js")
c = p.read_text(encoding="utf-8")

old_block = """<details class="panel"><summary>Roles y atributos de referencia</summary>${Object.values(m.roles).map(r=>`<details><summary>${esc(r.name)} · ${r.phase==='in_possession'?'Con posesión':'Sin posesión'}</summary><p>${esc(r.english)} · ${esc(r.positions.map(pos).join(', '))}</p><p>${esc(Object.keys(r.weights).map(k=>state.data.attributes[k]).join(', '))}</p><a href="${esc(r.source)}" target="_blank" rel="noreferrer">Fuente del rol ↗</a></details>`).join('')}</details>"""

new_block = """<details class="panel"><summary>Catálogo de roles de FM26 y atributos (${Object.keys(m.roles).length} roles)</summary>${Object.values(m.roles).map(r=>`<details><summary>${esc(r.name)} [${esc(r.abbreviation||'ROL')}] · ${r.phase==='in_possession'?'Con posesión (CP)':'Sin posesión (SP)'}</summary><p>${esc(r.english)} · Posiciones: ${esc(r.positions.map(pos).join(', '))}</p>${r.subposition_rule ? `<p class="notice">🛡️ Subpuesto: ${r.subposition_rule.min_central_defenders ? 'Requiere línea de al menos 3 centrales' : 'Requiere doble pivote'}</p>` : ''}${Array.isArray(r.behaviors) && r.behaviors.length ? `<p><strong>Comportamientos inherentes al rol:</strong></p><div class="role-behaviors-chips">${r.behaviors.map(b=>`<span class="behavior-chip">⚡ ${esc(b)}</span>`).join('')}</div>` : ''}<p><strong>Atributos requeridos:</strong> ${esc(Object.keys(r.weights).map(k=>state.data.attributes[k] || k).join(', '))}</p><p class="muted"><small>${r.key_attributes_ui_verified ? '✅ Atributos clave cotejados en interfaz de FM26' : 'ℹ️ Ponderación analítica propia de Touchline (80/20), no del motor interno de FM'}</small></p><a href="${esc(r.source)}" target="_blank" rel="noreferrer">Fuente del rol ↗</a></details>`).join('')}</details>"""

c_norm = c.replace("\r\n", "\n")
old_norm = old_block.replace("\r\n", "\n")
assert old_norm in c_norm, "old_block not found in views.js"

c_norm = c_norm.replace(old_norm, new_block, 1)
p.write_text(c_norm, encoding="utf-8")
print("views.js updated successfully")
