"""Refresh factual FM26 reference data; never store/copy source prose."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
BASE='https://fmsidekick.com/api/'

def get(path):
    with urllib.request.urlopen(BASE+path,timeout=30) as response:
        return json.load(response)

def fetch(item):
    kind,entry=item
    path=kind+'/'+entry['id']
    raw=get(path)
    # Titles, attribute names, options and position facts only. Explanations are ours.
    fields=('role_name','position','phase','key_attributes','player_instructions') if kind=='roles' else ('instruction_property','phase','category','options')
    result={k:raw[k] for k in fields if k in raw}
    if kind!='roles':
        # Source shape may contain a list of rich option objects; retain names only.
        options=raw.get('options',[])
        result['options']=[o if isinstance(o,str) else o['option_name'] for o in options]
    result.update(id=entry['id'],label=entry['label'],source=BASE+path)
    return kind,result,raw

def main():
    entries=[]
    for kind in ('roles','player_instructions','team_instructions'):
        entries.extend((kind,e) for e in get(kind)['entries'])
    catalog={'edition':'FM26','checked_at':date(2026,10,24).isoformat(),'source':BASE,'roles':[],'player_instructions':[],'team_instructions':[]}
    with ThreadPoolExecutor(max_workers=5) as pool:
        for kind,record,raw in pool.map(fetch,entries):
            catalog[kind].append(record)
            if kind!='roles' and not record['options']:
                print(kind,record['id'],'keys',list(raw),flush=True)
    destination=ROOT/'fm_app'/'data'
    destination.mkdir(exist_ok=True)
    (destination/'fm26_catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    print({kind:len(catalog[kind]) for kind in ('roles','player_instructions','team_instructions')})
    print('Example PI:',catalog['player_instructions'][0])
    print('Example TI:',catalog['team_instructions'][0])

if __name__=='__main__':
    main()
