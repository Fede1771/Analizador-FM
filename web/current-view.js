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
  // 22 screenshots confirmed: individual instructions and roles for all 11 players in both phases, 24/10/2026.
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
  return `<section class="panel capture-review"><span class="eyebrow">Tus 30 capturas · 24/10/2026</span><h2>Qué revisaría en tu 4-3-3</h2><p>El once, sus roles, las instrucciones individuales y las 26 órdenes colectivas completas están precargados a partir de tus 30 capturas de FM26. Estas observaciones analizan la coordinación entre tus órdenes:</p>
    <article class="instruction"><h3>Zaga central: Vušković y Cubarsí (cobertura y duelos)</h3><p>Ambos centrales combinan presión alta + marca de cerca + entrar más fuerte con la orden colectiva de ser agresivos. Vušković (entradas ${vu.attributes.tackling}/20, agresividad ${vu.attributes.aggression}/20) y Cubarsí (entradas ${cubarsi?.attributes.tackling||15}/20) tienen gran compromiso en el duelo, pero al sumar la línea defensiva más adelantada achicando hacia adelante, si ambos enciman a la vez pueden dejar desprotegida la espalda. Probar la presión de Vušković en Normal conserva la zona.</p></article>
    <article class="instruction"><h3>Mediocampo: tres organizadores (Pavlović, Ayari y Wharton)</h3><p>Pavlović organiza desde el pivote, Ayari tiene libertad de movimiento y Wharton actúa como mediocentro organizador. La orden de pases mucho más cortos, ritmo mucho más bajo y pase al pie encaja a la perfección con su perfil de posesión. La profundidad ofensiva descansa en las rupturas de Szoboszlai (con orden de más desmarques) y los apoyos de Ekitiké.</p></article>
    <article class="instruction"><h3>Bandas: Kerkez y Wirtz por izquierda, Spence y Szoboszlai por derecha</h3><p>Con la instrucción colectiva de volcar el avance por izquierda, el juego busca deliberadamente la asociación entre Wirtz (cerrándose en diagonal) y Kerkez (atacando el espacio exterior). En la derecha, Szoboszlai encara y rompe al espacio mientras Spence acompaña.</p></article>
    <article class="instruction"><h3>Ataque, remates y entradas de Ekitiké</h3><p>Ekitiké tiene entradas ${eki.attributes.tackling}/20 y está configurado en entrar más fuerte sumado a ser agresivos colectivamente; probar la orden de entradas en Normal es una mejora razonable para evitar faltas y amarillas tempranas, manteniendo intacta su contrapresión. En remates, paciencia para entrar al área convive con disparos lejanos alentados; evaluá si no reduce la calidad de las ocasiones.</p></article>
    <article class="instruction"><h3>Estructura colectiva y bloque defensivo</h3><p>Presión adelantada más insistente, contrapresión tras pérdida y línea defensiva más adelantada con zaga achicando hacia adelante ("Presionar más arriba"), sumado a impedir saques cortos del arquero rival y evitar centros. Un bloque asfixiante de presión total coordinado con la salida en corto superando la presión.</p></article>
    <article class="instruction"><h3>Arco: Verbruggen como Portero líbero sin balón</h3><p>Con posesión actúa como Portero con salida (PCS) distribuyendo con rapidez y en corto, y sin balón se posiciona como Portero líbero (POL) para barrer balones largos a espaldas de la zaga adelantada.</p></article>
    <p class="muted">Hipótesis tácticas para probar en FM; no son fallos demostrados por datos de partidos. Las 26 instrucciones colectivas de ambas fases están 100% confirmadas y analizadas.</p><button class="button" data-action="reference-current">Cargar mi táctica de referencia confirmada</button></section>`;
}

function options(items,selected,blank='Sin confirmar') {
  return `<option value="">${blank}</option>${items.map(o=>`<option value="${esc(o.value)}" ${String(o.value)===String(selected)?'selected':''}>${esc(o.label)}</option>`).join('')}`;
}

