import {spawn} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';

const testDirectory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(testDirectory, '..');
const outDir = path.join(root, 'docs', 'capturas-finales');
fs.mkdirSync(outDir, {recursive: true});

const python = process.env.PYTHON_BIN || path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const candidates = [
  process.env.CHROME_BIN,
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  '/usr/bin/chromium',
  '/usr/bin/google-chrome'
].filter(Boolean);
const browserExecutable = candidates.find(name => fs.existsSync(name));
assert.ok(browserExecutable, 'Install Chromium/Chrome/Edge or set CHROME_BIN');

fs.mkdirSync(path.join(root, '.tmp'), {recursive: true});
const tempFolder = fs.mkdtempSync(path.join(root, '.tmp', 'screenshots-'));
const serverFile = path.join(tempFolder, `ui-server-${Date.now()}-${process.pid}.json`);
const host = spawn(python, ['-B', path.join(root, 'tests', 'browser_host.py'), tempFolder, serverFile], {
  windowsHide: true,
  stdio: ['ignore', 'pipe', 'pipe']
});

let hostLog = '';
host.stdout.on('data', chunk => hostLog += chunk);
host.stderr.on('data', chunk => hostLog += chunk);

let hostReady = false;
for (let i = 0; i < 300; i++) {
  if (fs.existsSync(serverFile)) { hostReady = true; break; }
  if (host.exitCode !== null) break;
  await new Promise(r => setTimeout(r, 100));
}
if (!hostReady) { host.kill(); throw new Error('Test server failed: ' + hostLog); }

const {url} = JSON.parse(fs.readFileSync(serverFile, 'utf8'));
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'touchline-shots-'));
const chrome = spawn(browserExecutable, [
  '--headless=new',
  '--disable-gpu',
  '--no-first-run',
  '--no-default-browser-check',
  '--remote-debugging-port=0',
  '--remote-allow-origins=*',
  `--user-data-dir=${profile}`,
  'about:blank'
], {windowsHide: true, stdio: ['ignore', 'ignore', 'pipe']});

let diagnostics = '';
chrome.stderr.on('data', chunk => diagnostics += chunk);
const sleep = ms => new Promise(r => setTimeout(r, ms));

