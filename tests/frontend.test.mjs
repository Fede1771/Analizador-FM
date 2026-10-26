import test from 'node:test';
import assert from 'node:assert/strict';
import {reconcile,preferenceKey,contextKey,filteredPlayers} from '../web/session.js';
import {RequestGate} from '../web/api.js';
import {date,esc} from '../web/format.js';
import {matchesObservedContext} from '../web/instruction-context.js';
import {supportRunsRecovery} from '../web/tactics-view.js';

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
