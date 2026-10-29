import test from 'node:test';
import assert from 'node:assert/strict';
import {reconcile,preferenceKey,contextKey,filteredPlayers} from '../web/session.js';
import {RequestGate} from '../web/api.js';
import {date,esc} from '../web/format.js';
import {matchesObservedContext} from '../web/instruction-context.js';
import {supportRunsRecovery,rolePlan} from '../web/tactics-view.js';
import {storedDraft,reconcileCurrentDraft,draftPitch,currentView,CURRENT_READER_VERSION} from '../web/current-view.js';

const data={id:'save1',career_id:'career',default_primary_slot:0,slots:[0,1],styles:{possession:{},press:{}},players:[{uid:1,name:'Álvarez',team_slot:0,natural_positions:['STC'],age:23},{uid:2,name:'Gómez',team_slot:1,natural_positions:['MC'],age:18}],formations_catalog:[{id:'352'}],instruction_options:{tempo:[{value:'Lower'}]}};

test('preferences survive a new save, prune removed players and keep stable career key',()=>{
  const saved={primary_slot:0,labels:{0:'Titulares',99:'Old'},style:'press',excluded:[1,999],prompt:'Presión alta',formation:'352',overrides:{tempo:'Lower',bad:'bad'}};
  const next={...data,id:'save2'};
  assert.equal(preferenceKey(data),preferenceKey(next));
  const prefs=reconcile(next,saved);
  assert.deepEqual(prefs.excluded,[1]);assert.equal(prefs.labels[99],undefined);assert.deepEqual(prefs.overrides,{tempo:'Lower'});
  assert.equal(prefs.prompt,saved.prompt);assert.equal(prefs.style,'press');
  assert.notEqual(contextKey(data,prefs),contextKey(next,prefs));
});

test('request gate rejects stale simulations and old datasets',()=>{
  const gate=new RequestGate();const first=gate.begin('save1'),second=gate.begin('save1');
  assert.ok(first.signal.aborted);assert.equal(first.current('save1'),false);assert.equal(second.current('save1'),true);
  assert.equal(second.current('save2'),false);gate.invalidate();assert.equal(second.current('save1'),false);
});

test('all roster filters work on loans and accents',()=>{
  assert.equal(filteredPlayers(data.players,{query:'alvarez',group:'all',order:'name'}).length,1);
  assert.equal(filteredPlayers(data.players,{query:'',group:'1',order:'age'})[0].uid,2);
  assert.deepEqual(filteredPlayers(data.players,{query:'',group:'all',order:'age'}).map(p=>p.uid),[2,1]);
});

test('invalid dates and unsafe text remain presentable',()=>{
  assert.equal(date('invalid'),'Sin fecha');assert.equal(esc('<script>'),'&lt;script&gt;');
});

test('role evidence checks position, scope, side and number of same-position players',()=>{
  const observed={requirements:{position:'DC',scope:'position',side:'right',count:3}};
  const rows=Array.from({length:3},()=>({ip_position:'DC',instruction_scope:'Posición'}));
  assert.equal(matchesObservedContext(observed,rows,2,'ip'),true);
  assert.equal(matchesObservedContext(observed,rows,0,'ip'),false);
  assert.equal(matchesObservedContext(observed,rows.slice(1),1,'ip'),false);
  rows[2].instruction_scope='Personalizada';
  assert.equal(matchesObservedContext(observed,rows,2,'ip'),false);
  assert.equal(matchesObservedContext({},rows,2,'ip'),false);
});

test('legacy desdobles remain editable without a calculated proposal and preserve unrelated settings',()=>{
  const prefs={overrides:{tempo:'Lower',overlap_ip:'Overlap - Left',underlap_ip:'Underlap - Left'}};
  const original=structuredClone(prefs);
  const options={overlap_ip:['Overlap - Balanced','Overlap - Left','Overlap - Right'],underlap_ip:['Underlap - Balanced','Underlap - Left','Underlap - Right']};
  const recoveryData={tactic_editor:{team_properties:{overlap_ip:'Doblar por banda',underlap_ip:'Doblar por dentro'}},instruction_options:Object.fromEntries(Object.entries(options).map(([id,values])=>[id,values.map(value=>({value,label:value}))]))};
  const html=supportRunsRecovery(recoveryData,prefs);
  assert.ok(html.includes('id="override-overlap_ip"'));
  assert.ok(html.includes('id="override-underlap_ip"'));
  assert.ok(html.includes('data-action="apply-overrides"'));
  assert.deepEqual(prefs,original);
});

