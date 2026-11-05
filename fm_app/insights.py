"""Dated player observations and transparent squad analytics; no match-engine weights."""
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path

from fm_app.storage import atomic_json, read_json, valid_import_id
from fm_app.tactics import ATTRS, STYLES
from fm_app.fm26 import ROLES
from fm_app.recommendations import role_score

AXES = {
    'Velocidad': ('pace', 'acceleration'),
    'Físico': ('strength', 'stamina', 'balance', 'agility'),
    'Defensa': ('tackling', 'marking', 'positioning', 'anticipation'),
    'Creación': ('passing', 'vision', 'decisions'),
    'Técnica': ('technique', 'first_touch', 'dribbling'),
    'Gol': ('finishing', 'off_the_ball', 'composure'),
}


def context(data, params):
    if params.get('dataset_id') != data['id']:
        raise ValueError('La partida cambió. Volvé a abrir el análisis del plantel.')
    group = params.get('primary_slot', data['default_primary_slot'])
    style = params.get('style', 'possession')
    if type(group) is not int or group not in data['slots'] or style not in STYLES:
        raise ValueError('Grupo o estilo inválido.')
    return group, style


def comparison_context(params):
    role = params.get('role_id', 'central_midfielder_ip')
    position = params.get('position', 'MC')
    style = params.get('style', 'possession')
    if role not in ROLES or position not in ROLES[role]['positions'] or style not in STYLES:
        raise ValueError('Elegí un rol, puesto y estilo compatibles.')
    return role, position, style


def compare_players(data, params):
    context(data, params)
    role, position, style = comparison_context(params)
    pool = {p['uid']: p for p in data['players'] + data['loans']}
    ids = [params.get('left_uid'), params.get('right_uid')]
    if any(type(uid) is not int or uid not in pool for uid in ids) or ids[0] == ids[1]:
        raise ValueError('Elegí dos jugadores distintos de esta partida.')
    left, right = [pool[uid] for uid in ids]
    def card(p):
        return {k: p.get(k) for k in ('uid', 'name', 'age', 'club_name')} | {
            'score': role_score(p, role, style, position) if position.lower() in p['positions'] else None,
            'familiarity': p['positions'].get(position.lower()),
            'wage': (p.get('contract') or {}).get('wage'),
            'transfer_value': p.get('transfer_value')}
    return {'left': card(left), 'right': card(right), 'role': ROLES[role]['name'],
            'attributes': [{'id': k, 'name': label, 'left': left['attributes'][k],
                            'right': right['attributes'][k], 'delta': left['attributes'][k]-right['attributes'][k],
                            'priority': k in ROLES[role]['weights']} for k, label in ATTRS.items()]}


class HistoryStore:
    def __init__(self, root):
        self.root = Path(root) / 'history'

    def folder(self, career):
        return self.root / hashlib.sha256(career.encode('utf-8')).hexdigest()

    def record(self, data):
        date.fromisoformat(data['date'])
        fields = ('uid', 'name', 'age', 'team_slot', 'attributes', 'positions', 'contract',
                  'transfer_value', 'season_stats', 'season_stats_scope', 'season_stats_period')
        players = [{k: p.get(k) for k in fields} for p in data['players'] + data['loans']]
        value = {'schema': 1, 'date': data['date'], 'dataset_id': data['id'],
                 'career_id': data['career_id'], 'club': data['club'],
                 'source_kind': data.get('source', {}).get('kind', 'fm'), 'players': players}
        digest = hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        target = self.folder(data['career_id']) / (digest + '.json')
        if not target.exists():
            value['id'] = digest
            value['recorded_at'] = datetime.now(timezone.utc).isoformat()
            atomic_json(target, value)
        return digest

    def observations(self, data):
        rows = []
        for path in self.folder(data['career_id']).glob('*.json'):
            row = read_json(path)
            if isinstance(row, dict) and row.get('schema') == 1 and row.get('career_id') == data['career_id']:
                rows.append(row)
        return sorted(rows, key=lambda r: (r['date'], r['recorded_at'], r['id']))

    def backfill(self, store):
        """Read only retained extractions; never depend on source saves or alter them."""
        for folder in store.root.iterdir() if store.root.exists() else ():
            if not valid_import_id(folder.name) or folder.is_symlink() or not folder.is_dir():
                continue
            report = read_json(folder/'output/validation.json', {})
            if not isinstance(report, dict) or report.get('sanity_errors') or report.get('missing_required_fields'):
                continue
            try:
                club = report['club']
                manager = next(m for m in report['managed_clubs'] if m['club_uid'] == club['uid'])
                identity = f"{club['uid']}:{manager.get('manager_staff_uid', manager.get('manager_name', ''))}"
                career = report.get('external_career_id') or hashlib.sha256(identity.encode()).hexdigest()[:24]
                from fm_app.contracts import clean_player
                output = folder/'output'
                source = output/('squad_full.json' if (output/'squad_full.json').exists() else 'brighton_full.json')
                loans = output/('loaned_out.json' if (output/'loaned_out.json').exists() else 'brighton_loaned_out.json')
                self.record({'career_id': career, 'club': club['name'], 'date': report['game_date'],
                             'id': report['save_sha256'][:16], 'source': read_json(folder/'import.json', {}),
                             'players': [clean_player(p) for p in read_json(source, [])],
                             'loans': [clean_player(p) for p in read_json(loans, [])]})
            except (ValueError, KeyError, TypeError, StopIteration):
                continue

    def evolution(self, data, params):
        context(data, params)
        role, position, style = comparison_context(params)
        uid = params.get('uid')
        if type(uid) is not int or uid not in {p['uid'] for p in data['players'] + data['loans']}:
            raise ValueError('Jugador desconocido.')
        current_id = self.record(data)
        points = []
        for observation in self.observations(data):
            if observation['date'] > data['date']:
                continue
            p = next((p for p in observation['players'] if p['uid'] == uid), None)
            if p:
                points.append({'id': observation['id'], 'date': observation['date'], 'recorded_at': observation['recorded_at'],
                               'score': role_score(p, role, style, position) if position.lower() in p['positions'] else None, 'attributes': p['attributes'],
                               'source_kind': observation['source_kind']})
        current = next(p for p in points if p['id'] == current_id)
        baseline_id = params.get('baseline_id')
        baseline = next((p for p in points if p['id'] == baseline_id), None) if baseline_id else (points[0] if points else current)
        if baseline is None:
            raise ValueError('La observación elegida no pertenece a este jugador y carrera.')
        return {'points': points, 'current_id': current_id, 'baseline_id': baseline['id'],
                'score_delta': round(current['score']-baseline['score'], 1) if current['score'] is not None and baseline['score'] is not None else None,
                'attributes': [{'id': k, 'name': name, 'before': baseline['attributes'][k],
                                'now': current['attributes'][k], 'delta': current['attributes'][k]-baseline['attributes'][k]}
                               for k, name in ATTRS.items()]}


