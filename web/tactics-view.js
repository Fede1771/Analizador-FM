import {esc, number, score, playerButton, pos} from './format.js';
import {zoneMap} from './zones-view.js';

export function rolePlan(role) {
  const badge = role.role_abbrev || role.abbreviation || '';
  const subpos = role.subposition_rule ? `<div class="subpos-badge">🛡️ ${role.subposition_rule.min_central_defenders ? 'Requiere línea de al menos 3 centrales' : 'Requiere doble pivote'}</div>` : '';
  const behaviorsChips = Array.isArray(role.behaviors) && role.behaviors.length
    ? `<div class="role-behaviors-chips">${role.behaviors.map(b => `<span class="behavior-chip" title="Comportamiento inherente al rol en FM26">⚡ ${esc(b)}</span>`).join('')}</div>`
    : '';
  const scopeBadge = role.scope ? `<span class="advice-chip" style="margin-left:6px;">Ámbito: ${esc(role.scope)}</span>` : '';

  return `<section class="role-plan"><div class="split"><div><span class="eyebrow">${role.phase === 'in_possession' ? 'Con posesión' : 'Sin posesión'} · ${esc(pos(role.position))} ${scopeBadge}</span><h3>${esc(role.name)}</h3><small>${badge ? `<span class="role-abbrev-tag">${esc(badge)}</span> · ` : ''}${esc(role.english)}</small>${subpos}${behaviorsChips}</div>${score(role.score)}</div>
    <p>${esc(role.tactical_summary || role.reasons.at(-1))}</p><ul>${role.reasons.slice(0,3).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>
    ${role.warnings.length ? `<p class="notice warning">${esc(role.warnings.join(' '))}</p>` : ''}
    <details><summary>Instrucciones individuales y alternativas</summary>${role.instructions.map(i=>{
      const statusBadge = i.availability_status === 'locked_verified' || i.locked
        ? (i.locked_value == null ? '<span class="inst-badge-masked">🔒 Bloqueado (tapado)</span>' : '<span class="inst-badge-lock">🔒 Bloqueado comprobado</span>')
        : (i.availability_status === 'editable_verified' || (i.editable && i.locked === false && i.availability_status !== 'unverified')
          ? '<span class="inst-badge-edit">⚙️ Editable comprobado</span>'
          : '<span class="inst-badge-unverified" title="Disponibilidad no verificada en FM (no comprobado en este contexto)">❓ Disponibilidad no verificada</span>');
      return `<article class="instruction"><strong>${esc(i.property)}: ${esc(i.value ?? 'No asignado')} ${statusBadge}</strong><p>${esc(i.reason)}</p><small>${esc(i.availability_source || '')}</small></article>`;
    }).join('')}
    ${role.unconfirmed_instructions?`<p class="muted">${role.unconfirmed_instructions} instrucciones de esta fase sin confirmar. Las que se muestran proceden de tu carga o de bloqueos comprobados del rol.</p>`:''}
    <p>${esc(role.comparison)}</p><p class="muted">${esc(role.spanish_status)}</p><a href="${esc(role.source)}" target="_blank" rel="noreferrer">Referencia del rol ↗</a></details></section>`;
}

export function pitch(tactic, phase, byId) {
  const key = phase === 'ip' ? 'in_possession' : 'out_of_possession';
  const adviceMap = new Map();
  if (Array.isArray(tactic?.advice)) {
    for (const a of tactic.advice) {
      if (a.player_uid) {
        const cur = adviceMap.get(a.player_uid);
        if (!cur || a.severity === 'danger' || (a.severity === 'warning' && cur !== 'danger') || (a.severity === 'purple' && cur !== 'danger' && cur !== 'warning')) {
          adviceMap.set(a.player_uid, a.severity);
        }
      }
    }
  }
  return `<div class="pitch" role="group" aria-label="Once ${phase === 'ip' ? 'con' : 'sin'} posesión"><div class="pitch-line"></div><div class="pitch-center"></div><div class="pitch-area top"></div><div class="pitch-area bottom"></div><span class="pitch-direction">↑ Dirección de ataque</span>
    ${tactic.lineup.map((l,index)=>{
      const p=byId.get(l.uid), role=l[key];
      const alertSev = adviceMap.get(l.uid);
      const dot = alertSev ? `<span class="pitch-alert-dot dot-${esc(alertSev)}" title="Ajuste táctico"></span>` : '';
      return `<button class="pitch-player ${role.position === 'GK' ? 'keeper' : ''}" data-player="${p.uid}" style="left:${l[phase][0]}%;top:${l[phase][1]}%" aria-label="${esc(p.name)}, ${esc(role.name)}, encaje ${number(role.score)}">${dot}<span class="shirt">${index+1}</span><strong>${esc(p.name.split(' ').slice(-1)[0])}</strong><small>${esc(role.role_abbrev)} · ${number(role.score,0)}</small></button>`;
    }).join('')}</div>`;
}

