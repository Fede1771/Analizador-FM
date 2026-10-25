import {api, upload, RequestGate} from './api.js';
import {currentView, freshDraft, referenceDraft, reconcileCurrentDraft} from './current-view.js';
import {reconcile, preferenceKey, contextKey} from './session.js';
import {esc, date} from './format.js';
import {navigation, welcome, overview, tactics, contractsView, scoutingView, companionView, roster, methodology, playerRows, playerDialog, groupDialog, syncDialog} from './views.js';

const $ = selector => document.querySelector(selector);
const gate = new RequestGate();
const state = {data:null, analysis:null, simulation:null, byId:new Map(), prefs:null,
  view:'overview', phase:'ip', busy:false, uploadBusy:false, pendingUpload:false, error:'', connectionError:'',
  currentDraft:null, currentResult:null, currentBusy:false, currentError:'', currentVersion:0, promptDraft:'', overrideDraft:{}, contractsFilter:{urgency:'all',query:''}, scoutingFilter:{position:'all',query:'',sort:'score'}, filters:{query:'',group:'all',order:'score'}, job:null, sync:null};
let trackedJob=null, loadVersion=0, saveQueue=Promise.resolve(), stopped=false;
const handledJobs=new Set();

function toast(message, error=false) {
  const el=$('#toast');
  el.textContent=message; el.className='toast visible'+(error?' error':'');
  clearTimeout(toast.timer); toast.timer=setTimeout(()=>el.classList.remove('visible'),7000);
}

function progress() {
  const banner=$('#activity');
  const job=state.job;
  banner.hidden=!(state.uploadBusy||state.busy||state.connectionError);
  const message=state.connectionError || (state.uploadBusy?job?.message||'Preparando importación…':'Actualizando propuesta táctica…');
  if($('#activity-text').textContent!==message)$('#activity-text').textContent=message;
  const bar=$('#activity-progress');
  bar.hidden=!state.uploadBusy;
  if(job?.progress==null) bar.removeAttribute('value'); else bar.value=job.progress;
  $('#snapshot-note').textContent=state.uploadBusy&&state.analysis?'Podés seguir consultando el último análisis mientras se actualiza.':'';
  const sync=$('#sync-button'), s=state.sync;
  const labels={watching:'Monitoreando guardados',paused:'Sincronización pausada',folder_not_found:'Revisar carpeta',idle:'Esperando guardado',syncing:'Sincronizando',error:'Error de sincronización'};
  sync.textContent=labels[s?.state]||'Sincronización';
  sync.dataset.status=s?.state||'idle';
}

function render({focusHeading=false}={}) {
  const content=$('#content');
  const active=document.activeElement;
  const focus=content.contains(active)&&active.id?{id:active.id,start:active.selectionStart,end:active.selectionEnd}:null;
  const open=new Map([...content.querySelectorAll('details')].map(d=>[d.id||d.querySelector('summary')?.textContent,d.open]));
  if(new URLSearchParams(location.search).get('companion')==='1') {
    $('#sidebar').hidden=true;
    const top=$('header.topbar'); if(top) top.style.display='none';
    const foot=$('footer'); if(foot) foot.style.display='none';
    document.body.classList.add('companion-standalone');
    content.innerHTML=companionView(state);
    return;
  }
  $('#sidebar').hidden=!state.data;
  document.body.classList.toggle('has-dataset',!!state.data);
  $('#nav').innerHTML=Object.entries(navigation).map(([key,label])=>`<a href="#${key}" ${key===state.view?'aria-current="page"':''}>${label}</a>`).join('');
  $('#source-label').textContent=state.data?`${state.data.source.filename} · ${date(state.data.date)}`:'Análisis local · Football Manager 26';
  $('#groups-button').hidden=!state.data;
  const compBtn=$('#companion-button'); if(compBtn) compBtn.hidden=!state.data;
  let html;
  if(!state.data) html=welcome(state);
  else if(state.view==='overview') html=overview(state);
  else if(state.view==='current') html=currentView(state);
  else if(state.view==='tactics') html=tactics(state);
  else if(state.view==='contracts') html=contractsView(state);
  else if(state.view==='scouting') html=scoutingView(state);
  else if(state.view==='method') html=methodology(state);
  else html=roster(state,state.view);
  content.innerHTML=html;
  content.setAttribute('aria-busy',String(state.busy));
  if(state.data?.warnings.length) {
    const warning=document.createElement('details'); warning.className='notice warning';
    warning.innerHTML=`<summary>${state.data.warnings.length} advertencias de lectura</summary><ul>${state.data.warnings.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`;
    content.prepend(warning);
  }
  for(const d of content.querySelectorAll('details')) {const key=d.id||d.querySelector('summary')?.textContent;if(open.has(key))d.open=open.get(key);}
  if(focus) {
    const target=document.getElementById(focus.id);
    target?.focus({preventScroll:true});
    if(target?.setSelectionRange&&focus.start!=null) {try{target.setSelectionRange(focus.start,focus.end);}catch{}}
  }
  if(focusHeading) {const h=content.querySelector('h1');h?.setAttribute('tabindex','-1');h?.focus({preventScroll:true});window.scrollTo(0,0);}
  progress();
}

