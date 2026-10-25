import {esc, number, score, playerButton, pos} from './format.js';
import {zoneMap} from './zones-view.js';

export function rolePlan(role) {
  return `<section class="role-plan"><div class="split"><div><span class="eyebrow">${role.phase === 'in_possession' ? 'Con posesión' : 'Sin posesión'} · ${esc(pos(role.position))}</span><h3>${esc(role.name)}</h3><small>${esc(role.english)}</small></div>${score(role.score)}</div>
    <p>${esc(role.tactical_summary || role.reasons.at(-1))}</p><ul>${role.reasons.slice(0,3).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>
    ${role.warnings.length ? `<p class="notice warning">${esc(role.warnings.join(' '))}</p>` : ''}
    <details><summary>Instrucciones individuales y alternativas</summary>${role.instructions.map(i=>`<article class="instruction"><strong>${esc(i.property)}: ${esc(i.value)} ${i.locked ? '· Bloqueada por el rol' : ''}</strong><p>${esc(i.reason)}</p><small>${esc(i.availability_source || '')}</small></article>`).join('')}
    ${role.unconfirmed_instructions?`<p class="muted">${role.unconfirmed_instructions} instrucciones de esta fase sin confirmar. Las que se muestran proceden de tu carga o de bloqueos comprobados del rol.</p>`:''}
    <p>${esc(role.comparison)}</p><p class="muted">${esc(role.spanish_status)}</p><a href="${esc(role.source)}" target="_blank" rel="noreferrer">Referencia del rol ↗</a></details></section>`;
}

export function pitch(tactic, phase, byId) {
  const key = phase === 'ip' ? 'in_possession' : 'out_of_possession';
  return `<div class="pitch" role="group" aria-label="Once ${phase === 'ip' ? 'con' : 'sin'} posesión"><div class="pitch-line"></div><div class="pitch-center"></div><div class="pitch-area top"></div><div class="pitch-area bottom"></div><span class="pitch-direction">↑ Dirección de ataque</span>
    ${tactic.lineup.map((l,index)=>{const p=byId.get(l.uid), role=l[key]; return `<button class="pitch-player ${role.position === 'GK' ? 'keeper' : ''}" data-player="${p.uid}" style="left:${l[phase][0]}%;top:${l[phase][1]}%" aria-label="${esc(p.name)}, ${esc(role.name)}, encaje ${number(role.score)}"><span class="shirt">${index+1}</span><strong>${esc(p.name.split(' ').slice(-1)[0])}</strong><small>${esc(role.role_abbrev)} · ${number(role.score,0)}</small></button>`;}).join('')}</div>`;
}

export function formationCards(tactics, selectedId) {
  return `<div class="formation-grid">${tactics.map((t,index)=>`<button class="formation-card ${selectedId===t.id?'selected':''}" id="formation-${t.id}" data-formation="${t.id}" aria-pressed="${selectedId===t.id}"><span class="eyebrow">${index+1}. ${index===0?'Mayor encaje':'Alternativa'}</span><div class="split"><strong>${esc(t.name)}</strong>${score(t.score)}</div><small>${esc(t.defensive)} sin posesión</small><p>${esc(t.idea)}</p></button>`).join('')}</div>`;
}

export function instructions(tactic, data, prefs, draft = {}) {
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
}

export function tacticResult(tactic, state) {
  const {data, prefs, phase, byId} = state;
  const fit=tactic.fit_summary;
  return `<div class="result-heading"><div><span class="eyebrow">Propuesta para tu plantel</span><h2>${esc(tactic.name)} <span class="muted">→ ${esc(tactic.defensive)} sin posesión</span></h2><p>${esc(tactic.fm26_style)} · Mentalidad ${esc(tactic.fm26_mentality)}</p></div>${score(tactic.score)}</div>
    <div class="decision-strip"><span><strong>${fit.natural_count}/11</strong> con familiaridad alta</span><span><strong>${fit.weak_count}</strong> posiciones a revisar</span><span><strong>${fit.recalls_count}</strong> ${fit.recalls_count===1?'cedido como alternativa':'cedidos distintos como alternativas'}</span></div>
    <div class="tactical-layout"><section class="panel pitch-panel"><div class="split"><h3>Once propuesto</h3><div class="segmented" role="group" aria-label="Fase de juego"><button id="phase-ip" data-phase="ip" aria-pressed="${phase==='ip'}">Con posesión</button><button id="phase-oop" data-phase="oop" aria-pressed="${phase==='oop'}">Sin posesión</button></div></div>${pitch(tactic,phase,byId)}</section>
    <section class="panel"><h3>Jugador y función por puesto</h3><p class="muted">El puntaje del once combina 80 % con posesión y 20 % sin posesión. En la cancha se muestra el encaje de la fase elegida.</p><ol class="lineup">${tactic.lineup.map(l=>`<li><div>${playerButton(byId.get(l.uid))}<small>${esc(l[phase==='ip'?'in_possession':'out_of_possession'].name)} · familiaridad ${l.familiarity}/20</small></div>${score(l.score)}</li>`).join('')}</ol></section></div>
    ${zoneMap(tactic.coverage,phase)}
    <section class="panel"><h3>Decisiones para revisar</h3><p>${esc(fit.verdict)}</p>${tactic.tactical_recommendations.map(a=>`<p class="notice warning"><strong>${esc(a.title)}.</strong> ${esc(a.detail)}</p>`).join('')}
    ${tactic.reinforcements.map(r=>`<article class="reinforcement"><div class="split"><h4>${esc(r.position_label)}</h4><span class="tag">Prioridad ${esc(r.urgency.toLowerCase())}</span></div><p>${esc(r.issues.join(' '))}</p>${r.loan_recalls.length ? r.loan_recalls.map(c=>`<p><button class="text-button" data-player="${c.player_uid}">${esc(c.player_name)}</button> · ${number(c.score)} de encaje en este puesto. ${c.appearances == null ? 'Partidos sin verificar' : c.appearances+' PJ'} · media ${number(c.rating,2)}.</p>`).join('') + '<p class="muted">Alternativas sujetas a cláusulas, fechas, costos e inscripción en FM. Cada jugador puede cubrir un puesto a la vez.</p>' : `<p>${esc(r.market_profile?.scouting_note || 'Revisá las inferiores y el mercado.')}</p>`}</article>`).join('')}
    <details><summary>Riesgos y límites de la propuesta</summary><ul>${tactic.risks.map(r=>`<li>${esc(r)}</li>`).join('')}</ul><p>Confirmá lesiones, sanciones, inscripción, carga de partidos y el rival dentro de FM.</p></details></section>
    <section class="panel"><h3>Banco y cobertura</h3><p class="muted">Hasta nueve suplentes, priorizando arquero y cobertura del once. Las diferencias se calculan para el mismo puesto y ambas fases.</p><div class="table-scroll"><table><thead><tr><th scope="col">Jugador</th><th scope="col">Mejor reemplazo</th><th scope="col">Encaje en el puesto</th><th scope="col">Diferencia</th><th scope="col">Evaluación</th></tr></thead><tbody>${tactic.bench_replacements.map(b=>`<tr><td>${playerButton(byId.get(b.uid))}</td><td>${esc(b.replaces_name)}<small>${esc(b.replaces_role)}</small></td><td>${number(b.replacement_score)}</td><td>${b.gap==null?'—':`${b.gap>0?'+':''}${number(b.gap)}`}</td><td>${esc(b.quality_label)}</td></tr>`).join('')}</tbody></table></div></section>
    ${instructions(tactic,data,prefs,state.overrideDraft)}`;
}
