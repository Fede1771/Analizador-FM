import {esc,number,score,pos} from './format.js';
import {rolePlan,pitch} from './tactics-view.js';
import {zoneMap} from './zones-view.js';

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
    row.instructions=Object.fromEntries(Object.entries(old.instructions||{}).filter(([id,v])=>editor.player_options[id]?.options.some(o=>o.value===v)));
    return row;
  });
  return base;
}

export function freshDraft(data,formation='433') {
  const form=data.tactic_editor.formations.find(f=>f.id===formation)||data.tactic_editor.formations[0];
  return {formation:form.id,name:'Mi táctica',stored_id:'',style:'possession',confirmed:false,team:{},
    lineup:form.slots.map(slot=>({uid:'',ip_position:slot.ip_position,oop_position:slot.oop_position,ip_role:'',oop_role:'',instructions:{}}))};
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
    if(player)Object.assign(row,{ip_position:ref.ip_position,oop_position:ref.oop_position,ip_role:ref.ip_role||ref.ip,oop_role:ref.oop_role||ref.oop,instructions:{...standard,...(ref.instructions||{})}});
  });
  if(data.liverpool_reference?.team) {
    draft.team = {...data.liverpool_reference.team};
  }
  const saved=data.stored_tactics?.records?.find(t=>t.team_slot===data.default_primary_slot);
  if(saved){draft.stored_id=saved.id;draft.name=saved.name;}
  return draft;
}

