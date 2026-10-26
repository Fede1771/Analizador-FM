import {esc, date, number, score, playerButton, groupName, pos} from './format.js';
import {filteredPlayers} from './session.js';
import {formationCards, tacticResult, rolePlan, supportRunsRecovery} from './tactics-view.js';

export const navigation = {overview:'Centro del club',current:'Mi táctica',tactics:'Propuestas',contracts:'Contratos',scouting:'Ojeo',squad:'Plantilla',academy:'Inferiores',loans:'Cedidos',method:'Cómo se calcula'};

export function welcome(state) {
  return `<section class="welcome"><span class="eyebrow">Tu partida, en tu equipo</span><h1>Conocé tu plantel.<br><em>Encontrá tu plan de juego.</em></h1><p>Analizá tu club de Football Manager 26, compará diez esquemas y decidí con explicaciones para cada jugador.</p><button class="upload-drop" data-action="import"><span aria-hidden="true">↥</span><strong>Elegí o arrastrá tu partida .fm</strong><small>Hasta 400 MB · Procesamiento local</small></button><div class="welcome-steps"><p><b>01</b> Cargá tu partida</p><p><b>02</b> Confirmá los grupos del club</p><p><b>03</b> Compará tu once y sus alternativas</p></div><p class="muted">La partida original se conserva. Touchline calcula un índice propio de encaje y no predice resultados de partidos.</p>${state.error?`<p class="notice warning">${esc(state.error)}</p><button class="button" data-action="reload">Reintentar conexión</button>`:''}<button class="text-button" data-action="sync">Configurar sincronización automática</button></section>`;
}

function stat(label,value,detail) { return `<article class="stat"><span>${label}</span><strong>${value}</strong><small>${detail}</small></article>`; }

export function overview(state) {
  const {data,analysis,prefs} = state;
  const first = analysis?.tactics?.[0];
  const senior = data.players.filter(p=>p.team_slot===prefs.primary_slot);
  const youth = data.players.filter(p=>p.team_slot!==prefs.primary_slot);
  const urgentContracts = (data.contract_alerts || []).filter(a=>a.urgency==='danger');
  const scoutingCount = (data.scouting || []).length;
  const academyTrials = (analysis?.academy || []).filter(a=>a.action==='Probar con el primer equipo');
  const weakPos = first?.reinforcements?.[0]?.position_label || 'Plantilla balanceada';

  return `<div class="page-heading">
    <div>
      <span class="eyebrow">Panel de control ejecutivo · ${esc(data.manager || 'Tu club')} · ${esc(date(data.date))}</span>
      <h1>${esc(data.club)}</h1>
      <p>Tu centro de mando: estado del partido, alertas de contratos y oportunidades de mercado.</p>
    </div>
    <div class="actions">
      <button class="button primary" data-action="companion">⚡ Guía para FM</button>
      <button class="button" data-action="copy-match-instructions">📋 Copiar ajustes</button>
      <button class="button" data-view="current">Ver mi táctica actual →</button>
    </div>
  </div>

  <div class="executive-dashboard-grid">
    <article class="exec-card exec-card-match">
      <div class="exec-card-header">
        <div class="exec-card-title">
          <span class="exec-icon">⚽</span>
          <div>
            <h3>Resumen táctico del club</h3>
            <small>${state.currentResult ? 'Once actual revisado · ' + esc(state.currentResult.name) : first ? 'Propuesta recomendada · ' + esc(first.name) : 'Táctica activa'}</small>
          </div>
        </div>
        <span class="score-pill">${state.currentResult ? number(state.currentResult.score) : first ? number(first.score) : '—'}<small>/100</small></span>
      </div>
      <div class="exec-card-body">
        <div class="exec-alert-box alert-match">
          <span class="exec-alert-icon">⚡</span>
          <div>
            ${(() => {
              const audited = state.currentResult;
              const alerts = audited ? (audited.advice || []).filter(a => a.action) : (first?.tactical_recommendations || []);
              if (alerts.length) {
                return `<strong>${alerts.length} ${alerts.length === 1 ? 'ajuste táctico detectado' : 'ajustes tácticos detectados'}</strong>
                <p>${esc(alerts.slice(0, 2).map(a => a.action || a.title).join('. '))}${alerts.length > 2 ? '…' : ''}</p>`;
              }
              return `<strong>Estructura equilibrada</strong>
              <p>Tu táctica no presenta alertas críticas registradas.</p>`;
            })()}
          </div>
        </div>
      </div>
      <div class="exec-card-footer">
        <button class="button primary" data-view="current">Ver mi táctica actual →</button>
        <button class="button" data-action="companion">⚡ Guía para FM</button>
      </div>
    </article>

    <article class="exec-card exec-card-contracts">
      <div class="exec-card-header">
        <div class="exec-card-title">
          <span class="exec-icon">⚠️</span>
          <div>
            <h3>Contratos & Fugas</h3>
            <small>${(data.contract_alerts || []).length} contratos monitoreados</small>
          </div>
        </div>
        <span class="badge-time ${urgentContracts.length ? 'badge-danger' : 'badge-info'}">
          ${urgentContracts.length ? `🔴 ${urgentContracts.length} en riesgo` : '🟢 En término'}
        </span>
      </div>
      <div class="exec-card-body">
        ${urgentContracts.length ? `
          <div class="exec-alert-box alert-danger">
            <span class="exec-alert-icon">🚨</span>
            <div>
              <strong>${urgentContracts.length} futbolistas vencen en &lt; 10 meses</strong>
              <p>Riesgo de firma libre en enero (${esc(urgentContracts.slice(0, 2).map(a => a.player_name).join(', '))}${urgentContracts.length > 2 ? '…' : ''}).</p>
            </div>
          </div>
        ` : `
          <p class="muted">Situación contractual estable. Sin alertas críticas de fuga libre.</p>
        `}
      </div>
      <div class="exec-card-footer">
        <button class="button" data-view="contracts">Gestionar contratos y renovaciones →</button>
      </div>
    </article>

    <article class="exec-card exec-card-scouting">
      <div class="exec-card-header">
        <div class="exec-card-title">
          <span class="exec-icon">🔍</span>
          <div>
            <h3>Ojeo de Mercado</h3>
            <small>${scoutingCount} futbolistas evaluados en tu partida</small>
          </div>
        </div>
        <span class="role-badge-subtle">Mercado FM26</span>
      </div>
      <div class="exec-card-body">
        <div class="exec-alert-box alert-info">
          <span class="exec-alert-icon">🎯</span>
          <div>
            <strong>Puesto a reforzar: ${esc(weakPos)}</strong>
            <p>Futbolistas destacados de otros clubes con encaje /100 según tu estilo de juego.</p>
          </div>
        </div>
      </div>
      <div class="exec-card-footer">
        <button class="button" data-view="scouting">Explorar Ojeo de Mercado (${scoutingCount}) →</button>
      </div>
    </article>

    <article class="exec-card exec-card-academy">
      <div class="exec-card-header">
        <div class="exec-card-title">
          <span class="exec-icon">🌱</span>
          <div>
            <h3>Cantera y Cedidos</h3>
            <small>${data.loans.length} cedidos · ${youth.length} en inferiores</small>
          </div>
        </div>
        <span class="extension-tag">${academyTrials.length} para prueba</span>
      </div>
      <div class="exec-card-body">
        <p class="muted">${academyTrials.length ? `Hay ${academyTrials.length} juveniles con nivel competitivo para probar en primera división.` : 'Plantel de juveniles y cedidos en seguimiento habitual.'}</p>
      </div>
      <div class="exec-card-footer">
        <button class="button" data-view="academy">Ver cantera →</button>
        <button class="button" data-view="loans">Ver cedidos →</button>
      </div>
    </article>
  </div>

  <div class="stats-grid" style="margin-top: 18px;">
    ${stat('Disponibles en el grupo principal',senior.filter(p=>!prefs.excluded.includes(p.uid)).length,`${senior.length} jugadores en ${esc(groupName(data,prefs,prefs.primary_slot))}`)}
    ${stat('Mayor encaje del once',first?number(first.score):'—',first?`${esc(first.name)} · índice propio /100`:'Revisá el grupo principal')}
    ${stat('Otros grupos',youth.length,'Reservas y juveniles, según tu configuración')}
    ${stat('Cedidos',data.loans.length,'Alternativas para seguimiento')}
  </div>

  ${first?`<div class="section-heading" style="margin-top: 24px;"><h2>Las tres propuestas con mayor encaje</h2><span class="muted">Comparadas entre ${analysis.evaluated_formations} esquemas</span></div>${formationCards(analysis.tactics,null)}`:''}`;
}