export function currentView(state) {
  const {data,currentDraft:d,currentResult:result}=state,editor=data.tactic_editor;
  if(!editor||!d)return '<h1>Mi táctica</h1><p>Volvé a cargar la aplicación.</p>';
  const stored=data.stored_tactics||{records:[]};
  const phaseKey=state.phase==='ip'?'in_possession':'out_of_possession';
  return `<div class="page-heading"><div><span class="eyebrow">Tu plan actual, con mejoras concretas</span><h1>Mi táctica</h1><p>Evaluá los jugadores y los roles que usás en FM, conservando tu once.</p></div>${result?'<button class="button" data-action="export-current">Exportar revisión</button>':''}</div>
    ${captureReview(data)}
    <section class="panel"><h2>Confirmar tu táctica actual</h2><p class="notice">${esc(stored.limitations||'La táctica activa y sus roles necesitan confirmación.')}</p>
    <div class="control-grid"><label>Copia guardada<select id="current-stored" data-current="stored_id">${options(stored.records.map(t=>({value:t.id,label:`${t.name} · ${data.slot_labels[t.team_slot]||'Grupo '+t.team_slot} · ${t.mentality}`})),d.stored_id,'Carga manual')}</select></label>
    <label>Nombre<input id="current-name" data-current="name" value="${esc(d.name)}" maxlength="100"></label>
    <label>Plantilla inicial de posiciones <small>Aplicarla reemplaza posiciones, roles e instrucciones; conserva los jugadores por fila.</small><select id="current-formation" data-current="formation">${data.formations_catalog.map(f=>`<option value="${f.id}" ${d.formation===f.id?'selected':''}>${esc(f.name)} → ${esc(f.defensive)}</option>`).join('')}</select></label>
    <label>Objetivo para comparar el encaje<select id="current-style" data-current="style">${Object.entries(data.styles).map(([id,s])=>`<option value="${id}" ${d.style===id?'selected':''}>${esc(s.name)}</option>`).join('')}</select></label></div>
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
    ${state.currentError?`<p class="notice warning" role="alert">${esc(state.currentError)}</p>`:''}</section>
    ${result?`<section class="panel" id="current-result"><div class="split"><h2 tabindex="-1">Revisión de ${esc(result.name)}</h2>${score(result.score)}</div><p>Encaje de tu once confirmado · ${esc(data.styles[result.style].name)}</p><p>${esc(result.limits)}</p><p class="notice">Sin confirmar: ${result.unconfirmed_player_instructions} instrucciones de campo y ${result.unconfirmed_team_instructions} colectivas. No se evalúan como si fueran valores normales.</p>
    <h3>Cambios para probar sobre tu plan</h3>${result.advice.length?result.advice.map(a=>`<article class="instruction"><strong>${esc(a.title)}</strong><p>${esc(a.detail)}</p></article>`).join(''):'<p>No se detectaron alertas con las reglas disponibles. Confirmá las órdenes pendientes y observá la táctica en partidos.</p>'}</section>
    <section class="panel"><div class="split"><h2>Tu once confirmado</h2><div class="segmented"><button data-phase="ip" aria-pressed="${state.phase==='ip'}">Con posesión</button><button data-phase="oop" aria-pressed="${state.phase==='oop'}">Sin posesión</button></div></div>${pitch(result,state.phase,state.byId)}</section>
    ${zoneMap(result.coverage,state.phase)}
    <section class="panel"><h2>Ajustes de función sin cambiar al jugador</h2>${result.lineup.map(slot=>`<details><summary>${esc(state.byId.get(slot.uid).name)} · ${esc(slot[phaseKey].name)} · ${number(slot[phaseKey].score)}</summary>${rolePlan(slot[phaseKey])}<p>Alternativas por atributos, no sustituciones automáticas:</p><ul>${slot[phaseKey].alternatives.map(a=>`<li>${esc(a.name)} · ${number(a.score)}</li>`).join('')}</ul></details>`).join('')}</section>`:''}`;
}
