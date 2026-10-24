"""Validation and canonical keys shared by HTTP, imports and persisted preferences."""
from fm_app.tactics import ATTRS, STYLES, FORMATIONS_BY_ID
from fm_app.fm26 import TI

ACTIVE_STATES = frozenset(('uploading', 'copying', 'reading', 'analyzing'))
MAX_SAVE = 400 * 1024 * 1024


def normalize_stats(raw):
    raw = raw or {}
    if not isinstance(raw, dict):
        raise ValueError('Estadísticas inválidas.')
    def number(key, fallback=None):
        value = raw.get(key, fallback)
        if value is None:
            return None
        if not isinstance(value, (float, int)) or isinstance(value, bool) or value < 0:
            raise ValueError(f'Estadística inválida: {key}.')
        return value
    starts = number('starts')
    subs = number('substitutes', raw.get('subs'))
    appearances = number('appearances', (starts or 0) + (subs or 0) if starts is not None or subs is not None else None)
    return {'available': raw.get('available', bool(raw)), 'starts': starts, 'substitutes': subs,
            'appearances': appearances, 'goals': number('goals'), 'assists': number('assists'),
            'minutes': number('minutes'), 'average_rating': number('average_rating', raw.get('rating')),
            'clean_sheets': number('clean_sheets'), 'club_name': raw.get('club_name'),
            'loan_end': raw.get('loan_end'), 'loan_start': raw.get('loan_start')}


def clean_player(player):
    if not isinstance(player, dict):
        raise ValueError('Registro de jugador inválido.')
    if not isinstance(player.get('uid'), int) or isinstance(player['uid'], bool):
        raise ValueError('Jugador sin identificador válido.')
    if not isinstance(player.get('name'), str) or not player['name'].strip():
        raise ValueError('Jugador sin nombre.')
    attributes = player.get('attributes') or {}
    for key in ATTRS:
        value = attributes.get(key)
        if type(value) is not int or not 1 <= value <= 20:
            raise ValueError(f'Atributo inválido: {key}.')
    positions = player.get('positions')
    if not isinstance(positions, dict) or not positions or any(type(v) is not int or not 1 <= v <= 20 for v in positions.values()):
        raise ValueError('Familiaridad posicional inválida.')
    fields = ('uid','name','age','birth_date','height_cm','team_slot','natural_positions','accomplished_positions',
              'positions','left_foot','right_foot','on_loan','loan_parent_club_name','club_name','loan_end','loan_start')
    result = {key: player.get(key) for key in fields}
    result.update(attributes={key: attributes[key] for key in ATTRS}, loan_stats=normalize_stats(player.get('loan_stats')))
    result['natural_positions'] = result['natural_positions'] or []
    result['accomplished_positions'] = result['accomplished_positions'] or []
    return result


def validate_overrides(value):
    if not isinstance(value, dict) or len(value) > len(TI):
        raise ValueError('Los ajustes tácticos deben ser un objeto.')
    for key, option in value.items():
        if key not in TI or not isinstance(option, str) or option not in TI[key]['options']:
            raise ValueError(f'Instrucción desconocida o valor inválido: {key}.')
    return value


def analysis_parameters(params, data, simulate=False):
    if not isinstance(params, dict):
        raise ValueError('La solicitud debe ser un objeto.')
    if params.get('dataset_id') != data['id']:
        raise ValueError('La partida cambió. Actualizá el análisis.')
    style = params.get('style', 'possession')
    if not isinstance(style, str) or style not in STYLES:
        raise ValueError('Estilo desconocido.')
    primary = params.get('primary_slot', data['default_primary_slot'])
    if type(primary) is not int or primary not in data['slots']:
        raise ValueError('Grupo principal inválido.')
    excluded = params.get('excluded', [])
    valid_ids = {p['uid'] for p in data['players']}
    if not isinstance(excluded, list) or len(excluded) > len(valid_ids) or any(type(i) is not int or i not in valid_ids for i in excluded):
        raise ValueError('La lista de jugadores excluidos es inválida.')
    prompt = params.get('prompt', '')
    if not isinstance(prompt, str) or len(prompt) > 2000:
        raise ValueError('El pedido táctico admite hasta 2000 caracteres.')
    overrides = validate_overrides(params.get('overrides', {}))
    formation = params.get('formation', '352')
    if simulate and (not isinstance(formation, str) or formation not in FORMATIONS_BY_ID):
        raise ValueError('Formación desconocida.')
    return {'style': style, 'primary_slot': primary, 'excluded': tuple(sorted(set(excluded))),
            'prompt': prompt.strip(), 'overrides': overrides, **({'formation_id': formation} if simulate else {})}


def cache_key(dataset_id, style, primary_slot, excluded=(), prompt='', overrides=None, formation_id=None):
    return (dataset_id, style, primary_slot, tuple(sorted(set(excluded))), (prompt or '').strip(),
            tuple(sorted((overrides or {}).items())), formation_id)


def validate_preferences(value, data):
    if not isinstance(value, dict):
        raise ValueError('Preferencias inválidas.')
    normalized = analysis_parameters({**value, 'dataset_id': data['id']}, data)
    labels = value.get('labels', {})
    if not isinstance(labels, dict) or any(str(k) not in {str(s) for s in data['slots']} or not isinstance(v, str) or len(v) > 40 for k, v in labels.items()):
        raise ValueError('Nombres de grupos inválidos.')
    formation = value.get('formation', 'auto')
    if formation != 'auto' and formation not in FORMATIONS_BY_ID:
        raise ValueError('Formación desconocida.')
    return {**normalized, 'excluded': list(normalized['excluded']), 'labels': labels, 'formation': formation}
