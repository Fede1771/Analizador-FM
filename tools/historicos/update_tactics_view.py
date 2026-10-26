from pathlib import Path

p = Path("web/tactics-view.js")
c = p.read_text(encoding="utf-8")

old_plan = """export function rolePlan(role) {
  return `<section class="role-plan"><div class="split"><div><span class="eyebrow">${role.phase === 'in_possession' ? 'Con posesión' : 'Sin posesión'} · ${esc(pos(role.position))}</span><h3>${esc(role.name)}</h3><small>${esc(role.english)}</small></div>${score(role.score)}</div>
    <p>${esc(role.tactical_summary || role.reasons.at(-1))}</p><ul>${role.reasons.slice(0,3).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>
    ${role.warnings.length ? `<p class="notice warning">${esc(role.warnings.join(' '))}</p>` : ''}
    <details><summary>Instrucciones individuales y alternativas</summary>${role.instructions.map(i=>`<article class="instruction"><strong>${esc(i.property)}: ${esc(i.value)} ${i.locked ? '· Bloqueada por el rol' : ''}</strong><p>${esc(i.reason)}</p><small>${esc(i.availability_source || '')}</small></article>`).join('')}
    ${role.unconfirmed_instructions?`<p class="muted">${role.unconfirmed_instructions} instrucciones de esta fase sin confirmar. Las que se muestran proceden de tu carga o de bloqueos comprobados del rol.</p>`:''}
    <p>${esc(role.comparison)}</p><p class="muted">${esc(role.spanish_status)}</p><a href="${esc(role.source)}" target="_blank" rel="noreferrer">Referencia del rol ↗</a></details></section>`;
}"""

new_plan = """export function rolePlan(role) {
  const badge = role.role_abbrev || role.abbreviation || '';
  const subpos = role.subposition_rule ? `<div class="subpos-badge">🛡️ ${role.subposition_rule.min_central_defenders ? 'Requiere línea de al menos 3 centrales' : 'Requiere doble pivote'}</div>` : '';
  const behaviorsChips = Array.isArray(role.behaviors) && role.behaviors.length
    ? `<div class="role-behaviors-chips">${role.behaviors.map(b => `<span class="behavior-chip" title="Comportamiento inherente al rol en FM26">⚡ ${esc(b)}</span>`).join('')}</div>`
    : '';
  const scopeBadge = role.scope ? `<span class="advice-chip" style="margin-left:6px;">Ámbito: ${esc(role.scope)}</span>` : '';

  return `<section class="role-plan"><div class="split"><div><span class="eyebrow">${role.phase === 'in_possession' ? 'Con posesión' : 'Sin posesión'} · ${esc(pos(role.position))} ${scopeBadge}</span><h3>${esc(role.name)} ${badge ? `<span class="role-abbrev-tag">${esc(badge)}</span>` : ''}</h3><small>${esc(role.english)}</small>${subpos}${behaviorsChips}</div>${score(role.score)}</div>
    <p>${esc(role.tactical_summary || role.reasons.at(-1))}</p><ul>${role.reasons.slice(0,3).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>
    ${role.warnings.length ? `<p class="notice warning">${esc(role.warnings.join(' '))}</p>` : ''}
    <details><summary>Instrucciones individuales y alternativas</summary>${role.instructions.map(i=>{
      const statusBadge = i.locked ? (i.locked_value == null ? '<span class="inst-badge-masked">🔒 Bloqueada (tapada por tooltip)</span>' : '<span class="inst-badge-lock">🔒 Bloqueada por rol</span>') : (i.editable ? '<span class="inst-badge-edit">⚙️ Editable</span>' : '<span class="inst-badge-unverified">ℹ️ No comprobado</span>');
      return `<article class="instruction"><strong>${esc(i.property)}: ${esc(i.value ?? 'No asignado')} ${statusBadge}</strong><p>${esc(i.reason)}</p><small>${esc(i.availability_source || '')}</small></article>`;
    }).join('')}
    ${role.unconfirmed_instructions?`<p class="muted">${role.unconfirmed_instructions} instrucciones de esta fase sin confirmar. Las que se muestran proceden de tu carga o de bloqueos comprobados del rol.</p>`:''}
    <p>${esc(role.comparison)}</p><p class="muted">${esc(role.spanish_status)}</p><a href="${esc(role.source)}" target="_blank" rel="noreferrer">Referencia del rol ↗</a></details></section>`;
}"""

# Normalize CRLF
c_norm = c.replace("\r\n", "\n")
old_norm = old_plan.replace("\r\n", "\n")
assert old_norm in c_norm, "old_plan target not found"

c_norm = c_norm.replace(old_norm, new_plan, 1)
p.write_text(c_norm, encoding="utf-8")
print("tactics-view.js updated successfully")