def squad_insights(data, params):
    group, style = context(data, params)
    excluded = params.get('excluded', [])
    if not isinstance(excluded, list) or any(type(x) is not int for x in excluded):
        raise ValueError('Exclusiones inválidas.')
    players = [p for p in data['players'] if p['team_slot'] == group and p['uid'] not in excluded]
    # A common, explicit average prevents the top group depending on a different role per player.
    field = [p for p in players if 'GK' not in p.get('natural_positions', [])]
    ranked = sorted(field, key=lambda p: (-sum(sum(p['attributes'][k] for k in keys)/len(keys) for keys in AXES.values()), p['uid']))
    def profile(pool):
        return {axis: round(sum(sum(p['attributes'][k] for k in keys)/len(keys) for p in pool)/len(pool), 2) if pool else None for axis, keys in AXES.items()}
    groups = [{'label': name, 'count': len(pool), 'axes': profile(pool)} for name, pool in
              [('Núcleo (hasta 16)', ranked[:16]), ('Rotación (resto)', ranked[16:]), ('Campo completo', ranked)]]
    coverage = []
    for position in ('GK','DL','DC','DR','DM','MC','ML','MR','AML','AMC','AMR','STC','WBL','WBR'):
        options = sorted((p for p in players if p['positions'].get(position.lower(), 1) >= 15),
                         key=lambda p: (-max(role_score(p, rid, style, position) for rid, r in ROLES.items() if r['phase']=='in_possession' and position in r['positions']), p['uid']))
        coverage.append({'position': position, 'count': len(options), 'players': [{'uid': p['uid'], 'name': p['name']} for p in options[:3]]})
    return {'groups': groups, 'axes': AXES, 'coverage': coverage, 'player_count': len(players),
            'excluded_count': len([p for p in data['players'] if p['team_slot']==group and p['uid'] in excluded]),
            'performance': performance(players)}


def performance(players):
    rows = []
    for p in players:
        s = p.get('season_stats') or {}
        if s.get('available'):
            rows.append({'uid': p['uid'], 'name': p['name'], 'age': p.get('age'), **s,
                         'scope': p.get('season_stats_scope'), 'period': p.get('season_stats_period')})
    full = len(rows) == len(players) and bool(players)
    # Do not mix league with all competitions or distinct exported periods.
    scopes = {(r.get('scope'), r.get('period')) for r in rows}
    comparable = full and len(scopes)==1 and all(scope and period for scope, period in scopes) and all(all(r.get(k) is not None for k in ('minutes','goals','assists')) for r in rows)
    ordered = sorted(rows, key=lambda p: (-(p.get('minutes') or 0), p['uid']))
    minutes = sum(r.get('minutes') or 0 for r in rows)
    contributions = sorted(rows, key=lambda r: -((r.get('goals') or 0)+(r.get('assists') or 0)))
    total = sum((r.get('goals') or 0)+(r.get('assists') or 0) for r in rows)
    goals = sum(r.get('goals') or 0 for r in rows)
    def share(value, denominator):
        return round(value/denominator*100, 1) if comparable and denominator else None
    age_groups = []
    for label, lower, upper in [('<21',0,20),('21–26',21,26),('27–31',27,31),('32+',32,150)]:
        m = sum((p.get('minutes') or 0) for p in rows if p.get('age') is not None and lower<=p['age']<=upper)
        age_groups.append({'label': label, 'share': share(m, minutes) if all(p.get('age') is not None for p in rows) else None})
    return {'available': len(rows), 'expected': len(players), 'comparable': comparable,
            'top11_minutes': share(sum(p.get('minutes') or 0 for p in ordered[:11]), minutes),
            'top3_contributions': share(sum((p.get('goals') or 0)+(p.get('assists') or 0) for p in contributions[:3]), total),
            'top5_contributions': share(sum((p.get('goals') or 0)+(p.get('assists') or 0) for p in contributions[:5]), total),
            'scorer_share': share(max((p.get('goals') or 0 for p in rows), default=0), goals),
            'age_groups': age_groups, 'rows': ordered,
            'note': 'Porcentajes sobre los jugadores del grupo, no sobre todos los goles del club. Goles + asistencias cuenta dos aportes si ambos se registran en una jugada. No identifica causas ni prueba la eficacia de una táctica.'}
