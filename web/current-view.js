import {esc,number,score,pos} from './format.js';
import {rolePlan,pitch,checkSupportRunsConflict} from './tactics-view.js';
import {zoneMap} from './zones-view.js';
import {matchesObservedContext} from './instruction-context.js';

export function reconcileCurrentDraft(data,saved) {
  if(!saved||!Array.isArray(saved.lineup)||saved.lineup.length!==11)return data.club==='Liverpool'?referenceDraft(data):freshDraft(data);
  const base=freshDraft(data,saved.formation),editor=data.tactic_editor;
  const ids=new Set(data.players.map(p=>p.uid));
  base.name=typeof saved.name==='string'?saved.name.slice(0,100):base.name;
  base.style=data.styles[saved.style]?saved.style:'possession';
  base.stored_id=data.stored_tactics.records.some(r=>r.id===saved.stored_id)?saved.stored_id:'';
  const savedTeam = saved.team && Object.keys(saved.team).length ? saved.team : (data.liverpool_reference?.team || {});
  base.team=Object.fromEntries(Object.entries(savedTeam).filter(([id,v])=>data.instruction_options[id]?.some(o=>o.value===v)));
  base.lineup=base.lineup.map((row,index)=>{
    const old=saved.lineup[index]||{};row.uid=ids.has(old.uid)?old.uid:'';
    for(const phase of ['ip','oop']) {
      if(editor.positions.includes(old[phase+'_position']))row[phase+'_position']=old[phase+'_position'];
      const role=editor.roles[old[phase+'_role']];
      if(role?.phase===(phase==='ip'?'in_possession':'out_of_possession')&&role.positions.includes(row[phase+'_position']))row[phase+'_role']=old[phase+'_role'];
    }
    row.instruction_scope = old.instruction_scope || 'Posición';
    row.marking_target_player = old.marking_target_player || '';
    row.marking_target_position = old.marking_target_position || '';
    row.instructions=Object.fromEntries(Object.entries(old.instructions||{}).filter(([id,v])=>editor.player_options[id]?.options.some(o=>o.value===v)));
    return row;
  });
  return base;
}

export function freshDraft(data,formation='433') {
  const form=data.tactic_editor.formations.find(f=>f.id===formation)||data.tactic_editor.formations[0];
  return {formation:form.id,name:'Mi táctica',stored_id:'',style:'possession',confirmed:false,team:{},
    lineup:form.slots.map(slot=>({uid:'',ip_position:slot.ip_position,oop_position:slot.oop_position,ip_role:'',oop_role:'',instruction_scope:'Posición',marking_target_player:'',marking_target_position:'',instructions:{}}))};
}

