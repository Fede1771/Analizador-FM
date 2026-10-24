"""Loopback-only server, streaming save import and in-memory analysis cache."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import uuid
import webbrowser
from urllib.parse import unquote

from fm_app.analysis import ATTRS, ROLES, STYLES, analyze
from fm_app.recommendations import simulate_formation
from fm_app.tactics import FORMATION_CATALOG
from fm_app.fm26 import ENGINE_VERSION, CATALOG, LOCALE
from fm_app.watcher import SaveWatcher

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'web'
STORAGE = ROOT / 'data' / 'imports'
MAX_SAVE = 400 * 1024 * 1024


def load_dataset(folder):
    report=json.loads((folder/'validation.json').read_text(encoding='utf-8'))
    if report.get('sanity_errors') or report.get('missing_required_fields'):
        raise ValueError('La extracción no superó los controles de consistencia.')
    def clean(p):
        return {**{k:p.get(k) for k in ('uid','name','age','birth_date','height_cm','team_slot','natural_positions','accomplished_positions','positions','left_foot','right_foot','on_loan','loan_parent_club_name','club_name','loan_end','loan_start','loan_stats')},
                'attributes':{k:p['attributes'][k] for k in ATTRS}}
    # Compatibility with earlier, genuinely imported snapshots; new imports use generic names.
    squad_file=folder/('squad_full.json' if (folder/'squad_full.json').exists() else 'brighton_full.json')
    loans_file=folder/('loaned_out.json' if (folder/'loaned_out.json').exists() else 'brighton_loaned_out.json')
    players=[clean(p) for p in json.loads(squad_file.read_text(encoding='utf-8'))]
    loans=[clean(p) for p in json.loads(loans_file.read_text(encoding='utf-8'))]
    if not players:
        raise ValueError('La partida no contiene jugadores para el club detectado.')
    manager=next((m for m in report['managed_clubs'] if m['club_uid']==report['club']['uid']),{})
    metadata_path=folder.parent/'import.json'
    source=json.loads(metadata_path.read_text(encoding='utf-8')) if metadata_path.exists() else {'filename':'Partida importada anteriormente'}
    slots=sorted({p['team_slot'] for p in players if p['team_slot'] is not None})
    if not slots:
        raise ValueError('No se identificaron grupos de plantilla para analizar.')
    primary=slots[0]
    raw_labels=report.get('slot_labels') or {}
    slot_labels={}
    for s in slots:
        if str(s) in raw_labels:
            slot_labels[s]=raw_labels[str(s)]
        elif s==primary:
            slot_labels[s]='Primer equipo'
        else:
            slot_p=[p for p in players if p.get('team_slot')==s]
            ages=[p['age'] for p in slot_p if p.get('age') is not None]
            if ages:
                max_a=max(ages)
                slot_labels[s]='Sub-18' if max_a<=18 else 'Sub-21' if max_a<=21 else 'Sub-23' if max_a<=23 else f'Grupo {s}'
            else:
                slot_labels[s]=f'Grupo {s}'
    return {'id':report['save_sha256'][:16], 'club':report['club']['name'],
            'manager':manager.get('manager_name'), 'source':source,'default_primary_slot':slots[0],
            'date':report['game_date'],'build':report['build'], 'players':players,'loans':loans,
            'slots':slots, 'slot_labels':slot_labels,
            'warnings':report.get('reader_warnings',[]),'source_verified':False,
            'attributes':ATTRS,'styles':STYLES,
            'fm26_reference':{'edition':'FM26','checked_at':CATALOG['checked_at'],
                              'role_count':len(ROLES),'available_reference_roles':len(CATALOG['roles']),
                              'spanish_note':'Etiquetas extraídas de Español latinoamericano de FM26 26.3.2. Se conservan variantes por contexto; las vinculaciones con cada vista del menú no están todas comprobadas visualmente.',
                              'localization':{k:LOCALE[k] for k in ('locale','language','game_version','steam_build','source','sha256','verification')},
                              'sources':['https://fmsidekick.com/database/roles','https://fmsidekick.com/database/player_instructions','https://fmsidekick.com/database/team_instructions','https://fm.guidetofootball.com/fm26/roles/']},
            'formations_catalog': [{'id': f['id'], 'name': f['name'], 'category': f.get('category', 'Formación'), 'defensive': f['defensive'], 'idea': f['idea']} for f in FORMATION_CATALOG],
            'methodology':{'formula':'80% atributos de la función + 20% atributos del estilo, multiplicado por (0,25 + 0,75 × familiaridad/20). Ambos promedios se llevan a escala 0–100.',
                           'lineup':'Se maximiza la suma del encaje de los once, sin repetir jugadores. Cada puesto pondera 80% función con balón y 20% función defensiva. Se comparan tres estructuras.',
                           'academy':'Se compara el mejor encaje actual del juvenil contra la tercera opción disponible del primer equipo con familiaridad de al menos 15/20 en una posición de esa función. Si hay menos de tres opciones, se usa la última disponible. Sin opciones, no se recomienda promoción. Una diferencia de hasta −3 puntos permite sugerir una prueba. No predice potencial ni evolución.',
                           'roles':{key:{'name':v['name'],'english':v['english'],'positions':v['positions'],'phase':v['phase'],'weights':v['weights'],'source':v['source']} for key,v in ROLES.items()}}}


class AppState:
    def __init__(self, storage=STORAGE):
        self.lock=threading.RLock()
        self.executor=ThreadPoolExecutor(max_workers=1)
        self.jobs={}
        self.cache={}
        self.storage=Path(storage)
        self.dataset=None
        self.restore_error=None
        pointer=self.storage/'current.json'
        if pointer.exists():
            try:
                name=json.loads(pointer.read_text(encoding='utf-8'))['folder']
                if len(name)!=32 or not all(c in '0123456789abcdef' for c in name):
                    raise ValueError('Referencia de importación inválida.')
                folder=self.storage/name/'output'
                self.dataset=load_dataset(folder)
                bundle=folder/'analysis_bundle.json'
                if bundle.exists():
                    saved=json.loads(bundle.read_text(encoding='utf-8'))
                    # Validate identity before reusing a previous computation.
                    if saved.get('dataset_id')==self.dataset['id'] and saved.get('engine_version')==ENGINE_VERSION:
                        for style,result in saved['styles'].items():
                            self.cache[(self.dataset['id'],style,self.dataset['default_primary_slot'],())]=result
                if not self.cache:
                    styles={style:analyze(self.dataset,style,self.dataset['default_primary_slot']) for style in STYLES}
                    self.cache.update({(self.dataset['id'],style,self.dataset['default_primary_slot'],()):result for style,result in styles.items()})
                    (folder/'analysis_bundle.json').write_text(json.dumps({'engine_version':ENGINE_VERSION,'dataset_id':self.dataset['id'],'styles':styles},ensure_ascii=False),encoding='utf-8')
            except (ValueError,KeyError,OSError) as error:
                self.dataset=None
                self.restore_error=f'No se pudo restaurar la última partida: {error}. Podés cargarla nuevamente.'

    def progress(self, job_id, status, message, percent):
        with self.lock:
            self.jobs[job_id]={'status':status,'message':message,'progress':percent}

    def import_local_save(self, save_path):
        save_path = Path(save_path)
        if not save_path.exists():
            raise FileNotFoundError(f"La partida no existe: {save_path}")
        with self.lock:
            if any(j['status'] in ('uploading', 'reading', 'analyzing') for j in self.jobs.values()):
                return None
            job_id = uuid.uuid4().hex
            self.jobs[job_id] = {'status': 'reading', 'message': f'Leyendo partida {save_path.name}…', 'progress': 15}
        folder = self.storage / job_id
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / 'save.fm'
        shutil.copy2(save_path, target)
        (folder / 'import.json').write_text(json.dumps({
            'filename': save_path.name,
            'source_path': str(save_path),
            'imported_at': datetime.now(timezone.utc).isoformat(),
            'auto_synced': True
        }, ensure_ascii=False), encoding='utf-8')
        self.executor.submit(self.import_save, job_id, target, folder)
        return job_id

    def import_save(self, job_id, source, folder):
        self.progress(job_id,'reading','Detectando tu club y leyendo plantilla, inferiores y cedidos…',20)
        try:
            result=subprocess.run([sys.executable,'-m','fm_app.extraction',str(source),'--output',str(folder/'output')],
                                  cwd=ROOT,capture_output=True,encoding='utf-8',errors='replace',timeout=300)
            (folder/'extraction.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
            if result.returncode:
                raise ValueError('No se pudo extraer la plantilla. Verificá que sea una partida FM26 con un único club gestionado. Se conservó la partida anterior.')
            data=load_dataset(folder/'output')
            primary=data['default_primary_slot']
            styles={}
            for index,style in enumerate(STYLES):
                self.progress(job_id,'analyzing',f'Analizando primer equipo, inferiores y cedidos: {STYLES[style]["name"]} ({index+1}/{len(STYLES)})…',60+index*8)
                styles[style]=analyze(data,style,primary)
            bundle={'engine_version':ENGINE_VERSION,'dataset_id':data['id'],'styles':styles}
            (folder/'output'/'analysis_bundle.json').write_text(json.dumps(bundle,ensure_ascii=False),encoding='utf-8')
            with self.lock:
                temporary=self.storage/'current.tmp'
                temporary.write_text(json.dumps({'folder':job_id}),encoding='utf-8')
                os.replace(temporary,self.storage/'current.json')
                self.dataset=data
                self.restore_error=None
                self.cache.clear()
                self.cache.update({(data['id'],style,primary,()):result for style,result in styles.items()})
                self.jobs[job_id]={'status':'done','progress':100,'message':f"Análisis listo: {data['club']}, {len(data['players'])} jugadores y {len(data['loans'])} cedidos."}
        except Exception as error:
            with self.lock:
                self.jobs[job_id]={'status':'error','message':str(error)}


class Handler(BaseHTTPRequestHandler):
    server_version='FMAnalyst/1.0'

    def reply(self, status, payload):
        raw=json.dumps(payload,ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(raw)

    def trusted(self):
        # Only the same local app may mutate or upload. No permissive CORS.
        host=self.headers.get('Host','')
        allowed={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
        origin=self.headers.get('Origin')
        return host in allowed and (not origin or origin in {f'http://{h}' for h in allowed})

    def do_GET(self):
        if not self.trusted():
            return self.reply(403,{'error':'Origen no permitido.'})
        path=self.path.split('?')[0]
        if path=='/api/data':
            with self.server.state.lock:
                return self.reply(200,self.server.state.dataset)
        if path=='/api/status':
            with self.server.state.lock:
                job=next((dict(j,job_id=key) for key,j in self.server.state.jobs.items() if j['status'] in ('uploading','reading','analyzing')),None)
                data=self.server.state.dataset
                ready=[s for s in STYLES if data and (data['id'],s,data['default_primary_slot'],()) in self.server.state.cache]
                sync_info=self.server.watcher.get_status() if hasattr(self.server, 'watcher') and self.server.watcher else None
                return self.reply(200,{
                    'has_dataset':data is not None,
                    'dataset_id':data['id'] if data else None,
                    'club':data['club'] if data else None,
                    'game_date':data['date'] if data else None,
                    'ready_styles':ready,
                    'active_job':job,
                    'restore_error':self.server.state.restore_error,
                    'sync':sync_info
                })
        if path=='/api/sync/status':
            sync_info=self.server.watcher.get_status() if hasattr(self.server, 'watcher') and self.server.watcher else {}
            return self.reply(200, sync_info)
        if path=='/api/sync/saves':
            saves=self.server.watcher.list_saves() if hasattr(self.server, 'watcher') and self.server.watcher else []
            return self.reply(200, saves)
        if path.startswith('/api/jobs/'):
            with self.server.state.lock:
                job=self.server.state.jobs.get(path.rsplit('/',1)[1])
            return self.reply(200 if job else 404,job or {'error':'Importación no encontrada.'})
        resources={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/favicon.ico':'touchline.ico','/app_icon.ico':'touchline.ico','/touchline.ico':'touchline.ico'}
        if path not in resources:
            return self.reply(404,{'error':'No encontrado.'})
        file=STATIC/resources[path]
        if not file.exists():
            return self.reply(404,{'error':'Archivo no encontrado.'})
        raw=file.read_bytes()
        self.send_response(200)
        mime=mimetypes.guess_type(file)[0] or 'application/octet-stream'
        self.send_header('Content-Type',mime + ('; charset=utf-8' if 'text' in mime or 'json' in mime or 'javascript' in mime else ''))
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-cache')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        if not self.trusted() or self.headers.get('X-FM-App')!='1':
            return self.reply(403,{'error':'Origen no permitido.'})
        
        if self.path=='/api/sync/config':
            try:
                size=int(self.headers.get('Content-Length','0'))
                body=json.loads(self.rfile.read(size)) if size else {}
                if not hasattr(self.server, 'watcher') or not self.server.watcher:
                    return self.reply(503, {'error': 'Sincronizador no inicializado.'})
                updated=self.server.watcher.configure(
                    folder=body.get('watch_folder'),
                    target_save=body.get('target_save'),
                    enabled=body.get('enabled')
                )
                return self.reply(200, updated)
            except Exception as e:
                return self.reply(400, {'error': str(e)})

        if self.path=='/api/sync/trigger':
            try:
                size=int(self.headers.get('Content-Length','0'))
                body=json.loads(self.rfile.read(size)) if size else {}
                if not hasattr(self.server, 'watcher') or not self.server.watcher:
                    return self.reply(503, {'error': 'Sincronizador no inicializado.'})
                job_id=self.server.watcher.trigger_sync(filename=body.get('filename'))
                return self.reply(200, {'status': 'triggered', 'job_id': job_id})
            except Exception as e:
                return self.reply(400, {'error': str(e)})

        if self.path == '/api/simulate':
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if size > 16384 or size < 2:
                    raise ValueError('Solicitud inválida.')
                params = json.loads(self.rfile.read(size))
                with self.server.state.lock:
                    data = self.server.state.dataset
                if data is None:
                    return self.reply(409, {'error': 'Cargá una partida .fm para simular la formación.'})
                if params.get('dataset_id') != data['id']:
                    return self.reply(409, {'error': 'La partida cambió. Recargá la página.'})
                formation = params.get('formation', '352')
                style = params.get('style', 'possession')
                primary = int(params.get('primary_slot', data['default_primary_slot']))
                if primary not in data['slots']:
                    raise ValueError('Grupo principal inválido.')
                excluded = tuple(sorted({int(i) for i in params.get('excluded', [])}))
                prompt = (params.get('prompt') or '').strip()
                res = simulate_formation(data, formation_id=formation, style=style, primary_slot=primary, excluded=excluded, prompt=prompt if prompt else None)
                return self.reply(200, res)
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
                return self.reply(400, {'error': str(error)})

        if self.path!='/api/analyze':
            return self.reply(404,{'error':'No encontrado.'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size>16384 or size<2:
                raise ValueError('Solicitud inválida.')
            params=json.loads(self.rfile.read(size))
            with self.server.state.lock:
                data=self.server.state.dataset
            if data is None:
                return self.reply(409,{'error':'Cargá una partida .fm para generar el análisis.'})
            if params.get('dataset_id')!=data['id']:
                return self.reply(409,{'error':'La partida cambió. Recargá la página.'})
            style=params.get('style','possession')
            primary=int(params.get('primary_slot',data['default_primary_slot']))
            if primary not in data['slots']:
                raise ValueError('Grupo principal inválido.')
            excluded=tuple(sorted({int(i) for i in params.get('excluded',[])}))
            prompt=(params.get('prompt') or '').strip()
            key=(data['id'],style,primary,excluded,prompt)
            with self.server.state.lock:
                result=self.server.state.cache.get(key)
            if result is None:
                result=analyze(data,style,primary,excluded,prompt=prompt if prompt else None)
                with self.server.state.lock:
                    if len(self.server.state.cache)>64:
                        self.server.state.cache.clear()
                    self.server.state.cache[key]=result
            self.reply(200,result)
        except (ValueError,TypeError,KeyError,json.JSONDecodeError) as error:
            self.reply(400,{'error':str(error)})

    def do_PUT(self):
        if not self.trusted() or self.headers.get('X-FM-App')!='1':
            return self.reply(403,{'error':'Origen no permitido.'})
        if self.path!='/api/import':
            return self.reply(404,{'error':'No encontrado.'})
        try:
            length=int(self.headers.get('Content-Length','0'))
        except ValueError:
            return self.reply(400,{'error':'Tamaño inválido.'})
        if not 1000<=length<=MAX_SAVE:
            return self.reply(413,{'error':'Elegí una partida .fm de hasta 400 MB.'})
        with self.server.state.lock:
            if any(j['status'] in ('uploading','reading','analyzing') for j in self.server.state.jobs.values()):
                return self.reply(409,{'error':'Ya hay una importación en curso.'})
            job_id=uuid.uuid4().hex
            self.server.state.jobs[job_id]={'status':'uploading','message':'Recibiendo archivo…'}
        folder=self.server.state.storage/job_id
        folder.mkdir(parents=True)
        source=folder/'save.fm'
        try:
            filename=unquote(self.headers.get('X-FM-Filename','Partida.fm')).replace('\\','/').rsplit('/',1)[-1][:200]
            (folder/'import.json').write_text(json.dumps({'filename':filename,'imported_at':datetime.now(timezone.utc).isoformat()},ensure_ascii=False),encoding='utf-8')
            self.connection.settimeout(90)
            with source.open('wb') as stream:
                remaining=length
                while remaining:
                    chunk=self.rfile.read(min(1024*1024,remaining))
                    if not chunk:
                        raise ValueError('La carga se interrumpió.')
                    stream.write(chunk)
                    remaining-=len(chunk)
            with source.open('rb') as stream:
                if stream.read(6)!=b'\x02\x01fmf.':
                    raise ValueError('El archivo no tiene una cabecera de partida FM compatible.')
            self.server.state.executor.submit(self.server.state.import_save,job_id,source,folder)
            self.reply(202,{'job_id':job_id})
        except (ValueError,OSError) as error:
            with self.server.state.lock:
                self.server.state.jobs[job_id]={'status':'error','message':str(error)}
            self.reply(400,{'error':str(error)})


def create_app_server(port=8765, enable_watcher=True, storage=STORAGE):
    state=AppState(storage=storage)
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.state=state
    if enable_watcher:
        server.watcher=SaveWatcher(state)
        server.watcher.start()
    else:
        server.watcher=None
    return server


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--open',action='store_true',help='Open the app in the default browser')
    parser.add_argument('--no-sync',action='store_true',help='Disable save watcher')
    args=parser.parse_args()
    server=create_app_server(port=args.port, enable_watcher=not args.no_sync)
    print(f'Analizador FM: http://127.0.0.1:{args.port}',flush=True)
    if args.open:
        threading.Timer(.7,lambda:webbrowser.open(f'http://127.0.0.1:{args.port}/')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(server, 'watcher') and server.watcher:
            server.watcher.stop()
        server.server_close()
        server.state.executor.shutdown(wait=False)


if __name__=='__main__':
    main()