function brightonData() {
  const formations=[['433','4-3-3',['GK','DL','DC','DC','DR','DM','MC','MC','AML','STC','AMR']],['4231','4-2-3-1',['GK','DL','DC','DC','DR','DM','DM','AMC','AML','STC','AMR']]]
    .map(([id,name,positions])=>({id,name,slots:positions.map(p=>({ip_position:p,oop_position:p}))}));
  return {...data,club:'Brighton & Hove Albion',liverpool_reference:null,
    players:Array.from({length:11},(_,i)=>({uid:i+1,name:['Bart Verbruggen','Yasin Ayari','Adam Wharton'][i]||'Jugador '+(i+1)})),
    stored_tactics:{schema_version:2,records:formations.map((f,i)=>({id:i?'first':'reserves',name:i?'Plan personalizado':'4-3-3',team_slot:i?0:1,positions_available:true,formation_ip:f.name,formation_oop:f.name,lineup:f.slots.map((s,index)=>({...s,uid:i?index+1:null,ip_role:'',oop_role:'',instructions:{}}))}))},
    tactic_editor:{formations,roles:{},positions:['GK','DL','DC','DR','DM','MC','AMC','AML','AMR','STC'],player_options:{}}};
}

test('Brighton loads the saved shape and eleven players regardless of tactic name, without Liverpool data',()=>{
  const club=brightonData();
  for(const draft of [storedDraft(club),reconcileCurrentDraft(club,null),reconcileCurrentDraft(club,{...storedDraft(club),reader_version:0})]) {
    assert.equal(draft.formation,'stored');assert.equal(draft.formation_ip,'4-2-3-1');assert.equal(draft.name,'Plan personalizado');assert.equal(draft.stored_id,'first');
    assert.equal(draft.confirmed,false);assert.deepEqual(draft.team,{});
    assert.deepEqual(draft.lineup.map(r=>r.uid),Array.from({length:11},(_,i)=>i+1));
    assert.ok(draft.lineup.every(r=>!r.ip_role&&!r.oop_role&&Object.keys(r.instructions).length===0));
  }
  assert.equal(storedDraft(club,'reserves').formation_ip,'4-3-3');
  assert.ok(storedDraft(club,'reserves').lineup.every(r=>!r.uid));
  club.stored_tactics.records=[];
  assert.equal(storedDraft(club).stored_id,'');
});

test('draft pitch renders eleven editable slots before an audit, including missing players and phase changes',()=>{
  const club=brightonData(),draft=storedDraft(club),byId=new Map([[1,club.players[0]]]);
  draft.lineup[0].uid=1;draft.lineup[7].oop_position='MC';
  const ip=draftPitch(draft,'ip',byId,club.tactic_editor),oop=draftPitch(draft,'oop',byId,club.tactic_editor);
  assert.equal((ip.match(/data-current-slot=/g)||[]).length,11);
  assert.match(ip,/Verbruggen/);assert.match(ip,/Elegí jugador/);assert.match(ip,/Sin rol/);
  assert.notEqual(ip,oop);
  const dc=Array.from(ip.matchAll(/style="left:([\d.]+)%;top:76%"/g),m=>m[1]);
  assert.deepEqual(dc,['38','62']);
});