async function persist() {
  if(!state.data) return;
  const data=state.data, prefs=structuredClone(state.prefs);
  try {localStorage.setItem(preferenceKey(data),JSON.stringify(prefs));} catch {}
  saveQueue=saveQueue.catch(()=>{}).then(()=>api('/api/preferences',{method:'POST',body:{...prefs,career_id:data.career_id}}));
  try {await saveQueue;} catch(error) {toast('No pudimos guardar tus preferencias: '+error.message,true);}
}

async function refresh() {
  if(!state.data) return;
  const data=state.data, prefs=structuredClone(state.prefs), request=gate.begin(data.id);
  state.busy=true;state.error='';state.analysis=null;state.simulation=null;render();
  const body={dataset_id:data.id,...prefs};
  try {
    const analysis=await api('/api/analyze',{method:'POST',body,signal:request.signal});
    let simulation=null;
    if(prefs.formation!=='auto') simulation=await api('/api/simulate',{method:'POST',body:{...body,formation:prefs.formation},signal:request.signal});
    if(!request.current(state.data?.id)) return;
    state.analysis=analysis;state.simulation=simulation;state.prefs.style=analysis.style;
    state.busy=false;state.overrideDraft={};render();await persist();
  } catch(error) {
    if(!request.current(state.data?.id)) return;
    state.busy=false;state.error=error.message;render();
    if(state.view!=='tactics')toast(error.message,true);
    if(error.status===409) await loadDataset();
  }
}

async function loadDataset(provided) {
  const version=++loadVersion;
  gate.invalidate();
  const data=provided===undefined?await api('/api/data'):provided;
  if(version!==loadVersion) return;
  if(!data) {state.data=null;state.analysis=null;state.simulation=null;render();return;}
  const sameCareer=state.data?.career_id===data.career_id;
  let saved=sameCareer?state.prefs:null;
  if(!saved) {
    try {saved=await api('/api/preferences');} catch {}
    if(!saved) {try {saved=JSON.parse(localStorage.getItem(preferenceKey(data))||localStorage.getItem('touchline:'+data.id)||'null');}catch{}}
  }
  if(version!==loadVersion) return;
  state.currentVersion++;state.currentResult=null;state.currentBusy=false;
  if(!sameCareer) {
    try {state.currentDraft=JSON.parse(localStorage.getItem('touchline:current:'+data.career_id)||'null');}catch {state.currentDraft=null;}
  }
  state.currentDraft=reconcileCurrentDraft(data,state.currentDraft);
  state.currentDraft.confirmed=false;
  state.data=data;state.byId=new Map([...data.players,...data.loans].map(p=>[p.uid,p]));
  state.prefs=reconcile(data,saved);state.promptDraft=state.prefs.prompt;
  state.analysis=null;state.simulation=null;state.overrideDraft={};state.filters.group='all';
  const dialog=$('#dialog');if(dialog.open)dialog.close();
  await refresh();
}