const standard={attacking_width_ip:'Standard',dribbling_direction_ip:'Standard',dribbling_frequency_ip:'Standard',forward_runs_ip:'Standard',freedom_of_movement_ip:'Follow Tactical Position',hold_up_ball_ip:'No',shoot_ip:'Standard',passing_risk_ip:'Standard',passing_directness_ip:'Standard',cross_from_ip:'Standard',crossing_strategy_ip:'Standard',pressing_oop:'Standard',marking_oop:'Standard',tackling_oop:'Standard',marking_target_oop:'Standard'};
const references=[
  {match:'verbruggen',ip:'ball_playing_goalkeeper_ip',oop:'sweeper_keeper_oop',ip_position:'GK',oop_position:'GK',instructions:{passing_risk_ip:'Take More Risks'}},
  {match:'cubarsi',ip:'ball_playing_centre_back_ip',oop:'centre_back_oop',ip_position:'DC',oop_position:'DC',instructions:{forward_runs_ip:'Make Fewer Runs',passing_risk_ip:'Take More Risks',passing_directness_ip:'Shorter',pressing_oop:'More Often',marking_oop:'Mark Tighter',tackling_oop:'Tackle Harder'}},
  {match:'spence',ip:'wing_back_ip',oop:'full_back_oop',ip_position:'DR',oop_position:'DR',instructions:{forward_runs_ip:'Make More Runs',passing_directness_ip:'Shorter'}},
  {match:'wharton',ip:'midfield_playmaker_ip',oop:'attacking_midfielder_oop',ip_position:'MC',oop_position:'AMC',instructions:{freedom_of_movement_ip:'Roam From Position',passing_risk_ip:'Take More Risks',passing_directness_ip:'Shorter'}},
  {match:'szoboszlai',ip:'inside_winger_ip',oop:'wide_midfielder_oop',ip_position:'AMR',oop_position:'MR',instructions:{attacking_width_ip:'Sit Narrower',dribbling_direction_ip:'Cut Inside With Ball',dribbling_frequency_ip:'Dribble More',forward_runs_ip:'Make More Runs',freedom_of_movement_ip:'Roam From Position'}},
  {match:'kerkez',ip:'wing_back_ip',oop:'full_back_oop',ip_position:'DL',oop_position:'DL',instructions:{forward_runs_ip:'Make More Runs',passing_directness_ip:'Shorter',pressing_oop:'More Often',marking_oop:'Mark Tighter'}},
  {match:'vuskovic',ip:'centre_back_ip',oop:'centre_back_oop',ip_position:'DC',oop_position:'DC',instructions:{forward_runs_ip:'Make Fewer Runs',passing_directness_ip:'Shorter',pressing_oop:'More Often',marking_oop:'Mark Tighter',tackling_oop:'Tackle Harder'}},
  {match:'pavlovic',ip:'deep_lying_playmaker_ip',oop:'defensive_midfielder_oop',ip_position:'DM',oop_position:'DM',instructions:{forward_runs_ip:'Make Fewer Runs',passing_risk_ip:'Take More Risks',passing_directness_ip:'Shorter'}},
  {match:'ayari',ip:'advanced_playmaker_ip',oop:'defensive_midfielder_oop',ip_position:'MC',oop_position:'DM',instructions:{forward_runs_ip:'Make Fewer Runs',freedom_of_movement_ip:'Roam From Position',passing_risk_ip:'Take More Risks',passing_directness_ip:'Shorter',marking_oop:'Mark Tighter',tackling_oop:'Tackle Harder'}},
  {match:'wirtz',ip:'inside_winger_ip',oop:'wide_midfielder_oop',ip_position:'AML',oop_position:'ML',instructions:{attacking_width_ip:'Sit Narrower',dribbling_direction_ip:'Cut Inside With Ball',freedom_of_movement_ip:'Roam From Position',shoot_ip:'Shoot More Often'}},
  {match:'ekitike',ip:'deep_lying_forward_ip',oop:'centre_forward_oop',ip_position:'STC',oop_position:'STC',instructions:{freedom_of_movement_ip:'Roam From Position',hold_up_ball_ip:'Yes',shoot_ip:'Shoot More Often',pressing_oop:'More Often',tackling_oop:'Tackle Harder'}}
];
function normalized(value){return value.normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();}
function find(data,part){return data.players.find(p=>normalized(p.name).includes(part));}

export function referenceDraft(data) {
  const draft=freshDraft(data);
  const refList=(data.liverpool_reference?.lineup)||references;
  const names=['verbruggen','kerkez','cubarsi','vuskovic','spence','pavlovic','ayari','wharton','wirtz','ekitike','szoboszlai'];
  draft.lineup.forEach((row,index)=>{
    const ref=refList.find(r=>r.match===names[index])||refList[index];
    if(!ref)return;
    const player=find(data,ref.match);row.uid=player?.uid||'';
    if(player)Object.assign(row,{ip_position:ref.ip_position,oop_position:ref.oop_position,ip_role:ref.ip_role||ref.ip,oop_role:ref.oop_role||ref.oop,instruction_scope:ref.instruction_scope||'Posición',marking_target_player:ref.marking_target_player||'',marking_target_position:ref.marking_target_position||'',instructions:{...standard,...(ref.instructions||{})}});
  });
  if(data.liverpool_reference?.team) {
    draft.team = {...data.liverpool_reference.team};
  }
  const saved=data.stored_tactics?.records?.find(t=>t.team_slot===data.default_primary_slot);
  if(saved){draft.stored_id=saved.id;draft.name=saved.name;}
  return draft;
}

