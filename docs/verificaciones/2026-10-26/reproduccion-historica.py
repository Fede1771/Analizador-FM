from pathlib import Path

root = Path.cwd()
base = (root / 'tests/browser.test.mjs').read_text(encoding='utf-8')
prefix = base.split("  await check('startup and overview'")[0]
prefix = prefix.replace('const testDirectory=path.dirname(fileURLToPath(import.meta.url));\nconst root=path.dirname(testDirectory);', "const root=process.cwd();\nconst testDirectory=path.join(root,'tests');")
prefix = prefix.replace("const {url}=JSON.parse(fs.readFileSync(serverFile,'utf8'));", "const {url,storage}=JSON.parse(fs.readFileSync(serverFile,'utf8'));")
suffix = base[base.index('} finally {'):]
body = r'''
  await wait(`document.querySelector('h1')?.textContent==='Club de prueba'`,'startup');
  const data=await (await fetch(url+'/api/data')).json();
  const observations={};
  const request={dataset_id:data.id,style:'press',primary_slot:data.default_primary_slot,formation:'433',overrides:{underlap_ip:'Underlap - Left'}};
  const partial=await fetch(url+'/api/simulate',{method:'POST',headers:{'Content-Type':'application/json','X-FM-App':'1'},body:JSON.stringify(request)});
  const proposal=await partial.json();
  observations.partial_override={http_status:partial.status,values:proposal.instructions?.filter(i=>['overlap_ip','underlap_ip'].includes(i.id)).map(i=>({id:i.id,value:i.value_en}))};
  const isolated=path.resolve(storage);
  assert.ok(isolated.startsWith(path.resolve(root,'.tmp','revision-2026-10-26','temp')+path.sep));
  assert.ok(path.basename(isolated).startsWith('touchline-ui-'));
  const old={primary_slot:data.default_primary_slot,labels:{[data.default_primary_slot]:'Grupo conservado'},excluded:[],style:'possession',prompt:'',formation:'auto',overrides:{tempo:'Lower',overlap_ip:'Overlap - Left',underlap_ip:'Underlap - Left'}};
  await wait(`fetch('/api/preferences').then(r=>r.json()).then(p=>p!==null)`,'initial preferences persisted');
  fs.mkdirSync(path.join(isolated,'imports'),{recursive:true});
  fs.writeFileSync(path.join(isolated,'imports','preferences.json'),JSON.stringify({[data.career_id]:old}));
  await send('Page.navigate',{url:url+'/#tactics'});
  await send('Page.reload');
  await wait(`document.querySelector('[role="alert"]')?.textContent.includes('Carreras de apoyo')`,'old preference conflict');
  observations.legacy_conflict=await evaluate(`({error:document.querySelector('[role="alert"]').textContent,overlap_select:!!document.querySelector('#override-overlap_ip'),underlap_select:!!document.querySelector('#override-underlap_ip'),clear_button:!!document.querySelector('[data-action="clear-overrides"]'),text:document.querySelector('#content').textContent.includes('No hay un once completo')})`);
  const conflictShot=await send('Page.captureScreenshot',{format:'png'});
  fs.writeFileSync(path.join(folder,'legacy-conflict.png'),Buffer.from(conflictShot.data,'base64'));
  await set('#style-select','possession');await ready();
  await navigate('current');await wait(`document.querySelector('#current-ip-position-4')`,'current editor');
  await set('#current-ip-position-4','WBL');
  await set('#current-ip-role-4','playmaking_wing_back_ip');
  await set('#current-scope-4','Personalizada');
  observations.unverified_context=await evaluate(`(()=>{const select=document.querySelector('#current-pi-4-hold_up_ball_ip');return {position:document.querySelector('#current-ip-position-4').value,scope:document.querySelector('#current-scope-4').value,disabled:select.disabled,label:select.closest('label').textContent.trim().replace(/\s+/g,' ')};})()`);
  const after=await (await fetch(url+'/api/preferences')).json();
  observations.reset_workaround={overrides:after.overrides,labels:after.labels};
  fs.writeFileSync(path.join(folder,'audit-observations.json'),JSON.stringify(observations,null,2));
  console.log(JSON.stringify(observations,null,2));
'''
out = root / '.tmp/revision-2026-10-26/browser-audit.mjs'
out.write_text(prefix + body + suffix, encoding='utf-8')
print(out)
