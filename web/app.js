import {api, upload, RequestGate} from './api.js';
import {reconcile, preferenceKey, contextKey} from './session.js';
import {esc, date} from './format.js';
import {navigation, welcome, overview, tactics, roster, methodology, playerRows, playerDialog, groupDialog, syncDialog} from './views.js';

const $ = selector => document.querySelector(selector);
const gate = new RequestGate();
const state = {data:null, analysis:null, simulation:null, byId:new Map(), prefs:null,
  view:'overview', phase:'ip', busy:false, uploadBusy:false, pendingUpload:false, error:'', connectionError:'',
  promptDraft:'', overrideDraft:{}, filters:{query:'',group:'all',order:'score'}, job:null, sync:null};
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
  const open=new Map([...content.querySelectorAll('details')].map(d=>[d.querySelector('summary')?.textContent,d.open]));
  $('#sidebar').hidden=!state.data;
  document.body.classList.toggle('has-dataset',!!state.data);
  $('#nav').innerHTML=Object.entries(navigation).map(([key,label])=>`<a href="#${key}" ${key===state.view?'aria-current="page"':''}>${label}</a>`).join('');
  $('#source-label').textContent=state.data?`${state.data.source.filename} · ${date(state.data.date)}`:'Análisis local · Football Manager 26';
  $('#groups-button').hidden=!state.data;
  let html;
  if(!state.data) html=welcome(state);
  else if(state.view==='overview') html=overview(state);
  else if(state.view==='tactics') html=tactics(state);
  else if(state.view==='method') html=methodology(state);
  else html=roster(state,state.view);
  content.innerHTML=html;
  content.setAttribute('aria-busy',String(state.busy));
  if(state.data?.warnings.length) {
    const warning=document.createElement('details'); warning.className='notice warning';
    warning.innerHTML=`<summary>${state.data.warnings.length} advertencias de lectura</summary><ul>${state.data.warnings.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`;
    content.prepend(warning);
  }
  for(const d of content.querySelectorAll('details')) {const key=d.querySelector('summary')?.textContent;if(open.has(key))d.open=open.get(key);}
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

async function action(name, button) {
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
  if(name==='apply-prompt') {
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
  const button=event.target.closest('[data-action],[data-view],[data-player],[data-formation],[data-phase],[data-download-player]');
  if(!button)return;
  Promise.resolve().then(async()=>{
    if(button.dataset.action)return action(button.dataset.action,button);
    if(button.dataset.view) {location.hash=button.dataset.view;if(state.view===button.dataset.view)navigate(button.dataset.view);return;}
    if(button.dataset.player)return showDialog(playerDialog(state,button.dataset.player));
    if(button.dataset.phase) {state.phase=button.dataset.phase;render();return;}
    if(button.dataset.formation) {state.prefs.formation=button.dataset.formation;if(state.view!=='tactics'){state.view='tactics';location.hash='tactics';}return refresh();}
    if(button.dataset.downloadPlayer) {
      const p=state.byId.get(Number(button.dataset.downloadPlayer));
      const tactic=state.prefs.formation==='auto'?state.analysis.requested_tactic||state.analysis.tactics[0]:state.simulation;
      const plan=state.view==='tactics'?tactic?.lineup.find(x=>x.uid===p.uid)||state.analysis.profiles[p.uid]:state.analysis.profiles[p.uid];
      const text=[p.name,state.data.club,date(state.data.date),...['in_possession','out_of_possession'].flatMap(key=>{const r=plan[key];return ['',r.phase==='in_possession'?'CON POSESIÓN':'SIN POSESIÓN',r.name,...r.reasons,...r.instructions.map(i=>i.property+': '+i.value),r.source];})].join('\n');
      download('Touchline-'+p.uid+'.txt',text,'text/plain;charset=utf-8');
    }
  }).catch(error=>toast(error.message,true));
});

document.addEventListener('input',event=>{
  const input=event.target;
  if(input.id==='prompt-input')state.promptDraft=input.value;
  if(input.id==='search') {state.filters.query=input.value;$('#results').innerHTML=playerRows(state,state.view);}
});

document.addEventListener('change',event=>{
  const input=event.target;
  Promise.resolve().then(async()=>{
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

document.addEventListener('keydown',event=>{if(event.target.id==='prompt-input'&&event.key==='Enter'&&(event.ctrlKey||event.metaKey)){event.preventDefault();action('apply-prompt').catch(error=>toast(error.message,true));}});
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