let socket;
try {
  let endpoint;
  for (let i = 0; i < 100; i++) {
    endpoint = diagnostics.match(/DevTools listening on (ws:\/\/[^\s]+)/)?.[1];
    if (endpoint) break;
    await sleep(100);
  }
  assert.ok(endpoint, 'Chrome debugging endpoint');

  const address = new URL(endpoint);
  const targets = await (await fetch(`http://${address.host}/json/list`)).json();
  const target = targets.find(t => t.type === 'page');
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, {once: true});
    socket.addEventListener('error', reject, {once: true});
  });

  let sequence = 0;
  const pending = new Map();
  socket.addEventListener('message', event => {
    const value = JSON.parse(event.data);
    if (value.id) {
      const cb = pending.get(value.id);
      if (cb) {
        pending.delete(value.id);
        value.error ? cb.reject(new Error(value.error.message)) : cb.resolve(value.result);
      }
    }
  });

  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++sequence;
      pending.set(id, {resolve, reject});
      socket.send(JSON.stringify({id, method, params}));
    });
  }

  async function evaluate(expression) {
    const res = await send('Runtime.evaluate', {expression, returnByValue: true, awaitPromise: true});
    if (res.exceptionDetails) throw new Error(res.exceptionDetails.exception?.description || res.exceptionDetails.text);
    return res.result?.value;
  }

  async function wait(expression, label, timeout = 30000) {
    const started = Date.now();
    while (Date.now() - started < timeout) {
      if (await evaluate(expression)) return;
      await sleep(150);
    }
    throw new Error('Timeout: ' + label);
  }

  async function set(selector, value, event = 'change') {
    await evaluate(`(()=>{const el=document.querySelector(${JSON.stringify(selector)});el.value=${JSON.stringify(value)};el.dispatchEvent(new Event(${JSON.stringify(event)},{bubbles:true}));})()`);
  }

  async function snap(filename) {
    await sleep(500); // ensure layout/render completes
    const res = await send('Page.captureScreenshot', {format: 'png'});
    const buf = Buffer.from(res.data, 'base64');
    const dest = path.join(outDir, filename);
    fs.writeFileSync(dest, buf);
    console.log(`Saved screenshot: ${dest} (${buf.length} bytes)`);
  }

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Log.enable');

  // 1. Overview / Centro del club (1360x920)
  await send('Emulation.setDeviceMetricsOverride', {width: 1360, height: 920, deviceScaleFactor: 1, mobile: false});
  await send('Page.navigate', {url});
  await wait(`document.querySelector('h1')?.textContent==='Club de prueba'`, 'overview heading');
  await snap('01-inicio-centro-del-club.png');

  // Ojeo de mercado masculino
  await evaluate(`location.hash='scouting'`);
  await wait(`document.querySelector('.scouting-grid')`, 'scouting grid');
  await snap('07-ojeo-masculino.png');

  // Plantilla con gestión de sobrepoblación
  await evaluate(`location.hash='squad'`);
  await wait(`document.querySelector('#results table')`, 'squad table');
  await snap('08-plantilla-sobrepoblacion.png');

  // 2. Propuestas (1360x920)
  await evaluate(`location.hash='tactics'`);
  await wait(`document.querySelectorAll('.pitch-player').length===11 && document.querySelector('#formation-select')`, 'propuestas pitch');
  await snap('03-propuestas-desktop.png');

  // 3. Guía para FM (Mini-HUD dialog open)
  await evaluate(`document.querySelector('#companion-button').click()`);
  await wait(`document.querySelector('#dialog').open && document.querySelector('.companion-shell')`, 'companion shell');
  await snap('04-guia-fm-mini-hud.png');
  await evaluate(`document.querySelector('#dialog-close').click()`);
  await sleep(200);

  // 4. Mi táctica (1360x920): audit current tactic to populate pitch and dynamic checklist
  const data = await (await fetch(url + '/api/data')).json();
  const proposal = await (await fetch(url + '/api/simulate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'X-FM-App': '1'},
    body: JSON.stringify({dataset_id: data.id, formation: '433'})
  })).json();

  await evaluate(`location.hash='current'`);
  await wait(`document.querySelector('#current-player-0')`, 'current editor');
  for (let i = 0; i < 11; i++) {
    const row = proposal.lineup[i];
    await set('#current-player-' + i, row.uid);
    for (const [phase, key] of [['ip', 'in_possession'], ['oop', 'out_of_possession']]) {
      await set(`#current-${phase}-position-${i}`, row[key].position);
      await set(`#current-${phase}-role-${i}`, row[key].id);
    }
  }
  await evaluate(`document.querySelector('#current-confirm').click(); document.querySelector('[data-action="audit-current"]').click()`);
  await wait(`document.querySelector('#current-result') && document.querySelectorAll('.pitch-player').length===11`, 'current result pitch');
  await snap('02-mi-tactica-desktop.png');

  // 5. Ventana angosta (760x920) en Mi táctica
  await send('Emulation.setDeviceMetricsOverride', {width: 760, height: 920, deviceScaleFactor: 1, mobile: false});
  await snap('05-mi-tactica-ventana-angosta-760px.png');

  // 6. Ventana angosta (760x920) en Propuestas
  await evaluate(`location.hash='tactics'`);
  await wait(`document.querySelectorAll('.pitch-player').length===11`, 'propuestas 760px');
  await snap('06-propuestas-ventana-angosta-760px.png');

  console.log('ALL SCREENSHOTS CAPTURED SUCCESSFULLY');
} finally {
  socket?.close();
  chrome.kill();
  try {
    await fetch(url + '/api/shutdown', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'X-FM-App': '1'},
      body: '{}'
    });
  } catch {}
  if (host.exitCode === null) host.kill();
  try { fs.rmSync(profile, {recursive: true, force: true}); } catch {}
  try { fs.rmSync(tempFolder, {recursive: true, force: true}); } catch {}
}