export function tactics(state) {
  const {data,prefs,analysis,simulation} = state;
  const selected = prefs.formation==='auto' ? analysis?.requested_tactic || analysis?.tactics[0] : simulation;
  const pa=analysis?.prompt_analysis;
  return `<div class="page-heading"><div><span class="eyebrow">Propuestas tácticas · Esquemas para tu plantel</span><h1>Propuestas</h1><p>Compará esquemas y evaluá la mejor propuesta para tu plantilla.</p></div><div class="actions"><button class="button primary" data-action="companion">⚡ Guía para FM</button><button class="button" data-action="copy-match-instructions">📋 Copiar ajustes</button><button class="button" data-action="export">Exportar JSON</button></div></div>
    <section class="panel controls">
      <div class="control-grid">
        <label>Formación propuesta
          <select id="formation-select">
            <option value="auto" ${prefs.formation==='auto'?'selected':''}>★ Recomendar el mejor esquema (entre 10)</option>
            ${data.formations_catalog.map(f=>`<option value="${f.id}" ${prefs.formation===f.id?'selected':''}>${esc(f.name)} → ${esc(f.defensive)}</option>`).join('')}
          </select>
        </label>
        <label>Estilo táctico aplicado
          <select id="style-select">
            ${Object.entries(data.styles).map(([k,s])=>`<option value="${k}" ${prefs.style===k?'selected':''}>${esc(s.name)} · ${esc(s.fm26_style)}</option>`).join('')}
          </select>
        </label>
      </div>
      <details id="prompt-details" ${state.promptDraft ? 'open' : ''}>
        <summary>💬 Idea de juego o pedido personalizado</summary>
        <label for="prompt-input">Instrucción en lenguaje natural <small>Interpretación con reglas y estilos de FM26 · Ctrl + Enter</small></label>
        <textarea id="prompt-input" maxlength="2000" rows="2" placeholder="Ej.: posesión paciente, muchas ocasiones y solidez atrás...">${esc(state.promptDraft)}</textarea>
        <div class="actions">
          <button class="button primary" data-action="apply-prompt">Aplicar idea</button>
          <button class="button" data-action="clear-prompt">Restablecer</button>
        </div>
        ${pa?`<div class="interpretation"><strong>Interpretación aplicada</strong><p>${esc(data.styles[pa.recommended_style]?.name || pa.recommended_style)} · ${esc(pa.recommended_mentality)}${pa.avoided.length?' · Evitar: '+esc(pa.avoided.join(', ')):''}</p>${pa.warnings.map(x=>`<p class="notice warning">${esc(x)}</p>`).join('')}<p class="muted">Podés ajustar la formación, el estilo y las instrucciones de equipo a continuación.</p></div>`:''}
      </details>
    </section>
    ${analysis?.tactics.length?`<details class="ranking"><summary>Comparar las tres mejores · ${analysis.evaluated_formations} esquemas evaluados</summary>${formationCards(analysis.tactics,selected?.id)}</details>`:''}
    ${state.error?`<div class="notice warning" role="alert">${esc(state.error)} <button class="text-button" data-action="retry">Reintentar</button></div>`:''}
    ${selected?tacticResult(selected,state):state.busy?'<div class="panel skeleton" role="status">Calculando tu propuesta…</div>':state.error?.includes('Carreras de apoyo')?supportRunsRecovery(data,prefs,state.overrideDraft):'<section class="panel empty"><h2>No hay un once completo</h2><p>Necesitás al menos once jugadores disponibles en el grupo principal. Revisá tus exclusiones y la asignación de grupos.</p><button class="button" data-action="groups">Configurar grupos</button></section>'}`;
}

