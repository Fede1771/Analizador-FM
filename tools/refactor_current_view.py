from pathlib import Path

p = Path("web/current-view.js")
c = p.read_text(encoding="utf-8")

# Helper to normalize CRLF
c_norm = c.replace("\r\n", "\n")

# Find where captureReview starts and where renderGroupedAdvice ends
idx_start = c_norm.find("function captureReview(data) {")
assert idx_start != -1, "captureReview start not found"

idx_grouped_end = c_norm.find("function options(items,selected,blank='Sin confirmar') {")
assert idx_grouped_end != -1, "options function not found"

new_review_and_advice = """function captureReview(data) {
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

"""

c_norm = c_norm[:idx_start] + new_review_and_advice + c_norm[idx_grouped_end:]

# Now update currentView
old_cv_start = "export function currentView(state) {"
idx_cv = c_norm.find(old_cv_start)
assert idx_cv != -1, "currentView start not found"

# Find details panel accordion start
idx_acc = c_norm.find('<details class="panel" id="current-editor-accordion"', idx_cv)
assert idx_acc != -1, "current-editor-accordion not found"

cv_header_and_main = """export function currentView(state) {
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

  """

c_norm = c_norm[:idx_cv] + cv_header_and_main + c_norm[idx_acc:]

p.write_text(c_norm, encoding="utf-8")
print("Successfully updated web/current-view.js")