function captureReview(data) {
  return `<section class="panel capture-review">
    <div class="split">
      <div>
        <span class="eyebrow">Diagnóstico táctico de tu equipo</span>
        <h2>Revisá tu once y detectá mejoras inmediatas</h2>
        <p class="muted">Confirmá o ajustá tus 11 titulares para evaluar la estructura con posesión y sin posesión con el motor de análisis de Touchline.</p>
      </div>
      <button class="button primary" data-action="reference-current">⚡ Cargar y revisar táctica activa</button>
    </div>
  </section>`;
}

function renderAdviceCard(a) {
  const sev = a.severity || 'warning';
  const badge = a.badge || (sev==='danger'?'🔴 Alerta crítica':sev==='warning'?'🟡 Ajuste táctico':'🔵 Recomendación');
  return `<article class="advice-card severity-${esc(sev)}">
    <div class="advice-header">
      <span class="advice-badge badge-${esc(sev)}">${esc(badge)}</span>
      <h4 class="advice-title">${esc(a.title)}</h4>
    </div>
    ${a.action ? `<div class="advice-action"><span class="advice-action-icon">⚡</span><div class="advice-action-text"><strong>Ajuste recomendado en FM:</strong> <span>${esc(a.action)}</span></div></div>` : ''}
    ${Array.isArray(a.chips) && a.chips.length ? `<div class="advice-chips">${a.chips.map(c=>`<span class="advice-chip ${c.includes('baja')||c.includes('7/20')||c.includes('MPC')?'alert':''}">${esc(c)}</span>`).join('')}</div>` : ''}
    <p class="advice-detail">${esc(a.detail)}</p>
  </article>`;
}

export function renderDynamicChecklist(result, state) {
  const actionItems = (result.advice || []).filter(a => a.action);
  if (!actionItems.length) {
    return `
      <div class="match-checklist-card">
        <div class="checklist-header">
          <div class="checklist-title-box">
            <span class="checklist-icon">✓</span>
            <div>
              <h4>Once equilibrado en FM26</h4>
              <small class="checklist-subtitle">No se detectaron alertas críticas ni ajustes necesarios para este once.</small>
            </div>
          </div>
          <div class="checklist-status-pill status-ready"><span>0 pendientes</span></div>
        </div>
        <div class="checklist-actions-bar">
          <button type="button" class="button primary" data-action="companion">⚡ Guía para FM</button>
          <button type="button" class="button" data-action="copy-match-instructions">📋 Copiar ajustes</button>
        </div>
      </div>
    `;
  }

  const savedKeys = [];
  actionItems.forEach((item, idx) => {
    const key = (item.player_uid || 'team') + '_' + (item.category || item.title || idx);
    try {
      if (localStorage.getItem('touchline:chk:' + key) === '1') savedKeys.push(key);
    } catch {}
  });

  const allChecked = (savedKeys.length === actionItems.length);

  return `
    <div class="match-checklist-card">
      <div class="checklist-header">
        <div class="checklist-title-box">
          <span class="checklist-icon">📋</span>
          <div>
            <h4>Ajustes prioritarios para FM</h4>
            <small class="checklist-subtitle">Marcá los ajustes aplicados en la pantalla táctica de FM26.</small>
          </div>
        </div>
        <div class="checklist-status-pill ${allChecked ? 'status-ready' : 'status-pending'}">
          <span id="checklist-counter">${savedKeys.length} de ${actionItems.length} aplicados por vos</span>
        </div>
      </div>

      <div class="checklist-items">
        ${actionItems.map((item, idx) => {
          const key = (item.player_uid || 'team') + '_' + (item.category || item.title || idx);
          const isDone = savedKeys.includes(key);
          const phaseBadge = item.phase === 'ip' ? '<span class="phase-badge phase-cp">CP · Con posesión</span>' : item.phase === 'oop' ? '<span class="phase-badge phase-sp">SP · Sin posesión</span>' : '<span class="phase-badge">Equipo</span>';
          return `
            <label class="checklist-item ${isDone ? 'checked' : ''}" data-audit-item="${esc(key)}">
              <input type="checkbox" id="check-audit-${idx}" data-audit-check="${esc(key)}" ${isDone ? 'checked' : ''}>
              <span class="check-box-custom"></span>
              <div class="check-text">
                <div class="check-top-line">
                  <span class="check-player-title"><strong>${esc(item.player_name || 'Ajuste colectivo')}</strong> · ${phaseBadge}</span>
                  <span class="check-state-badge ${isDone ? 'state-done' : 'state-pending'}">${isDone ? '✓ Marcado como aplicado' : 'Pendiente en FM'}</span>
                </div>
                <span class="check-action-desc">${esc(item.action)}</span>
              </div>
            </label>
          `;
        }).join('')}
      </div>

      <div class="checklist-complete-banner" id="checklist-complete-banner" ${allChecked ? '' : 'hidden'}>
        <span class="complete-icon">✓</span>
        <div>
          <strong>${actionItems.length} ajustes marcados como aplicados en tu partida</strong>
          <p>Ya completaste los ajustes tácticos registrados. Continuá tu partido dentro de Football Manager.</p>
        </div>
      </div>

      <div class="checklist-actions-bar">
        <button type="button" class="button primary" data-action="companion">⚡ Guía para FM</button>
        <button type="button" class="button" data-action="copy-match-instructions">📋 Copiar ajustes</button>
      </div>
    </div>
  `;
}