function toolbar(state, kind) {
  const groups=kind==='loans'?[]:state.data.slots.filter(s=>kind!=='academy'||s!==state.prefs.primary_slot);
  return `<div class="table-toolbar"><label class="search">Buscar jugador o posición<input id="search" type="search" value="${esc(state.filters.query)}" placeholder="Nombre o código de posición"></label><label>Grupo<select id="group-filter"><option value="all">Todos</option>${groups.map(s=>`<option value="${s}" ${state.filters.group===String(s)?'selected':''}>${esc(groupName(state.data,state.prefs,s))}</option>`).join('')}</select></label><label>Ordenar<select id="sort-order">${[['score','Mayor encaje'],['age','Menor edad'],['name','Nombre']].map(([k,v])=>`<option value="${k}" ${state.filters.order===k?'selected':''}>${v}</option>`).join('')}</select></label></div>`;
}

export function playerRows(state,kind) {
  const {data,prefs,analysis} = state;
  const profiles=analysis?.profiles||{};
  const pool=kind==='loans'?data.loans:kind==='academy'?data.players.filter(p=>p.team_slot!==prefs.primary_slot):data.players;
  const rows=filteredPlayers(pool,state.filters,profiles);
  if (!rows.length) return '<p class="empty" role="status">No encontramos jugadores con esos filtros.</p>';
  if(kind==='academy') return `<div class="academy-grid">${rows.map(p=>{const a=analysis?.academy.find(x=>x.uid===p.uid),prof=profiles[p.uid];return `<article class="academy-card">${playerButton(p)}<span class="tag">${esc(groupName(data,prefs,p.team_slot))}</span><div class="split"><h3>${esc(prof?.role_name)}</h3>${score(prof?.score)}</div><strong>${esc(a?.action)}</strong><p>${esc(a?.plan)}</p><small>${a?.gap==null?'Sin referencia':`${a.gap>0?'+':''}${number(a.gap)} puntos frente a la referencia del primer equipo`}</small><p class="muted">Entrenar: ${esc(prof?.focus.map(f=>`${f.name} (${f.value})`).join(', '))}</p></article>`;}).join('')}</div>`;
  if(kind==='loans') {
    const activeWithMins = rows.filter(p=>(p.loan_stats?.minutes||0)>0);
    const topScorer = [...rows].filter(p=>(p.loan_stats?.goals||0)>0).sort((a,b)=>(b.loan_stats?.goals||0)-(a.loan_stats?.goals||0))[0];
    const topRated = [...rows].filter(p=>(p.loan_stats?.appearances||0)>=2&&(p.loan_stats?.average_rating||0)>0).sort((a,b)=>(b.loan_stats?.average_rating||0)-(a.loan_stats?.average_rating||0))[0];
    const winSample = pool[0]?.loan_window || {};
    return `
      <div class="loan-summary-strip">
        <div class="loan-summary-pill"><span class="loan-pill-title">Total cedidos</span><strong>${rows.length}</strong></div>
        <div class="loan-summary-pill"><span class="loan-pill-title">Con rodaje</span><strong>${activeWithMins.length}</strong><small>${rows.length - activeWithMins.length} sin minutos</small></div>
        <div class="loan-summary-pill ${winSample.is_open ? 'urgency-stable' : 'urgency-warning'}"><span class="loan-pill-title">Ventana repescas FM</span><strong>${winSample.is_open ? '🟢 Abierta' : '🔒 Cerrada'}</strong><small>${esc(winSample.next_open || 'Ver calendario FM')}</small></div>
        ${topScorer ? `<div class="loan-summary-pill"><span class="loan-pill-title">Goleador cedido</span><strong>${esc(topScorer.name)}</strong><small>${topScorer.loan_stats.goals} goles · ${topScorer.loan_stats.appearances} PJ</small></div>` : ''}
        ${topRated ? `<div class="loan-summary-pill"><span class="loan-pill-title">Mejor calificación</span><strong>${esc(topRated.name)}</strong><small>Media ${number(topRated.loan_stats.average_rating, 2)} (${topRated.loan_stats.appearances} PJ)</small></div>` : ''}
      </div>
      <div class="table-scroll"><table><caption>${rows.length} cedidos · “—” indica datos no disponibles</caption><thead><tr>${['Jugador','Club','Rol / Función','PJ','Goles','Asistencias','Minutos','Media','Fin del préstamo','Estado de repesca','Encaje'].map(x=>`<th scope="col">${x}</th>`).join('')}</tr></thead><tbody>${rows.map(p=>{
        const s=p.loan_stats||{};
        const prof=profiles[p.uid];
        const roleName=prof?.role_name || (p.natural_positions?.[0] ? pos(p.natural_positions[0]) : '—');
        const isHighlight = (s.average_rating||0) >= 7.0;
        const win = p.loan_window || {};
        return `<tr>
          <td>${playerButton(p)}</td>
          <td>${esc(s.club_name||p.club_name)}</td>
          <td><span class="role-badge-subtle">${esc(roleName)}</span></td>
          <td>${number(s.appearances,0)}</td>
          <td>${number(s.goals,0)}</td>
          <td>${number(s.assists,0)}</td>
          <td>${number(s.minutes,0)}</td>
          <td>${isHighlight ? `<span class="rating-highlight">${number(s.average_rating,2)} ⭐</span>` : number(s.average_rating,2)}</td>
          <td>${esc(date(s.loan_end||p.loan_end))}${win.months_remaining != null ? `<br><small class="muted">(${win.months_remaining} meses)</small>` : ''}</td>
          <td><span class="window-pill ${win.is_open ? 'window-open' : 'window-closed'}">${esc(win.badge || '—')}</span></td>
          <td>${score(prof?.score)}</td>
        </tr>`;
      }).join('')}</tbody></table></div>`;
  }
  if (kind === 'squad') {
    const selectedTactic = prefs.formation === 'auto'
      ? analysis?.requested_tactic || analysis?.tactics?.[0]
      : state.simulation || analysis?.tactics?.[0];
    const startersSet = new Set((selectedTactic?.lineup || []).map(l => l.uid));
    const benchSet = new Set(selectedTactic?.bench || []);
    const surplusMap = selectedTactic?.surplus_players || analysis?.surplus_players || {};

    return `<div class="table-scroll"><table><caption>${rows.length} jugadores · Encaje individual en su mejor función y situación en la plantilla</caption><thead><tr>${['Jugador','Grupo','Mejor función','Situación en plantilla','Encaje','Pases','Técnica','Velocidad','Disponible'].map(x=>`<th scope="col">${x}</th>`).join('')}</tr></thead><tbody>${rows.map(p=>{
      const isExcluded = prefs.excluded.includes(p.uid);
      const prof = profiles[p.uid];
      const surplus = surplusMap[p.uid];
      let statusHtml;
      if (startersSet.has(p.uid)) {
        statusHtml = '<span class="squad-status-badge starter" title="Titular en el once propuesto">⭐ Titular</span>';
      } else if (surplus) {
        if (surplus.action === 'loan') {
          statusHtml = `<span class="squad-status-badge loan" title="${esc(surplus.reason)}">📤 Préstamo (${surplus.age}a)</span>`;
        } else {
          statusHtml = `<span class="squad-status-badge sell" title="${esc(surplus.reason)}">🏷️ Evaluar venta</span>`;
        }
      } else if (benchSet.has(p.uid)) {
        statusHtml = '<span class="squad-status-badge bench" title="Opción principal en el banco de suplentes">🔄 Rotación</span>';
      } else {
        statusHtml = '<span class="squad-status-badge reserve" title="Suplente de reserva">Reserva</span>';
      }

      return `<tr class="${isExcluded ? 'excluded' : ''}">
        <td>${playerButton(p)}</td>
        <td>${esc(groupName(data,prefs,p.team_slot))}</td>
        <td>${esc(prof?.role_name)}</td>
        <td>${statusHtml}</td>
        <td>${score(prof?.score)}</td>
        <td>${p.attributes.passing}</td>
        <td>${p.attributes.technique}</td>
        <td>${p.attributes.pace}</td>
        <td><input id="available-${p.uid}" type="checkbox" data-available="${p.uid}" ${isExcluded ? '' : 'checked'} aria-label="Incluir a ${esc(p.name)} en las propuestas"></td>
      </tr>`;
    }).join('')}</tbody></table></div>`;
  }
  return `<div class="table-scroll"><table><caption>${rows.length} jugadores · Encaje individual en su mejor función</caption><thead><tr>${['Jugador','Grupo','Mejor función','Encaje','Pases','Técnica','Velocidad','Disponible'].map(x=>`<th scope="col">${x}</th>`).join('')}</tr></thead><tbody>${rows.map(p=>`<tr class="${prefs.excluded.includes(p.uid)?'excluded':''}"><td>${playerButton(p)}</td><td>${esc(groupName(data,prefs,p.team_slot))}</td><td>${esc(profiles[p.uid]?.role_name)}</td><td>${score(profiles[p.uid]?.score)}</td><td>${p.attributes.passing}</td><td>${p.attributes.technique}</td><td>${p.attributes.pace}</td><td><input id="available-${p.uid}" type="checkbox" data-available="${p.uid}" ${prefs.excluded.includes(p.uid)?'':'checked'} aria-label="Incluir a ${esc(p.name)} en las propuestas"></td></tr>`).join('')}</tbody></table></div>`;
}

