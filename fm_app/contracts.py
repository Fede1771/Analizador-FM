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
              'positions','left_foot','right_foot','on_loan','loan_parent_club_name','club_name','loan_end','loan_start',
              'transfer_value')
    result = {key: player.get(key) for key in fields}
    result.update(attributes={key: attributes[key] for key in ATTRS}, loan_stats=normalize_stats(player.get('loan_stats')))
    result['natural_positions'] = result['natural_positions'] or []
    result['accomplished_positions'] = result['accomplished_positions'] or []
    raw_contract = player.get('contract') or {}
    clauses = raw_contract.get('clauses') or []
    has_ext = any(c.get('kind') == 'optional_extension_by_club' for c in clauses if isinstance(c, dict))
    release_clause = next((c.get('value') for c in clauses if isinstance(c, dict) and 'release' in str(c.get('kind', '')).lower()), None)
    result['contract'] = {
        'wage': raw_contract.get('wage'),
        'start': raw_contract.get('start'),
        'end': raw_contract.get('end'),
        'squad_status': raw_contract.get('squad_status'),
        'has_extension_option': has_ext,
        'release_clause': release_clause,
        'clauses_summary': [c.get('kind') for c in clauses if isinstance(c, dict) and c.get('kind')]
    }
    return result


SUPPORT_RUNS_SIDES = {
    'Overlap - Balanced': frozenset(),
    'Overlap - Left': frozenset({'L'}),
    'Overlap - Right': frozenset({'R'}),
    'Overlap - Both Flanks': frozenset({'L', 'R'}),
    'Underlap - Balanced': frozenset(),
    'Underlap - Left': frozenset({'L'}),
    'Underlap - Right': frozenset({'R'}),
    'Underlap - Both Flanks': frozenset({'L', 'R'}),
}


def check_support_runs_compatibility(overlap, underlap):
    if not overlap or not underlap:
        return True, None
    o_sides = SUPPORT_RUNS_SIDES.get(overlap, frozenset())
    u_sides = SUPPORT_RUNS_SIDES.get(underlap, frozenset())
    conflict = o_sides & u_sides
    if not conflict:
        return True, None
    if conflict == frozenset({'L', 'R'}):
        return False, 'Incompatibilidad en Carreras de apoyo: al seleccionar ambas bandas en un eje, el otro debe ser Equilibrado.'
    if 'L' in conflict:
        return False, 'Incompatibilidad en Carreras de apoyo: no es posible doblar por banda y por dentro en la banda izquierda simultáneamente.'
    if 'R' in conflict:
        return False, 'Incompatibilidad en Carreras de apoyo: no es posible doblar por banda y por dentro en la banda derecha simultáneamente.'
    return False, 'Incompatibilidad en Carreras de apoyo observada en FM26.'


def validate_overrides(value):
    if not isinstance(value, dict) or len(value) > len(TI):
        raise ValueError('Los ajustes tácticos deben ser un objeto.')
    for key, option in value.items():
        if key not in TI or not isinstance(option, str) or option not in TI[key]['options']:
            raise ValueError(f'Instrucción desconocida o valor inválido: {key}.')
    # Support runs verified 16-combination matrix
    ok, err = check_support_runs_compatibility(value.get('overlap_ip'), value.get('underlap_ip'))
    if not ok:
        raise ValueError(err)
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


def get_transfer_window_status(game_date_str, loan_end_str=None):
    from datetime import datetime
    if not game_date_str:
        return {
            'is_open': False,
            'status': 'unknown',
            'badge': '❓ Ventana sin verificar',
            'status_text': 'Verificá el calendario de transferencias en FM.',
            'next_open': '1 de enero',
            'fm_guide': 'En FM: Perfil del jugador ➔ Menú "Contrato" ➔ "Repescar de cesión"',
            'return_countdown': None,
            'months_remaining': None
        }
    try:
        g_dt = datetime.fromisoformat(game_date_str)
        month, day, year = g_dt.month, g_dt.day, g_dt.year
        # Summer window in Europe / UK: July 1 to Sept 1
        # Winter window: Jan 1 to Feb 1
        is_summer = (month == 7) or (month == 8) or (month == 9 and day <= 1)
        is_winter = (month == 1) or (month == 2 and day <= 1)

        if is_summer:
            is_open = True
            status = 'open'
            badge = '🟢 Ventana de fichajes ABIERTA (Verano)'
            next_open = f"Cierra el 1 de septiembre de {year}"
            status_text = "Período de fichajes activo en FM. Podés solicitar la repesca inmediata hoy si la cesión incluyó cláusula."
        elif is_winter:
            is_open = True
            status = 'open'
            badge = '🟢 Ventana de fichajes ABIERTA (Invierno)'
            next_open = f"Cierra el 1 de febrero de {year}"
            status_text = "Período de fichajes de invierno activo en FM. Podés solicitar la repesca inmediata hoy si la cesión incluyó cláusula."
        elif (month == 9 and day > 1) or month in (10, 11, 12):
            is_open = False
            status = 'closed'
            badge = f'🔒 Ventana CERRADA (Abre 1 ene {year + 1})'
            next_open = f"1 de enero de {year + 1} (Ventana de invierno)"
            status_text = f"Ventana cerrada en Inglaterra. En FM las repescas requieren ventana activa: programá el regreso para el 1 de enero de {year + 1}."
        else:
            is_open = False
            status = 'closed'
            badge = f'🔒 Ventana CERRADA (Abre 1 jul {year})'
            next_open = f"1 de julio de {year} (Ventana de verano)"
            status_text = f"Ventana cerrada en Inglaterra. En FM las repescas requieren ventana activa: programá el regreso para el 1 de julio de {year}."

        return_countdown = None
        months_remaining = None
        if loan_end_str:
            e_dt = datetime.fromisoformat(loan_end_str)
            days = (e_dt - g_dt).days
            months_remaining = max(0, round(days / 30.4))
            formatted_end = f"{e_dt.day}/{e_dt.month}/{e_dt.year}"
            if months_remaining <= 1:
                return_countdown = f"⚠️ Préstamo a punto de vencer: regresa este mes a tu club sin costo ({formatted_end})."
            elif months_remaining <= 3:
                return_countdown = f"⚠️ Préstamo por vencer: regresa en {months_remaining} meses ({formatted_end})."
            else:
                return_countdown = f"Regresa automáticamente en {months_remaining} meses ({formatted_end})."

        return {
            'is_open': is_open,
            'status': status,
            'badge': badge,
            'status_text': status_text,
            'next_open': next_open,
            'fm_guide': 'En FM: Perfil del jugador ➔ Menú "Contrato" ➔ "Repescar de cesión" (si el botón está inactivo, el club no aceptó repesca en el acuerdo inicial).',
            'return_countdown': return_countdown,
            'months_remaining': months_remaining
        }
    except Exception:
        return {
            'is_open': False,
            'status': 'unknown',
            'badge': '❓ Ventana sin verificar',
            'status_text': 'Verificá el calendario de transferencias en FM.',
            'next_open': '1 de enero',
            'fm_guide': 'En FM: Perfil del jugador ➔ Menú "Contrato" ➔ "Repescar de cesión"',
            'return_countdown': None,
            'months_remaining': None
        }