function renderGroupedAdvice(result, state) {
  if (!result.advice || !result.advice.length) {
    return '<div class="advice-card severity-success"><div class="advice-header"><span class="advice-badge badge-success">✅ Todo en orden</span><h4 class="advice-title">Estructura equilibrada</h4></div><p class="advice-detail">No se detectaron alertas con las reglas disponibles. Confirmá las órdenes pendientes y observá la táctica en partidos.</p></div>';
  }

  const playerMap = new Map();
  const teamItems = [];

  for (const a of result.advice) {
    if (a.player_uid) {
      if (!playerMap.has(a.player_uid)) {
        playerMap.set(a.player_uid, {
          uid: a.player_uid,
          name: a.player_name || state.byId.get(a.player_uid)?.name || 'Jugador',
          player: state.byId.get(a.player_uid),
          slot: result.lineup.find(l => l.uid === a.player_uid),
          items: []
        });
      }
      playerMap.get(a.player_uid).items.push(a);
    } else {
      teamItems.push(a);
    }
  }

  let html = '';

  if (teamItems.length) {
    html += `
      <div class="section-heading-visual" style="margin-top: 14px;">
        <h3>Estructura colectiva y zaga</h3>
        <span class="badge-count">${teamItems.length} ajustes de equipo</span>
      </div>
      <div class="advice-grid">
        ${teamItems.map(renderAdviceCard).join('')}
      </div>
    `;
  }

  if (playerMap.size) {
    html += `
      <div class="section-heading-visual" style="margin-top: 20px;">
        <h3>Ajustes individuales agrupados por jugador</h3>
        <span class="badge-count">${playerMap.size} jugadores con recomendaciones</span>
      </div>
      <div class="player-advice-grid">
        ${Array.from(playerMap.values()).map(g => {
          const slot = g.slot;
          const slotIndex = slot ? result.lineup.indexOf(slot) : -1;
          const hasDanger = g.items.some(i => i.severity === 'danger');
          const hasWarning = g.items.some(i => i.severity === 'warning');
          const badgeClass = hasDanger ? 'badge-danger' : hasWarning ? 'badge-warning' : 'badge-info';
          const cardClass = hasDanger ? 'severity-danger' : hasWarning ? 'severity-warning' : 'severity-info';

          return `
            <article class="player-grouped-card ${cardClass}" id="player-advice-${g.uid}">
              <div class="player-grouped-header">
                <div class="player-grouped-identity">
                  <span class="player-shirt-circle">${slotIndex >= 0 ? slotIndex + 1 : '•'}</span>
                  <div>
                    <h4 class="player-name">${esc(g.name)}</h4>
                    <small class="player-positions-line">
                      ${slot ? `CP: <strong>${esc(pos(slot.in_possession?.position))}</strong> · SP: <strong>${esc(pos(slot.out_of_possession?.position))}</strong>` : ''}
                    </small>
                  </div>
                </div>
                <span class="advice-badge ${badgeClass}">${g.items.length} ${g.items.length === 1 ? 'ajuste' : 'ajustes'}</span>
              </div>

              <div class="player-alerts-list">
                ${g.items.map(item => `
                  <div class="player-alert-item severity-${esc(item.severity)}">
                    <div class="alert-phase-row">
                      <span class="phase-pill ${item.phase === 'ip' ? 'pill-cp' : item.phase === 'oop' ? 'pill-sp' : 'pill-both'}">
                        ${item.phase === 'ip' ? 'CP · Con posesión' : item.phase === 'oop' ? 'SP · Sin posesión' : 'Ambas fases'}
                      </span>
                      <span class="alert-type-badge">${esc(item.badge)}</span>
                    </div>
                    <div class="advice-action">
                      <span class="advice-action-icon">⚡</span>
                      <div class="advice-action-text"><strong>Ajuste recomendado en FM:</strong> <span>${esc(item.action)}</span></div>
                    </div>
                    ${Array.isArray(item.chips) && item.chips.length ? `
                      <div class="advice-chips">${item.chips.map(c => `<span class="advice-chip ${c.includes('baja') || c.includes('7/20') || c.includes('MPC') ? 'alert' : ''}">${esc(c)}</span>`).join('')}</div>
                    ` : ''}
                    <p class="advice-detail">${esc(item.detail)}</p>
                  </div>
                `).join('')}
              </div>
            </article>
          `;
        }).join('')}
      </div>
    `;
  }

  return html;
}