export function formationCards(tactics, selectedId) {
  return `<div class="formation-grid">${tactics.map((t,index)=>`<button class="formation-card ${selectedId===t.id?'selected':''}" id="formation-${t.id}" data-formation="${t.id}" aria-pressed="${selectedId===t.id}"><span class="eyebrow">${index+1}. ${index===0?'Mayor encaje':'Alternativa'}</span><div class="split"><strong>${esc(t.name)}</strong>${score(t.score)}</div><small>${esc(t.defensive)} sin posesión</small><p>${esc(t.idea)}</p></button>`).join('')}</div>`;
}

export const SUPPORT_SIDES = {
  'Overlap - Balanced': [],
  'Overlap - Left': ['left'],
  'Overlap - Right': ['right'],
  'Overlap - Both Flanks': ['left', 'right'],
  'Underlap - Balanced': [],
  'Underlap - Left': ['left'],
  'Underlap - Right': ['right'],
  'Underlap - Both Flanks': ['left', 'right'],
};

export function checkSupportRunsConflict(overlapVal, underlapVal) {
  const oSides = SUPPORT_SIDES[overlapVal] || [];
  const uSides = SUPPORT_SIDES[underlapVal] || [];
  return oSides.filter(s => uSides.includes(s));
}

export function instructions(tactic, data, prefs, draft = {}) {
  const pendingCount = Object.keys(draft).length;
  const currentUnderlap = draft.underlap_ip ?? prefs.overrides.underlap_ip ?? tactic.instructions.find(i => i.id === 'underlap_ip')?.value_en;
  const currentOverlap = draft.overlap_ip ?? prefs.overrides.overlap_ip ?? tactic.instructions.find(i => i.id === 'overlap_ip')?.value_en;
  const existingConflict = checkSupportRunsConflict(currentOverlap, currentUnderlap);

  const instruction = item => {
    const applied = prefs.overrides[item.id] ?? item.value_en;
    const selected = draft[item.id] ?? applied;
    const origin = Object.hasOwn(draft, item.id) ? 'Cambio pendiente'
      : prefs.overrides[item.id] ? 'Ajuste manual' : item.origin === 'prompt' ? 'Pedido aplicado' : 'Propuesta';

    const isOverlap = item.id === 'overlap_ip';
    const isUnderlap = item.id === 'underlap_ip';

    const helperNote = item.id === 'short_goalkeeper_distribution_oop'
      ? `<span class="inst-scope-tag">Presionar salida rival</span>`
      : item.id === 'dribbling_ip'
      ? `<span class="inst-scope-tag">Compartido: Avance / Último tercio</span>`
      : item.id === 'pressing_trap_oop'
      ? `<span class="inst-scope-tag">Compartido: Presión alta / Bloque medio</span>`
      : item.id === 'gk_distribution_ip'
      ? `<span class="inst-scope-tag">Destino colectivo único</span>`
      : '';

    const opts = (data.instruction_options[item.id] || []).map(option => {
      let disabled = false;
      let reasonMsg = '';
      if (isOverlap) {
        const conflict = checkSupportRunsConflict(option.value, currentUnderlap);
        if (conflict.length > 0) {
          disabled = true;
          reasonMsg = ` (Incompatible con desdoble interior en ${conflict.includes('left') && conflict.includes('right') ? 'ambas bandas' : conflict.includes('left') ? 'la izquierda' : 'la derecha'})`;
        }
      } else if (isUnderlap) {
        const conflict = checkSupportRunsConflict(currentOverlap, option.value);
        if (conflict.length > 0) {
          disabled = true;
          reasonMsg = ` (Incompatible con desdoble exterior en ${conflict.includes('left') && conflict.includes('right') ? 'ambas bandas' : conflict.includes('left') ? 'la izquierda' : 'la derecha'})`;
        }
      }
      return `<option value="${esc(option.value)}" ${option.value === selected ? 'selected' : ''} ${disabled ? 'disabled' : ''}>${esc(option.label)}${reasonMsg}</option>`;
    }).join('');

    return `<article class="instruction"><label for="override-${item.id}">${esc(item.property)} ${helperNote} <small>${origin}</small></label>
      <select id="override-${item.id}" data-override="${item.id}" data-applied="${esc(applied)}">${opts}</select>
      <p>${esc(item.reason)}</p></article>`;
  };
  return `<details class="panel"><summary>Instrucciones de equipo · ${tactic.instructions.length} ajustes</summary><p class="muted">Las etiquetas proceden del catálogo FM26; las elecciones y el índice de encaje son recomendaciones de Touchline.</p>
    ${existingConflict.length ? `<div class="notice warning" role="alert">
      <strong>⚠️ Incompatibilidad detectada en Carreras de apoyo:</strong>
      <p>Doblar por banda («${esc(currentOverlap)}») y Doblar por dentro («${esc(currentUnderlap)}») coinciden en ${existingConflict.includes('left') && existingConflict.includes('right') ? 'ambas bandas' : existingConflict.includes('left') ? 'la banda izquierda' : 'la banda derecha'}. En FM26 se excluyen en el mismo costado. Podés seleccionar una opción compatible en los selectores a continuación.</p>
    </div>` : ''}
    ${pendingCount ? `<p class="notice" data-pending-overrides role="status">Tenés ${pendingCount} ${pendingCount === 1 ? 'cambio sin aplicar' : 'cambios sin aplicar'}. Revisá los valores y pulsá “Aplicar ajustes” para actualizar la propuesta.</p>` : ''}
    <div class="instruction-grid">${['in_possession', 'out_of_possession'].map(phase => `<section><h3>${phase === 'in_possession' ? 'Con posesión' : 'Sin posesión'}</h3>${tactic.instructions.filter(item => item.phase === phase).map(instruction).join('')}</section>`).join('')}</div>
    <div class="actions"><button class="button primary" data-action="apply-overrides">Aplicar ajustes</button><button class="button" data-action="clear-overrides">Restablecer ajustes manuales</button></div></details>`;
}