function squadOvercrowdingPanel(overcrowding, tactic) {
  if (!overcrowding || !overcrowding.length) {
    return `<div class="squad-balance-banner">
      <span class="icon">✅</span>
      <div>
        <strong>Plantilla equilibrada sin sobrepoblación</strong>
        <p>No se detectaron puestos con exceso de futbolistas para el esquema propuesto (${esc(tactic?.name || 'táctico')}). Todos los puestos cuentan con una cobertura adecuada de 1 a 2 jugadores sin sobrecosto salarial ni juveniles tapados.</p>
      </div>
    </div>`;
  }
  const totalSurplus = overcrowding.reduce((acc, x) => acc + (x.surplus_count || 0), 0);
  return `<section class="panel squad-overcrowding-panel">
    <div class="overcrowding-header">
      <div>
        <span class="eyebrow">Gestión de plantilla · Sobrepoblación detectada</span>
        <h2>⚖️ Salidas recomendadas por exceso de cupo (${totalSurplus} ${totalSurplus === 1 ? 'jugador excedente' : 'jugadores excedentes'})</h2>
        <p class="muted">Para el esquema ${esc(tactic?.name || 'titular')} con cupo ideal de hasta 2 futbolistas por puesto activo, estos jugadores quedan relegados en la rotación. Touchline recomienda <strong>préstamo</strong> para menores de 23 años (rodaje competitivo) y <strong>evaluar venta</strong> para mayores de 22 años (alivio salarial y capitalización de mercado).</p>
      </div>
    </div>
    <div class="overcrowding-grid">
      ${overcrowding.map(item => `
        <article class="overcrowding-card">
          <div class="oc-card-header">
            <div>
              <h3>${esc(item.position_label || item.position)}</h3>
              <span class="oc-meta-badge">${item.player_count} jugadores · ${item.starters_needed > 0 ? `${item.starters_needed} titular(es)` : 'Sin titular en el esquema'} (Cupo ideal: ${item.max_ideal})</span>
            </div>
            <span class="oc-surplus-badge">+${item.surplus_count} excedente${item.surplus_count > 1 ? 's' : ''}</span>
          </div>
          <div class="oc-candidate-list">
            ${item.candidates.map(c => `
              <div class="oc-candidate-row">
                <div class="oc-candidate-info">
                  <div class="oc-candidate-name-row">
                    <button class="player-link text-button" data-player="${c.uid}"><strong>${esc(c.name)}</strong></button>
                    <span class="oc-action-badge ${c.action === 'loan' ? 'loan' : 'sell'}">${c.action === 'loan' ? '📤 Mandar a préstamo' : '🏷️ Evaluar venta'}</span>
                  </div>
                  <div class="oc-candidate-sub">
                    <span>${c.age} años</span>
                    <span>${score(c.score)}</span>
                    ${c.wage_formatted ? `<span class="wage-pill">${esc(c.wage_formatted)}</span>` : ''}
                    <span class="muted">${c.rank}ª opción</span>
                  </div>
                  <p class="oc-reason">${esc(c.reason)}</p>
                </div>
              </div>
            `).join('')}
          </div>
        </article>
      `).join('')}
    </div>
  </section>`;
}