function captureReview(data) {
  const kerkez=find(data,'kerkez'),wirtz=find(data,'wirtz'),ayari=find(data,'ayari'),pavlovic=find(data,'pavlovic'),vu=find(data,'vuskovic'),eki=find(data,'ekitike'),wharton=find(data,'wharton'),szobo=find(data,'szoboszlai'),cubarsi=find(data,'cubarsi');
  if(![kerkez,wirtz,ayari,pavlovic,vu,eki].every(Boolean))return '';
  return `<section class="panel capture-review">
    <div class="split">
      <div>
        <span class="eyebrow">Diagnóstico visual · Tus 30 capturas de FM26</span>
        <h2>Revisión rápida de tu 4-3-3</h2>
      </div>
      <button class="button primary" data-action="reference-current">⚡ Cargar y revisar mi táctica confirmada</button>
    </div>
    <p class="muted">Ajustes recomendados agrupados con fases tácticas precisas (Con posesión y Sin posesión):</p>

    <div class="match-checklist-card">
      <div class="checklist-header">
        <div class="checklist-title-box">
          <span class="checklist-icon">📋</span>
          <div>
            <h4>Checklist antes del partido · 3 ajustes clave</h4>
            <small>Marcá los cambios aplicados en FM antes de dar «Continuar»</small>
          </div>
        </div>
        <span class="checklist-badge">⚡ Prioridad Máxima</span>
      </div>
      <div class="checklist-items">
        <label class="checklist-item">
          <input type="checkbox" id="check-capture-0">
          <span class="check-box-custom"></span>
          <div class="check-text">
            <span class="check-player-title"><strong>Hugo Ekitiké</strong> · <span class="phase-badge phase-sp">🔴 Sin posesión (SP)</span></span>
            <span class="check-action-desc">Cambiar <u>Entradas</u> a <strong>«Normal»</strong> (evita faltas y rojas innecesarias con entradas 7/20).</span>
          </div>
        </label>
        <label class="checklist-item">
          <input type="checkbox" id="check-capture-1">
          <span class="check-box-custom"></span>
          <div class="check-text">
            <span class="check-player-title"><strong>Luka Vušković</strong> · <span class="phase-badge phase-sp">🔴 Sin posesión (SP)</span></span>
            <span class="check-action-desc">Cambiar <u>Presión</u> a <strong>«Normal»</strong> (para que Vušković haga la cobertura y Cubarsí anticipe).</span>
          </div>
        </label>
        <label class="checklist-item">
          <input type="checkbox" id="check-capture-2">
          <span class="check-box-custom"></span>
          <div class="check-text">
            <span class="check-player-title"><strong>Adam Wharton</strong> · <span class="phase-badge phase-sp">🔴 Sin posesión (SP)</span></span>
            <span class="check-action-desc">Cambiar puesto defensivo de <u>MPC</u> (12/20) ➔ a <strong>MC (20/20 Natural)</strong> como <em>Centrocampista defensivo</em>.</span>
          </div>
        </label>
      </div>
    </div>

    <div class="advice-grid" style="margin-top: 18px;">
      <article class="advice-card severity-danger">
        <div class="advice-header">
          <span class="advice-badge badge-danger">🔴 Riesgo disciplinario y tarjetas</span>
          <h4 class="advice-title">Hugo Ekitiké · Entradas al límite</h4>
        </div>
        <div class="advice-action">
          <span class="advice-action-icon">⚡</span>
          <div class="advice-action-text"><strong>Ajuste recomendado en FM:</strong> Cambiar a <strong>«Entradas en Normal»</strong> en fase <span class="phase-badge phase-sp">🔴 Sin posesión (SP)</span></div>
        </div>
        <div class="advice-chips">
          <span class="advice-chip">Fase: Sin posesión (SP)</span>
          <span class="advice-chip alert">Ekitiké: Entradas 7/20</span>
          <span class="advice-chip">Colectivo: Ser agresivos</span>
        </div>
        <p class="advice-detail">Con la orden colectiva de entrar fuerte y 7/20 de entradas, Ekitiké arriesga amarillas tempranas sin ganar duelos. Bajarlo a Normal evita faltas sin perder contrapresión.</p>
      </article>

      <article class="advice-card severity-warning">
        <div class="advice-header">
          <span class="advice-badge badge-warning">🟡 Cobertura zaga central</span>
          <h4 class="advice-title">Zaga DFC: Pau Cubarsí + Luka Vušković</h4>
        </div>
        <div class="advice-action">
          <span class="advice-action-icon">⚡</span>
          <div class="advice-action-text"><strong>Ajuste recomendado en FM:</strong> Poner a <u>Vušković con Presión en «Normal»</u> en fase <span class="phase-badge phase-sp">🔴 Sin posesión (SP)</span></div>
        </div>
        <div class="advice-chips">
          <span class="advice-chip">Fase: Sin posesión (SP)</span>
          <span class="advice-chip">Línea: Más adelantada</span>
          <span class="advice-chip">Cubarsí: Anticipador</span>
          <span class="advice-chip">Vušković: Cobertura</span>
        </div>
        <p class="advice-detail">Cubarsí y Vušković salen juntos a encimar al receptor. Si Vušković conserva la zona en Normal, escalonan la cobertura y protegen el espacio a espaldas de la zaga adelantada.</p>
      </article>

      <article class="advice-card severity-purple">
        <div class="advice-header">
          <span class="advice-badge badge-purple">🟣 Posición no natural defensiva</span>
          <h4 class="advice-title">Adam Wharton · Puesto sin balón</h4>
        </div>
        <div class="advice-action">
          <span class="advice-action-icon">⚡</span>
          <div class="advice-action-text"><strong>Ajuste recomendado en FM:</strong> Cambiar puesto de <u>MPC</u> (12/20) ➔ a <strong>MC (20/20 Natural)</strong> en fase <span class="phase-badge phase-sp">🔴 Sin posesión (SP)</span></div>
        </div>
        <div class="advice-chips">
          <span class="advice-chip">Fase: Sin posesión (SP)</span>
          <span class="advice-chip alert">Actual: MPC (12/20)</span>
          <span class="advice-chip">Recomendado: MC (20/20)</span>
          <span class="advice-chip">Rol: Centrocampista defensivo</span>
        </div>
        <p class="advice-detail">En MPC queda descolgado sin marcar y con penalización de familiaridad. Pasarlo a defender en MC forma un trivote compacto junto a Pavlović y Ayari.</p>
      </article>

      <article class="advice-card severity-info">
        <div class="advice-header">
          <span class="advice-badge badge-info">🧠 Mediocampo asociativo</span>
          <h4 class="advice-title">Trivote central: Tres organizadores con pase al pie</h4>
        </div>
        <div class="advice-action">
          <span class="advice-action-icon">⚡</span>
          <div class="advice-action-text"><strong>Ajuste recomendado en FM:</strong> Sostener desmarques de Szoboszlai en fase <span class="phase-badge phase-cp">🟢 Con posesión (CP)</span></div>
        </div>
        <div class="advice-chips">
          <span class="advice-chip">Fase: Con posesión (CP)</span>
          <span class="advice-chip">Pavlović: ORD</span>
          <span class="advice-chip">Ayari: OAD</span>
          <span class="advice-chip">Wharton: MOR</span>
        </div>
        <p class="advice-detail">Gran posesión y control con ritmo bajo. Como los tres piden al pie, la profundidad del ataque descansa en las rupturas de Szoboszlai y los apoyos de Ekitiké.</p>
      </article>
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

  const checklist = [
    {
      player: 'Hugo Ekitiké',
      phase: '🔴 Sin posesión (SP)',
      action: 'Cambiar <u>Entradas</u> a <strong>«Normal»</strong> (evita tarjetas y expulsiones innecesarias con entradas 7/20)'
    },
    {
      player: 'Luka Vušković',
      phase: '🔴 Sin posesión (SP)',
      action: 'Cambiar <u>Presión</u> a <strong>«Normal»</strong> (para que Vušković haga la cobertura y Cubarsí anticipe)'
    },
    {
      player: 'Adam Wharton',
      phase: '🔴 Sin posesión (SP)',
      action: 'Cambiar puesto defensivo de <u>MPC</u> (12/20) ➔ a <strong>MC (20/20 Natural)</strong> como <em>Centrocampista defensivo</em>'
    }
  ];

  let html = `
    <div class="match-checklist-card">
      <div class="checklist-header">
        <div class="checklist-title-box">
          <span class="checklist-icon">📋</span>
          <div>
            <h4>Checklist antes del partido · 3 ajustes clave</h4>
            <small>Marcá los cambios aplicados en FM antes de dar «Continuar»</small>
          </div>
        </div>
        <span class="checklist-badge">⚡ Prioridad Máxima</span>
      </div>
      <div class="checklist-items">
        ${checklist.map((item, idx) => `
          <label class="checklist-item">
            <input type="checkbox" id="check-audit-${idx}">
            <span class="check-box-custom"></span>
            <div class="check-text">
              <span class="check-player-title"><strong>${item.player}</strong> · <span class="phase-badge phase-sp">${item.phase}</span></span>
              <span class="check-action-desc">${item.action}</span>
            </div>
          </label>
        `).join('')}
      </div>
    </div>
  `;

  if (teamItems.length) {
    html += `
      <div class="section-heading-visual" style="margin-top: 20px;">
        <h3>Estructura colectiva y zaga</h3>
        <span class="badge-count">${teamItems.length} ajustes de equipo</span>
      </div>
      <div class="advice-grid">
        ${teamItems.map(renderAdviceCard).join('')}
      </div>
    `;
  }

  html += `
    <div class="section-heading-visual" style="margin-top: 24px;">
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
                      ${item.phase === 'ip' ? '🟢 Con posesión (CP)' : item.phase === 'oop' ? '🔴 Sin posesión (SP)' : '⚪ Ambas fases'}
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
      <span class="eyebrow">Tu plan actual, con mejoras concretas</span>
      <h1>Mi táctica</h1>
      <p>Evaluá los jugadores y los roles que usás en FM, conservando tu once.</p>
    </div>
    <div class="actions">
      <button class="button primary" data-action="reference-current">⚡ Cargar y revisar mi táctica confirmada</button>
      ${result?'<button class="button" data-action="export-current">Exportar revisión</button>':''}
    </div>
  </div>

  ${!result ? captureReview(data) : ''}

  ${result ? `
    <section class="panel" id="current-result">
      <div class="split"><h2 tabindex="-1">Revisión de ${esc(result.name)}</h2>${score(result.score)}</div>
      <p>Encaje de tu once confirmado · ${esc(data.styles[result.style].name)}</p>
      <div class="status-summary-strip">
        <span class="status-pill ${result.unconfirmed_player_instructions===0?'pill-ok':'pill-pending'}">${result.unconfirmed_player_instructions===0?'✓ 0 órdenes individuales pendientes (100% confirmadas)':`⚠ ${result.unconfirmed_player_instructions} órdenes individuales sin confirmar`}</span>
        <span class="status-pill ${result.unconfirmed_team_instructions===0?'pill-ok':'pill-pending'}">${result.unconfirmed_team_instructions===0?'✓ 0 órdenes colectivas pendientes (100% confirmadas)':`⚠ ${result.unconfirmed_team_instructions} órdenes colectivas sin confirmar`}</span>
      </div>
      <p class="muted" style="margin: 8px 0 16px;"><small>${esc(result.limits)}</small></p>
      ${renderGroupedAdvice(result, state)}
    </section>

    <section class="panel">
      <div class="split">
        <h2>Tu once confirmado</h2>
        <div class="segmented">
          <button data-phase="ip" aria-pressed="${state.phase==='ip'}">Con posesión</button>
          <button data-phase="oop" aria-pressed="${state.phase==='oop'}">Sin posesión</button>
        </div>
      </div>
      ${pitch(result,state.phase,state.byId)}
    </section>

    ${zoneMap(result.coverage,state.phase)}

    <section class="panel">
      <h2>Ajustes de función sin cambiar al jugador</h2>
      ${result.lineup.map(slot=>`<details><summary>${esc(state.byId.get(slot.uid).name)} · ${esc(slot[phaseKey].name)} · ${number(slot[phaseKey].score)}</summary>${rolePlan(slot[phaseKey])}<p>Alternativas por atributos, no sustituciones automáticas:</p><ul>${slot[phaseKey].alternatives.map(a=>`<li>${esc(a.name)} · ${number(a.score)}</li>`).join('')}</ul></details>`).join('')}
    </section>
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
    <div class="current-lineup">${d.lineup.map((row,index)=>`<section class="current-slot"><h3>Puesto ${index+1}</h3><label>Jugador<select id="current-player-${index}" data-current="uid" data-row="${index}">${options(data.players.map(p=>({value:p.uid,label:p.name})),row.uid,'Elegí jugador')}</select></label>
    <div class="control-grid">${['ip','oop'].map(phase=>`<fieldset><legend>${phase==='ip'?'Con posesión':'Sin posesión'}</legend><label>Posición<select id="current-${phase}-position-${index}" data-current="${phase}_position" data-row="${index}">${editor.positions.map(p=>`<option value="${p}" ${row[phase+'_position']===p?'selected':''}>${esc(pos(p))}</option>`).join('')}</select></label><label>Rol actual<select id="current-${phase}-role-${index}" data-current="${phase}_role" data-row="${index}">${options(Object.entries(editor.roles).filter(([,r])=>r.phase===(phase==='ip'?'in_possession':'out_of_possession')&&r.positions.includes(row[phase+'_position'])).map(([id,r])=>({value:id,label:r.name})),row[phase+'_role'])}</select></label></fieldset>`).join('')}</div>
    <details id="current-instructions-${index}"><summary>Instrucciones individuales actuales</summary><p class="muted">Confirmá solo las órdenes que podés cotejar en FM. Sin confirmar no significa Normal. Menús completos para jugadores de campo y arquero.</p>
    <div class="instruction-grid">${Object.entries(editor.player_options).map(([id,v])=>{
      const phase=v.phase==='in_possession'?'ip':'oop',lock=editor.locks[row[phase+'_role']]?.[id];
      return `<label>${esc(v.label)} · ${phase==='ip'?'CP':'SP'} ${lock!==undefined?'<small>Bloqueada por el rol</small>':''}<select id="current-pi-${index}-${id}" data-current="instruction" data-row="${index}" data-pi="${id}" ${lock!==undefined?'disabled':''}>${options(v.options,lock??row.instructions[id])}</select></label>`;
    }).join('')}</div></details></section>`).join('')}</div>
    <details><summary>Instrucciones colectivas actuales</summary><p>Las que no confirmes quedan fuera de la revisión. Los valores son los del catálogo disponible.</p><div class="instruction-grid">${Object.entries(data.instruction_options).map(([id,opts])=>`<label>${esc(editor.team_properties[id])}<select id="current-team-${id}" data-current="team" data-team="${id}">${options(opts,d.team[id])}</select></label>`).join('')}</div></details>
    <label class="current-confirm"><input type="checkbox" id="current-confirm" data-current="confirmed" ${d.confirmed?'checked':''}> Confirmo que este once, sus posiciones y roles coinciden con la táctica que estoy usando en FM.</label>
    <button class="button primary" data-action="audit-current" ${state.currentBusy?'disabled':''}>${state.currentBusy?'Revisando…':'Revisar mi táctica'}</button>
    ${state.currentError?`<p class="notice warning" role="alert">${esc(state.currentError)}</p>`:''}
  </details>`;
}
