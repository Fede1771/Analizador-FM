import {spawn} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';

const testDirectory=path.dirname(fileURLToPath(import.meta.url));
const root=path.dirname(testDirectory);
fs.mkdirSync(path.join(root,'.tmp'),{recursive:true});
const folder=process.env.TOUCHLINE_TEST_ARTIFACTS || fs.mkdtempSync(path.join(root,'.tmp','browser-'));
fs.mkdirSync(folder,{recursive:true});
const python=process.env.PYTHON_BIN || path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
const candidates=[process.env.CHROME_BIN,'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe','C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe','/usr/bin/chromium','/usr/bin/google-chrome'].filter(Boolean);
const browserExecutable=candidates.find(name=>fs.existsSync(name));
assert.ok(browserExecutable,'Install Chromium/Chrome/Edge or set CHROME_BIN');
const serverFile=path.join(folder,`ui-server-${Date.now()}-${process.pid}.json`);
const host=spawn(python,['-B',path.join(testDirectory,'browser_host.py'),folder,serverFile],{windowsHide:true,stdio:['ignore','pipe','pipe']});
let hostLog='';host.stdout.on('data',chunk=>hostLog+=chunk);host.stderr.on('data',chunk=>hostLog+=chunk);
let hostReady=false;
for(let i=0;i<300;i++) {
  if(fs.existsSync(serverFile)){hostReady=true;break;}
  if(host.exitCode!==null)break;
  await new Promise(resolve=>setTimeout(resolve,100));
}
if(!hostReady){host.kill();throw new Error('Test server failed: '+hostLog);}
const {url}=JSON.parse(fs.readFileSync(serverFile,'utf8'));
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'touchline-browser-'));
const chrome=spawn(browserExecutable,[
  '--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',
  '--remote-debugging-port=0','--remote-allow-origins=*',`--user-data-dir=${profile}`,'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
let diagnostics='';chrome.stderr.on('data',chunk=>diagnostics+=chunk);
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let socket;
const results=[];
try {
  let endpoint;
  for(let i=0;i<100;i++){endpoint=diagnostics.match(/DevTools listening on (ws:\/\/[^\s]+)/)?.[1];if(endpoint)break;await sleep(100);}
  assert.ok(endpoint,'Chrome debugging endpoint');
  const address=new URL(endpoint);
  const targets=await (await fetch(`http://${address.host}/json/list`)).json();
  const target=targets.find(t=>t.type==='page');
  socket=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
  let sequence=0;const pending=new Map();const errors=[];
  socket.addEventListener('message',event=>{
    const value=JSON.parse(event.data);
    if(value.id){const callback=pending.get(value.id);if(callback){pending.delete(value.id);value.error?callback.reject(new Error(value.error.message)):callback.resolve(value.result);}}
    if(value.method==='Runtime.exceptionThrown')errors.push(value.params.exceptionDetails.exception?.description||value.params.exceptionDetails.text);
    if(value.method==='Log.entryAdded'&&value.params.entry.level==='error') {
      const entry=value.params.entry;
      if(!(entry.url?.includes('/api/simulate')&&entry.text.includes('400')))errors.push(entry.text);
    }
  });
  function send(method,params={}){return new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}));});}
  async function evaluate(expression){const result=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw new Error(result.exceptionDetails.exception?.description||result.exceptionDetails.text);return result.result.value;}
  async function wait(expression,label,timeout=30000){const started=Date.now();while(Date.now()-started<timeout){if(await evaluate(expression))return;await sleep(150);}throw new Error('Timeout: '+label);}
  async function check(name,fn){await fn();results.push(name);console.log('PASS '+name);}
  async function navigate(hash){await evaluate(`location.hash=${JSON.stringify(hash)}`);await sleep(100);}
  async function set(selector,value,event='change'){await evaluate(`(()=>{const el=document.querySelector(${JSON.stringify(selector)});el.value=${JSON.stringify(value)};el.dispatchEvent(new Event(${JSON.stringify(event)},{bubbles:true}));})()`);}
  async function ready(){await wait(`document.querySelector('#content')?.getAttribute('aria-busy')==='false' && document.querySelector('.pitch-player')`,'tactical result');}
  async function change(value){await fetch(url+'/__test/change',{method:'POST',headers:{'Content-Type':'application/json','X-FM-App':'1'},body:JSON.stringify(value)});}
  await send('Page.enable');await send('Runtime.enable');await send('Log.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:1360,height:1000,deviceScaleFactor:1,mobile:false});
  await change({id:'initial-save'});
  await send('Page.navigate',{url});
  await check('startup and overview',async()=>{await wait(`document.querySelector('h1')?.textContent==='Club de prueba' && document.querySelectorAll('.formation-card').length===3`,'overview');});
  await check('unified tactics and eleven players',async()=>{await navigate('tactics');await ready();assert.equal(await evaluate(`document.querySelectorAll('.pitch-player').length`),11);});
  await check('formation simulation and localized controls',async()=>{await set('#formation-select','352');await ready();assert.ok(await evaluate(`document.querySelector('.result-heading h2').textContent.includes('3-5-2')`));assert.ok(await evaluate(`document.querySelector('#override-tempo').options[0].textContent.includes('bajo')`));});
  await check('pending instructions survive phase changes and navigation',async()=>{
    await evaluate(`document.querySelector('#override-tempo').closest('details').open=true`);
    const original=await evaluate(`document.querySelector('#override-tempo').value`);
    const options=await evaluate(`Array.from(document.querySelector('#override-tempo').options).map(o=>o.value)`);
    const chosen=options.find(o=>o!==original);
    await set('#override-tempo',chosen);
    for(const phase of ['oop','ip']) {
      await evaluate(`document.querySelector('#phase-${phase}').click()`);
      assert.equal(await evaluate(`document.querySelector('#override-tempo').value`),chosen);
    }
    await navigate('overview');await navigate('tactics');await ready();
    assert.equal(await evaluate(`document.querySelector('#override-tempo').value`),chosen);
    assert.equal(await evaluate(`document.querySelector('#override-tempo').closest('.instruction').querySelector('label small').textContent`),'Cambio pendiente');
    assert.equal(await evaluate(`document.querySelector('[data-pending-overrides]').textContent.includes('1 cambio sin aplicar')`),true);
    assert.notEqual(await evaluate(`fetch('/api/preferences').then(r=>r.json()).then(p=>p.overrides.tempo)`),chosen);
    await evaluate(`document.querySelector('[data-action="apply-overrides"]').click()`);await ready();
    assert.equal(await evaluate(`document.querySelector('#override-tempo').value`),chosen);
    await wait(`fetch('/api/preferences').then(r=>r.json()).then(p=>p.overrides.tempo===${JSON.stringify(chosen)})`,'manual instruction persisted');
    assert.equal(await evaluate(`document.querySelector('[data-pending-overrides]')===null`),true);
  });
  await check('returning to applied instruction removes pending change',async()=>{
    await evaluate(`document.querySelector('#override-tempo').closest('details').open=true`);
    const applied=await evaluate(`document.querySelector('#override-tempo').value`);
    const other=await evaluate(`Array.from(document.querySelector('#override-tempo').options).map(o=>o.value).find(o=>o!==${JSON.stringify(applied)})`);
    await set('#override-tempo',other);await set('#override-tempo',applied);
    await evaluate(`document.querySelector('#phase-oop').click()`);
    assert.equal(await evaluate(`document.querySelector('#override-tempo').value`),applied);
    assert.equal(await evaluate(`document.querySelector('[data-pending-overrides]')===null`),true);
  });
  await check('reset manual instructions discards the pending draft',async()=>{
    const applied=await evaluate(`document.querySelector('#override-tempo').value`);
    const other=await evaluate(`Array.from(document.querySelector('#override-tempo').options).map(o=>o.value).find(o=>o!==${JSON.stringify(applied)})`);
    await set('#override-tempo',other);
    await evaluate(`document.querySelector('[data-action="clear-overrides"]').click()`);await ready();
    await wait(`fetch('/api/preferences').then(r=>r.json()).then(p=>Object.keys(p.overrides).length===0)`,'manual instructions reset');
    const reset=await evaluate(`document.querySelector('#override-tempo').value`);
    await evaluate(`document.querySelector('#phase-ip').click()`);
    assert.equal(await evaluate(`document.querySelector('#override-tempo').value`),reset);
    assert.equal(await evaluate(`document.querySelector('[data-pending-overrides]')===null`),true);
  });
  await check('avoiding possession loss keeps short passing in the UI',async()=>{
    await evaluate(`document.querySelector('#prompt-details').open=true`);
    await set('#prompt-input','Quiero mantener la posesión sin perder el balón','input');
    await evaluate(`document.querySelector('[data-action="apply-prompt"]').click()`);await ready();
    assert.equal(await evaluate(`document.querySelector('#style-select').value`),'possession');
    assert.equal(await evaluate(`document.querySelector('#override-passing_directness').value`),'Shorter');
    assert.equal(await evaluate(`document.querySelector('#override-tempo').value`),'Lower');
    assert.equal(await evaluate(`document.querySelector('.interpretation').textContent.includes('Evitar: possession')`),false);
  });
  await check('negative pressure request',async()=>{await evaluate(`document.querySelector('#prompt-details').open=true`);await set('#prompt-input','No quiero presión alta','input');await evaluate(`document.querySelector('[data-action="apply-prompt"]').click()`);await ready();assert.equal(await evaluate(`document.querySelector('#style-select').value`),'possession');assert.notEqual(await evaluate(`document.querySelector('#override-line_of_engagement_oop').value`),'High Press');});
  await check('pressing request retains counterpress',async()=>{await set('#prompt-input','Presión alta, recuperar rápido','input');await evaluate(`document.querySelector('[data-action="apply-prompt"]').click()`);await ready();assert.equal(await evaluate(`document.querySelector('#style-select').value`),'press');assert.equal(await evaluate(`document.querySelector('#override-defensive_transition_oop').value`),'Counter-Press');});
  await check('player plan dialog',async()=>{await evaluate(`document.querySelector('.pitch-player').click()`);assert.ok(await evaluate(`document.querySelector('#dialog').open`));assert.equal(await evaluate(`document.querySelectorAll('.role-plan').length`),2);await evaluate(`document.querySelector('#dialog-close').click()`);});
  await check('loan search and sort',async()=>{await navigate('loans');await wait(`document.querySelector('#search')`,'loans');await set('#search','200','input');assert.equal(await evaluate(`document.querySelectorAll('#results tbody tr').length`),1);await set('#sort-order','age');assert.equal(await evaluate(`document.querySelectorAll('#results tbody tr').length`),1);});
  await check('preferences survive a new save',async()=>{await change({id:'save-next'});await wait(`document.querySelector('#source-label') && !document.querySelector('#activity').hidden`,'dataset refresh');await wait(`document.querySelector('#activity').hidden`,'refresh finished');await navigate('tactics');await ready();assert.equal(await evaluate(`document.querySelector('#formation-select').value`),'352');assert.equal(await evaluate(`document.querySelector('#style-select').value`),'press');});
  await check('desktop layout',async()=>{await evaluate(`document.querySelectorAll('details').forEach(d=>d.open=false);window.scrollTo(0,0)`);assert.ok(await evaluate(`document.documentElement.scrollWidth<=window.innerWidth`));const shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(folder,'touchline-desktop.png'),Buffer.from(shot.data,'base64'));});
  await check('responsive layout and keyboard focus',async()=>{await send('Emulation.setDeviceMetricsOverride',{width:760,height:1000,deviceScaleFactor:1,mobile:false});await sleep(200);assert.ok(await evaluate(`document.documentElement.scrollWidth<=window.innerWidth`));await evaluate(`document.querySelector('#formation-select').focus()`);assert.equal(await evaluate(`document.activeElement.id`),'formation-select');const shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(folder,'touchline-responsive.png'),Buffer.from(shot.data,'base64'));});
  await check('insufficient squad stops without retry loop',async()=>{await change({id:'short-save',short:true});await wait(`document.querySelector('[role="alert"]')?.textContent.includes('suficientes')`,'insufficient squad');const before=await (await fetch(url+'/__test/counts')).json();await sleep(5500);const after=await (await fetch(url+'/__test/counts')).json();assert.equal(after['/api/simulate'],before['/api/simulate']);});
  await check('welcome and synchronization settings',async()=>{await change({empty:true});await send('Page.reload');await wait(`document.querySelector('.upload-drop')`,'welcome');await evaluate(`document.querySelector('#sync-button').click()`);await wait(`document.querySelector('#sync-form')`,'sync dialog');assert.ok(await evaluate(`document.querySelector('#retention-form')`));await evaluate(`document.querySelector('#dialog-close').click()`);});
  await check('application can close from welcome',async()=>{
    await evaluate(`document.querySelector('.topbar [data-action="shutdown"]').click()`);
    await wait(`document.querySelector('h1')?.textContent==='Touchline se cerró'`,'application shutdown');
  });
  assert.deepEqual(errors,[],'Browser runtime errors');
  fs.writeFileSync(path.join(folder,'browser-results.json'),JSON.stringify({passed:results,errors},null,2));
  console.log(JSON.stringify({passed:results.length,errors:errors.length}));
} finally {
  socket?.close();chrome.kill();
  try { await fetch(url+'/api/shutdown',{method:'POST',headers:{'Content-Type':'application/json','X-FM-App':'1'},body:'{}',signal:AbortSignal.timeout(1000)}); } catch {}
  if(host.exitCode===null){await Promise.race([new Promise(resolve=>host.once('exit',resolve)),new Promise(resolve=>setTimeout(resolve,2000))]);if(host.exitCode===null)host.kill();}
  console.log('Browser artifacts: '+folder);
  await sleep(700);
  const resolved=path.resolve(profile);
  if(resolved.startsWith(path.resolve(os.tmpdir())+path.sep)&&path.basename(resolved).startsWith('touchline-browser-'))fs.rmSync(resolved,{recursive:true,force:true,maxRetries:5,retryDelay:300});
}