test('storedDraft and reconcileCurrentDraft load decoded instructions, preserve manual overrides across upgrades/saves, and never mix careers',()=>{
  const club=brightonData();
  club.slot_labels={0:'Titulares',1:'Suplentes'};
  club.instruction_options={tempo:[{value:'Lower',label:'Bajo'},{value:'Higher',label:'Alto'}],passing_directness:[{value:'Shorter',label:'Corto'}]};
  club.tactic_editor.roles={
    goalkeeper_ip:{phase:'in_possession',positions:['GK'],name:'Portero',abbreviation:'POR'},
    goalkeeper_oop:{phase:'out_of_possession',positions:['GK'],name:'Portero',abbreviation:'POR'},
  };
  club.tactic_editor.player_options={
    passing_directness_ip:{phase:'in_possession',label:'Pases',options:[{value:'Shorter',label:'Más cortos'},{value:'Standard',label:'Estándar'}]},
  };
  club.stored_tactics.records[1].team_instructions={tempo:'Higher',passing_directness:'Shorter'};
  club.stored_tactics.records[1].lineup[0].ip_role='goalkeeper_ip';
  club.stored_tactics.records[1].lineup[0].oop_role='goalkeeper_oop';
  club.stored_tactics.records[1].lineup[0].instructions={passing_directness_ip:'Standard'};
  club.stored_tactics.records[1].lineup[0].instruction_sources={passing_directness_ip:'role'};

  const initial=storedDraft(club);
  assert.equal(initial.reader_version,CURRENT_READER_VERSION);
  assert.deepEqual(initial.team,{tempo:'Higher',passing_directness:'Shorter'});
  assert.deepEqual(initial.team_sources,{tempo:'save',passing_directness:'save'});
  assert.equal(initial.lineup[0].instructions.passing_directness_ip,'Standard');
  assert.equal(initial.lineup[0].instruction_sources.passing_directness_ip,'role');

  // Legacy v2 draft from same career with manual overrides preserves manual edits while loading newly decoded fields
  const v2Saved={
    ...initial,
    reader_version:2,
    team:{tempo:'Lower'},
    lineup:initial.lineup.map((r,i)=>i===0?{...r,instructions:{passing_directness_ip:'Shorter'}}:{...r,instructions:{}}),
  };
  const upgraded=reconcileCurrentDraft(club,v2Saved);
  assert.equal(upgraded.reader_version,CURRENT_READER_VERSION);
  assert.equal(upgraded.team.tempo,'Lower');
  assert.equal(upgraded.team_sources.tempo,'manual');
  assert.equal(upgraded.team.passing_directness,'Shorter');
  assert.equal(upgraded.team_sources.passing_directness,'save');
  assert.equal(upgraded.lineup[0].instructions.passing_directness_ip,'Shorter');
  assert.equal(upgraded.lineup[0].instruction_sources.passing_directness_ip,'manual');

  // Newer save of the same career preserves manual overrides
  const nextSave={...club,id:'save2'};
  const afterNewSave=reconcileCurrentDraft(nextSave,upgraded);
  assert.equal(afterNewSave.source_dataset_id,'save2');
  assert.equal(afterNewSave.team.tempo,'Lower');
  assert.equal(afterNewSave.team_sources.tempo,'manual');
  assert.equal(afterNewSave.lineup[0].instructions.passing_directness_ip,'Shorter');
  assert.equal(afterNewSave.lineup[0].instruction_sources.passing_directness_ip,'manual');

  // Different career_id or unrelated player UIDs never mix careers
  const otherCareerDraft={...upgraded,career_id:'other-career',team:{tempo:'Lower'}};
  const fromOtherCareer=reconcileCurrentDraft(club,otherCareerDraft);
  assert.equal(fromOtherCareer.team.tempo,'Higher');
  assert.equal(fromOtherCareer.team_sources.tempo,'save');
});

test('currentView and rolePlan separate value provenance badges from control availability badges',()=>{
  const club=brightonData();
  club.slot_labels={0:'Titulares',1:'Suplentes'};
  club.instruction_options={tempo:[{value:'Higher',label:'Alto'}]};
  club.tactic_editor.team_properties={tempo:'Ritmo de juego'};
  club.tactic_editor.roles={
    goalkeeper_ip:{phase:'in_possession',positions:['GK'],name:'Portero',abbreviation:'POR'},
    goalkeeper_oop:{phase:'out_of_possession',positions:['GK'],name:'Portero',abbreviation:'POR'},
  };
  club.tactic_editor.player_options={
    passing_directness_ip:{phase:'in_possession',label:'Pases',options:[{value:'Shorter',label:'Más cortos'},{value:'Standard',label:'Estándar'}]},
    shooting_distance_ip:{phase:'in_possession',label:'Disparo',options:[{value:'Standard',label:'Estándar'}]},
  };
  club.stored_tactics.records[1].team_instructions={tempo:'Higher'};
  club.stored_tactics.records[1].lineup[0].ip_role='goalkeeper_ip';
  club.stored_tactics.records[1].lineup[0].oop_role='goalkeeper_oop';
  club.stored_tactics.records[1].lineup[0].instructions={passing_directness_ip:'Shorter',shooting_distance_ip:'Standard'};
  club.stored_tactics.records[1].lineup[0].instruction_sources={passing_directness_ip:'save',shooting_distance_ip:'role'};

  const draft=storedDraft(club);
  const byId=new Map(club.players.map(p=>[p.uid,p]));
  const html=currentView({data:club,currentDraft:draft,currentResult:null,phase:'ip',byId,uploadBusy:false,currentBusy:false});
  assert.ok(html.includes('📥 Leído del guardado'));
  assert.ok(html.includes('🔒 Definido por el rol'));
  assert.ok(html.includes('❓ Disponibilidad no verificada'));

  const planHtml=rolePlan({
    phase:'in_possession',position:'GK',name:'Portero',english:'Goalkeeper',score:75,
    reasons:['Buen encaje'],warnings:[],comparison:'',spanish_status:'',source:'https://example.com',
    instructions:[
      {property:'Pases',value:'Más cortos',origin:'save',availability_status:'unverified',reason:'Leído del guardado'},
      {property:'Disparo',value:'Estándar',origin:'adjustment',availability_status:'editable_verified',reason:'Recomendado'},
    ],
  });
  assert.ok(planHtml.includes('📥 Leído del guardado'));
  assert.ok(planHtml.includes('❓ Disponibilidad no verificada'));
  assert.ok(planHtml.includes('💡 Recomendación'));
  assert.ok(planHtml.includes('⚙️ Editable comprobado'));
});