export function roster(state,kind) {
  const texts={
    squad:['Plantilla','Marcá los jugadores disponibles para el once y el banco, y gestioná el equilibrio de puestos.'],
    academy:['Inferiores','Compará otros grupos con el primer equipo y elegí una prioridad de desarrollo.'],
    loans:['Cedidos','Seguí minutos y rendimiento. Las estadísticas ausentes se muestran sin estimar.']
  };
  const selectedTactic = state.prefs?.formation === 'auto'
    ? state.analysis?.requested_tactic || state.analysis?.tactics?.[0]
    : state.simulation || state.analysis?.tactics?.[0];
  const overcrowding = selectedTactic?.overcrowding || state.analysis?.squad_overcrowding || [];

  return `<div class="page-heading">
    <div>
      <h1>${texts[kind][0]}</h1>
      <p>${texts[kind][1]}</p>
    </div>
    <button class="button" data-action="export">Exportar análisis</button>
  </div>
  ${kind==='academy'?'<p class="notice">Se incluyen todos los grupos salvo el principal; pueden contener reservas adultos. El encaje actual no estima potencial.</p>':''}
  ${kind==='squad'?squadOvercrowdingPanel(overcrowding, selectedTactic):''}
  <section class="panel">
    ${toolbar(state,kind)}
    <div id="results">${playerRows(state,kind)}</div>
  </section>`;
}

export function methodology(state) {
  const m=state.data.methodology;
  return `<div class="page-heading"><div><h1>Cómo se calcula</h1><p>Las reglas, los datos y sus límites.</p></div></div><section class="panel prose"><h2>Índice propio de Touchline</h2><p>${esc(m.formula)}</p><p>El puntaje no es una probabilidad de victoria ni una calificación del motor de FM.</p><h3>Construcción del once y banco</h3><p>${esc(m.lineup)}</p><p>Las alertas de nivel comparan cada puesto con la media del once, con un margen de ocho puntos. La cobertura del banco usa familiaridad de ambas fases.</p><h3>Inferiores</h3><p>${esc(m.academy)}</p><h3>Lenguaje natural</h3><p>Se utilizan reglas de reconocimiento, negaciones y prioridades explícitas. La interpretación se muestra en Tácticas y puede corregirse mediante estilo, formación y ajustes de equipo.</p><h3>Datos y límites</h3><p>Se usan atributos visibles. La extracción realiza controles de estructura y rangos; eso no demuestra que cada dato coincida con la ficha del juego. La verificación de etiquetas se informa por rol.</p><p>Confirmá lesiones, sanciones, inscripción, familiaridad táctica, rival, carga de partidos y condiciones de repesca dentro de FM. No se exportan tácticas .fmf.</p><h3>Persistencia</h3><p>Las preferencias se conservan por club e identificador del manager; las copias de una misma carrera comparten configuración. Los resultados se invalidan con cada guardado y cambio de contexto.</p></section><details class="panel"><summary>Catálogo de roles de FM26 y atributos (${Object.keys(m.roles).length} roles)</summary>${Object.values(m.roles).map(r=>`<details><summary>${esc(r.name)} [${esc(r.abbreviation||'ROL')}] · ${r.phase==='in_possession'?'Con posesión (CP)':'Sin posesión (SP)'}</summary><p>${esc(r.english)} · Posiciones: ${esc(r.positions.map(pos).join(', '))}</p>${r.subposition_rule ? `<p class="notice">🛡️ Subpuesto: ${r.subposition_rule.min_central_defenders ? 'Requiere línea de al menos 3 centrales' : 'Requiere doble pivote'}</p>` : ''}${Array.isArray(r.behaviors) && r.behaviors.length ? `<p><strong>Comportamientos inherentes al rol:</strong></p><div class="role-behaviors-chips">${r.behaviors.map(b=>`<span class="behavior-chip">⚡ ${esc(b)}</span>`).join('')}</div>` : ''}<p><strong>Atributos requeridos:</strong> ${esc(Object.keys(r.weights).map(k=>state.data.attributes[k] || k).join(', '))}</p><p class="muted"><small>${r.key_attributes_ui_verified ? '✅ Atributos clave cotejados en interfaz de FM26' : 'ℹ️ Ponderación analítica propia de Touchline (80/20), no del motor interno de FM'}</small></p><a href="${esc(r.source)}" target="_blank" rel="noreferrer">Fuente del rol ↗</a></details>`).join('')}</details>`;
}

export function playerDialog(state,id) {
  const p=state.byId.get(Number(id)), prof=state.analysis?.profiles[id];
  if(!p||!prof) return '<h2>El jugador ya no está en este análisis</h2>';
  const tactic=state.prefs.formation==='auto'?state.analysis.requested_tactic||state.analysis.tactics[0]:state.simulation;
  const slot=state.view==='current'?state.currentResult?.lineup.find(x=>x.uid===p.uid):state.view==='tactics'?tactic?.lineup.find(x=>x.uid===p.uid):null;
  const a=state.analysis.academy.find(x=>x.uid===p.uid);
  const surplus = tactic?.surplus_players?.[p.uid] || state.analysis?.surplus_players?.[p.uid];
  return `<div class="profile-heading"><span class="eyebrow">${slot?(state.view==='current'?'En tu once confirmado':'En el once propuesto'):'Mejor encaje individual'}</span><h2 id="dialog-title">${esc(p.name)}</h2><p>${p.age??'—'} años · ${esc(p.natural_positions.map(pos).join(' / '))} · ${esc(p.club_name||state.data.club)}</p></div>${rolePlan((slot||prof).in_possession)}${rolePlan((slot||prof).out_of_possession)}
    ${surplus ? `<section class="panel squad-candidate-notice ${surplus.action === 'loan' ? 'notice-loan' : 'notice-sell'}">
      <h3>${surplus.action === 'loan' ? '📤 Sugerencia de plantilla: Mandar a préstamo' : '🏷️ Sugerencia de plantilla: Evaluar venta'}</h3>
      <p>${esc(surplus.reason)}</p>
      ${surplus.wage_formatted ? `<p class="muted"><small>Salario actual: <strong>${esc(surplus.wage_formatted)}</strong>${surplus.contract_end ? ` · Fin de contrato: ${esc(surplus.contract_end)}` : ''}</small></p>` : ''}
    </section>` : ''}
    ${a?`<section class="panel"><h3>${esc(a.action)}</h3><p>${esc(a.plan)}</p><p>${esc(a.development)}</p>${a.comparison.map(c=>`<div class="split"><span>${esc(c.name)}</span>${score(c.score)}</div>`).join('')}</section>`:''}
    <details><summary>Atributos visibles y familiaridad</summary><div class="attribute-grid">${Object.entries(state.data.attributes).map(([k,label])=>`<div><span>${esc(label)}</span><b>${p.attributes[k]}</b></div>`).join('')}</div><p>${esc(Object.entries(p.positions).filter(([,v])=>v>=10).map(([k,v])=>`${pos(k)} ${v}/20`).join(' · '))}</p><p>Pie izquierdo ${p.left_foot??'—'}/20 · derecho ${p.right_foot??'—'}/20</p></details><button class="button" data-download-player="${p.uid}">Descargar plan del jugador</button>`;
}

