"""Updates web/tactics-view.js, web/current-view.js, and web/app.js for collective instructions reactivity."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 1. Update web/tactics-view.js
tactics_view_path = ROOT / 'web' / 'tactics-view.js'
tv_code = tactics_view_path.read_text(encoding='utf-8')

old_inst_fn = """export function instructions(tactic, data, prefs, draft = {}) {
  const pendingCount = Object.keys(draft).length;
  const instruction = item => {
    const applied = prefs.overrides[item.id] ?? item.value_en;
    const selected = draft[item.id] ?? applied;
    const origin = Object.hasOwn(draft, item.id) ? 'Cambio pendiente'
      : prefs.overrides[item.id] ? 'Ajuste manual' : item.origin === 'prompt' ? 'Pedido aplicado' : 'Propuesta';
    return `<article class="instruction"><label for="override-${item.id}">${esc(item.property)} <small>${origin}</small></label>
      <select id="override-${item.id}" data-override="${item.id}" data-applied="${esc(applied)}">${(data.instruction_options[item.id] || []).map(option => `<option value="${esc(option.value)}" ${option.value === selected ? 'selected' : ''}>${esc(option.label)}</option>`).join('')}</select>
      <p>${esc(item.reason)}</p></article>`;
  };
  return `<details class="panel"><summary>Instrucciones de equipo · ${tactic.instructions.length} ajustes</summary><p class="muted">Las etiquetas proceden del catálogo FM26; las elecciones y el índice de encaje son recomendaciones de Touchline.</p>
    ${pendingCount ? `<p class="notice" data-pending-overrides role="status">Tenés ${pendingCount} ${pendingCount === 1 ? 'cambio sin aplicar' : 'cambios sin aplicar'}. Revisá los valores y pulsá “Aplicar ajustes” para actualizar la propuesta.</p>` : ''}
    <div class="instruction-grid">${['in_possession', 'out_of_possession'].map(phase => `<section><h3>${phase === 'in_possession' ? 'Con posesión' : 'Sin posesión'}</h3>${tactic.instructions.filter(item => item.phase === phase).map(instruction).join('')}</section>`).join('')}</div>
    <div class="actions"><button class="button primary" data-action="apply-overrides">Aplicar ajustes</button><button class="button" data-action="clear-overrides">Restablecer ajustes manuales</button></div></details>`;
}"""

new_inst_fn = """export function instructions(tactic, data, prefs, draft = {}) {
  const pendingCount = Object.keys(draft).length;
  const currentUnderlap = draft.underlap_ip ?? prefs.overrides.underlap_ip ?? tactic.instructions.find(i => i.id === 'underlap_ip')?.value_en;
  const currentOverlap = draft.overlap_ip ?? prefs.overrides.overlap_ip ?? tactic.instructions.find(i => i.id === 'overlap_ip')?.value_en;

  const instruction = item => {
    const applied = prefs.overrides[item.id] ?? item.value_en;
    const selected = draft[item.id] ?? applied;
    const origin = Object.hasOwn(draft, item.id) ? 'Cambio pendiente'
      : prefs.overrides[item.id] ? 'Ajuste manual' : item.origin === 'prompt' ? 'Pedido aplicado' : 'Propuesta';

    const isOverlap = item.id === 'overlap_ip';
    const isUnderlap = item.id === 'underlap_ip';
    const underlapBothFlanks = currentUnderlap === 'Underlap - Both Flanks';
    const overlapBothFlanks = currentOverlap === 'Overlap - Both Flanks';

    const helperNote = item.id === 'short_goalkeeper_distribution_oop'
      ? `<span class="inst-scope-tag">Presionar salida rival</span>`
      : item.id === 'dribbling_ip'
      ? `<span class="inst-scope-tag">Compartido: Avance / Último tercio</span>`
      : item.id === 'pressing_trap_oop'
      ? `<span class="inst-scope-tag">Compartido: Presión alta / Bloque medio</span>`
      : '';

    const opts = (data.instruction_options[item.id] || []).map(option => {
      let disabled = false;
      if (isOverlap && underlapBothFlanks && option.value !== 'Overlap - Balanced') disabled = true;
      if (isUnderlap && overlapBothFlanks && option.value !== 'Underlap - Balanced') disabled = true;
      return `<option value="${esc(option.value)}" ${option.value === selected ? 'selected' : ''} ${disabled ? 'disabled' : ''}>${esc(option.label)}${disabled ? ' (Incompatible con desdoble interior en ambas bandas)' : ''}</option>`;
    }).join('');

    return `<article class="instruction"><label for="override-${item.id}">${esc(item.property)} ${helperNote} <small>${origin}</small></label>
      <select id="override-${item.id}" data-override="${item.id}" data-applied="${esc(applied)}">${opts}</select>
      <p>${esc(item.reason)}</p></article>`;
  };
  return `<details class="panel"><summary>Instrucciones de equipo · ${tactic.instructions.length} ajustes</summary><p class="muted">Las etiquetas proceden del catálogo FM26; las elecciones y el índice de encaje son recomendaciones de Touchline.</p>
    ${pendingCount ? `<p class="notice" data-pending-overrides role="status">Tenés ${pendingCount} ${pendingCount === 1 ? 'cambio sin aplicar' : 'cambios sin aplicar'}. Revisá los valores y pulsá “Aplicar ajustes” para actualizar la propuesta.</p>` : ''}
    <div class="instruction-grid">${['in_possession', 'out_of_possession'].map(phase => `<section><h3>${phase === 'in_possession' ? 'Con posesión' : 'Sin posesión'}</h3>${tactic.instructions.filter(item => item.phase === phase).map(instruction).join('')}</section>`).join('')}</div>
    <div class="actions"><button class="button primary" data-action="apply-overrides">Aplicar ajustes</button><button class="button" data-action="clear-overrides">Restablecer ajustes manuales</button></div></details>`;
}"""

assert old_inst_fn in tv_code, 'old_inst_fn not found in tactics-view.js'
tv_code = tv_code.replace(old_inst_fn, new_inst_fn)
tactics_view_path.write_text(tv_code, encoding='utf-8')
print('Updated web/tactics-view.js')

# 2. Update web/app.js
app_path = ROOT / 'web' / 'app.js'
app_code = app_path.read_text(encoding='utf-8')

# Handle mutual exclusion in override
old_override_block = """    if(input.dataset.override) {
      if(input.value===input.dataset.applied)delete state.overrideDraft[input.dataset.override];
      else state.overrideDraft[input.dataset.override]=input.value;
      render();
    }"""

new_override_block = """    if(input.dataset.override) {
      const key = input.dataset.override;
      const val = input.value;
      if(val===input.dataset.applied) delete state.overrideDraft[key];
      else state.overrideDraft[key] = val;

      // Handle support runs mutual exclusions
      if (key === 'underlap_ip' && val === 'Underlap - Both Flanks') {
        const curOverlap = state.overrideDraft.overlap_ip ?? state.prefs.overrides.overlap_ip;
        if (curOverlap && curOverlap !== 'Overlap - Balanced') {
          state.overrideDraft.overlap_ip = 'Overlap - Balanced';
        }
      } else if (key === 'overlap_ip' && val === 'Overlap - Both Flanks') {
        const curUnderlap = state.overrideDraft.underlap_ip ?? state.prefs.overrides.underlap_ip;
        if (curUnderlap && curUnderlap !== 'Underlap - Balanced') {
          state.overrideDraft.underlap_ip = 'Underlap - Balanced';
        }
      }
      render();
    }"""

assert old_override_block in app_code, 'old_override_block not found in app.js'
app_code = app_code.replace(old_override_block, new_override_block)

# Handle mutual exclusion in currentDraft.team
old_team_block = """} else if(input.dataset.team) {if(input.value)draft.team[input.dataset.team]=input.value;else delete draft.team[input.dataset.team];}"""

new_team_block = """} else if(input.dataset.team) {
        const key = input.dataset.team;
        const val = input.value;
        if(val) draft.team[key] = val;
        else delete draft.team[key];
        if (key === 'underlap_ip' && val === 'Underlap - Both Flanks') {
          if (draft.team.overlap_ip && draft.team.overlap_ip !== 'Overlap - Balanced') {
            draft.team.overlap_ip = 'Overlap - Balanced';
          }
        } else if (key === 'overlap_ip' && val === 'Overlap - Both Flanks') {
          if (draft.team.underlap_ip && draft.team.underlap_ip !== 'Underlap - Balanced') {
            draft.team.underlap_ip = 'Underlap - Balanced';
          }
        }
      }"""

assert old_team_block in app_code, 'old_team_block not found in app.js'
app_code = app_code.replace(old_team_block, new_team_block)
app_path.write_text(app_code, encoding='utf-8')
print('Updated web/app.js')

# 3. Update web/current-view.js for team grid and neutral SP tag
cv_path = ROOT / 'web' / 'current-view.js'
cv_code = cv_path.read_text(encoding='utf-8')

old_cv_grid = """      <div class="instruction-grid">
        ${Object.entries(data.instruction_options).map(([id,opts])=>`<label>${esc(editor.team_properties[id])}<select id="current-team-${id}" data-current="team" data-team="${id}">${options(opts,d.team[id])}</select></label>`).join('')}
      </div>"""

new_cv_grid = """      <div class="instruction-grid">
        ${Object.entries(data.instruction_options).map(([id, opts]) => {
          const isOverlap = id === 'overlap_ip';
          const isUnderlap = id === 'underlap_ip';
          const underlapBothFlanks = d.team['underlap_ip'] === 'Underlap - Both Flanks';
          const overlapBothFlanks = d.team['overlap_ip'] === 'Overlap - Both Flanks';
          const filteredOpts = opts.map(o => {
            let disabled = false;
            if (isOverlap && underlapBothFlanks && o.value !== 'Overlap - Balanced') disabled = true;
            if (isUnderlap && overlapBothFlanks && o.value !== 'Underlap - Balanced') disabled = true;
            return { ...o, disabled };
          });
          const note = id === 'short_goalkeeper_distribution_oop'
            ? ' <small style="color:var(--text-muted);">(Presionar salida rival)</small>'
            : id === 'dribbling_ip'
            ? ' <small style="color:var(--text-muted);">(Compartido)</small>'
            : id === 'pressing_trap_oop'
            ? ' <small style="color:var(--text-muted);">(Compartido)</small>'
            : '';
          return `<label>${esc(editor.team_properties[id])}${note}<select id="current-team-${id}" data-current="team" data-team="${id}">${filteredOpts.map(o => `<option value="${esc(o.value)}" ${d.team[id] === o.value ? 'selected' : ''} ${o.disabled ? 'disabled' : ''}>${esc(o.label)}${o.disabled ? ' (Incompatible con interior en ambas bandas)' : ''}</option>`).join('')}</select></label>`;
        }).join('')}
      </div>"""

assert old_cv_grid in cv_code, 'old_cv_grid not found in current-view.js'
cv_code = cv_code.replace(old_cv_grid, new_cv_grid)

# Neutral SP icon in 8-views card
old_sp_circle = "const k = `${entry.phase === 'CP' ? '🟢 Con posesión' : '🔴 Sin posesión'} · ${entry.area}`;"
new_sp_circle = "const k = `${entry.phase === 'CP' ? '⚽ Con posesión' : '🛡️ Sin posesión'} · ${entry.area}`;"
if old_sp_circle in cv_code:
    cv_code = cv_code.replace(old_sp_circle, new_sp_circle)

cv_path.write_text(cv_code, encoding='utf-8')
print('Updated web/current-view.js')