function options(items,selected,blank='Sin confirmar') {
  return `<option value="">${blank}</option>${items.map(o=>`<option value="${esc(o.value)}" ${String(o.value)===String(selected)?'selected':''}>${esc(o.label)}</option>`).join('')}`;
}

export function currentView(state) {
  const {data,currentDraft:d,currentResult:result}=state,editor=data.tactic_editor;
  if(!editor||!d)return '<h1>Mi táctica</h1><p>Volvé a cargar la aplicación.</p>';
  const stored=data.stored_tactics||{records:[]};
  const phaseKey=state.phase==='ip'?'in_possession':'out_of_possession';
  return `<div class="page-heading">
    <div>
      <span class="eyebrow">Tu once en FM26 · Revisión táctica</span>
      <h1>Mi táctica</h1>
      <p>Evaluación de encaje y ajustes prioritarios para tu once titular actual.</p>
    </div>
    <div class="actions">
      <button class="button primary" data-action="companion">⚡ Guía para FM</button>
      <button class="button" data-action="copy-match-instructions">📋 Copiar ajustes</button>
      <button class="button" data-action="reference-current">⚡ Cargar táctica guardada</button>
      ${result?'<button class="button" data-action="export-current">Exportar revisión</button>':''}
    </div>
  </div>

  ${!result ? captureReview(data) : ''}

  ${result ? `
    <section class="panel current-summary-panel" id="current-result">
      <div class="split">
        <div>
          <span class="eyebrow">Once titular confirmado</span>
          <h2 tabindex="-1">Revisión de ${esc(result.name)}</h2>
          <small class="muted">Estilo de referencia: ${esc(data.styles[result.style]?.name || result.style)}</small>
        </div>
        ${score(result.score)}
      </div>
      <div class="status-summary-strip">
        <span class="status-pill ${result.unconfirmed_player_instructions===0?'pill-ok':'pill-pending'}">
          ${result.unconfirmed_player_instructions===0?'✓ Órdenes individuales confirmadas':`⚠ ${result.unconfirmed_player_instructions} órdenes individuales sin confirmar`}
        </span>
        <span class="status-pill ${result.unconfirmed_team_instructions===0?'pill-ok':'pill-pending'}">
          ${result.unconfirmed_team_instructions===0?'✓ Órdenes colectivas confirmadas':`⚠ ${result.unconfirmed_team_instructions} órdenes colectivas sin confirmar`}
        </span>
      </div>
      <p class="muted" style="margin: 8px 0 0;"><small>${esc(result.limits)}</small></p>
    </section>

    <div class="current-main-grid">
      <section class="panel current-pitch-panel">
        <div class="split">
          <h2>Tu once en cancha</h2>
          <div class="segmented" role="group" aria-label="Fase táctica">
            <button data-phase="ip" aria-pressed="${state.phase==='ip'}">Con posesión (CP)</button>
            <button data-phase="oop" aria-pressed="${state.phase==='oop'}">Sin posesión (SP)</button>
          </div>
        </div>
        ${pitch(result,state.phase,state.byId)}
      </section>

      <section class="panel current-priorities-panel">
        ${renderDynamicChecklist(result, state)}
      </section>
    </div>

    ${result.advice && result.advice.length ? `
      <details class="panel current-details-panel">
        <summary>🔍 Ver todas las alertas y ajustes detallados (${result.advice.length})</summary>
        ${renderGroupedAdvice(result, state)}
      </details>
    ` : ''}

    ${zoneMap(result.coverage,state.phase)}

    <details class="panel">
      <summary>🔄 Ajustes de función por puesto (${result.lineup.length} jugadores)</summary>
      ${result.lineup.map(slot=>`<details><summary>${esc(state.byId.get(slot.uid).name)} · ${esc(slot[phaseKey].name)} · ${number(slot[phaseKey].score)}</summary>${rolePlan(slot[phaseKey])}<p>Alternativas por atributos, no sustituciones automáticas:</p><ul>${slot[phaseKey].alternatives.map(a=>`<li>${esc(a.name)} · ${number(a.score)}</li>`).join('')}</ul></details>`).join('')}
    </details>
  ` : ''}

  <details class="panel" id="current-editor-accordion" ${!result ? 'open' : ''}>
    <summary>⚙️ Modificar alineación, puestos y roles manualmente (${d.lineup.filter(x=>x.uid).length}/11 titulares)</summary>
    <p class="notice">${esc(stored.limitations||'La táctica activa y sus roles necesitan confirmación.')}</p>
    <div class="control-grid">
      <label>Copia guardada<select id="current-stored" data-current="stored_id">${options(stored.records.map(t=>({value:t.id,label:`${t.name} · ${data.slot_labels[t.team_slot]||'Grupo '+t.team_slot} · ${t.mentality}`})),d.stored_id,'Carga manual')}</select></label>
      <label>Nombre<input id="current-name" data-current="name" value="${esc(d.name)}" maxlength="100"></label>
      <label>Plantilla inicial de posiciones <small>Aplicarla reemplaza posiciones, roles e instrucciones; conserva los jugadores por fila.</small><select id="current-formation" data-current="formation">${data.formations_catalog.map(f=>`<option value="${f.id}" ${d.formation===f.id?'selected':''}>${esc(f.name)} → ${esc(f.defensive)}</option>`).join('')}</select></label>
      <label>Objetivo para comparar el encaje<select id="current-style" data-current="style">${Object.entries(data.styles).map(([id,s])=>`<option value="${id}" ${d.style===id?'selected':''}>${esc(s.name)}</option>`).join('')}</select></label>
    </div>
    <p class="muted">La plantilla facilita cargar las posiciones: no demuestra la formación del guardado. Las filas mantienen la identidad del jugador entre fases. Wharton queda como mediapunta sin balón en tu referencia confirmada. Completá los roles faltantes según tu juego; no se reemplazan por los de mayor puntaje.</p>
    <div class="current-lineup">${d.lineup.map((row,index)=>{
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

              if (matchesObservedContext(ctx, d.lineup, index, phase)) {
                if (id in ctx.locked_values) {
                  isDisabled = true;
                  const lockedVal = ctx.locked_values[id];
                  if (lockedVal === null) {
                    lockBadge = '<span class="inst-badge-masked" title="Tapado por ayuda emergente en captura de FM26">🔒 Bloqueado (valor tapado)</span>';
                    selectedVal = null;
                  } else {
                    selectedVal = lockedVal;
                    titleAttr = `title="Bloqueado comprobado por el rol en FM26 (${ctx.evidence})"`;
                    lockBadge = `<span class="inst-badge-lock" ${titleAttr}>🔒 Bloqueado comprobado</span>`;
                  }
                } else if (ctx.editable_groups?.includes(id)) {
                  titleAttr = `title="Editable comprobado en FM26 (${ctx.evidence})"`;
                  lockBadge = `<span class="inst-badge-edit" ${titleAttr}>⚙️ Editable comprobado</span>`;
                } else {
                  titleAttr = 'title="Disponibilidad no verificada en FM para este contexto específico (edición permitida en borrador)"';
                  lockBadge = `<span class="inst-badge-unverified" ${titleAttr}>❓ Disponibilidad no verificada</span>`;
                }
              } else {
                titleAttr = 'title="Disponibilidad no verificada para este puesto, costado y ámbito (edición permitida en borrador)"';
                lockBadge = `<span class="inst-badge-unverified" ${titleAttr}>❓ Disponibilidad no verificada</span>`;
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
                const k = `${entry.phase === 'CP' ? '⚽ Con posesión' : '🛡️ Sin posesión'} · ${entry.area}`;
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

      ${(() => {
        const curOverlap = d.team['overlap_ip'];
        const curUnderlap = d.team['underlap_ip'];
        const conflict = checkSupportRunsConflict(curOverlap, curUnderlap);
        if (conflict.length > 0) {
          return `<div class="notice warning" role="alert" style="margin-bottom: 14px;">
            <strong>⚠️ Incompatibilidad detectada en Carreras de apoyo:</strong>
            <p>Doblar por banda («${esc(curOverlap)}») y Doblar por dentro («${esc(curUnderlap)}») coinciden en ${conflict.includes('left') && conflict.includes('right') ? 'ambas bandas' : conflict.includes('left') ? 'la banda izquierda' : 'la banda derecha'}. En FM26 se excluyen en el mismo costado. Podés seleccionar una opción compatible en los selectores a continuación.</p>
          </div>`;
        }
        return '';
      })()}

      <div class="instruction-grid">
        ${Object.entries(data.instruction_options).map(([id, opts]) => {
          const isOverlap = id === 'overlap_ip';
          const isUnderlap = id === 'underlap_ip';
          const curOverlap = d.team['overlap_ip'];
          const curUnderlap = d.team['underlap_ip'];
          const filteredOpts = opts.map(o => {
            let disabled = false;
            let reasonMsg = '';
            if (isOverlap) {
              const conflict = checkSupportRunsConflict(o.value, curUnderlap);
              if (conflict.length > 0) {
                disabled = true;
                reasonMsg = ` (Incompatible con interior en ${conflict.includes('left') && conflict.includes('right') ? 'ambas bandas' : conflict.includes('left') ? 'la izquierda' : 'la derecha'})`;
              }
            } else if (isUnderlap) {
              const conflict = checkSupportRunsConflict(curOverlap, o.value);
              if (conflict.length > 0) {
                disabled = true;
                reasonMsg = ` (Incompatible con exterior en ${conflict.includes('left') && conflict.includes('right') ? 'ambas bandas' : conflict.includes('left') ? 'la izquierda' : 'la derecha'})`;
              }
            }
            return { ...o, disabled, reasonMsg };
          });
          const note = id === 'short_goalkeeper_distribution_oop'
            ? ' <small style="color:var(--text-muted);">(Presionar salida rival)</small>'
            : id === 'dribbling_ip'
            ? ' <small style="color:var(--text-muted);">(Compartido: Avance / Último tercio)</small>'
            : id === 'pressing_trap_oop'
            ? ' <small style="color:var(--text-muted);">(Compartido: Presión alta / Bloque medio)</small>'
            : id === 'gk_distribution_ip'
            ? ' <small style="color:var(--text-muted);">(Destino colectivo único)</small>'
            : '';
          return `<label>${esc(editor.team_properties[id])}${note}<select id="current-team-${id}" data-current="team" data-team="${id}">${filteredOpts.map(o => `<option value="${esc(o.value)}" ${d.team[id] === o.value ? 'selected' : ''} ${o.disabled ? 'disabled' : ''}>${esc(o.label)}${o.reasonMsg || ''}</option>`).join('')}</select></label>`;
        }).join('')}
      </div>
    </details>
    <label class="current-confirm"><input type="checkbox" id="current-confirm" data-current="confirmed" ${d.confirmed?'checked':''}> Confirmo que este once, sus posiciones y roles coinciden con la táctica que estoy usando en FM.</label>
    <button class="button primary" data-action="audit-current" ${state.currentBusy?'disabled':''}>${state.currentBusy?'Revisando…':'Revisar mi táctica'}</button>
    ${state.currentError?`<p class="notice warning" role="alert">${esc(state.currentError)}</p>`:''}
  </details>`;
}
