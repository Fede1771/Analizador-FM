"""Publish a verified MSI as a new GitHub release; credentials stay in process memory."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import urllib.error
import urllib.parse
import urllib.request

REPOSITORY = 'Fede1771/Analizador-FM'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--notes', type=Path, required=True)
    parser.add_argument('--asset', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    if head != args.commit or subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip():
        raise SystemExit('El commit debe ser HEAD y el repositorio debe estar limpio.')
    if not args.asset.is_file() or args.asset.suffix.lower() != '.msi' or not args.notes.is_file():
        raise SystemExit('Faltan el MSI o las notas de versión.')
    remote = subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=root,text=True).split()[0]
    if remote != head:
        raise SystemExit('Subí primero el commit a origin/main.')
    token = os.environ.get('GH_TOKEN')
    if not token:
        credential = subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',
            capture_output=True,text=True,cwd=root,env={**os.environ,'GIT_TERMINAL_PROMPT':'0'},check=True)
        values = dict(line.split('=',1) for line in credential.stdout.splitlines() if '=' in line)
        token = values.get('password')
    if not token:
        raise SystemExit('No hay credencial de GitHub disponible.')
    def request(url, method='GET', body=None, content_type='application/json'):
        if urllib.parse.urlparse(url).hostname not in ('api.github.com','uploads.github.com'):
            raise ValueError('Destino inesperado en la API de GitHub.')
        raw = body if isinstance(body,bytes) else (json.dumps(body).encode() if body is not None else None)
        req=urllib.request.Request(url,data=raw,method=method,headers={
            'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json',
            'X-GitHub-Api-Version':'2022-11-28','Content-Type':content_type,'User-Agent':'Touchline-release'})
        try:
            with urllib.request.urlopen(req,timeout=180) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            try: message=json.load(exc).get('message','Error HTTP')
            finally:exc.close()
            raise RuntimeError(f'GitHub HTTP {exc.code}: {message}') from None
    base='https://api.github.com/repos/'+REPOSITORY
    releases=request(base+'/releases?per_page=100')
    release=next((r for r in releases if r['tag_name']==args.tag),None)
    if release and not release['draft']:
        raise SystemExit('La versión ya está publicada. Usá un número nuevo; no se reemplazan releases anteriores.')
    if release and release['target_commitish'] != head:
        raise SystemExit('Existe un borrador dirigido a otro commit; revisalo antes de publicar.')
    body=args.notes.read_text(encoding='utf-8')
    def absolute_document(match):
        target=match.group(1)
        if '://' in target or target.startswith('#'):
            return match.group(0)
        path, _, anchor=target.partition('#')
        relative=(args.notes.resolve().parent/path).resolve().relative_to(root).as_posix()
        return '](https://github.com/'+REPOSITORY+'/blob/'+head+'/'+urllib.parse.quote(relative,safe='/')+('#'+anchor if anchor else '')+')'
    body=re.sub(r'\]\(([^)]+)\)',absolute_document,body)
    raw=args.asset.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    checksum=(digest+'  '+args.asset.name+'\n').encode()
    if not release:
        release=request(base+'/releases','POST',{'tag_name':args.tag,'target_commitish':head,
            'name':'Touchline '+args.tag,'body':body,'draft':True,'prerelease':False})
    for name, content, kind in [(args.asset.name,raw,'application/x-msi'),('SHA256SUMS.txt',checksum,'text/plain')]:
        existing=next((a for a in release.get('assets',[]) if a['name']==name),None)
        expected='sha256:'+hashlib.sha256(content).hexdigest()
        if existing:
            if existing.get('digest') != expected or existing['size'] != len(content):
                raise SystemExit('El borrador contiene un archivo diferente. No se sobrescribe: '+name)
        else:
            asset=request(release['upload_url'].split('{')[0]+'?name='+urllib.parse.quote(name),'POST',content,kind)
            if asset['size'] != len(content) or (asset.get('digest') and asset['digest'] != expected):
                raise SystemExit('Falló la verificación de la subida: '+name)
    published=request(base+'/releases/'+str(release['id']),'PATCH',{'body':body,'draft':False,'make_latest':'true'})
    print(json.dumps({'url':published['html_url'],'tag':args.tag,'commit':head,'sha256':digest},ensure_ascii=False))


if __name__ == '__main__':
    main()
