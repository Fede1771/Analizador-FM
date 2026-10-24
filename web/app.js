function fmTeamInstructions(t) {
  const ipItems = t.instructions.filter(i => i.phase === 'in_possession');
  const oopItems = t.instructions.filter(i => i.phase === 'out_of_possession');
  const promptCount = t.instructions.filter(i => i.origin === 'prompt').length;
  
  const groupSections = (items) => {
    const map = new Map();
    items.forEach(item => {
      const secName = item.section_name || 'General';
      const secDesc = item.section_desc || '';
      if (!map.has(secName)) map.set(secName, { name: secName, desc: secDesc, items: [] });
      map.get(secName).items.push(item);
    });
    return Array.from(map.values());
  };

  const ipSections = groupSections(ipItems);
  const oopSections = groupSections(oopItems);

  return `
  <section class="panel team-instructions-panel">
    <div class="team-instructions-header">
      <div class="team-header-left">
        <span class="tag">CONFIGURACIÓN FM26 OFICIAL</span>
        <h2>Instrucciones de equipo completas</h2>
        <p>Instrucciones exactas para replicar en el menú táctico de Football Manager 26 según tu plantilla y estilo.</p>
      </div>
      <div class="fm-tactical-badges">
        <div class="fm-tactical-badge style">
          <small>ESTILO FM26 (10 OPCIONES)</small>
          <strong>${esc(t.fm26_style || 'Tiquitaca')}</strong>
          ${t.fm26_style_alt ? `<span class="badge-sub-text">Alt: ${esc(t.fm26_style_alt)}</span>` : ''}
        </div>
        <div class="fm-tactical-badge mentality">
          <small>MENTALIDAD (7 OPCIONES)</small>
          <strong>${esc(t.fm26_mentality || 'Positiva')}</strong>
          <span class="badge-sub-text">Escala oficial FM26</span>
        </div>
      </div>
    </div>

    ${(t.tactical_recommendations && t.tactical_recommendations.length > 0) ? `
      <div class="tactical-advice-box">
        <div class="advice-header">
          <span class="advice-icon">💡</span>
          <div>
            <strong>Diagnóstico y recomendaciones tácticas para tu estilo (${esc(t.fm26_style || 'Tiquitaca')})</strong>
            <p>Observaciones analíticas sobre la coordinación de tus 25 instrucciones colectivas:</p>
          </div>
        </div>
        <div class="advice-grid">
          ${t.tactical_recommendations.map(rec => `
            <div class="advice-card ${rec.type}">
              <div class="advice-card-title">
                <span>${rec.type === 'warning' ? '⚠️' : '💡'}</span>
                <strong>${esc(rec.title)}</strong>
              </div>
              <p>${esc(rec.detail)}</p>
            </div>
          `).join('')}
        </div>
      </div>
    ` : ''}

    ${tacticalPrompt ? `
      <div class="ti-prompt-alignment-banner">
        <div class="alignment-left">
          <span class="ti-prompt-tag">💡 PLANTEO PERSONALIZADO ACTIVO (${promptCount} AJUSTES CLAVE)</span>
          <p>Instrucciones adaptadas para: <strong>"${esc(tacticalPrompt)}"</strong></p>
        </div>
        <div class="alignment-right">
          <small>Las tarjetas con distintivo <b class="tag-chip">✨ TU PLANTEO</b> son las órdenes recomendadas específicamente para reflejar tu idea en el menú de FM26.</small>
        </div>
      </div>
    ` : ''}

    <div class="team-instructions-layout">
      <!-- Panel Con posesión -->
      <div class="phase-instructions-block ip-block">
        <div class="phase-header">
          <div class="phase-title">
            <span class="phase-indicator ip"></span>
            <h3>Con posesión <small>(${esc(t.name)})</small></h3>
          </div>
          <span class="phase-count">${ipItems.length} instrucciones</span>
        </div>

        ${ipSections.map(sec => `
          <div class="instruction-section">
            <div class="instruction-section-title">
              <h4>${esc(sec.name)}</h4>
              ${sec.desc ? `<small>${esc(sec.desc)}</small>` : ''}
            </div>
            <div class="ti-cards-grid">
              ${sec.items.map(item => {
                const isPrompt = item.origin === 'prompt';
                return `
                <div class="ti-card ${item.origin || ''} ${isPrompt ? 'prompt-highlight' : ''}">
                  <div class="ti-card-top">
                    <span class="ti-prop-name">${esc(item.property)}</span>
                    ${isPrompt ? `<span class="ti-prompt-badge">✨ TU PLANTEO</span>` : ''}
                  </div>
                  <strong class="ti-value-text ${isPrompt ? 'highlight' : ''}">${esc(item.value)}</strong>
                  ${item.reason ? `<p class="ti-reason ${isPrompt ? 'prompt-reason' : ''}">${esc(item.reason)}</p>` : ''}
                </div>`;
              }).join('')}
            </div>
          </div>
        `).join('')}
      </div>

      <!-- Panel Sin posesión -->
      <div class="phase-instructions-block oop-block">
        <div class="phase-header">
          <div class="phase-title">
            <span class="phase-indicator oop"></span>
            <h3>Sin posesión <small>(${esc(t.defensive)})</small></h3>
          </div>
          <span class="phase-count">${oopItems.length} instrucciones</span>
        </div>

        ${oopSections.map(sec => `
          <div class="instruction-section">
            <div class="instruction-section-title">
              <h4>${esc(sec.name)}</h4>
              ${sec.desc ? `<small>${esc(sec.desc)}</small>` : ''}
            </div>
            <div class="ti-cards-grid">
              ${sec.items.map(item => {
                const isPrompt = item.origin === 'prompt';
                return `
                <div class="ti-card ${item.origin || ''} ${isPrompt ? 'prompt-highlight' : ''}">
                  <div class="ti-card-top">
                    <span class="ti-prop-name">${esc(item.property)}</span>
                    ${isPrompt ? `<span class="ti-prompt-badge">✨ TU PLANTEO</span>` : ''}
                  </div>
                  <strong class="ti-value-text ${isPrompt ? 'highlight' : ''}">${esc(item.value)}</strong>
                  ${item.reason ? `<p class="ti-reason ${isPrompt ? 'prompt-reason' : ''}">${esc(item.reason)}</p>` : ''}
                </div>`;
              }).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  </section>`;
}

'use strict';
const $ = s => document.querySelector(s);
const esc = v => String(v ?? '—').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const icons = {overview:'◫',tactics:'⌘',squad:'☷',academy:'◇',loans:'↗',method:'ⓘ'};
const nav = {overview:'Centro del club',tactics:'Laboratorio táctico',squad:'Plantilla',academy:'Inferiores',loans:'Cedidos',method:'Cómo se calcula'};
let data, analysis, view='overview', selectedTactic=0, phase='ip', query='', filter='all', order='score', uploadBusy=false, analysisBusy=false, tacticalPrompt='', loanTab='performance';
let syncStatus=null, lastKnownDatasetId=null;
let prefs={primary:0,labels:{}}, excluded=new Set(), style='possession';
let requestVersion=0;
let uploadInfo={message:'Seleccioná tu partida',progress:0};
let showWelcome=true;
const playerById = id => [...data.players,...data.loans].find(p => p.uid===Number(id));
const profile = p => analysis.profiles[p.uid];
const senior = () => data.players.filter(p=>p.team_slot===prefs.primary);
const youth = () => data.players.filter(p=>p.team_slot!==prefs.primary);
const initials = name => name.split(' ').map(p=>p[0]).slice(0,2).join('');
const score = value => `<span class="score ${value>=75?'good':value>=60?'mid':'low'}">${Number(value).toFixed(1)}</span>`;
const groupName = slot => prefs.labels[slot] || data?.slot_labels?.[slot] || (slot===prefs.primary?'Primer equipo':`Grupo ${slot}`);
const dateLabel = value => value?new Intl.DateTimeFormat('es-AR',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(value+'T12:00:00Z')):'Fecha no disponible';

function syncPill(){
  if(uploadBusy){
    return `<button class="button subtle sync-pill syncing" id="sync-status-btn" title="Extrayendo y analizando partida de FM26…"><span class="sync-dot pulsing"></span><span>Sincronizando…</span></button>`;
  }
  if(!syncStatus){
    return `<button class="button subtle sync-pill" id="sync-status-btn" title="Configuración de auto-sincronización FM26"><span class="sync-dot green"></span><span>Auto-Sync FM26</span></button>`;
  }
  const st=syncStatus.state;
  if(st==='paused'){
    return `<button class="button subtle sync-pill paused" id="sync-status-btn" title="Sincronización pausada. Hacé clic para reanudar."><span class="sync-dot gray"></span><span>Sync pausado</span></button>`;
  }
  if(st==='folder_not_found'){
    return `<button class="button subtle sync-pill warning" id="sync-status-btn" title="Carpeta de partidas no encontrada: ${esc(syncStatus.watch_folder)}"><span class="sync-dot yellow"></span><span>Carpeta no hallada</span></button>`;
  }
  const label=syncStatus.active_file||'Esperando guardado';
  return `<button class="button subtle sync-pill active" id="sync-status-btn" title="Monitoreando en vivo: ${esc(label)} (${syncStatus.active_file_size_mb?syncStatus.active_file_size_mb+' MB':'FM26'})"><span class="sync-dot green"></span><span>FM26: ${esc(label)}</span></button>`;
}

const playerName = p => `<button class="player-link" data-player="${p.uid}"><span class="avatar">${esc(initials(p.name))}</span><span>${esc(p.name)}<small>${p.age??'—'} años · ${esc(p.natural_positions.join(' / '))}</small></span></button>`;
function savePrefs(){localStorage.setItem('touchline:'+data.id,JSON.stringify({...prefs,excluded:[...excluded],style,prompt:tacticalPrompt}));}
function restorePrefs(){
  try {const p=JSON.parse(localStorage.getItem('touchline:'+data.id)||'null'); if(p){prefs={primary:p.primary,labels:p.labels||{}};excluded=new Set(p.excluded||[]);style=data.styles[p.style]?p.style:'possession';tacticalPrompt=p.prompt||'';}}
  catch {prefs={primary:data.slots[0],labels:{}};excluded=new Set();tacticalPrompt='';}
  if(!data.slots.includes(prefs.primary))prefs.primary=data.slots[0];
}
function toast(message,error=false){const t=$('#toast');t.textContent=message;t.className='show'+(error?' error':'');clearTimeout(toast.timer);toast.timer=setTimeout(()=>t.className='',6000);}
async function api(path,options={}){const r=await fetch(path,options);const d=await r.json();if(!r.ok)throw Error(d.error||'No se pudo completar la operación.');return d;}
async function calculate(promptOverride){
  if(promptOverride!==undefined)tacticalPrompt=promptOverride;
  const version=++requestVersion;analysisBusy=true;render();
  try{
    const result=await api('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json','X-FM-App':'1'},body:JSON.stringify({dataset_id:data.id,style,primary_slot:prefs.primary,excluded:[...excluded],prompt:tacticalPrompt})});
    if(version!==requestVersion)return;
    analysis=result;selectedTactic=0;analysisBusy=false;render();
  }catch(e){if(version!==requestVersion)return;analysisBusy=false;analysis=null;render();toast(e.message,true);}
}
function render(){
  if(!data||showWelcome){renderWelcome();return;}
  const counts={squad:data.players.length,academy:youth().length,loans:data.loans.length};
  $('#app').innerHTML=`<aside class="sidebar"><a class="brand" href="#overview" data-view="overview"><span class="brand-icon">T<span>·</span></span><span>touchline<small>FOOTBALL INTELLIGENCE</small></span></a>
    <div class="workspace-label">TU ESPACIO DE TRABAJO</div>
    <nav aria-label="Navegación principal">${Object.entries(nav).map(([key,label])=>`<button data-view="${key}" class="nav-item ${view===key?'active':''}" ${view===key?'aria-current="page"':''}><span class="nav-icon">${icons[key]}</span>${label}${counts[key]!=null?`<span class="nav-count">${counts[key]}</span>`:''}</button>`).join('')}</nav>
    <div class="sidebar-bottom"><div class="local-dot"></div><span>Tu partida, en tu equipo<small>Procesamiento local · FM26</small></span></div></aside>
    <div class="main-shell"><header class="topbar"><div class="breadcrumb">Mi club <span>/</span> <strong>${nav[view]}</strong></div><div class="top-actions">${syncPill()}<span class="save-date">${esc(dateLabel(data.date))}</span><button class="button subtle" id="settings-button">⚙ <span>Grupos</span></button><button class="button primary" id="import-button" ${uploadBusy?'disabled':''}>↥ <span>${uploadBusy?'Importando…':'Importar partida'}</span></button></div></header>
    <main><div class="page-heading"><div><div class="eyebrow">FM26 / ${esc(data.manager||'MANAGER')}</div><h1>${view==='overview'?esc(data.club):nav[view]}</h1><p>${subheading()}</p></div>${view!=='method'?`<button class="button subtle" id="export-button" aria-label="Exportar análisis"><span aria-hidden="true">↓</span><span class="export-label">Exportar análisis</span></button>`:''}</div>
    <div class="source-file">ARCHIVO ANALIZADO <strong>${esc(data.source?.filename||'Partida importada')}</strong> · ${data.players.length} jugadores · ${data.loans.length} cedidos</div>
    ${uploadBusy?importProgress():''}
    ${data.warnings.length?`<div class="notice">El lector emitió ${data.warnings.length} advertencia(s). Revisá los datos antes de tomar decisiones.</div>`:''}
    ${uploadBusy?`<div class="loading-panel"><span class="spinner"></span><h2>Tu nueva partida, bajo análisis</h2><p>Detectamos el club, analizamos los equipos y preparamos todas las propuestas.</p><p>El resultado anterior se conserva hasta que el nuevo análisis esté listo.</p></div>`:analysisBusy?`<div class="loading-panel"><span class="spinner"></span><h2>Buscando el mejor equilibrio</h2><p>Comparando atributos, posiciones y combinaciones del equipo…</p></div>`:!analysis?`<div class="empty"><h2>No se pudo completar el análisis</h2><button class="button primary" id="retry-button">Reintentar</button></div>`:content()}
    <footer>TOUCHLINE <span>Lectura local · ${esc(data.build)} · Datos aún pendientes de cotejo con FM</span></footer>
    </main></div>`;
  bind();
}
function importProgress(){return `<div id="upload-status" class="upload-status" role="status" aria-live="polite"><span class="spinner"></span><span id="upload-message">${esc(uploadInfo.message)}</span><progress id="upload-progress" max="100" ${uploadInfo.progress==null?'':`value="${uploadInfo.progress}"`} aria-label="Progreso del análisis"></progress></div>`;}
function updateImport(message,progress=null){uploadInfo={message,progress};if($('#upload-message'))$('#upload-message').textContent=message;const bar=$('#upload-progress');if(bar){if(progress==null)bar.removeAttribute('value');else bar.value=progress;}}
function renderWelcome(){
 $('#app').innerHTML=`<div class="welcome-shell"><header class="welcome-header"><div class="brand"><span class="brand-icon">T<span>·</span></span><span>touchline<small>FOOTBALL INTELLIGENCE</small></span></div><span class="local-badge"><i></i> Análisis local · FM26</span></header><main class="welcome-main"><span class="tag">DE TU PARTIDA A UN PLAN DE JUEGO</span><h1>Cargá tu partida.<br><em>Encontrá tu equipo.</em></h1><p>Tu plantilla, tus juveniles y tus cedidos. Subí el archivo guardado y recibí un análisis construido con los jugadores de tu club.</p>${uploadBusy?`${importProgress()}<div class="welcome-processing"><span class="spinner"></span><h2>Estamos preparando tu análisis</h2><p>La lectura de una partida grande puede tardar unos minutos. Los cuatro estilos se calculan automáticamente.</p></div>`:`<button class="upload-drop" id="import-button"><span class="upload-symbol">↥</span><strong>Elegí o arrastrá tu partida .fm</strong><span>FM26 · Hasta 400 MB · Se procesa en tu equipo</span><b>Cargar y analizar partida →</b></button>`}<div class="welcome-steps"><article><span>01</span><h2>Cargás el archivo</h2><p>Detectamos tu club y leemos los datos de los jugadores.</p></article><article><span>02</span><h2>Analizamos todo el club</h2><p>Primer equipo, grupos de inferiores, cedidos y focos de entrenamiento.</p></article><article><span>03</span><h2>Elegís cómo jugar</h2><p>Explorás formaciones, funciones e instrucciones según tu estilo.</p></article></div><p class="welcome-note">La partida original no se modifica. Las recomendaciones se generan con atributos visibles y deben probarse en FM.</p></main></div>`;
 if(data&&!uploadBusy){const previous=document.createElement('div');previous.className='previous-analysis';previous.innerHTML=`<span>Último análisis: <strong>${esc(data.club)}</strong> · ${esc(dateLabel(data.date))}</span><button class="button subtle" id="resume-analysis">Ver análisis anterior →</button>`;$('.welcome-main').insertBefore(previous,$('.welcome-steps'));$('#resume-analysis').onclick=async()=>{showWelcome=false;prefs.primary=data.default_primary_slot;restorePrefs();await calculate();};}
 if($('#import-button')){const drop=$('#import-button');drop.onclick=()=>$('#save-file').click();drop.ondragover=e=>{e.preventDefault();drop.classList.add('dragover');};drop.ondragleave=()=>drop.classList.remove('dragover');drop.ondrop=e=>{e.preventDefault();drop.classList.remove('dragover');startImport(e.dataTransfer.files[0]);};}
}
function subheading(){return ({overview:'Conocé tu equipo. Encontrá su mejor versión.',tactics:'Elegí una idea de juego y explorá cómo encaja tu equipo.',squad:'Atributos, funciones y alternativas. Cada decisión con sus razones.',academy:'Del fútbol formativo al primer equipo, con un plan para cada jugador.',loans:'Seguí a los jugadores que se están desarrollando fuera del club.',method:'Un análisis transparente, construido sobre los datos de tu partida.'})[view];}
function styleBar(){return `<div class="style-bar"><div><span class="eyebrow">TU IDEA DE JUEGO</span><strong>${esc(data.styles[style].description)}</strong></div><div class="segmented" role="group" aria-label="Estilo de juego">${Object.entries(data.styles).map(([key,s])=>`<button data-style="${key}" class="${style===key?'selected':''}" aria-pressed="${style===key}">${esc(s.name)} <small class="style-pill-sub">${esc(s.fm26_style||'')} · ${esc(s.mentality||'')}</small></button>`).join('')}</div></div>`;}
function stat(label,value,detail,icon){return `<article class="stat"><div class="stat-label">${label}<span>${icon}</span></div><div class="stat-value">${value}</div><div class="stat-detail">${detail}</div></article>`;}
function sectionTitle(title,subtitle,viewLink){return `<div class="section-heading"><div><h2>${title}</h2>${subtitle?`<p>${subtitle}</p>`:''}</div>${viewLink?`<button class="text-button" data-view="${viewLink}">Ver todo ↗</button>`:''}</div>`;}
function content(){switch(view){case'overview':return overview();case'tactics':return tactics();case'squad':return squad();case'academy':return academy();case'loans':return loans();case'method':return methodology();}}
function overview(){
 const young=youth().filter(p=>p.age!=null&&p.age<=21), avg=senior().length?(senior().reduce((a,p)=>a+(p.age||0),0)/senior().length).toFixed(1):'—';
 const best=analysis.tactics[0], prospects=analysis.academy.slice(0,4);
 return `<div class="stats-grid">${stat('Primer equipo',senior().length,`${avg} años de edad media`,'◫')}${stat('Inferiores',youth().length,`${young.length} jugadores de hasta 21 años`,'◇')}${stat('Cedidos fuera',data.loans.length,'Analizados por separado','↗')}${stat('Para probar arriba',analysis.academy.filter(p=>p.gap!=null&&p.gap>=-3).length,'Por encaje actual · sujeto a evaluación','✧')}</div>
 ${styleBar()}<div class="overview-grid"><section class="panel tactical-preview">${sectionTitle('Tu punto de partida','La estructura que mejor encaja entre las tres evaluadas.','tactics')}${best?`<div class="formation-banner"><div><span class="tag">MAYOR ENCAJE ACTUAL</span><h3>${best.name} <small>→ ${best.defensive} sin balón</small></h3></div>${score(best.score)}</div>${pitch(best,'ip',true)}<div class="preview-bottom"><span>Índice propio de encaje /100</span><button class="text-button" data-view="tactics">Explorar propuesta →</button></div>`:emptyTactics()}</section>
 <section class="panel">${sectionTitle('El próximo paso','Jugadores de inferiores más cerca de tus opciones actuales.','academy')}<div class="prospect-list">${prospects.map((p,i)=>{const x=playerById(p.uid);return `<div class="prospect"><span class="rank">0${i+1}</span><div>${playerName(x)}<div class="prospect-role">${esc(profile(x).role_name)}</div></div><div>${score(profile(x).score)}<small class="gap">${gapLabel(p.gap)}</small></div></div>`;}).join('')||'<div class="empty">No hay jugadores en otros grupos.</div>'}</div><div class="callout"><span>◇</span><p>El encaje mide su nivel actual. Una buena puntuación no garantiza su desarrollo futuro.</p></div></section></div>
 <section class="panel">${sectionTitle('Una cantera con dirección','Tres decisiones posibles según su distancia al primer equipo.','academy')}<div class="path-grid">${[['Probar con el primer equipo','Integración gradual','Entrenamientos y minutos de rotación.'],['Desarrollar en inferiores','Tiempo para crecer','Entrenamiento y competición juvenil.'],['Evaluar minutos o cesión','Un lugar para jugar','Valorar una cesión si faltan oportunidades.']].map(([a,t,d])=>`<article><span class="path-count">${analysis.actions[a]||0}</span><h3>${t}</h3><p>${d}</p></article>`).join('')}</div></section>`;
}
function pitch(t,which,compact=false){return `<div class="pitch ${compact?'compact':''}" aria-label="Formación ${esc(which==='ip'?t.name:t.defensive)} ${which==='ip'?'con':'sin'} posesión"><div class="pitch-boundary"></div><div class="halfway"></div><div class="center-circle"></div><div class="penalty top"></div><div class="penalty bottom"></div><div class="goal top"></div><div class="goal bottom"></div><span class="pitch-direction">↑ DIRECCIÓN DE ATAQUE</span>${t.lineup.map((l,i)=>{const p=playerById(l.uid),[x,y]=l[which];return `<button class="pitch-player" data-player="${p.uid}" style="left:${x}%;top:${y}%" aria-label="Ver ${esc(p.name)}"><span class="shirt ${l.role_id==='gk'?'keeper':''}">${i+1}</span><strong>${esc(p.name.split(' ').slice(-1)[0])}</strong><small>${l.score.toFixed(0)}</small></button>`;}).join('')}</div>`;}
function emptyTactics(){return `<div class="empty"><h3>Faltan jugadores para completar un once</h3><p>Hay ${analysis.senior_count} disponibles. Revisá las exclusiones o el grupo principal.</p><button class="button subtle" id="settings-inline">Configurar grupos</button></div>`;}
function tacticalPromptBox(){
  const pa=analysis?.prompt_analysis;
  return `<section class="panel tactical-prompt-panel">
    <div class="prompt-header">
      <span class="tag">LABORATORIO TÁCTICO INTELIGENTE</span>
      <h2>Definí tu idea de juego con tus propias palabras</h2>
      <p>Escribí cómo querés que juegue tu equipo en FM26 (posesión, llegadas, remates, solidez, contraataque, presión alta). El sistema interpretará tu planteo, optimizará las 3 mejores formaciones, la alineación ideal y definirá todas las instrucciones necesarias.</p>
    </div>
    <div class="prompt-input-row">
      <textarea id="prompt-input" rows="2" placeholder="Ej.: Quiero jugar con mucha posesión e intentar tener muchas chances de gol y evitar que me rematen mucho al arco">${esc(tacticalPrompt||'')}</textarea>
      <div class="prompt-actions">
        <button class="button primary" id="btn-apply-prompt">Optimizar táctica ✨</button>
        ${tacticalPrompt?`<button class="button subtle" id="btn-clear-prompt">Restablecer táctica</button>`:''}
      </div>
    </div>
    <div class="prompt-suggestions">
      <small>Sugerencias tácticas:</small>
      <button class="prompt-chip" data-prompt="Quiero jugar con mucha posesión e intentar tener muchas chances de gol y evitar que me rematen mucho al arco">Posesión, ocasiones y evitar remates</button>
      <button class="prompt-chip" data-prompt="Presión alta asfixiante, recuperar rápido en campo rival y transiciones letales">Presión alta y transiciones</button>
      <button class="prompt-chip" data-prompt="Juego por bandas con extremos abiertos, centros al área y bloque sólido">Juego por bandas y centros</button>
      <button class="prompt-chip" data-prompt="Control paciente de la pelota, pases cortos y arco en cero">Control y solidez defensiva</button>
    </div>
    ${pa?`
      <div class="prompt-interpretation">
        <div class="interpretation-header">
          <div>
            <strong>💡 Planteo interpretado y aplicado a tu equipo:</strong>
            <div class="prompt-meta-row">
              <span class="fm-meta-chip style">📋 Estilo FM26: <b>${esc(data.styles[pa.recommended_style]?.fm26_style||'Tiquitaca')}</b></span>
              <span class="fm-meta-chip mentality">⚡ Mentalidad FM26: <b>${esc(pa.recommended_mentality||'Positiva')}</b></span>
            </div>
          </div>
          <div class="pillar-tags">${pa.pillars.map(x=>`<span class="tag tag-${x.color}">${esc(x.badge)}</span>`).join('')}</div>
        </div>
        <div class="pillar-grid">
          ${pa.pillars.map(pill=>`
            <div class="pillar-card pillar-${pill.color}">
              <div class="pillar-top">
                <span class="pillar-badge">${esc(pill.badge)}</span>
                <h4>${esc(pill.title)}</h4>
              </div>
              <p>${esc(pill.summary)}</p>
              <div class="pillar-fm-instruction"><strong>FM26:</strong> ${esc(pill.fm26_instruction)}</div>
            </div>
          `).join('')}
        </div>
        ${pa.player_guides&&pa.player_guides.length?`
          <div class="player-guides-box">
            <strong>Pautas tácticas individuales recomendadas (Guía de roles FM26):</strong>
            <ul>${pa.player_guides.map(g=>`
              <li>
                <b>${esc(g.line||g)}:</b> ${esc(g.tip||'')}
                ${g.guide_ref?`<span class="guide-ref-pill">📖 ${esc(g.guide_ref)}</span>`:''}
              </li>
            `).join('')}</ul>
          </div>
        `:''}
      </div>
    `:''}
  </section>`;
}
function benchPanel(t) {
  const replacements = t.bench_replacements || [];
  if (!replacements.length) {
    const fallbackIds = t.bench || [];
    if (!fallbackIds.length) return '';
    return `
    <div class="bench-replacement-section">
      <div class="bench-header">
        <div class="bench-header-title">
          <span class="tag">BANCO DE SUPLENTES</span>
          <h3>Alternativas disponibles (${fallbackIds.length})</h3>
        </div>
      </div>
      <div class="bench-cards-list">
        ${fallbackIds.map(id => playerName(playerById(id))).join('')}
      </div>
    </div>`;
  }

  const lineStats = { GK: 0, DEF: 0, MID: 0, ATT: 0 };
  replacements.forEach(b => {
    const pos = (b.replaces_position || '').toUpperCase();
    if (pos === 'GK') lineStats.GK++;
    else if (['DL', 'DC', 'DR', 'WBL', 'WBR'].includes(pos)) lineStats.DEF++;
    else if (['DM', 'CM', 'MC', 'AM', 'AMC'].includes(pos)) lineStats.MID++;
    else lineStats.ATT++;
  });

  return `
  <div class="bench-replacement-section">
    <div class="bench-header">
      <div class="bench-header-title">
        <span class="tag">SUPLENTES Y JERARQUÍA DE RECAMBIOS</span>
        <h3>Banco de suplentes · Mejor nivel para reemplazar</h3>
      </div>
      <div class="bench-line-summary">
        ${lineStats.GK ? `<span class="line-badge gk">🧤 ${lineStats.GK} Arquero</span>` : ''}
        ${lineStats.DEF ? `<span class="line-badge def">🛡️ ${lineStats.DEF} Defensas</span>` : ''}
        ${lineStats.MID ? `<span class="line-badge mid">⚙️ ${lineStats.MID} Medios</span>` : ''}
        ${lineStats.ATT ? `<span class="line-badge att">⚡ ${lineStats.ATT} Ataque</span>` : ''}
      </div>
    </div>
    <p class="bench-desc">
      A qué titular de los once reemplaza mejor cada suplente según su rol, familiaridad posicional y atributos para entrar al partido con el mayor nivel posible.
    </p>

    <div class="bench-cards-list">
      ${replacements.map(b => {
        const qualityClass = b.quality || 'reliable';
        return `
        <div class="bench-card ${qualityClass}">
          <div class="bench-card-main">
            <button class="player-link" data-player="${b.uid}">
              <span class="avatar">${esc(initials(b.name))}</span>
              <div class="bench-player-info">
                <strong>${esc(b.name)}</strong>
                <small>${b.age ?? '—'} años · ${esc((b.natural_positions || []).join(' / '))}</small>
              </div>
            </button>
            <div class="bench-score-col">
              <span class="bench-score-label">Encaje individual</span>
              ${score(b.score)}
            </div>
          </div>

          <div class="bench-replacement-detail">
            <div class="replacement-target-row">
              ${b.gap > 0 ? `
                <span class="rel-badge better">🔥 TIENE MEJOR NIVEL QUE:</span>
                <span class="rel-name">
                  <strong>${esc(b.replaces_name)}</strong> 
                  <small>(${esc(b.replaces_position)} · ${esc(b.replaces_role)})</small>
                </span>
                <span class="rel-gap-pill good">+${Number(b.gap).toFixed(1)} vs titular</span>
              ` : b.gap === 0 ? `
                <span class="rel-badge equal">⚖️ EMPATA EN NIVEL CON:</span>
                <span class="rel-name">
                  <strong>${esc(b.replaces_name)}</strong> 
                  <small>(${esc(b.replaces_position)})</small>
                </span>
                <span class="rel-gap-pill good">Mismo nivel</span>
              ` : `
                <span class="rel-badge alt">⭐ ALTERNATIVA DIRECTA A:</span>
                <span class="rel-name">
                  <strong>${esc(b.replaces_name || 'Rotación')}</strong> 
                  <small>(${esc(b.replaces_position || 'Puesto')} · ${esc(b.replaces_role || '')})</small>
                </span>
                <span class="rel-gap-pill ${b.gap >= -1.5 ? 'good' : b.gap >= -4.5 ? 'mid' : 'low'}">
                  ${Number(b.gap).toFixed(1)} vs titular
                </span>
              `}
            </div>
            ${b.better_than_starters && b.better_than_starters.length > 0 ? `
              <div class="beaten-starters-pill">
                <span class="beaten-tag">⚡ Supera en valoración a ${b.better_than_starters.length} del Once Titular:</span>
                <span class="beaten-list">${b.better_than_starters.map(s => `<b>${esc(s.name.split(' ').slice(-1)[0])}</b> (${s.score.toFixed(0)})`).join(' · ')}</span>
              </div>
            ` : ''}
            <div class="bench-quality-row">
              <span class="bench-quality-pill ${qualityClass}">${esc(b.quality_label)}</span>
              <small class="bench-role-hint">Función recomendada: <b>${esc(b.role_name)}</b> (Nivel en puesto: <b>${b.replacement_score.toFixed(1)}</b>)</small>
            </div>
          </div>
        </div>`;
      }).join('')}
    </div>
  </div>`;
}

function tactics(){
  const t=analysis.tactics[selectedTactic], s=data.styles[style];
  return `${styleBar()}
  ${tacticalPromptBox()}
  <div class="notice quiet">Español latinoamericano de FM26 26.3.2, verificado con capturas de pantalla de los menús del juego. Roles e instrucciones cotejados directamente. Los índices son propios de encaje sobre 100 puntos.</div>
  ${!t?emptyTactics():`
  <div class="top-formations-heading">
    <div>
      <span class="tag">TOP 3 FORMACIONES</span>
      <h2>Las 3 mejores formaciones para tu equipo</h2>
      <p>Rankeadas según el encaje global del plantel tanto con posesión como sin posesión${analysis.custom_prompt?' bajo tu planteo táctico personalizado':''}.</p>
    </div>
  </div>
  <div class="formation-options">
    ${analysis.tactics.map((x,i)=>`
      <button data-tactic="${i}" class="formation-option ${i===selectedTactic?'selected':''}">
        <div class="formation-badge-row">
          <span class="formation-rank-badge ${i===0?'first':'alt'}">${i===0?'🏆 #1 MEJOR ENCAJE':i===1?'🥈 #2 ALTERNATIVA':'🥉 #3 ALTERNATIVA'}</span>
          ${score(x.score)}
        </div>
        <strong class="formation-name">${x.name} <small class="possession-phase">Con posesión</small></strong>
        <div class="defensive-badge">🛡️ <strong>${x.defensive}</strong> <small>Sin posesión</small></div>
        
        <div class="card-fm-meta">
          <span class="fm-meta-badge style">📋 ${esc(x.fm26_style||'Tiquitaca')}</span>
          <span class="fm-meta-badge mentality">⚡ ${esc(x.fm26_mentality||'Positiva')}</span>
        </div>

        <p class="formation-idea">${esc(x.idea)}</p>
      </button>
    `).join('')}
  </div>

  <!-- Barra destacada de Estilo y Mentalidad oficial de FM26 -->
  <div class="fm26-match-banner">
    <div class="banner-group">
      <span class="banner-eyebrow">DIBUJO DE JUEGO SELECCIONADO</span>
      <h3 class="banner-title">
        <span class="ip-tag">${t.name} <small>(Con posesión)</small></span>
        <span class="banner-arrow">→</span>
        <span class="oop-tag">${t.defensive} <small>(Sin posesión)</small></span>
      </h3>
    </div>
    <div class="banner-badges">
      <div class="banner-badge style">
        <span class="badge-label">ESTILO EN MENÚ FM26</span>
        <strong class="badge-main">${esc(t.fm26_style||'Tiquitaca')}</strong>
        ${t.fm26_style_alt ? `<small class="badge-sub">Alternativa: ${esc(t.fm26_style_alt)}</small>` : ''}
      </div>
      <div class="banner-badge mentality">
        <span class="badge-label">MENTALIDAD EN MENÚ FM26</span>
        <strong class="badge-main">${esc(t.fm26_mentality||'Positiva')}</strong>
        <small class="badge-sub">Escala oficial de 7 mentalidades</small>
      </div>
    </div>
  </div>

  <div class="tactics-grid">
    <section class="panel pitch-panel">
      <div class="section-heading">
        <div>
          <h2>${t.name} <small>(${phase==='ip'?'Fase con posesión':'Fase sin posesión: '+t.defensive})</small></h2>
          <p>${esc(t.idea)}</p>
        </div>
      </div>
      <div class="segmented phase-switch">
        <button data-phase="ip" class="${phase==='ip'?'selected':''}">Con posesión (${t.name})</button>
        <button data-phase="oop" class="${phase==='oop'?'selected':''}">Sin posesión (${t.defensive})</button>
      </div>
      ${pitch(t,phase)}
      <div class="pitch-legend"><i></i> Mismos 11 jugadores adaptando su posición y rol según la fase de juego</div>
      ${benchPanel(t)}
    </section>

    <section class="panel lineup-panel">
      ${sectionTitle('Once propuesto · Roles e instrucciones individuales','Comparativa del rol en la táctica vs rol natural óptimo para cada jugador.')}
      <div class="lineup-list">
        ${t.lineup.map(l=>{
          const p=playerById(l.uid);
          return `
          <div class="lineup-card">
            <div class="lineup-card-top">
              <div class="player-info-col">
                ${playerName(p)}
                <div class="roles-comparison">
                  <div class="role-box natural">
                    <span class="role-kind-label">ROL ACTUAL / NATURAL EN EL CLUB</span>
                    <strong class="role-title">${esc(l.natural_role||l.role)} <small>(${esc(l.natural_position||'—')})</small></strong>
                    <span class="match-pill ${l.role_matches_natural?'green':'amber'}">
                      ${l.role_matches_natural?'✓ Su función natural coincide con el planteo':'⚡ Rol base en el club (adaptado a este esquema)'}
                    </span>
                  </div>
                  <div class="role-box recommended">
                    <span class="role-kind-label highlight">⭐ MEJOR ROL PARA ESTE PLANTEO (${phase==='ip'?'CON POSESIÓN':'SIN BALÓN'})</span>
                    <div class="role-title-row">
                      <strong class="role-title highlight-title">${esc(phase==='ip'?l.role:l.without_ball)}</strong>
                      ${(phase==='ip'?l.tactical_badge:l.tactical_badge_oop)?`<span class="tactical-badge-pill">${esc(phase==='ip'?l.tactical_badge:l.tactical_badge_oop)}</span>`:''}
                    </div>
                    ${(phase==='ip'?l.tactical_summary:l.tactical_summary_oop)?`<p class="tactical-summary-text"><b>En esta alineación (${esc(t.name)}):</b> ${esc(phase==='ip'?l.tactical_summary:l.tactical_summary_oop)}</p>`:''}
                  </div>
                </div>
              </div>
              <div class="lineup-score-col">
                ${score(l.score)}
              </div>
            </div>

            <div class="lineup-instructions-row">
              <span class="instructions-label">Instrucciones individuales asignadas:</span>
              <div class="instruction-chips">
                ${(l.individual_instructions||[]).map(ins=>`
                  <span class="inst-chip ${ins.origin}" title="${esc(ins.reason)}">
                    <b>${esc(ins.property)}:</b> ${esc(ins.value)}
                    <i class="origin-tag">${ins.origin==='role'?'Rol':ins.origin==='standard'?'Normal':'Ajuste'}</i>
                  </span>
                `).join('')}
              </div>
              <button class="text-button lineup-detail-btn" data-player="${p.uid}">Ver análisis y ficha completa →</button>
            </div>
          </div>`;
        }).join('')}
      </div>
    </section>
  </div>

  ${fmTeamInstructions(t)}

  <section class="panel instructions fm26-guide-panel" style="margin-top:20px">
    <h2>Cómo aplicarlo en FM26 paso a paso</h2>
    <div class="fm26-step-list">
      <div class="step-item">
        <span class="step-num">1</span>
        <div>
          <strong>Estilo y Mentalidad oficial en FM26</strong>
          <p>En el menú superior de FM26, seleccioná el estilo <strong>${esc(t.fm26_style||'Tiquitaca')}</strong> (o <em>${esc(t.fm26_style_alt||'Control de la posesión')}</em>) y la mentalidad <strong>${esc(t.fm26_mentality||'Positiva')}</strong>. Luego seleccioná <strong>${t.name}</strong> en Con posesión y <strong>${t.defensive}</strong> en Sin posesión.</p>
        </div>
      </div>
      <div class="step-item">
        <span class="step-num">2</span>
        <div>
          <strong>Instrucciones de equipo (Con y Sin posesión)</strong>
          <p>En la pestaña <em>Instr. de equipo</em>, configurá cada tarjeta según los valores de arriba (Pases, Ritmo, Estrategia previa, Líneas de presión y Activar presión).</p>
        </div>
      </div>
      <div class="step-item">
        <span class="step-num">3</span>
        <div>
          <strong>Roles e instrucciones individuales</strong>
          <p>Para cada titular en el dibujo táctico, asigná el rol indicado y ajustá las instrucciones individuales de pase, regate, tiros y desmarques.</p>
        </div>
      </div>
    </div>
    <p class="muted">Nombres y secciones cotejados directamente con los menús oficiales de FM26 en español latinoamericano.</p>
  </section>

  <section class="panel">
    <h2>Puntos a vigilar en el partido</h2>
    <ul class="risk-list">${t.risks.map(r=>`<li>${esc(r)}</li>`).join('')}</ul>
    <p class="muted">La disponibilidad médica y las sanciones del día no están verificadas. Excluí jugadores desde Plantilla antes de recalcular.</p>
  </section>

`}`;
}
function toolbar(kind){const groups=kind==='loans'?[]:data.slots.filter(s=>kind==='academy'?s!==prefs.primary:true);return `<div class="table-toolbar"><label class="search"><span>⌕</span><input id="search" type="search" placeholder="Buscar jugador o posición…" value="${esc(query)}" aria-label="Buscar jugadores"></label><div class="filters">${groups.length?`<select id="group-filter" aria-label="Filtrar grupo"><option value="all">Todos los grupos</option>${groups.map(s=>`<option value="${s}" ${filter===String(s)?'selected':''}>${esc(groupName(s))}</option>`).join('')}</select>`:''}<select id="sort-order" aria-label="Ordenar jugadores"><option value="score" ${order==='score'?'selected':''}>Mayor encaje</option><option value="age" ${order==='age'?'selected':''}>Menor edad</option><option value="name" ${order==='name'?'selected':''}>Nombre</option></select></div></div>`;}
function filtered(rows){const term=query.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();return rows.filter(p=>(filter==='all'||String(p.team_slot)===filter)&&(p.name+' '+p.natural_positions.join(' ')).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().includes(term)).sort((a,b)=>order==='age'?(a.age??99)-(b.age??99):order==='name'?a.name.localeCompare(b.name):profile(b).score-profile(a).score);}
function squad(){return `${styleBar()}<section class="panel">${toolbar('squad')}<div id="results">${playerTable(filtered(data.players))}</div></section><div class="notice quiet">Desmarcá “Disponible” para excluir a un jugador del once. La selección se guarda en este navegador para esta partida.</div>`;}
function playerTable(rows){return `<div class="table-scroll"><table><thead><tr><th>Jugador</th><th>Grupo</th><th>Mejor función</th><th>Encaje</th><th>Pases</th><th>Técnica</th><th>Velocidad</th><th>Disponible</th></tr></thead><tbody>${rows.map(p=>`<tr class="${excluded.has(p.uid)?'excluded':''}"><td>${playerName(p)}</td><td><span class="group-tag">${esc(groupName(p.team_slot))}</span></td><td>${esc(profile(p).role_name)}</td><td>${score(profile(p).score)}</td><td>${p.attributes.passing}</td><td>${p.attributes.technique}</td><td>${p.attributes.pace}</td><td><input class="available" type="checkbox" data-available="${p.uid}" ${excluded.has(p.uid)?'':'checked'} aria-label="Incluir a ${esc(p.name)}"></td></tr>`).join('')}</tbody></table>${rows.length?'':'<div class="empty">No encontramos jugadores con esos filtros.</div>'}</div><div class="table-foot">${rows.length} jugadores · Índice propio de encaje /100</div>`;}
function gapLabel(gap){return gap==null?'Sin referencia':`${gap>0?'+':''}${gap.toFixed(1)} vs. referencia`;}
function academy(){return `${styleBar()}<div class="notice quiet"><strong>Grupos pendientes de confirmar.</strong> Las inferiores incluyen todos los grupos salvo el principal. <button class="text-button" id="settings-inline">Asignar nombres →</button></div><div class="academy-intro"><div><span class="tag">DESARROLLO CON PROPÓSITO</span><h2>El futuro empieza con una oportunidad.</h2><p>Buscá una función, identificá qué entrenar y evaluá el salto a la siguiente categoría.</p></div><span class="academy-number">${youth().length}<small>jugadores en formación*</small></span></div><section class="panel">${toolbar('academy')}<div id="results">${academyCards(filtered(youth()))}</div></section><p class="footnote">* Grupos distintos del principal; pueden incluir reservas adultos. Edad y encaje actual no permiten estimar el potencial. Las sugerencias requieren revisar minutos, entrenadores e instalaciones en FM.</p>`;}
function academyCards(rows){return `<div class="academy-grid">${rows.map(p=>{const a=analysis.academy.find(a=>a.uid===p.uid), prof=profile(p);return `<article class="academy-card"><div class="academy-card-head">${playerName(p)}${score(prof.score)}</div><span class="group-tag">${esc(groupName(p.team_slot))}</span><h3>${esc(prof.role_name)}<small class="canonical-small">Con balón · ${esc(prof.in_possession.english)}</small></h3><p class="youth-defensive-role">Sin balón: ${esc(prof.out_of_possession.name)}<small>${esc(prof.out_of_possession.english)}</small></p><div class="comparison-meter"><span style="width:${Math.min(100,Math.max(0,prof.score))}%"></span>${a.benchmark!=null?`<i style="left:${Math.min(100,a.benchmark)}%" title="Tercera opción del primer equipo"></i>`:''}</div><div class="comparison-caption"><span>Encaje actual /100</span><strong>${gapLabel(a.gap)}</strong></div><div class="development-action ${a.gap!=null&&a.gap>=-3?'ready':''}"><span>↗</span>${esc(a.action)}</div><p>${esc(a.plan)}</p><div class="focus"><small>FOCOS A TRABAJAR</small>${prof.focus.slice(0,2).map(f=>`<span>${esc(f.name)} <b>${f.value}</b></span>`).join('')}</div><button class="text-button" data-player="${p.uid}">Ver perfil y comparación →</button></article>`;}).join('')||'<div class="empty">No encontramos jugadores con esos filtros.</div>'}</div><div class="table-foot">${rows.length} jugadores · Comparados con el grupo ${esc(groupName(prefs.primary))}</div>`;}
function loans(){
  const rows = filtered(data.loans);
  const totalLoans = data.loans.length;
  const totalGoals = data.loans.reduce((sum,p)=>sum+((p.loan_stats&&p.loan_stats.goals)||0),0);
  const totalAssists = data.loans.reduce((sum,p)=>sum+((p.loan_stats&&p.loan_stats.assists)||0),0);
  const activeMinutes = data.loans.filter(p=>p.loan_stats&&p.loan_stats.minutes>0).length;

  return `${styleBar()}
  <div class="loans-summary-strip">
    <div class="loan-summary-box">
      <span class="ls-label">Total Cedidos</span>
      <strong>${totalLoans} jugadores</strong>
      <small>En clubes externos</small>
    </div>
    <div class="loan-summary-box">
      <span class="ls-label">Con Rodaje Oficial</span>
      <strong>${activeMinutes} jugando</strong>
      <small>Con minutos registrados</small>
    </div>
    <div class="loan-summary-box">
      <span class="ls-label">Goles en Cesión</span>
      <strong class="green">${totalGoals} ⚽</strong>
      <small>Anotados esta temporada</small>
    </div>
    <div class="loan-summary-box">
      <span class="ls-label">Asistencias</span>
      <strong class="cyan">${totalAssists} 👟</strong>
      <small>Pases de gol</small>
    </div>
  </div>

  <div class="loan-tabs-container">
    <div class="segmented loan-tabs" role="tablist">
      <button class="${loanTab==='performance'?'selected':''}" data-loantab="performance">
        📊 Rendimiento en el club cedido (Partidos, Goles, Asistencias, Minutos y Vencimiento)
      </button>
      <button class="${loanTab==='development'?'selected':''}" data-loantab="development">
        🎯 Plan de desarrollo y encaje al volver
      </button>
    </div>
  </div>

  <section class="panel">
    ${toolbar('loans')}
    <div id="results">
      ${loanTab==='performance' ? loanPerformanceTable(rows) : loanDevelopmentTable(rows)}
    </div>
  </section>`;
}

function loanPerformanceTable(rows){
  return `<div class="table-scroll">
    <table class="loan-perf-table">
      <thead>
        <tr>
          <th>Jugador</th>
          <th>Club Cedido</th>
          <th>Partidos (PJ)</th>
          <th>Goles</th>
          <th>Asist.</th>
          <th>Minutos</th>
          <th>Media ⭐</th>
          <th>Rol / Puesto en cesión</th>
          <th>Vence el préstamo</th>
          <th>Ficha</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map(p=>{
          const st = p.loan_stats || {};
          const apps = st.appearances != null ? st.appearances : (st.starts != null ? (st.starts + (st.substitutes || 0)) : '—');
          const starts = st.starts || 0;
          const subs = st.substitutes || 0;
          const goals = st.goals || 0;
          const assists = st.assists || 0;
          const mins = st.minutes ? Number(st.minutes).toLocaleString() : '—';
          const rating = st.average_rating != null ? Number(st.average_rating).toFixed(2) : (p.rating != null ? Number(p.rating).toFixed(2) : '—');
          const roleInClub = (p.natural_positions && p.natural_positions.length) ? p.natural_positions.join(' / ') : profile(p).role_name;
          const loanEnd = st.loan_end || p.loan_end || '—';
          const formattedEnd = (loanEnd !== '—' && loanEnd.includes('-')) ? dateLabel(loanEnd) : loanEnd;
          
          return `
          <tr>
            <td>
              ${playerName(p)}
            </td>
            <td>
              <strong class="loan-club-name">${esc(st.club_name || p.club_name || '—')}</strong>
            </td>
            <td>
              <span class="loan-stat-badge apps">
                <strong>${apps}</strong>
                <small>(${starts} tit${subs > 0 ? ` / ${subs} sup` : ''})</small>
              </span>
            </td>
            <td>
              <span class="loan-stat-badge goals ${goals > 0 ? 'highlight' : ''}">${goals > 0 ? `⚽ ${goals}` : '0'}</span>
            </td>
            <td>
              <span class="loan-stat-badge assists ${assists > 0 ? 'highlight' : ''}">${assists > 0 ? `👟 ${assists}` : '0'}</span>
            </td>
            <td>
              <span class="loan-stat-text">${mins} min</span>
            </td>
            <td>
              <span class="loan-rating-pill ${rating >= 7.0 ? 'high' : rating >= 6.7 ? 'mid' : 'low'}">
                ${rating !== '—' ? `${rating} ⭐` : '—'}
              </span>
            </td>
            <td>
              <span class="loan-role-badge">${esc(roleInClub)}</span>
            </td>
            <td>
              <span class="loan-date-pill">📅 ${esc(formattedEnd)}</span>
            </td>
            <td>
              <button class="text-button" data-player="${p.uid}">Ver perfil →</button>
            </td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>
    ${rows.length ? '' : '<div class="empty">No encontramos jugadores con esos filtros.</div>'}
  </div>
  <div class="table-foot">${rows.length} jugadores cedidos monitoreados</div>`;
}

function loanDevelopmentTable(rows){
  return `<div class="table-scroll"><table><thead><tr><th>Jugador</th><th>Club actual</th><th>Función a desarrollar</th><th>Encaje al volver</th><th>Prioridades de entrenamiento</th><th>Vencimiento</th></tr></thead><tbody>${rows.map(p=>`<tr><td>${playerName(p)}</td><td><strong class="loan-club-name">${esc(p.club_name)}</strong></td><td>${esc(profile(p).role_name)}</td><td>${score(profile(p).score)}</td><td>${profile(p).focus.slice(0,2).map(f=>`${esc(f.name)} (${f.value})`).join(' · ')}</td><td><span class="loan-date-pill">📅 ${esc(p.loan_end?dateLabel(p.loan_end):'—')}</span></td></tr>`).join('')}</tbody></table>${rows.length?'':'<div class="empty">No hay jugadores con esos filtros.</div>'}</div><div class="table-foot">${rows.length} cedidos · Plan para su regreso</div>`;
}
function methodology(){const m=data.methodology;return `<div class="method-layout"><section class="panel prose"><span class="tag">CRITERIO, A LA VISTA</span><h2>Recomendaciones que podés discutir.</h2><p>Touchline usa reglas y cálculos sobre atributos visibles. No utiliza capacidad actual, capacidad potencial ni personalidad oculta para elegir jugadores.</p><h3>1. Encaje individual</h3><p>${esc(m.formula)}</p><h3>2. Construcción del once</h3><p>${esc(m.lineup)}</p><p>Se evalúan 4-3-3, 4-2-3-1 y 4-4-2. Un índice más alto significa mejor encaje según esta fórmula; no es una probabilidad de victoria ni una puntuación del motor de FM.</p><h3>3. Inferiores y desarrollo</h3><p>${esc(m.academy)}</p><p>Los focos de entrenamiento son los tres atributos de menor valor entre los considerados importantes para la función. Su crecimiento no está garantizado.</p><h3>4. Límites de esta versión</h3><p>Los roles y los valores de las instrucciones proceden del catálogo FM26 consultado. Solo se recomiendan roles disponibles en la posición y fase elegidas. Las etiquetas españolas se extrajeron de Español latinoamericano de la instalación de FM26 26.3.2. Se seleccionan por clave y contexto, con variantes conservadas. Esto comprueba el texto del archivo; falta confirmar visualmente qué variante usa cada vista. Se conserva el nombre original. No se exportan tácticas .fmf.</p><p>No se verifican disponibilidad médica, sanciones del día, pie preferido para cada banda, reglas de inscripción, familiaridad táctica, nivel de rivales ni carga de partidos. La clasificación de reservas y juveniles se asigna manualmente.</p><p>El lector superó controles de estructura y rangos en la partida inicial. La correspondencia exacta con las fichas del juego sigue pendiente de cotejo.</p><a href="https://www.footballmanager.com/fm26/features/possession-out-possession-fm26s-new-tactical-evolution" target="_blank" rel="noreferrer">Sistema de fases de FM26 ↗</a> · <a href="https://github.com/rhiever/fmsave" target="_blank" rel="noreferrer">Lector fmsave ↗</a></section><section class="panel prose"><h2>Roles FM26 y atributos</h2><p>Los atributos de referencia de cada rol tienen el mismo peso. La fórmula de encaje es propia, no una fórmula publicada por Sports Interactive.</p>${Object.entries(m.roles).map(([id,r])=>`<details><summary>${esc(r.name)} · ${r.phase==='in_possession'?'Con balón':'Sin balón'}</summary><p>${esc(r.english)} · Posiciones: ${r.positions.join(', ')}</p><a href="${esc(r.source)}" target="_blank" rel="noreferrer">Fuente del rol ↗</a><div class="weight-list">${Object.entries(r.weights).map(([a,w])=>`<span>${esc(data.attributes[a])}<b>×${w}</b></span>`).join('')}</div></details>`).join('')}<h3>Pesos del estilo actual</h3><div class="weight-list">${Object.entries(data.styles[style].weights).map(([a,w])=>`<span>${esc(data.attributes[a])}<b>×${w}</b></span>`).join('')}</div></section></div>`;}
function localeAliases(local){const names=[...new Set((local?.aliases||[]).map(a=>a.text))].filter(n=>n!==local.text);return names.length?`<span class="muted"> Otras etiquetas del archivo: ${names.map(esc).join(" / ")}.</span>`:"";}
function fmInstructions(items){return items.length?`<div class="fm-instructions">${items.map(i=>`<article><div><strong>${esc(i.property)}: ${esc(i.value)}</strong><span class="instruction-origin ${i.origin}">${i.origin==='role'?'Indicada por el rol':i.origin==='standard'?'Mantener':'Ajustar'}</span></div><small>${esc(i.property_en)} → ${esc(i.value_en)}</small>${localeAliases(i.localization?.value)}<p>${esc(i.reason)}</p><a href="${esc(i.source)}" target="_blank" rel="noreferrer">Opción del catálogo ↗</a></article>`).join('')}</div>`:'<p class="muted">Conservar las instrucciones individuales por defecto para este rol. No se agregan ajustes no comprobados.</p>';}
function fmRole(r){return `<section class="fm-role"><div class="fm-role-heading"><div><span class="eyebrow">${r.phase==='in_possession'?'CON POSESIÓN':'SIN POSESIÓN'} · ${esc(r.position)}</span><h3>${esc(r.name)}</h3><strong class="canonical-name">${esc(r.english)}</strong>${r.tactical_badge?`<span class="tactical-badge-pill">${esc(r.tactical_badge)}</span>`:''}</div>${score(r.score)}</div>${r.tactical_summary?`<div class="tactical-role-highlight"><strong>Función táctica clave:</strong> ${esc(r.tactical_summary)}</div>`:''}<p class="translation-note">${esc(r.spanish_status)}.${localeAliases(r.localization)}</p><h4>Por qué lo elige</h4><ul>${r.reasons.map(s=>`<li>${esc(s)}</li>`).join('')}</ul><p class="role-comparison">${esc(r.comparison)}</p>${r.warnings.length?`<div class="role-warning">${r.warnings.map(w=>`<p>${esc(w)}</p>`).join('')}</div>`:''}<details class="fm-settings" open><summary>Instrucciones individuales</summary>${fmInstructions(r.instructions)}${r.behaviours.length?`<p class="muted">Comportamientos indicados por la referencia del rol: ${esc(r.behaviours.join(' · '))}. No son todos controles independientes.</p>`:''}</details><a class="source-link" href="${esc(r.source)}" target="_blank" rel="noreferrer">Ver rol y posición en la fuente ↗</a></section>`;}
function playerFM26(p,prof){const context=view==='tactics'?analysis.tactics[selectedTactic]?.lineup.find(l=>l.uid===p.uid):null;const recommendation=context||prof;return `<div class="fm26-player-plan"><span class="tag">PLAN FM26 · ${context?'EN EL ONCE PROPUESTO':'ENCAJE INDIVIDUAL'}</span><p class="muted">${context?'Estos son los roles asignados en la estructura seleccionada. Pueden diferir del mejor encaje individual.':'Roles e instrucciones para su posición actual, también aplicables a juveniles y cedidos.'}</p>${fmRole(recommendation.in_possession)}${fmRole(recommendation.out_of_possession)}<button class="button subtle" id="download-player-plan">↓ Descargar configuración FM26</button></div>`;}
function downloadPlayerPlan(p,prof){const context=view==='tactics'?analysis.tactics[selectedTactic]?.lineup.find(l=>l.uid===p.uid):null;const plan=context||prof;const blocks=[`${p.name} · ${data.club} · ${data.date}`,`Estilo: ${data.styles[style].name}`,'Español latinoamericano extraído de FM26 26.3.2. Algunas vinculaciones con las vistas del menú siguen pendientes de cotejo visual.'];for(const r of [plan.in_possession,plan.out_of_possession]){blocks.push('',`${r.phase==='in_possession'?'CON':'SIN'} POSESIÓN · ${r.position}: ${r.name} [${r.english}]`,...(r.localization?.aliases?.length?["Otras etiquetas del archivo: "+r.localization.aliases.map(a=>a.text).join(" / ")]:[]),...r.reasons.map(x=>'• '+x),r.comparison,...r.instructions.map(i=>`${i.property}: ${i.value} [${i.property_en}: ${i.value_en}]\n${i.reason}`),`Fuente: ${r.source}`);}const url=URL.createObjectURL(new Blob([blocks.join('\n')],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='FM26-'+p.name.replace(/[^\p{L}\p{N} -]/gu,'')+'.txt';a.click();URL.revokeObjectURL(url);}

async function openSyncDialog(){
  const d=$('#sync-dialog');if(!d)return;
  let status=syncStatus;
  try{status=await api('/api/sync/status');syncStatus=status;}catch(e){}
  const saves=status?.available_saves||[];
  const currentTarget=status?.target_save||'auto';
  const isEnabled=status?.enabled!==false;
  const lastTime=status?.last_sync_time?(dateLabel(status.last_sync_time.split('T')[0])+' '+(status.last_sync_time.split('T')[1]?.substring(0,8)||'')):'Ninguna aún';
  d.innerHTML=`<button class="dialog-close" aria-label="Cerrar sincronización">×</button>
    <div class="sync-dialog-body">
      <div class="sync-dialog-header">
        <div class="sync-dialog-icon">⚡</div>
        <div>
          <span class="tag">TIEMPO REAL · FM26</span>
          <h2>Sincronización en vivo con FM26</h2>
        </div>
      </div>
      <p class="sync-dialog-desc">Cada vez que guardás tu partida en Football Manager 26 (manual o autoguardado), Touchline detecta automáticamente el archivo, extrae tu club y actualiza la alineación, informes y tácticas al instante sin reiniciar la aplicación.</p>
      <div class="sync-status-box">
        <div class="sync-status-row"><span>Estado del monitor:</span><strong>${status?.state==='watching'?'🟢 Monitoreando en tiempo real':status?.state==='paused'?'⚪ Pausado':status?.state==='folder_not_found'?'⚠️ Carpeta no encontrada':'En espera'}</strong></div>
        <div class="sync-status-row"><span>Partida activa detectada:</span><strong>${esc(status?.active_file||'Ninguna')} ${status?.active_file_size_mb?`(${status.active_file_size_mb} MB)`:''}</strong></div>
        <div class="sync-status-row"><span>Última sincronización:</span><span>${esc(status?.last_sync_save||'—')} · <small>${esc(lastTime)}</small></span></div>
        ${status?.last_error?`<div class="notice" style="margin:8px 0 0;padding:8px 12px;font-size:11px">Aviso: ${esc(status.last_error)}</div>`:''}
      </div>
      <form id="sync-form">
        <div class="sync-field-group">
          <label style="display:flex;align-items:center;gap:10px;cursor:pointer">
            <input type="checkbox" name="enabled" ${isEnabled?'checked':''} style="width:18px;height:18px">
            <span>Activar sincronización automática al guardar en FM26</span>
          </label>
        </div>
        <div class="sync-field-group">
          <label for="sync-mode">Modo de detección</label>
          <select id="sync-mode" name="target_save">
            <option value="auto" ${currentTarget==='auto'?'selected':''}>⭐ Modo Automático: Detectar la última partida guardada (Recomendado)</option>
            ${saves.map(s=>`<option value="${esc(s.filename)}" ${currentTarget===s.filename?'selected':''}>Partida específica: ${esc(s.filename)} (${s.size_mb} MB · ${esc(s.date_label)})</option>`).join('')}
          </select>
          <small>En Modo Automático podés usar autoguardados rotativos o guardar con nombres distintos y se actualizará solo.</small>
        </div>
        <div class="sync-field-group">
          <label for="sync-folder">Carpeta de partidas guardadas de FM26</label>
          <input id="sync-folder" type="text" name="watch_folder" value="${esc(status?.watch_folder||'')}">
          <small>Ruta por defecto en Windows: C:\Users\feder\Documents\Sports Interactive\Football Manager 26\games</small>
        </div>
        <div class="sync-dialog-actions">
          <button type="button" class="button subtle" id="btn-force-sync" ${uploadBusy?'disabled':''}>⚡ Sincronizar ahora</button>
          <button type="submit" class="button primary">Guardar configuración</button>
        </div>
      </form>
    </div>`;
  d.querySelector('.dialog-close').onclick=()=>d.close();
  d.querySelector('#btn-force-sync').onclick=async()=>{
    try{
      const mode=d.querySelector('#sync-mode').value;
      const filename=mode!=='auto'?mode:null;
      toast('Iniciando sincronización de partida…');
      d.close();uploadBusy=true;render();
      await api('/api/sync/trigger',{method:'POST',headers:{'Content-Type':'application/json','X-FM-App':'1'},body:JSON.stringify({filename})});
    }catch(err){uploadBusy=false;render();toast(err.message,true);}
  };
  d.querySelector('#sync-form').onsubmit=async e=>{
    e.preventDefault();
    const fd=new FormData(e.target);
    const enabled=fd.get('enabled')==='on';
    const target_save=fd.get('target_save');
    const watch_folder=fd.get('watch_folder');
    try{
      syncStatus=await api('/api/sync/config',{method:'POST',headers:{'Content-Type':'application/json','X-FM-App':'1'},body:JSON.stringify({enabled,target_save,watch_folder})});
      d.close();render();toast('Configuración de sincronización guardada.');
    }catch(err){toast(err.message,true);}
  };
  d.showModal();
}

async function pollStatus(){
  try{
    const status=await api('/api/status');
    syncStatus=status.sync;
    const syncBtn=$('#sync-status-btn');
    if(syncBtn&&!uploadBusy&&syncStatus){
      const dot=syncBtn.querySelector('.sync-dot');
      const txt=syncBtn.querySelector('span:last-child');
      if(dot&&txt){
        if(syncStatus.state==='paused'){dot.className='sync-dot gray';txt.textContent='Sync pausado';}
        else if(syncStatus.state==='folder_not_found'){dot.className='sync-dot yellow';txt.textContent='Carpeta no hallada';}
        else{dot.className='sync-dot green';txt.textContent='FM26: '+(syncStatus.active_file||'Esperando guardado');}
      }
    }
    if(status.active_job){
      if(!uploadBusy){uploadBusy=true;render();}
      updateImport(status.active_job.message,status.active_job.progress);
    }else if(uploadBusy){
      uploadBusy=false;
      data=await api('/api/data');
      lastKnownDatasetId=data.id;
      await calculate();
      toast('⚽ ¡Partida actualizada en vivo desde FM26! ('+data.club+')');
    }else if(data&&status.dataset_id&&status.dataset_id!==data.id){
      data=await api('/api/data');
      lastKnownDatasetId=data.id;
      await calculate();
      toast('⚽ ¡Partida actualizada en vivo desde FM26! ('+data.club+')');
    }
  }catch(e){}
}

function openPlayer(id){
 const p=playerById(id), prof=profile(p), a=analysis.academy.find(a=>a.uid===p.uid), d=$('#player-dialog');
 d.innerHTML=`<button class="dialog-close" aria-label="Cerrar ficha">×</button><div class="profile-hero"><span class="avatar big">${esc(initials(p.name))}</span><span class="eyebrow">${esc(p.club_name)}</span><h2>${esc(p.name)}</h2><p>${p.age??'—'} años · ${p.height_cm??'—'} cm · ${esc(p.natural_positions.join(' / '))}</p><span class="tag">${esc(data.players.some(q=>q.uid===p.uid)?groupName(p.team_slot):'Cedido fuera')}</span></div><div class="profile-body"><div class="profile-main-role"><div><small>MEJOR FUNCIÓN · ${esc(data.styles[style].name.toUpperCase())}</small><h3>${esc(prof.role_name)}</h3></div>${score(prof.score)}</div><div class="role-alternatives">${prof.roles.map(r=>`<div><span>${esc(r.name)}</span>${score(r.score)}</div>`).join('')}</div>${playerFM26(p,prof)}<h3>Lo que aporta</h3><div class="chips">${prof.strengths.map(s=>`<span>${esc(s.name)} <b>${s.value}</b></span>`).join('')}</div><h3>Focos de entrenamiento</h3><p class="muted">Atributos más bajos entre los importantes para esta función. Elegí una prioridad y revisá la respuesta en el juego.</p><div class="chips">${prof.focus.map(s=>`<span>${esc(s.name)} <b>${s.value}</b></span>`).join('')}</div>${a?`<div class="development-box"><span class="eyebrow">SIGUIENTE PASO</span><h3>${esc(a.action)}</h3><p>${esc(a.plan)}</p><strong>${gapLabel(a.gap)}</strong><h4>Opciones actuales del primer equipo</h4>${a.comparison.map(c=>`<div class="compare-row"><span>${esc(c.name)}</span>${score(c.score)}</div>`).join('')}</div>`:''}<h3>Atributos visibles</h3><div class="attributes-grid">${Object.entries(data.attributes).map(([key,label])=>`<div><span>${esc(label)}</span><b class="attr-value ${p.attributes[key]>=15?'high':''}">${p.attributes[key]}</b></div>`).join('')}</div><h3>Familiaridad posicional</h3><div class="chips">${Object.entries(p.positions).filter(([,v])=>v>=10).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`<span>${k.toUpperCase()} <b>${v}/20</b></span>`).join('')}</div><p class="muted">Pie izquierdo ${p.left_foot}/20 · Pie derecho ${p.right_foot}/20</p></div>`;
 d.querySelector('.dialog-close').onclick=()=>d.close();d.querySelector('#download-player-plan').onclick=()=>downloadPlayerPlan(p,prof);d.showModal();
}
function settings(){const d=$('#settings-dialog');d.innerHTML=`<button class="dialog-close" aria-label="Cerrar configuración">×</button><div class="settings-body"><span class="eyebrow">ESTRUCTURA DEL CLUB</span><h2>Poné nombre a cada grupo</h2><p>El archivo identifica grupos por número. Confirmá en FM cuál corresponde al primer equipo, reservas y juveniles.</p><form id="settings-form"><label class="field">Grupo del primer equipo<select name="primary">${data.slots.map(s=>`<option value="${s}" ${prefs.primary===s?'selected':''}>${esc(groupName(s))} · ${data.players.filter(p=>p.team_slot===s).length} jugadores</option>`).join('')}</select></label>${data.slots.map(s=>`<label class="field">Nombre del grupo ${s}<input name="label-${s}" maxlength="40" placeholder="Ej.: Sub-21 / Sub-18" value="${esc(prefs.labels[s]||data?.slot_labels?.[s]||(s===prefs.primary?'Primer equipo':''))}"><small>${esc(data.players.filter(p=>p.team_slot===s).slice(0,3).map(p=>p.name).join(', '))}</small></label>`).join('')}<button class="button primary" type="submit">Guardar y recalcular</button></form></div>`;d.querySelector('.dialog-close').onclick=()=>d.close();d.querySelector('form').onsubmit=async e=>{e.preventDefault();const f=new FormData(e.target);prefs.primary=Number(f.get('primary'));for(const s of data.slots)prefs.labels[s]=String(f.get('label-'+s)).trim();savePrefs();d.close();filter='all';await calculate();};d.showModal();}
function refreshResults(){const el=$('#results');if(!el)return;el.innerHTML=view==='squad'?playerTable(filtered(data.players)):view==='academy'?academyCards(filtered(youth())):loanTable(filtered(data.loans));bindPlayers(el);bindAvailable(el);}
function bindPlayers(el=document){el.querySelectorAll('[data-player]').forEach(b=>b.onclick=()=>openPlayer(b.dataset.player));}
function bindAvailable(el=document){el.querySelectorAll('[data-available]').forEach(b=>b.onchange=async()=>{const id=Number(b.dataset.available);b.checked?excluded.delete(id):excluded.add(id);savePrefs();await calculate();});}
function bind(){
 document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{view=b.dataset.view;query='';filter='all';render();window.scrollTo(0,0);});
 document.querySelectorAll('[data-style]').forEach(b=>b.onclick=async()=>{style=b.dataset.style;savePrefs();await calculate();});
 document.querySelectorAll('[data-tactic]').forEach(b=>b.onclick=()=>{selectedTactic=Number(b.dataset.tactic);render();});
 document.querySelectorAll('[data-phase]').forEach(b=>b.onclick=()=>{phase=b.dataset.phase;render();});
 document.querySelectorAll('[data-loantab]').forEach(b=>b.onclick=()=>{loanTab=b.dataset.loantab;render();});
 bindPlayers();bindAvailable();
 if($('#sync-status-btn'))$('#sync-status-btn').onclick=openSyncDialog;
  $('#settings-button').onclick=settings;
 if($('#settings-inline'))$('#settings-inline').onclick=settings;
 $('#import-button').onclick=()=>$('#save-file').click();
 if($('#retry-button'))$('#retry-button').onclick=calculate;
 const pi=$('#prompt-input'), btnApply=$('#btn-apply-prompt'), btnClear=$('#btn-clear-prompt');
 if(btnApply&&pi){
   btnApply.onclick=()=>calculate(pi.value.trim());
   pi.onkeydown=e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();calculate(pi.value.trim());}};
 }
 if(btnClear)btnClear.onclick=()=>calculate('');
 document.querySelectorAll('.prompt-chip').forEach(c=>{
   c.onclick=()=>{if(pi)pi.value=c.dataset.prompt;calculate(c.dataset.prompt);};
 });
 if($('#search'))$('#search').oninput=e=>{query=e.target.value;refreshResults();};
 if($('#group-filter'))$('#group-filter').onchange=e=>{filter=e.target.value;refreshResults();};
 if($('#sort-order'))$('#sort-order').onchange=e=>{order=e.target.value;refreshResults();};
 if($('#export-button'))$('#export-button').onclick=()=>{
   if(!analysis||analysisBusy)return toast('Esperá a que termine el análisis.');
   const raw=JSON.stringify({club:data.club,date:data.date,style,groups:prefs,players:data.players,loans:data.loans,analysis,methodology:data.methodology},null,2);
   const url=URL.createObjectURL(new Blob([raw],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='touchline-analisis.json';a.click();URL.revokeObjectURL(url);toast('Análisis exportado.');};
}
async function finishImport(jobId){
 while(true){const j=await api('/api/jobs/'+jobId);if(j.status==='error')throw Error(j.message);updateImport(j.message,j.progress??null);if(j.status==='done')break;await new Promise(r=>setTimeout(r,1200));}
 data=await api('/api/data');prefs={primary:data.default_primary_slot,labels:{}};excluded=new Set();if(!data.styles[style])style='possession';savePrefs();filter='all';query='';view='overview';showWelcome=false;uploadBusy=false;await calculate();toast('Análisis completo listo: '+data.club+'.');
}
async function startImport(file){
 if(!file)return;if(uploadBusy)return toast('Esperá a que termine el análisis actual.');
 if(!file.name.toLowerCase().endsWith('.fm')||file.size>400*1024*1024||file.size<1000)return toast('Seleccioná una partida .fm de hasta 400 MB.',true);
 ++requestVersion;analysisBusy=false;uploadInfo={message:'Cargando '+file.name+'…',progress:0};uploadBusy=true;render();
 try{
   const job=await new Promise((resolve,reject)=>{const x=new XMLHttpRequest();x.open('PUT','/api/import');x.setRequestHeader('X-FM-App','1');x.setRequestHeader('X-FM-Filename',encodeURIComponent(file.name));x.upload.onprogress=e=>{if(e.lengthComputable)updateImport('Cargando '+file.name+'…',Math.round(e.loaded/e.total*15));};x.onload=()=>{try{const d=JSON.parse(x.responseText);x.status===202?resolve(d):reject(Error(d.error));}catch{reject(Error('Respuesta de importación inválida.'));}};x.onerror=()=>reject(Error('No se pudo conectar con la aplicación local.'));x.send(file);});
   updateImport('Leyendo la partida y preparando el análisis…',18);
   await finishImport(job.job_id);
 }catch(err){uploadBusy=false;render();toast(err.message,true);}
}
$('#save-file').onchange=e=>{const file=e.target.files[0];e.target.value='';startImport(file);};
for(const d of document.querySelectorAll('dialog'))d.addEventListener('click',e=>{if(e.target===d)d.close();});
(async()=>{try{const status=await api('/api/status');syncStatus=status.sync;setInterval(pollStatus,2500);data=await api('/api/data');lastKnownDatasetId=data?.id;if(status.active_job){uploadBusy=true;updateImport(status.active_job.message,status.active_job.progress);render();try{await finishImport(status.active_job.job_id);}catch(e){uploadBusy=false;render();toast(e.message,true);}}else{render();if(status.restore_error)toast(status.restore_error,true);}}catch(e){$('#app').innerHTML=`<div class="initial"><h1>No pudimos conectar con la aplicación</h1><p>${esc(e.message)}</p><p>Comprobá que el servidor local esté en ejecución y recargá.</p></div>`;}})();