export function groupDialog(state) {
  const {data,prefs}=state;
  return `<h2 id="dialog-title">Estructura del club</h2><p>Confirmá el primer equipo y los nombres de reservas y juveniles.</p><form id="groups-form"><label>Grupo del primer equipo<select name="primary_slot">${data.slots.map(s=>`<option value="${s}" ${prefs.primary_slot===s?'selected':''}>${esc(groupName(data,prefs,s))} · ${data.players.filter(p=>p.team_slot===s).length} jugadores</option>`).join('')}</select></label>${data.slots.map(s=>`<label>Nombre del grupo ${s}<input name="label-${s}" maxlength="40" value="${esc(groupName(data,prefs,s))}"><small>${esc(data.players.filter(p=>p.team_slot===s).slice(0,3).map(p=>p.name).join(', '))}</small></label>`).join('')}<button class="button primary" type="submit">Guardar y recalcular</button></form>`;
}

export function syncDialog(status, retention) {
  const s=status||{};
  return `<h2 id="dialog-title">Sincronización y almacenamiento</h2><p>El monitor espera a que el archivo se estabilice y conserva el análisis anterior hasta completar la actualización.</p><div class="notice"><strong>Última actualización exitosa:</strong> ${esc(s.last_sync_save||'Ninguna')} · ${esc(date(s.last_sync_time,true))}</div>${s.last_error?`<p class="notice warning" role="alert">${esc(s.last_error)}</p>`:''}
  <form id="sync-form"><label class="check"><input name="enabled" type="checkbox" ${s.enabled!==false?'checked':''}> Activar sincronización automática</label><label>Carpeta de partidas<input name="watch_folder" value="${esc(s.watch_folder||'')}" required></label><label>Partida<select name="target_save"><option value="auto">Última partida guardada</option>${(s.available_saves||[]).map(x=>`<option value="${esc(x.filename)}" ${s.target_save===x.filename?'selected':''}>${esc(x.filename)} · ${esc(date(x.modified_at,true))}</option>`).join('')}${s.target_save&&!(s.available_saves||[]).some(x=>x.filename===s.target_save)?`<option selected value="${esc(s.target_save)}">${esc(s.target_save)} (no encontrada)</option>`:''}</select></label><div class="actions"><button class="button primary" type="submit">Guardar configuración</button><button class="button" type="button" data-action="force-sync">Sincronizar ahora</button></div></form>
  <details><summary>Retención de copias locales</summary><p>Después de una importación exitosa se conservan las copias más recientes dentro de estos límites. La copia activa se conserva siempre. Las partidas originales de FM quedan fuera de esta limpieza.</p><form id="retention-form"><label>Máximo de copias<input name="max_snapshots" type="number" min="1" max="100" value="${retention.max_snapshots}" required></label><label>Espacio máximo en MB<input name="max_total_mb" type="number" min="400" max="102400" value="${retention.max_total_mb}" required></label><button class="button" type="submit">Guardar límites</button></form></details>`;
}


