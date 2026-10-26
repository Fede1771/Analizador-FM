from pathlib import Path

p = Path("web/current-view.js")
c = p.read_text(encoding="utf-8")

# 1. Update freshDraft
old_fresh = """export function freshDraft(data,formation='433') {
  const form=data.tactic_editor.formations.find(f=>f.id===formation)||data.tactic_editor.formations[0];
  return {formation:form.id,name:'Mi táctica',stored_id:'',style:'possession',confirmed:false,team:{},
    lineup:form.slots.map(slot=>({uid:'',ip_position:slot.ip_position,oop_position:slot.oop_position,ip_role:'',oop_role:'',instructions:{}}))};
}"""

new_fresh = """export function freshDraft(data,formation='433') {
  const form=data.tactic_editor.formations.find(f=>f.id===formation)||data.tactic_editor.formations[0];
  return {formation:form.id,name:'Mi táctica',stored_id:'',style:'possession',confirmed:false,team:{},
    lineup:form.slots.map(slot=>({uid:'',ip_position:slot.ip_position,oop_position:slot.oop_position,ip_role:'',oop_role:'',instruction_scope:'Posición',marking_target_player:'',marking_target_position:'',instructions:{}}))};
}"""

# 2. Update reconcileCurrentDraft
old_reconcile = """    row.instructions=Object.fromEntries(Object.entries(old.instructions||{}).filter(([id,v])=>editor.player_options[id]?.options.some(o=>o.value===v)));
    return row;"""

new_reconcile = """    row.instruction_scope = old.instruction_scope || 'Posición';
    row.marking_target_player = old.marking_target_player || '';
    row.marking_target_position = old.marking_target_position || '';
    row.instructions=Object.fromEntries(Object.entries(old.instructions||{}).filter(([id,v])=>editor.player_options[id]?.options.some(o=>o.value===v)));
    return row;"""

# 3. Update referenceDraft
old_ref = """    if(player)Object.assign(row,{ip_position:ref.ip_position,oop_position:ref.oop_position,ip_role:ref.ip_role||ref.ip,oop_role:ref.oop_role||ref.oop,instructions:{...standard,...(ref.instructions||{})}});"""

new_ref = """    if(player)Object.assign(row,{ip_position:ref.ip_position,oop_position:ref.oop_position,ip_role:ref.ip_role||ref.ip,oop_role:ref.oop_role||ref.oop,instruction_scope:ref.instruction_scope||'Posición',marking_target_player:ref.marking_target_player||'',marking_target_position:ref.marking_target_position||'',instructions:{...standard,...(ref.instructions||{})}});"""

# 4. Update the lineup and instructions rendering
old_lineup = """    <div class="current-lineup">${d.lineup.map((row,index)=>`<section class="current-slot"><h3>Puesto ${index+1}</h3><label>Jugador<select id="current-player-${index}" data-current="uid" data-row="${index}">${options(data.players.map(p=>({value:p.uid,label:p.name})),row.uid,'Elegí jugador')}</select></label>
    <div class="control-grid">${['ip','oop'].map(phase=>`<fieldset><legend>${phase==='ip'?'Con posesión':'Sin posesión'}</legend><label>Posición<select id="current-${phase}-position-${index}" data-current="${phase}_position" data-row="${index}">${editor.positions.map(p=>`<option value="${p}" ${row[phase+'_position']===p?'selected':''}>${esc(pos(p))}</option>`).join('')}</select></label><label>Rol actual<select id="current-${phase}-role-${index}" data-current="${phase}_role" data-row="${index}">${options(Object.entries(editor.roles).filter(([,r])=>r.phase===(phase==='ip'?'in_possession':'out_of_possession')&&r.positions.includes(row[phase+'_position'])).map(([id,r])=>({value:id,label:r.name})),row[phase+'_role'])}</select></label></fieldset>`).join('')}</div>
    <details id="current-instructions-${index}"><summary>Instrucciones individuales actuales</summary><p class="muted">Confirmá solo las órdenes que podés cotejar en FM. Sin confirmar no significa Normal. Menús completos para jugadores de campo y arquero.</p>
    <div class="instruction-grid">${Object.entries(editor.player_options).map(([id,v])=>{
      const phase=v.phase==='in_possession'?'ip':'oop',lock=editor.locks[row[phase+'_role']]?.[id];
      return `<label>${esc(v.label)} · ${phase==='ip'?'CP':'SP'} ${lock!==undefined?'<small>Bloqueada por el rol</small>':''}<select id="current-pi-${index}-${id}" data-current="instruction" data-row="${index}" data-pi="${id}" ${lock!==undefined?'disabled':''}>${options(v.options,lock??row.instructions[id])}</select></label>`;
    }).join('')}</div></details></section>`).join('')}</div>
    <details><summary>Instrucciones colectivas actuales</summary><p>Las que no confirmes quedan fuera de la revisión. Los valores son los del catálogo disponible.</p><div class="instruction-grid">${Object.entries(data.instruction_options).map(([id,opts])=>`<label>${esc(editor.team_properties[id])}<select id="current-team-${id}" data-current="team" data-team="${id}">${options(opts,d.team[id])}</select></label>`).join('')}</div></details>"""