async function poll() {
  if(stopped)return;
  try {
    const status=await api('/api/status',{timeout:8000});
    state.connectionError='';state.sync=status.sync;
    if(status.active_job) {
      trackedJob=status.active_job.job_id;state.job=status.active_job;state.uploadBusy=true;
    } else if(!state.pendingUpload) {
      const latest=status.last_job;
      const id=trackedJob||(!handledJobs.has(latest?.job_id)?latest?.job_id:null);
      if(id) {
        const job=latest?.job_id===id?latest:await api('/api/jobs/'+id);
        if(['done','error','cancelled'].includes(job.status)) {
          handledJobs.add(id);trackedJob=null;state.uploadBusy=false;state.job=null;
          if(job.status==='done') {await loadDataset();toast('Partida actualizada: '+state.data.club+'.');}
          else toast(job.message,true);
        }
      }
      if(status.dataset_id&&status.dataset_id!==state.data?.id&&!state.uploadBusy) await loadDataset();
    }
  } catch(error) {
    state.connectionError='No podemos conectar con Touchline. Reintentando automáticamente.';
  } finally {
    progress();if(!stopped)setTimeout(poll,2500);
  }
}

async function startImport(file) {
  if(!file)return;
  if(state.uploadBusy)return toast('Ya hay una importación en curso.');
  if(!file.name.toLowerCase().endsWith('.fm')||file.size<1000||file.size>400*1024**2)return toast('Elegí una partida .fm de hasta 400 MB.',true);
  state.uploadBusy=true;state.pendingUpload=true;state.job={message:'Cargando '+file.name+'…',progress:0};progress();
  try {
    const result=await upload(file,percent=>{state.job={message:'Cargando '+file.name+'…',progress:percent};progress();});
    trackedJob=result.job_id;state.job={message:'Leyendo la partida…',progress:18};
  } catch(error) {state.uploadBusy=false;toast(error.message,true);}
  finally {state.pendingUpload=false;progress();}
}

function showDialog(html) {
  const dialog=$('#dialog');
  $('#dialog-body').innerHTML=html;
  if(!dialog.open)dialog.showModal();
}