export function tacticResult(tactic, state) {
  const {data, prefs, phase, byId} = state;
  const fit=tactic.fit_summary;
  return `<div class="result-heading"><div><span class="eyebrow">Propuesta para tu plantel</span><h2>${esc(tactic.name)} <span class="muted">→ ${esc(tactic.defensive)} sin posesión</span></h2><p>${esc(tactic.fm26_style)} · Mentalidad ${esc(tactic.fm26_mentality)}</p></div>${score(tactic.score)}</div>
    <div class="decision-strip"><span><strong>${fit.natural_count}/11</strong> con familiaridad alta</span><span><strong>${fit.weak_count}</strong> posiciones a revisar</span><span><strong>${fit.recalls_count}</strong> ${fit.recalls_count===1?'cedido como alternativa':'cedidos distintos como alternativas'}</span></div>
    <div class="tactical-layout"><section class="panel pitch-panel"><div class="split"><h3>Once propuesto</h3><div class="segmented" role="group" aria-label="Fase de juego"><button id="phase-ip" data-phase="ip" aria-pressed="${phase==='ip'}">Con posesión</button><button id="phase-oop" data-phase="oop" aria-pressed="${phase==='oop'}">Sin posesión</button></div></div>${pitch(tactic,phase,byId)}</section>
    <section class="panel"><h3>Jugador y función por puesto</h3><p class="muted">El puntaje del once combina 80 % con posesión y 20 % sin posesión. En la cancha se muestra el encaje de la fase elegida.</p><ol class="lineup">${tactic.lineup.map(l=>`<li><div>${playerButton(byId.get(l.uid))}<small>${esc(l[phase==='ip'?'in_possession':'out_of_possession'].name)} · familiaridad ${l.familiarity}/20</small></div>${score(l.score)}</li>`).join('')}</ol></section></div>
    ${zoneMap(tactic.coverage,phase)}
    <section class="panel"><h3>Decisiones para revisar</h3><p>${esc(fit.verdict)}</p>
    ${tactic.tactical_recommendations.length ? `<div class="advice-grid" style="margin: 16px 0;">${tactic.tactical_recommendations.map(a=>`
      <article class="advice-card severity-warning">
        <div class="advice-header">
          <span class="advice-badge badge-warning">⚠️ Ajuste de propuesta</span>
          <h4 class="advice-title">${esc(a.title)}</h4>
        </div>
        ${a.action ? `<div class="advice-action"><span class="advice-action-icon">⚡</span><div class="advice-action-text"><strong>Ajuste recomendado:</strong> <span>${esc(a.action)}</span></div></div>` : ''}
        <p class="advice-detail">${esc(a.detail)}</p>
      </article>`).join('')}</div>` : ''}
    ${tactic.reinforcements.map(r=>`
      <article class="reinforcement-card priority-${esc(r.urgency.toLowerCase())}">
        <div class="split">
          <div class="reinforcement-title-box">
            <span class="reinforcement-priority-badge ${r.urgency==='Alta'?'badge-danger':r.urgency==='Media'?'badge-warning':'badge-info'}">Prioridad ${esc(r.urgency)}</span>
            <h4>${esc(r.position_label)}</h4>
          </div>
        </div>
        <p class="reinforcement-issues">${esc(r.issues.join(' '))}</p>
        ${r.loan_recalls.length ? `
          <div class="recall-box">
            <div class="recall-box-header">
              <span class="recall-tag">⚡ RECOMENDACIÓN DE REPESCA:</span>
              <span class="window-general-tag">${esc(r.loan_recalls[0]?.window?.badge || 'Calendario FM')}</span>
            </div>
            ${r.loan_recalls.map(c=>{
              const win = c.window || {};
              return `
                <div class="recall-item">
                  <div class="recall-item-top">
                    <button class="text-button" data-player="${c.player_uid}"><strong>${esc(c.player_name)}</strong></button>
                    <span class="window-pill ${win.is_open ? 'window-open' : 'window-closed'}">${esc(win.badge || 'Ventana de fichajes')}</span>
                    <span class="score-pill">${number(c.score)} encaje</span>
                    <span class="match-pill">${c.appearances == null ? 'Sin PJ' : c.appearances+' PJ'}</span>
                    <span class="rating-pill">media ${number(c.rating,2)}</span>
                  </div>
                  ${win.return_countdown ? `<div class="recall-countdown"><small>📅 ${esc(win.return_countdown)}</small></div>` : ''}
                  ${win.status_text ? `<div class="recall-window-note"><small>ℹ️ ${esc(win.status_text)}</small></div>` : ''}
                </div>
              `;
            }).join('')}
            <div class="recall-guide-box">
              <span class="recall-guide-icon">💡</span>
              <small><strong>Atajo en FM:</strong> Perfil del jugador ➔ Menú 'Contrato' ➔ 'Repescar de cesión'. Si la opción está deshabilitada en el juego, la cesión no contempló repesca o la ventana está cerrada.</small>
            </div>
          </div>
        ` : `
          <div class="market-box">
            <span class="market-tag">🔍 BÚSQUEDA EN MERCADO / INFERIORES:</span>
            <p>${esc(r.market_profile?.scouting_note || 'Revisá las inferiores y el mercado.')}</p>
          </div>
        `}
        ${r.scout_targets && r.scout_targets.length ? `
          <div class="market-scout-box">
            <div class="scout-box-header">
              <span class="scout-tag">🎯 OBJETIVOS DE OJEO RECOMENDADOS EN TU PARTIDA:</span>
              <button class="text-button" data-view="scouting" data-scout-pos="${esc(r.position)}">Ver en Ojeo →</button>
            </div>
            <div class="scout-targets-list">
              ${r.scout_targets.map(st=>`
                <div class="scout-target-card">
                  <div class="scout-target-main">
                    <strong>${esc(st.name)}</strong>
                    <span class="scout-sub">${st.age} años · ${esc(st.club_name)}</span>
                  </div>
                  <div class="scout-target-meta">
                    <span class="role-badge-subtle">${esc(st.best_role)}</span>
                    <span class="score-pill">${number(st.score)} encaje</span>
                    ${st.wage ? `<span class="wage-pill">€${number(st.wage)}/sem</span>` : ''}
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </article>
    `).join('')}
    <details><summary>Riesgos y límites de la propuesta</summary><ul>${tactic.risks.map(r=>`<li>${esc(r)}</li>`).join('')}</ul><p>Confirmá lesiones, sanciones, inscripción, carga de partidos y el rival dentro de FM.</p></details></section>
    <section class="panel"><h3>Banco y cobertura</h3><p class="muted">Hasta nueve suplentes, priorizando arquero y cobertura del once. Las diferencias se calculan para el mismo puesto y ambas fases.</p><div class="table-scroll"><table><thead><tr><th scope="col">Jugador</th><th scope="col">Mejor reemplazo</th><th scope="col">Encaje en el puesto</th><th scope="col">Diferencia</th><th scope="col">Evaluación</th></tr></thead><tbody>${tactic.bench_replacements.map(b=>`<tr><td>${playerButton(byId.get(b.uid))}</td><td>${esc(b.replaces_name)}<small>${esc(b.replaces_role)}</small></td><td>${number(b.replacement_score)}</td><td>${b.gap==null?'—':`${b.gap>0?'+':''}${number(b.gap)}`}</td><td>${esc(b.quality_label)}</td></tr>`).join('')}</tbody></table></div></section>
    ${instructions(tactic,data,prefs,state.overrideDraft)}`;
}