new_lineup = """    <div class="current-lineup">${d.lineup.map((row,index)=>{
      const ipRoleObj = editor.roles[row.ip_role];
      const oopRoleObj = editor.roles[row.oop_role];

      return `<section class="current-slot">
        <div class="split">
          <h3>Puesto ${index+1}</h3>
          <label class="scope-toggle-label">Ámbito
            <select id="current-scope-${index}" data-current="instruction_scope" data-row="${index}">
              <option value="Posición" ${row.instruction_scope!=='Personalizada'?'selected':''}>Posición</option>
              <option value="Personalizada" ${row.instruction_scope==='Personalizada'?'selected':''}>Personalizada (jugador)</option>
            </select>
          </label>
        </div>
        <label>Jugador
          <select id="current-player-${index}" data-current="uid" data-row="${index}">
            ${options(data.players.map(p=>({value:p.uid,label:p.name})),row.uid,'Elegí jugador')}
          </select>
        </label>
        <div class="control-grid">
          ${['ip','oop'].map(phase=>{
            const rObj = phase === 'ip' ? ipRoleObj : oopRoleObj;
            const subpos = rObj?.subposition_rule ? `<div class="subpos-badge">🛡️ ${rObj.subposition_rule.min_central_defenders ? 'Solo zagas de 3 centrales' : 'Requiere doble pivote'}</div>` : '';
            const behaviors = (Array.isArray(rObj?.behaviors) && rObj.behaviors.length)
              ? `<div class="role-behaviors-chips">${rObj.behaviors.map(b=>`<span class="behavior-chip" title="Comportamiento inherente al rol en FM26">⚡ ${esc(b)}</span>`).join('')}</div>`
              : '';

            return `<fieldset>
              <legend>${phase==='ip'?'Con posesión':'Sin posesión'}</legend>
              <label>Posición
                <select id="current-${phase}-position-${index}" data-current="${phase}_position" data-row="${index}">
                  ${editor.positions.map(p=>`<option value="${p}" ${row[phase+'_position']===p?'selected':''}>${esc(pos(p))}</option>`).join('')}
                </select>
              </label>
              <label>Rol actual ${rObj?.abbreviation ? `<span class="role-abbrev-tag">${esc(rObj.abbreviation)}</span>` : ''}
                <select id="current-${phase}-role-${index}" data-current="${phase}_role" data-row="${index}">
                  ${options(Object.entries(editor.roles).filter(([,r])=>r.phase===(phase==='ip'?'in_possession':'out_of_possession')&&r.positions.includes(row[phase+'_position'])).map(([id,r])=>({value:id,label:r.name})),row[phase+'_role'])}
                </select>
              </label>
              ${subpos}
              ${behaviors}
            </fieldset>`;
          }).join('')}
        </div>
        <details id="current-instructions-${index}">
          <summary>Instrucciones individuales actuales (${row.instruction_scope || 'Posición'})</summary>
          <p class="muted">Confirmá solo las órdenes que podés cotejar en FM. Los candados 🔒 proceden de las capturas comprobadas en FM26; los controles ⚙️ son los editables observados.</p>
          <div class="instruction-grid">
            ${Object.entries(editor.player_options).map(([id,v])=>{
              const phase = v.phase === 'in_possession' ? 'ip' : 'oop';
              const roleId = row[phase + '_role'];
              const ctx = editor.observed_contexts?.[roleId];

              let lockBadge = '';
              let isDisabled = false;
              let selectedVal = row.instructions[id];
              let titleAttr = '';

              if (ctx) {
                if (id in ctx.locked_values) {
                  isDisabled = true;
                  const lockedVal = ctx.locked_values[id];
                  if (lockedVal === null) {
                    lockBadge = '<span class="inst-badge-masked" title="Tapado por ayuda emergente en captura de FM26">🔒 Bloqueada (valor tapado)</span>';
                    selectedVal = null;
                  } else {
                    selectedVal = lockedVal;
                    titleAttr = `title="Bloqueada por el rol en FM26 (${ctx.evidence})"`;
                    lockBadge = `<span class="inst-badge-lock" ${titleAttr}>🔒 Bloqueada</span>`;
                  }
                } else if (ctx.editable_groups?.includes(id)) {
                  titleAttr = `title="Comprobado editable en FM26 (${ctx.evidence})"`;
                  lockBadge = `<span class="inst-badge-edit" ${titleAttr}>⚙️ Editable</span>`;
                } else {
                  lockBadge = '<span class="inst-badge-unverified" title="Fuera de panel comprobado para este rol">No disponible</span>';
                }
              } else {
                lockBadge = '<span class="inst-badge-unverified" title="Disponibilidad no comprobada en capturas">ℹ️ No comprobado</span>';
              }

              const isMarkingOop = (id === 'marking_target_oop');
              const currentMarkingVal = selectedVal ?? row.instructions['marking_target_oop'];

              let markingSubInput = '';
              if (isMarkingOop) {
                if (currentMarkingVal === 'Mark Specific') {
                  markingSubInput = `<div class="marking-sub-input">
                    <label>Jugador rival a marcar (nombre o dorsal):
                      <input type="text" id="current-target-player-${index}" data-current="marking_target_player" data-row="${index}" value="${esc(row.marking_target_player || '')}" placeholder="Ej. Erling Haaland">
                    </label>
                  </div>`;
                } else if (currentMarkingVal === 'Mark Position') {
                  markingSubInput = `<div class="marking-sub-input">
                    <label>Puesto rival a marcar:
                      <select id="current-target-pos-${index}" data-current="marking_target_position" data-row="${index}">
                        ${options(editor.positions.map(p => ({value: p, label: pos(p)})), row.marking_target_position || '', 'Elegí puesto rival')}
                      </select>
                    </label>
                  </div>`;
                }
              }

              return `<div>
                <label>${esc(v.label)} · ${phase==='ip'?'CP':'SP'} ${lockBadge}
                  <select id="current-pi-${index}-${id}" data-current="instruction" data-row="${index}" data-pi="${id}" ${isDisabled ? 'disabled' : ''}>
                    ${options(v.options, selectedVal)}
                  </select>
                </label>
                ${markingSubInput}
              </div>`;
            }).join('')}
          </div>
        </details>
      </section>`;
    }).join('')}</div>
    <details>
      <summary>Instrucciones colectivas actuales y vistas comprobadas en FM26</summary>
      <p class="muted">Las que no confirmes quedan fuera de la revisión. Los valores son los del catálogo disponible de FM26.</p>

      ${Array.isArray(editor.team_views_current) && editor.team_views_current.length ? `
        <details style="margin-bottom: 14px;">
          <summary>📋 Registro empírico: 8 vistas y 29 estados observados en FM26</summary>
          <p class="muted"><small>Estados observados directamente en la interfaz del juego durante el relevamiento de la táctica:</small></p>
          <div class="team-views-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 10px;">
            ${(() => {
              const grouped = {};
              for (const entry of editor.team_views_current) {
                const k = `${entry.phase === 'CP' ? '🟢 Con posesión' : '🔴 Sin posesión'} · ${entry.area}`;
                if (!grouped[k]) grouped[k] = [];
                grouped[k].push(entry);
              }
              return Object.entries(grouped).map(([title, items]) => `
                <div class="team-view-card">
                  <div class="team-view-header"><span class="team-view-title">${esc(title)}</span></div>
                  <div class="team-view-items">
                    ${items.map(it => `<span class="team-view-item">${esc(it.name)}: <strong>${esc(it.value)}</strong></span>`).join('')}
                  </div>
                </div>
              `).join('');
            })()}
          </div>
        </details>
      ` : ''}

      <div class="instruction-grid">
        ${Object.entries(data.instruction_options).map(([id,opts])=>`<label>${esc(editor.team_properties[id])}<select id="current-team-${id}" data-current="team" data-team="${id}">${options(opts,d.team[id])}</select></label>`).join('')}
      </div>
    </details>"""

c_norm = c.replace("\r\n", "\n")
old_fresh_norm = old_fresh.replace("\r\n", "\n")
old_reconcile_norm = old_reconcile.replace("\r\n", "\n")
old_ref_norm = old_ref.replace("\r\n", "\n")
old_lineup_norm = old_lineup.replace("\r\n", "\n")

assert old_fresh_norm in c_norm, "old_fresh not found"
assert old_reconcile_norm in c_norm, "old_reconcile not found"
assert old_ref_norm in c_norm, "old_ref not found"
assert old_lineup_norm in c_norm, "old_lineup not found"

c_norm = c_norm.replace(old_fresh_norm, new_fresh, 1)
c_norm = c_norm.replace(old_reconcile_norm, new_reconcile, 1)
c_norm = c_norm.replace(old_ref_norm, new_ref, 1)
c_norm = c_norm.replace(old_lineup_norm, new_lineup, 1)

p.write_text(c_norm, encoding="utf-8")
print("current-view.js updated successfully")
