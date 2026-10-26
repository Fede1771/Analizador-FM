from pathlib import Path

p = Path("web/views.js")
c = p.read_text(encoding="utf-8")
c_norm = c.replace("\r\n", "\n")

# 1. Update overview match card
old_match_block = """    <article class="exec-card exec-card-match">
      <div class="exec-card-header">
        <div class="exec-card-title">
          <span class="exec-icon">⚽</span>
          <div>
            <h3>Próximo Partido</h3>
            <small>${first ? esc(first.name) + ' · Posesión' : 'Táctica activa'}</small>
          </div>
        </div>
        <span class="score-pill">${first ? number(first.score) : '—'}<small>/100</small></span>
      </div>
      <div class="exec-card-body">
        <div class="exec-alert-box alert-match">
          <span class="exec-alert-icon">⚡</span>
          <div>
            <strong>3 ajustes tácticos sugeridos antes de jugar</strong>
            <p>Wharton a MC defensivo, entradas normales en Ekitiké y cobertura de Vušković.</p>
          </div>
        </div>
      </div>
      <div class="exec-card-footer">
        <button class="button primary" data-view="current">Ver checklist de partido →</button>
        <button class="button" data-action="companion">⚡ Abrir Mini-HUD</button>
      </div>
    </article>"""

new_match_block = """    <article class="exec-card exec-card-match">
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
    </article>"""

assert old_match_block in c_norm, "old_match_block not found in views.js"
c_norm = c_norm.replace(old_match_block, new_match_block, 1)

# Also update overview header buttons
old_ov_btn = '<button class="button primary" data-action="companion">⚡ Mini-HUD Flotante</button>'
new_ov_btn = '<button class="button primary" data-action="companion">⚡ Guía para FM</button>'
c_norm = c_norm.replace(old_ov_btn, new_ov_btn, 1)

# 2. Update tactics(state)
old_tactics_start = """export function tactics(state) {
  const {data,prefs,analysis,simulation} = state;
  const selected = prefs.formation==='auto' ? analysis?.requested_tactic || analysis?.tactics[0] : simulation;
  const pa=analysis?.prompt_analysis;
  const quickList = [
    {id:'433',label:'4-3-3'},
    {id:'352',label:'3-5-2'},
    {id:'4231',label:'4-2-3-1'},
    {id:'532',label:'5-3-2'},
    {id:'442',label:'4-4-2'},
    {id:'424',label:'4-2-4'},
    {id:'343',label:'3-4-3'},
    {id:'5212',label:'5-2-1-2'},
    {id:'auto',label:'★ Recomendada'}
  ];
  return `<div class="page-heading"><div><span class="eyebrow">Idea, estructura y decisiones</span><h1>Tácticas</h1><p>Un espacio para comparar esquemas y ajustar tu propuesta.</p></div><div class="actions"><button class="button primary" data-action="companion">⚡ Mini-HUD Flotante</button><button class="button" data-action="copy-match-instructions">📋 Copiar ajustes</button><button class="button" data-action="export">Exportar JSON</button></div></div>
    <section class="panel quick-panel">
      <div class="quick-tactics-bar">
        <div class="quick-formations-wrapper">
          <span class="quick-label">⚡ Probar formación en 1 clic:</span>
          <div class="formation-pills" role="group" aria-label="Esquemas rápidos">
            ${quickList.map(f=>`<button type="button" class="formation-pill ${prefs.formation===f.id?'active':''}" data-formation="${f.id}">${f.label}</button>`).join('')}
          </div>
        </div>
        <div class="quick-prompt-row">
          <input type="text" id="quick-prompt-input" class="quick-prompt-input" placeholder="💬 Escribí tu idea de juego o formación (ej: 3-5-2 posesión, 4-4-2 contragolpe)..." value="${esc(state.promptDraft)}">
          <button type="button" class="button primary" data-action="apply-quick-prompt">Probar idea</button>
        </div>
      </div>
    </section>
    <section class="panel controls"><div class="control-grid"><label>Estilo aplicado<select id="style-select">${Object.entries(data.styles).map(([k,s])=>`<option value="${k}" ${prefs.style===k?'selected':''}>${esc(s.name)} · ${esc(s.fm26_style)}</option>`).join('')}</select></label><label>Formación<select id="formation-select"><option value="auto" ${prefs.formation==='auto'?'selected':''}>Recomendar entre los diez esquemas</option>${data.formations_catalog.map(f=>`<option value="${f.id}" ${prefs.formation===f.id?'selected':''}>${esc(f.name)} → ${esc(f.defensive)}</option>`).join('')}</select></label></div>
    <details id="prompt-details"><summary>Ajustes avanzados de la idea de juego</summary><label for="prompt-input">Pedido táctico <small>Interpretación mediante reglas · Ctrl + Enter para aplicar</small></label><textarea id="prompt-input" maxlength="2000" rows="3" placeholder="Ej.: posesión, muchas ocasiones y evitar remates rivales">${esc(state.promptDraft)}</textarea><div class="actions"><button class="button primary" data-action="apply-prompt">Aplicar idea</button><button class="button" data-action="clear-prompt">Restablecer idea</button></div>
    ${pa?`<div class="interpretation"><strong>Interpretación aplicada</strong><p>${esc(data.styles[pa.recommended_style].name)} · ${esc(pa.recommended_mentality)}${pa.avoided.length?' · Evitar: '+esc(pa.avoided.join(', ')):''}</p>${pa.warnings.map(x=>`<p class="notice warning">${esc(x)}</p>`).join('')}<p class="muted">Podés elegir otro estilo, formación y ajustar cada instrucción debajo de la propuesta.</p></div>`:''}</details></section>"""

new_tactics_start = """export function tactics(state) {
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
    </section>"""

assert old_tactics_start in c_norm, "old_tactics_start not found in views.js"
c_norm = c_norm.replace(old_tactics_start, new_tactics_start, 1)

# 3. Update companionView(state)
idx_comp = c_norm.find("export function companionView(state) {")
assert idx_comp != -1, "companionView not found in views.js"

new_companion_view = """export function companionView(state) {
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
"""

c_norm = c_norm[:idx_comp] + new_companion_view

p.write_text(c_norm, encoding="utf-8")
print("views.js updated successfully")