export function contractsView(state) {
  const {data, prefs, byId} = state;
  const alerts = data.contract_alerts || [];
  const cf = state.contractsFilter || {urgency: 'all', query: ''};

  const danger = alerts.filter(a => a.urgency === 'danger');
  const warning = alerts.filter(a => a.urgency === 'warning');
  const withOption = alerts.filter(a => a.has_extension_option);

  let filtered = alerts;
  if (cf.urgency !== 'all') {
    if (cf.urgency === 'option') filtered = filtered.filter(a => a.has_extension_option);
    else filtered = filtered.filter(a => a.urgency === cf.urgency);
  }
  if (cf.query) {
    const q = cf.query.toLowerCase();
    filtered = filtered.filter(a => a.player_name.toLowerCase().includes(q));
  }

  return `<div class="page-heading">
    <div>
      <span class="eyebrow">Gestión de plantilla y patrimonio del club</span>
      <h1>Contratos y Renovaciones</h1>
      <p>Seguimiento de vencimientos, riesgo de fuga libre y opciones unilaterales del club.</p>
    </div>
    <button class="button" data-action="export">Exportar análisis</button>
  </div>

  <div class="contract-summary-strip">
    <div class="contract-summary-pill urgency-danger">
      <span class="loan-pill-title">🔴 Vencen en &lt; 10 meses</span>
      <strong>${danger.length}</strong>
      <small>Riesgo de firma libre en enero / julio</small>
    </div>
    <div class="contract-summary-pill urgency-warning">
      <span class="loan-pill-title">🟡 Vencen en 1-2 años</span>
      <strong>${warning.length}</strong>
      <small>Ventana óptima para negociar renovación</small>
    </div>
    <div class="contract-summary-pill urgency-option">
      <span class="loan-pill-title">🛡️ Opción unilateral del club</span>
      <strong>${withOption.length}</strong>
      <small>El club puede extender +1 año sin negociar</small>
    </div>
    <div class="contract-summary-pill urgency-stable">
      <span class="loan-pill-title">🟢 En término (&gt; 2 años)</span>
      <strong>${alerts.length - danger.length - warning.length}</strong>
      <small>Situación contractual asegurada</small>
    </div>
  </div>

  ${danger.length ? `
    <section class="panel urgent-contracts-panel">
      <div class="split">
        <div>
          <h2 class="alert-title-danger">⚠️ Atención inmediata: contratos en sus últimos meses</h2>
          <p class="muted">Estos futbolistas podrán negociar libremente con otros clubes a partir del 1 de enero si no renovás su contrato.</p>
        </div>
      </div>
      <div class="urgent-cards-grid">
        ${danger.map(a => {
          const p = byId.get(a.player_uid);
          return `
            <article class="urgent-contract-card">
              <div class="urgent-card-top">
                <div>
                  <h3 class="urgent-player-name">${esc(a.player_name)}</h3>
                  <span class="tag">${p ? esc(groupName(data, prefs, p.team_slot)) : 'Plantilla'}</span>
                </div>
                <span class="urgent-badge-pill">${a.months_remaining} meses</span>
              </div>
              <div class="urgent-card-meta">
                <span><strong>Salario:</strong> ${a.wage ? '€' + number(a.wage) + '/sem' : '—'}</span>
                <span><strong>Vence:</strong> ${esc(date(a.contract_end))}</span>
                ${a.has_extension_option ? '<span class="extension-tag">🛡️ Opción +1 año</span>' : ''}
              </div>
              <div class="urgent-action-box">
                <span class="urgent-action-icon">💡</span>
                <p class="urgent-action-text">${esc(a.action)}</p>
              </div>
            </article>
          `;
        }).join('')}
      </div>
    </section>
  ` : ''}

  <section class="panel">
    <div class="contracts-toolbar">
      <label class="search">Buscar jugador<input id="contracts-search" type="search" value="${esc(cf.query)}" placeholder="Nombre de jugador..."></label>
      <div class="formation-pills" role="group" aria-label="Filtro de urgencia">
        <button type="button" class="formation-pill ${cf.urgency==='all'?'active':''}" data-contract-filter="all">Todos (${alerts.length})</button>
        <button type="button" class="formation-pill ${cf.urgency==='danger'?'active':''}" data-contract-filter="danger">🔴 &lt; 10 meses (${danger.length})</button>
        <button type="button" class="formation-pill ${cf.urgency==='warning'?'active':''}" data-contract-filter="warning">🟡 1-2 años (${warning.length})</button>
        <button type="button" class="formation-pill ${cf.urgency==='option'?'active':''}" data-contract-filter="option">🛡️ Con opción club (${withOption.length})</button>
      </div>
    </div>

    <div class="table-scroll">
      <table>
        <caption>${filtered.length} jugadores · Control contractual de plantilla</caption>
        <thead>
          <tr>
            <th scope="col">Jugador</th>
            <th scope="col">Grupo</th>
            <th scope="col">Vence</th>
            <th scope="col">Tiempo restante</th>
            <th scope="col">Salario semanal</th>
            <th scope="col">Opción extensión</th>
            <th scope="col">Estado y recomendación</th>
          </tr>
        </thead>
        <tbody>
          ${filtered.length ? filtered.map(a => {
            const p = byId.get(a.player_uid);
            return `
              <tr class="row-${esc(a.urgency)}">
                <td>${p ? playerButton(p) : `<strong>${esc(a.player_name)}</strong>`}</td>
                <td>${p ? esc(groupName(data, prefs, p.team_slot)) : '—'}</td>
                <td>${esc(date(a.contract_end))}</td>
                <td><span class="badge-time badge-${esc(a.urgency)}">${a.months_remaining} meses</span></td>
                <td>${a.wage ? '€' + number(a.wage) : '—'}</td>
                <td>${a.has_extension_option ? '<span class="extension-tag">🛡️ +1 año (Club)</span>' : '<span class="muted">No</span>'}</td>
                <td>
                  <div class="contract-rec-cell">
                    <span class="contract-status-badge badge-${esc(a.urgency)}">${esc(a.badge)}</span>
                    <small class="contract-rec-desc">${esc(a.action)}</small>
                  </div>
                </td>
              </tr>
            `;
          }).join('') : `<tr><td colspan="7" class="empty">No encontramos jugadores con los filtros seleccionados.</td></tr>`}
        </tbody>
      </table>
    </div>
  </section>`;
}

