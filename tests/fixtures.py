"""Synthetic clubs and saves: tests never need a personal FM installation or career."""
from copy import deepcopy
import json
from pathlib import Path
from fm_app.tactics import ATTRS
from fm_app.dataset import load_dataset


def player(uid, position, value=14, slot=0, age=24):
    return {'uid':uid, 'name':f'Jugador {uid}', 'team_slot':slot, 'age':age, 'club_name':'Club de prueba',
            'natural_positions':[position.upper()], 'accomplished_positions':[], 'left_foot':12,'right_foot':15,
            'attributes':{k:value for k in ATTRS},
            'positions':{p:20 if p==position else 1 for p in ('gk','dl','dc','dr','dm','ml','mc','mr','aml','amc','amr','stc','wbl','wbr')}}


def raw_players():
    positions=['gk','gk','dl','dr','dc','dc','dc','dm','dm','mc','mc','mc','aml','amr','amc','stc','stc','ml','mr','wbl','wbr','dc']
    players=[player(i+1,p,14+(i%3),age=22+i%8) for i,p in enumerate(positions)]
    players += [player(100+i,p,12,slot=1,age=17) for i,p in enumerate(('gk','dc','mc','stc'))]
    loans=[player(200,'wbl',15),player(201,'wbr',15),player(202,'mc',15)]
    for p in loans:
        p['club_name']='Club destino'
        p['loan_end']='2027-06-30'
        p['loan_stats']={'appearances':7,'starts':4,'substitutes':3,'minutes':390,'goals':1,'assists':2,'average_rating':7.1}
    return players,loans


def write_snapshot(output, digest='a'*64):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    players,loans=raw_players()
    report={'sanity_errors':[], 'missing_required_fields':{}, 'managed_clubs':[{'club_uid':11,'manager_name':'Manager de prueba','manager_staff_uid':1234}],
            'club':{'uid':11,'name':'Club de prueba'}, 'game_date':'2026-10-24','build':'FM26-test','save_sha256':digest,
            'slot_labels':{'0':'Primer equipo','1':'Sub-18'},'reader_warnings':[]}
    for name,value in [('validation.json',report),('squad_full.json',players),('loaned_out.json',loans)]:
        (output/name).write_text(json.dumps(value),encoding='utf-8')
    return load_dataset(output)


def dataset():
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as temp:
        return write_snapshot(Path(temp)/'output')


def fake_save(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b'\x02\x01fmf.' + b'\x00'*2000)
    return path