function download(name, value, type='application/json') {
  const url=URL.createObjectURL(new Blob([typeof value==='string'?value:JSON.stringify(value,null,2)],{type}));
  const link=document.createElement('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

function navigate(view) {
  state.view=navigation[view]?view:'overview';state.filters={query:'',group:'all',order:'score'};state.error='';render({focusHeading:true});
}

function saveCurrentDraft() {
  state.currentResult=null;state.currentError='';state.currentDraft.confirmed=false;state.currentVersion++;
  try {localStorage.setItem('touchline:current:'+state.data.career_id,JSON.stringify(state.currentDraft));}catch{}
}

async function auditCurrent() {
  if(state.currentBusy)return;
  const version=state.currentVersion, id=state.data.id;
  state.currentBusy=true;state.currentError='';render();
  try {
    const result=await api('/api/current-tactic',{method:'POST',body:{...state.currentDraft,dataset_id:id}});
    if(version===state.currentVersion&&id===state.data?.id)state.currentResult=result;
  } catch(error) {if(version===state.currentVersion)state.currentError=error.message;}
  finally {state.currentBusy=false;render();if(state.currentResult&&state.view==='current'){const result=$('#current-result');result?.scrollIntoView({block:'start'});result?.querySelector('h2')?.focus({preventScroll:true});}}
}

async function action(name, button) {
  if(name==='companion')return showDialog(companionView(state));
  if(name==='popout-companion') {
    window.open('/?companion=1#'+(state.view==='current'?'current':'tactics'),'TouchlineCompanion','width=460,height=720,menubar=no,toolbar=no,location=no,status=no,resizable=yes');
    return;
  }
  if(name==='copy-match-instructions') {
    const tactic = state.prefs?.formation==='auto' ? state.analysis?.requested_tactic||state.analysis?.tactics?.[0] : state.simulation;
    const acts = (state.currentResult?.tactical_advice || tactic?.tactical_recommendations || [])
      .map(a => a.action ? `• ${a.title}: ${a.action} (${a.phase_label || 'Táctica'})` : `• ${a.title}`);
    const text = [
      `📋 TOUCHLINE FM26 - AJUSTES PARA EL PARTIDO (${state.data?.club || 'Club'}):`,
      `Esquema: ${tactic?.name || state.prefs?.formation || '4-3-3'} | Estilo: ${state.data?.styles?.[state.prefs?.style]?.name || 'Posesión'}`,
      '',
      ...(acts.length ? acts : ['• Confirmá el once titular y roles en FM.']),
      '',
      `Generado por Touchline · ${date(state.data?.date)}`
    ].join('\n');
    try {
      await navigator.clipboard.writeText(text);
      toast('¡Ajustes copiados al portapapeles!');
    } catch(e) {
      download('ajustes-partido-fm.txt', text, 'text/plain;charset=utf-8');
      toast('Ajustes descargados.');
    }
    return;
  }
  if(name==='export-tactic-fm') {
    if(!state.data) return toast('Cargá una partida primero.');
    const tactic = state.prefs?.formation==='auto' ? state.analysis?.requested_tactic||state.analysis?.tactics?.[0] : state.simulation;
    const acts = (state.currentResult?.tactical_advice || tactic?.tactical_recommendations || [])
      .map(a => a.action ? `${a.title}: ${a.action}` : a.title);
    try {
      const res = await api('/api/export-tactic', {
        method: 'POST',
        body: {
          formation: tactic?.id || state.prefs?.formation || '433',
          name: `Touchline_${(state.data.club||'Club').replace(/\s+/g,'_')}_${tactic?.id || state.prefs?.formation || '433'}`,
          style: state.prefs?.style,
          style_name: state.data.styles?.[state.prefs?.style]?.name || 'Posesión',
          mentality: tactic?.mentality || 'Positiva',
          team: tactic?.team_instructions || {},
          lineup: tactic?.lineup || [],
          actions: acts
        }
      });
      try { await navigator.clipboard.writeText(res.clipboard_summary); } catch {}
      toast('¡Táctica guardada en Documentos\\Sports Interactive\\Football Manager 26\\tactics!');
    } catch(e) {
      toast('Error al exportar táctica: ' + e.message, true);
    }
    return;
  }
  if(name==='audit-current')return auditCurrent();
  if(name==='reference-current') {state.currentDraft=referenceDraft(state.data);saveCurrentDraft();state.currentDraft.confirmed=true;await auditCurrent();return;}
  if(name==='export-current') {if(state.currentResult)download('touchline-mi-tactica.json',{draft:state.currentDraft,result:state.currentResult});return;}
  if(name==='shutdown') { await api('/api/shutdown',{method:'POST',body:{}}); stopped=true;gate.invalidate();$('#content').innerHTML='<h1>Touchline se cerró</h1><p>Podés cerrar esta pestaña.</p>';return; }
  if(name==='import')return $('#save-file').click();
  if(name==='reload')return bootstrap();
  if(name==='retry')return refresh();
  if(name==='groups')return showDialog(groupDialog(state));
  if(name==='sync') {
    const [status,retention]=await Promise.all([api('/api/sync/status'),api('/api/retention')]);
    state.sync=status;showDialog(syncDialog(status,retention));return;
  }
  if(name==='force-sync') {
    const form=$('#sync-form');
    const fd=new FormData(form), filename=fd.get('target_save');
    // Save edited folder/mode before triggering so the operation follows the visible controls.
    state.sync=await api('/api/sync/config',{method:'POST',body:{enabled:fd.get('enabled')==='on',watch_folder:fd.get('watch_folder'),target_save:filename}});
    const result=await api('/api/sync/trigger',{method:'POST',body:{filename:filename==='auto'?null:filename}});
    trackedJob=result.job_id;state.uploadBusy=true;state.job={message:'Preparando sincronización…'};$('#dialog').close();progress();return;
  }
  if(name==='apply-prompt'||name==='apply-quick-prompt') {
    state.prefs.prompt=state.promptDraft.trim();state.prefs.overrides={};return refresh();
  }
  if(name==='clear-prompt') {state.prefs.prompt='';state.promptDraft='';state.prefs.overrides={};return refresh();}
  if(name==='apply-overrides') {Object.assign(state.prefs.overrides,state.overrideDraft);return refresh();}
  if(name==='clear-overrides') {state.prefs.overrides={};state.overrideDraft={};return refresh();}
  if(name==='export') {
    if(!state.analysis||state.busy)return toast('Esperá a que termine el análisis.');
    download('touchline-analisis.json',{club:state.data.club,date:state.data.date,dataset_id:state.data.id,preferences:state.prefs,analysis:state.analysis,simulation:state.simulation,methodology:state.data.methodology});toast('Análisis exportado en JSON.');
  }
}

document.addEventListener('click',event=>{
  const button=event.target.closest('[data-action],[data-view],[data-player],[data-formation],[data-phase],[data-download-player],[data-contract-filter],[data-scout-position],[data-scout-pos]');
  if(!button)return;
  Promise.resolve().then(async()=>{
    if(button.dataset.contractFilter) {state.contractsFilter.urgency=button.dataset.contractFilter;render();return;}
    if(button.dataset.scoutPosition) {state.scoutingFilter.position=button.dataset.scoutPosition;render();return;}
    if(button.dataset.scoutPos) {state.scoutingFilter.position=button.dataset.scoutPos;state.view='scouting';location.hash='scouting';render();return;}
    if(button.dataset.action)return action(button.dataset.action,button);
    if(button.dataset.view) {location.hash=button.dataset.view;if(state.view===button.dataset.view)navigate(button.dataset.view);return;}
    if(button.dataset.player)return showDialog(playerDialog(state,button.dataset.player));
    if(button.dataset.phase) {state.phase=button.dataset.phase;render();return;}
    if(button.dataset.formation) {state.prefs.formation=button.dataset.formation;if(state.view!=='tactics'){state.view='tactics';location.hash='tactics';}return refresh();}
    if(button.dataset.downloadPlayer) {
      const p=state.byId.get(Number(button.dataset.downloadPlayer));
      const tactic=state.prefs.formation==='auto'?state.analysis.requested_tactic||state.analysis.tactics[0]:state.simulation;
      const plan=state.view==='current'?state.currentResult?.lineup.find(x=>x.uid===p.uid)||state.analysis.profiles[p.uid]:state.view==='tactics'?tactic?.lineup.find(x=>x.uid===p.uid)||state.analysis.profiles[p.uid]:state.analysis.profiles[p.uid];
      const text=[p.name,state.data.club,date(state.data.date),...['in_possession','out_of_possession'].flatMap(key=>{const r=plan[key];return ['',r.phase==='in_possession'?'CON POSESIÓN':'SIN POSESIÓN',r.name,...r.reasons,...r.instructions.map(i=>i.property+': '+i.value),r.source];})].join('\n');
      download('Touchline-'+p.uid+'.txt',text,'text/plain;charset=utf-8');
    }
  }).catch(error=>toast(error.message,true));
});

document.addEventListener('input',event=>{
  const input=event.target;
  if(input.id==='prompt-input'||input.id==='quick-prompt-input')state.promptDraft=input.value;
  if(input.id==='contracts-search') {state.contractsFilter.query=input.value;render();}
  if(input.id==='scouting-search') {state.scoutingFilter.query=input.value;render();}
  if(input.id==='search') {state.filters.query=input.value;$('#results').innerHTML=playerRows(state,state.view);}
});

document.addEventListener('change',event=>{
  const input=event.target;
  Promise.resolve().then(async()=>{
    if(input.dataset.current) {
      const draft=state.currentDraft, field=input.dataset.current;
      if(field==='confirmed'){draft.confirmed=input.checked;return;}
      if(field==='formation') {
        const before=draft.lineup;const fresh=freshDraft(state.data,input.value);
        fresh.lineup.forEach((row,i)=>row.uid=before[i]?.uid||'');state.currentDraft={...fresh,name:draft.name,stored_id:draft.stored_id};
      } else if(field==='stored_id') {
        draft.stored_id=input.value;
        const selected=state.data.stored_tactics.records.find(t=>t.id===input.value);if(selected)draft.name=selected.name;
      } else if(input.dataset.row!==undefined) {
        const row=draft.lineup[Number(input.dataset.row)];
        if(input.dataset.pi){if(input.value)row.instructions[input.dataset.pi]=input.value;else delete row.instructions[input.dataset.pi];}
        else {row[field]=field==='uid'?Number(input.value)||'':input.value;
          if(field.endsWith('_position'))row[field.replace('_position','_role')]='';
          if(field.endsWith('_role')) {
            const phase=field==='ip_role'?'in_possession':'out_of_possession';
            for(const key of Object.keys(row.instructions))if(state.data.tactic_editor.player_options[key]?.phase===phase)delete row.instructions[key];
          }
        }
      } else if(input.dataset.team) {if(input.value)draft.team[input.dataset.team]=input.value;else delete draft.team[input.dataset.team];}
      else draft[field]=input.value;
      saveCurrentDraft();render();return;
    }
    if(input.dataset.companionCheck) {
      try { localStorage.setItem('touchline:chk:' + input.dataset.companionCheck, input.checked ? '1' : '0'); } catch {}
      input.closest('.companion-check-item')?.classList.toggle('checked', input.checked);
      return;
    }
    if(input.id==='scouting-sort') {state.scoutingFilter.sort=input.value;render();return;}
    if(input.id==='style-select') {state.prefs.style=input.value;state.prefs.prompt='';state.prefs.overrides={};await refresh();}
    if(input.id==='formation-select') {state.prefs.formation=input.value;await refresh();}
    if(input.dataset.override) {
      if(input.value===input.dataset.applied)delete state.overrideDraft[input.dataset.override];
      else state.overrideDraft[input.dataset.override]=input.value;
      render();
    }
    if(input.dataset.available) {const id=Number(input.dataset.available);state.prefs.excluded=input.checked?state.prefs.excluded.filter(x=>x!==id):[...new Set([...state.prefs.excluded,id])];await refresh();}
    if(input.id==='group-filter'||input.id==='sort-order') {state.filters[input.id==='group-filter'?'group':'order']=input.value;$('#results').innerHTML=playerRows(state,state.view);}
  }).catch(error=>toast(error.message,true));
});

document.addEventListener('submit',event=>{
  if(!['groups-form','sync-form','retention-form'].includes(event.target.id))return;
  event.preventDefault();const form=event.target,fd=new FormData(form);
  Promise.resolve().then(async()=>{
    if(form.id==='groups-form') {
      state.prefs.primary_slot=Number(fd.get('primary_slot'));state.prefs.labels=Object.fromEntries(state.data.slots.map(s=>[s,String(fd.get('label-'+s)).trim()]));
      state.filters.group='all';$('#dialog').close();await refresh();
    } else if(form.id==='sync-form') {
      state.sync=await api('/api/sync/config',{method:'POST',body:{watch_folder:fd.get('watch_folder'),target_save:fd.get('target_save'),enabled:fd.get('enabled')==='on'}});
      $('#dialog').close();progress();toast('Configuración guardada.');
    } else {
      await api('/api/retention',{method:'POST',body:{max_snapshots:Number(fd.get('max_snapshots')),max_total_mb:Number(fd.get('max_total_mb'))}});toast('Límites guardados. Se aplican después de la próxima importación exitosa.');
    }
  }).catch(error=>toast(error.message,true));
});

document.addEventListener('keydown',event=>{if((event.target.id==='prompt-input'||event.target.id==='quick-prompt-input')&&event.key==='Enter'&&(event.ctrlKey||event.metaKey||event.target.id==='quick-prompt-input')){event.preventDefault();action('apply-prompt').catch(error=>toast(error.message,true));}});
document.addEventListener('dragover',event=>{if(event.target.closest('.upload-drop')){event.preventDefault();event.target.closest('.upload-drop').classList.add('dragover');}});
document.addEventListener('dragleave',event=>event.target.closest('.upload-drop')?.classList.remove('dragover'));
document.addEventListener('drop',event=>{const drop=event.target.closest('.upload-drop');if(drop){event.preventDefault();drop.classList.remove('dragover');startImport(event.dataTransfer.files[0]);}});
$('#save-file').addEventListener('change',event=>{const file=event.target.files[0];event.target.value='';startImport(file);});
$('#dialog-close').addEventListener('click',()=>$('#dialog').close());
$('#dialog').addEventListener('click',event=>{if(event.target===$('#dialog'))$('#dialog').close();});
window.addEventListener('hashchange',()=>navigate(location.hash.slice(1)==='simulator'?'tactics':location.hash.slice(1)));
window.addEventListener('beforeunload',()=>{stopped=true;gate.invalidate();});

async function bootstrap() {
  try {
    state.error='';
    const [status,data]=await Promise.all([api('/api/status'),api('/api/data')]);
    state.sync=status.sync;
    if(status.active_job){trackedJob=status.active_job.job_id;state.uploadBusy=true;state.job=status.active_job;}
    else if(status.last_job)handledJobs.add(status.last_job.job_id);
    state.view=navigation[location.hash.slice(1)]?location.hash.slice(1):location.hash==='#simulator'?'tactics':'overview';
    await loadDataset(data);
    if(status.restore_error)toast(status.restore_error,true);
  } catch(error) {state.error=error.message;render();}
}

await bootstrap();
poll();