export function scoutingView(state) {
  const {data} = state;
  const scoutingList = data.scouting || [];
  const sf = state.scoutingFilter || {position: 'all', query: '', sort: 'score'};

  const positionsList = [
    {id: 'all', label: 'Todos'},
    {id: 'DFC', label: 'DFC'},
    {id: 'DFI', label: 'DFI'},
    {id: 'DFD', label: 'DFD'},
    {id: 'MCD', label: 'MCD'},
    {id: 'MC', label: 'MC'},
    {id: 'MPC', label: 'MPC'},
    {id: 'MPI', label: 'MPI'},
    {id: 'MPD', label: 'MPD'},
    {id: 'DLC', label: 'DLC'},
    {id: 'POR', label: 'POR'}
  ];

  let filtered = scoutingList;
  if (sf.position !== 'all') {
    filtered = filtered.filter(p => p.position_primary === sf.position || (p.natural_positions && p.natural_positions.includes(sf.position)));
  }
  if (sf.query) {
    const q = sf.query.toLowerCase();
    filtered = filtered.filter(p => p.name.toLowerCase().includes(q) || (p.club_name && p.club_name.toLowerCase().includes(q)) || (p.best_role && p.best_role.toLowerCase().includes(q)));
  }

  filtered = [...filtered].sort((a, b) => {
    if (sf.sort === 'age') return (a.age || 99) - (b.age || 99);
    if (sf.sort === 'wage') return (a.wage || 9999999) - (b.wage || 9999999);
    return (b.score || 0) - (a.score || 0);
  });

  return `<div class="page-heading">
    <div>
      <span class="eyebrow">Mercado de fichajes y Scouting FM26</span>
      <h1>Ojeo de Mercado</h1>
      <p>Futbolistas destacados de otros clubes en tu partida, analizados según su encaje táctico con tu idea de juego.</p>
    </div>
    <button class="button" data-action="export">Exportar análisis</button>
  </div>

  <div class="scouting-banner-strip">
    <div class="scouting-status-badge">
      <span class="scanner-icon">📡</span>
      <div>
        <strong>${scoutingList.length} jugadores escaneados desde tu archivo .fm</strong>
        <small>Extracción directa de la partida guardada con atributos reales, contratos y roles FM26 calculados.</small>
      </div>
    </div>
  </div>

  <section class="panel">
    <div class="scouting-toolbar">
      <div class="scouting-search-row">
        <label class="search" style="flex:1">Buscar jugador o club<input id="scouting-search" type="search" placeholder="Nombre de jugador, club o función..." value="${esc(sf.query)}"></label>
        <label>Ordenar<select id="scouting-sort">
          <option value="score" ${sf.sort==='score'?'selected':''}>Mayor encaje táctico</option>
          <option value="age" ${sf.sort==='age'?'selected':''}>Menor edad</option>
          <option value="wage" ${sf.sort==='wage'?'selected':''}>Menor salario</option>
        </select></label>
      </div>
      <div class="formation-pills" role="group" aria-label="Filtrar por posición">
        ${positionsList.map(p => `
          <button type="button" class="formation-pill ${sf.position===p.id?'active':''}" data-scout-position="${p.id}">${p.label}</button>
        `).join('')}
      </div>
    </div>

    <div class="scouting-grid">
      ${filtered.length ? filtered.map(p => {
        const natPos = (p.natural_positions || [p.position_primary]).map(pos).join(' · ');
        const topAttrs = Object.entries(p.attributes || {})
          .filter(([k, v]) => typeof v === 'number')
          .sort((a, b) => b[1] - a[1])
          .slice(0, 4)
          .map(([k, v]) => `${data.attributes?.[k] || k}: ${v}`);

        return `
          <article class="scout-card">
            <div class="scout-card-top">
              <div>
                <h3 class="scout-card-name">${esc(p.name)}</h3>
                <div class="scout-card-sub">${p.age ?? '—'} años · ${esc(p.club_name)}</div>
              </div>
              <div class="scout-card-score">
                ${score(p.score)}
              </div>
            </div>

            <div class="scout-card-tags">
              <span class="pos-badge-primary">${esc(pos(p.position_primary))}</span>
              <span class="role-badge-subtle">${esc(p.best_role)}</span>
              <small class="muted">${esc(natPos)}</small>
            </div>

            <div class="scout-card-attrs">
              <span class="attrs-label">Atributos destacados:</span>
              <div class="attr-chips">
                ${topAttrs.map(a => `<span class="attr-chip">${esc(a)}</span>`).join('')}
              </div>
            </div>

            <div class="scout-card-financials">
              <span><strong>Salario:</strong> ${p.wage ? '€' + number(p.wage) + '/sem' : '—'}</span>
              <span><strong>Contrato:</strong> ${p.contract_end ? esc(date(p.contract_end)) : '—'}</span>
            </div>

            <div class="scout-card-verdict">
              <span class="verdict-icon">⚡</span>
              <span class="verdict-text">Recomendado para reforzar el puesto de <strong>${esc(pos(p.position_primary))}</strong> como <em>${esc(p.best_role)}</em>.</span>
            </div>
          </article>
        `;
      }).join('') : `
        <div class="scouting-empty">
          <p class="empty">No se encontraron futbolistas con los filtros seleccionados.</p>
        </div>
      `}
    </div>
  </section>`;
}


export function companionView(state) {
  const {data, analysis, currentResult} = state;
  const isCurrent = state.view === 'current' && currentResult;
  const tactic = state.prefs?.formation === 'auto' ? analysis?.requested_tactic || analysis?.tactics?.[0] : state.simulation;
  const club = data?.club || 'Tu club';
  const formationName = isCurrent ? currentResult.name : (tactic?.name || state.prefs?.formation || '4-3-3');
  const styleName = isCurrent ? (data?.styles?.[currentResult.style]?.name || currentResult.style) : (data?.styles?.[state.prefs?.style]?.name || 'Posesión');
  const contextTag = isCurrent ? 'MINI-HUD · MI TÁCTICA' : 'MINI-HUD · PROPUESTAS';

  const actions = [];
  if (isCurrent && currentResult?.advice) {
    for (const a of currentResult.advice) {
      if (a.action) {
        const itemId = (a.player_uid || 'team') + '_' + (a.category || a.title);
        actions.push({
          id: itemId,
          title: a.title,
          text: a.action,
          phase: a.phase_label || (a.phase==='ip'?'Con posesión':a.phase==='oop'?'Sin posesión':'Equipo')
        });
      }
    }
  } else if (tactic?.tactical_recommendations) {
    for (const a of tactic.tactical_recommendations) {
      if (a.action) {
        const itemId = 'prop_' + (a.category || a.title);
        actions.push({
          id: itemId,
          title: a.title,
          text: a.action,
          phase: 'Propuesta'
        });
      }
    }
  }
  if (!actions.length) {
    actions.push({id: 'once', title: 'Confirmar once', text: 'Verificá el once titular en FM antes de iniciar.', phase: 'Pre-partido'});
    actions.push({id: 'roles', title: 'Verificar roles', text: 'Revisá que los roles asignados coincidan con el plan táctico.', phase: 'Pre-partido'});
  }

  return `
    <div class="companion-shell">
      <div class="companion-header">
        <div class="companion-title-row">
          <span class="companion-brand">⚡ TOUCHLINE GUÍA PARA FM</span>
          <span class="companion-tag">${esc(contextTag)}</span>
        </div>
        <h2>${esc(club)}</h2>
        <div class="companion-meta">
          <span class="meta-pill">${esc(formationName)}</span>
          <span class="meta-pill">${esc(styleName)}</span>
          <span class="meta-pill">Mentalidad ${esc(tactic?.mentality || 'Positiva')}</span>
        </div>
      </div>

      <div class="companion-body">
        <section class="companion-section">
          <div class="section-top">
            <h3>📋 Ajustes para aplicar en FM</h3>
            <span class="muted">${actions.length} acciones</span>
          </div>
          <div class="companion-checklist">
            ${actions.map((act) => {
              const isChecked = localStorage.getItem('touchline:chk:' + act.id) === '1';
              return `
              <label class="companion-check-item ${isChecked ? 'checked' : ''}">
                <input type="checkbox" data-companion-check="${esc(act.id)}" ${isChecked ? 'checked' : ''}>
                <div class="check-content">
                  <div class="check-title-row">
                    <strong>${esc(act.title)}</strong>
                    <span class="phase-mini-tag">${esc(act.phase || '')}</span>
                  </div>
                  <p>${esc(act.text)}</p>
                </div>
              </label>
            `;}).join('')}
          </div>
        </section>
      </div>

      <div class="companion-footer">
        <button class="button primary" data-action="copy-match-instructions">📋 Copiar ajustes</button>
        <button class="button" data-action="close-dialog">Cerrar</button>
      </div>
    </div>
  `;
}
