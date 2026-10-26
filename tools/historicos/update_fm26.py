"""Update fm_app/fm26.py with comprehensive 79 roles pools, observed locks, and sub-position support."""

import re
from pathlib import Path

fm26_path = Path(__file__).resolve().parents[2] / 'fm_app' / 'fm26.py'
text = fm26_path.read_text(encoding='utf-8')

# 1. Update IP_POOLS and OOP_POOLS
new_pools = """IP_POOLS = {
    'GK': ['goalkeeper', 'ball_playing_goalkeeper', 'no_nonsense_goalkeeper'],
    'DC': ['centre_back', 'advanced_centre_back', 'ball_playing_centre_back', 'no_nonsense_center_back', 'wide_centre_back', 'overlapping_centre_back'],
    'DL': ['full_back', 'wing_back', 'inside_wing_back', 'inside_full_back', 'playmaking_wing_back'],
    'DR': ['full_back', 'wing_back', 'inside_wing_back', 'inside_full_back', 'playmaking_wing_back'],
    'WBL': ['wing_back', 'inside_wing_back', 'playmaking_wing_back', 'advanced_wing_back'],
    'WBR': ['wing_back', 'inside_wing_back', 'playmaking_wing_back', 'advanced_wing_back'],
    'DM': ['defensive_midfielder', 'deep_lying_playmaker', 'half_back', 'box_to_box_midfielder', 'box_to_box_playmaker'],
    'MC': ['central_midfielder', 'wide_central_midfielder', 'midfield_playmaker', 'attacking_midfielder', 'advanced_playmaker', 'channel_midfielder'],
    'AMC': ['attacking_midfielder', 'advanced_playmaker', 'channel_midfielder', 'free_role', 'second_striker'],
    'AML': ['winger', 'inside_winger', 'playmaking_winger', 'inside_forward', 'wide_forward'],
    'AMR': ['winger', 'inside_winger', 'playmaking_winger', 'inside_forward', 'wide_forward'],
    'ML': ['wide_midfielder', 'winger', 'inside_winger', 'playmaking_winger'],
    'MR': ['wide_midfielder', 'winger', 'inside_winger', 'playmaking_winger'],
    'STC': ['deep_lying_forward', 'centre_forward', 'target_forward', 'poacher', 'channel_forward', 'false_nine'],
}

OOP_POOLS = {
    'GK': ['goalkeeper', 'sweeper_keeper', 'line_holding_keeper'],
    'DC': ['centre_back', 'stopping_centre_back', 'covering_centre_back', 'wide_centre_back', 'covering_wide_centre_back', 'stopping_wide_centre_back'],
    'DL': ['full_back', 'holding_full_back', 'pressing_full_back'],
    'DR': ['full_back', 'holding_full_back', 'pressing_full_back'],
    'WBL': ['wing_back', 'holding_wing_back', 'pressing_wing_back'],
    'WBR': ['wing_back', 'holding_wing_back', 'pressing_wing_back'],
    'DM': ['defensive_midfielder', 'dropping_defensive_midfielder', 'pressing_defensive_midfielder', 'screening_defensive_midfielder', 'wide_covering_defensive_midfielder'],
    'MC': ['central_midfielder', 'pressing_central_midfielder', 'screening_central_midfielder', 'wide_covering_central_midfielder'],
    'AMC': ['attacking_midfielder', 'tracking_attacking_midfielder', 'central_outlet_attacking_midfielder', 'splitting_outlet_attacking_midfielder'],
    'AML': ['winger', 'tracking_winger', 'inside_outlet_winger', 'wide_outlet_winger'],
    'AMR': ['winger', 'tracking_winger', 'inside_outlet_winger', 'wide_outlet_winger'],
    'ML': ['wide_midfielder', 'tracking_wide_midfielder', 'wide_outlet_wide_midfielder'],
    'MR': ['wide_midfielder', 'tracking_wide_midfielder', 'wide_outlet_wide_midfielder'],
    'STC': ['centre_forward', 'tracking_centre_forward', 'central_outlet_centre_forward', 'splitting_outlet_centre_forward'],
}"""

pattern_pools = r'IP_POOLS\s*=\s*\{.*?\n\}\n+OOP_POOLS\s*=\s*\{.*?\n\}'
text = re.sub(pattern_pools, new_pools, text, flags=re.DOTALL)

# 2. Update record function to include subpositions, behaviors and rich data
new_record = """def record(role_id):
    raw = REFERENCES[role_id]
    stem = role_id.rsplit('_', 1)[0]
    pos = raw['position'] if isinstance(raw['position'], list) else [raw['position']]
    positions = [p for value in pos for p in (POSITION_MAP[value] if value in POSITION_MAP else [value])]
    attrs = [ATTRIBUTE_MAP.get(a, a.lower().replace(' ', '_')) for a in raw['key_attributes']]
    local = LOCALE['roles'].get(role_id) or LOCALE['roles'][stem]
    verified = local.get('runtime_verified', False) or local.get('menu_verified_es', False)
    status = ('Español latinoamericano · verificado en menú de FM26 ' + LOCALE['game_version']) if verified else ('Español latinoamericano · archivo de FM26 ' + LOCALE['game_version'])
    src = local.get('verified_source', LOCALE['source'])
    behaviors = raw.get('behaviors') or local.get('behaviors') or []
    subposition_rule = raw.get('subposition_rule')
    locked_runtime = raw.get('locked_instructions_runtime')
    abbreviation = ROLE_ABBREV.get(role_id, raw.get('abbreviation', 'ROL'))
    return {
        **raw,
        'name': local['text'],
        'positions': positions,
        'weights': {a: 1 for a in attrs},
        'english': raw['role_name'],
        'spanish_status': status,
        'spanish_source': src,
        'menu_verified_es': verified,
        'behaviors': behaviors,
        'subposition_rule': subposition_rule,
        'locked_instructions_runtime': locked_runtime,
        'abbreviation': abbreviation,
        'localization': {**local, 'locale': LOCALE['locale'], 'steam_build': LOCALE['steam_build']}
    }"""

pattern_record = r'def record\(role_id\):.*?\n\n\n\n\nROLE_IDS'
text = re.sub(pattern_record, new_record + "\n\n\n\n\nROLE_IDS", text, flags=re.DOTALL)

# 3. Update SCREENSHOT_LOCKS and player_instructions
new_locks_and_pi = """# Runtime locks and contexts dynamically loaded from empirical survey matrix
SCREENSHOT_LOCKS = {item['role']: dict(item['locked_values']) for item in CATALOG.get('observed_instruction_contexts', [])}
EDITABLE_GROUPS = {item['role']: list(item['editable_groups']) for item in CATALOG.get('observed_instruction_contexts', [])}
OBSERVED_CONTEXTS = {item['role']: item for item in CATALOG.get('observed_instruction_contexts', [])}


def player_instructions(player, role):
    a = player['attributes']
    phase = role['phase']
    stem = role['id'].rsplit('_', 1)[0]
    builtin = role.get('player_instructions', [])
    result = []

    def add(key, value, why, base=False):
        result.append(instruction('player', key, value, why, 'role' if base else 'standard' if value in ('Standard', 'Follow Tactical Position', 'No') else 'adjustment'))

    if phase == 'in_possession':
        more = 'Take More Risks' in builtin
        fewer = 'Take Fewer Risks' in builtin
        value = 'Take More Risks' if more else 'Take Fewer Risks' if fewer or min(a['passing'], a['decisions']) < 11 else 'Standard'
        add('passing_risk_ip', value, f'Pases {a["passing"]}, visión {a["vision"]} y decisiones {a["decisions"]}. ' + ('El rol ya pide ese nivel de riesgo; no agregar la orden contraria.' if more or fewer else 'Se limita el riesgo si pases o decisiones están por debajo de 11; en el resto se mantiene el comportamiento del rol.'), more or fewer)
        if 'GK' not in role['positions']:
            dribble = 'Dribble More' if ('Dribble More Often' in builtin or (stem in ('winger', 'inside_winger', 'inside_forward', 'wide_forward') and min(a['dribbling'], a['acceleration']) >= 13)) else 'Dribble Less' if a['dribbling'] < 11 or any('dribble less' in s.lower() for s in builtin) else 'Standard'
            add('dribbling_frequency_ip', dribble, f'Regate {a["dribbling"]} y aceleración {a["acceleration"]}: ' + ('aprovechar el uno contra uno.' if dribble == 'Dribble More' else 'reducir pérdidas en la conducción.' if dribble == 'Dribble Less' else 'conservar la elección de conducción del rol.'), 'Dribble More Often' in builtin or any('dribble less' in s.lower() for s in builtin))
    else:
        press = 'More Often' if (stem.startswith('pressing_') or stem in ('sweeper_keeper',) or min(a['work_rate'], a['stamina']) >= 14) else 'Less Often' if max(a['work_rate'], a['stamina']) < 10 else 'Standard'
        add('pressing_oop', press, f'Sacrificio {a["work_rate"]}, resistencia {a["stamina"]} y anticipación {a["anticipation"]}: ' + ('el rol sale a presionar; necesita cobertura detrás.' if press == 'More Often' else 'proteger la posición antes de perseguir al portador.' if press == 'Less Often' else 'coordinar la presión con el bloque.'), press != 'Standard')
        ease = a['tackling'] < 11 or a['aggression'] >= 16
        add('tackling_oop', 'Ease Off Tackles' if ease else 'Standard', f'Entradas {a["tackling"]} y agresividad {a["aggression"]}: ' + ('evitar entradas precipitadas; no elimina el riesgo de faltas.' if ease else 'mantener la dureza normal; no sumar agresividad sin necesidad.'))

    known = {i['id']: i for i in result}
    for key in PLAYER_MENU[phase]:
        if key not in known:
            value = 'Follow Tactical Position' if key == 'freedom_of_movement_ip' else 'No' if key == 'hold_up_ball_ip' else 'Standard'
            item = instruction('player', key, value, 'Mantener el valor normal salvo que el plan colectivo requiera un cambio.', 'standard')
            result.append(item)

    has_context = role['id'] in SCREENSHOT_LOCKS
    locks = SCREENSHOT_LOCKS.get(role['id'], {})
    editable_list = EDITABLE_GROUPS.get(role['id'], [])
    ctx = OBSERVED_CONTEXTS.get(role['id'], {})

    for i in result:
        key = i['id']
        if has_context:
            if key in locks:
                i['locked'] = True
                i['editable'] = False
                locked_val = locks[key]
                i['locked_value'] = locked_val
                i['availability_source'] = f"Capturas del menú FM26 ({ctx.get('evidence', '')})"
                if locked_val is not None:
                    i.update(instruction('player', key, locked_val, 'Valor bloqueado por el rol en las capturas: cambiar el rol para modificarlo.', 'role'))
                else:
                    i['value_en'] = None
                    i['value'] = 'Desconocido (tapado por ayuda emergente en FM26)'
                    i['origin'] = 'role'
                    i['reason'] = 'Valor bloqueado en el juego pero tapado en las capturas por ayuda emergente.'
            elif key in editable_list:
                i['locked'] = False
                i['editable'] = True
                i['locked_value'] = None
                i['availability_source'] = f"Control editable comprobado en capturas FM26 ({ctx.get('evidence', '')})"
            else:
                i['locked'] = False
                i['editable'] = True
                i['locked_value'] = None
                i['availability_source'] = f"Control observado en FM26 ({ctx.get('evidence', '')})"
        else:
            i['locked'] = None
            i['editable'] = None
            i['locked_value'] = None
            i['availability_source'] = 'Disponibilidad no comprobada en las capturas de este rol'

    result.sort(key=lambda item: PLAYER_MENU[phase].index(item['id']))
    return result"""

pattern_pi_block = r'def player_instructions\(player,role\):.*?\nSCREENSHOT_LOCKS\s*=\s*\{.*?\n\}'
text = re.sub(pattern_pi_block, new_locks_and_pi, text, flags=re.DOTALL)

# 4. Update ROLE_ABBREV dictionary to include all 79 roles
ROLE_ABBREV_DICT = """ROLE_ABBREV = {
    'goalkeeper_ip': 'POR',
    'ball_playing_goalkeeper_ip': 'PCS',
    'no_nonsense_goalkeeper_ip': 'POR',
    'goalkeeper_oop': 'POR',
    'sweeper_keeper_oop': 'POL',
    'line_holding_keeper_oop': 'PEP',
    'centre_back_ip': 'DFC',
    'advanced_centre_back_ip': 'CAV',
    'ball_playing_centre_back_ip': 'CCS',
    'no_nonsense_center_back_ip': 'DFC',
    'wide_centre_back_ip': 'CRA',
    'overlapping_centre_back_ip': 'CQD',
    'centre_back_oop': 'DFC',
    'stopping_centre_back_oop': 'ZAG',
    'covering_centre_back_oop': 'DFC',
    'wide_centre_back_oop': 'CRA',
    'covering_wide_centre_back_oop': 'CCA',
    'stopping_wide_centre_back_oop': 'ZGA',
    'full_back_ip': 'LAT',
    'wing_back_ip': 'CR',
    'inside_wing_back_ip': 'CRI',
    'inside_full_back_ip': 'LAI',
    'playmaking_wing_back_ip': 'CRO',
    'advanced_wing_back_ip': 'CAV',
    'full_back_oop': 'LAT',
    'holding_full_back_oop': 'LAT',
    'pressing_full_back_oop': 'LAT',
    'wing_back_oop': 'CR',
    'holding_wing_back_oop': 'CR',
    'pressing_wing_back_oop': 'CR',
    'defensive_midfielder_ip': 'MD',
    'deep_lying_playmaker_ip': 'ORD',
    'half_back_ip': 'MCI',
    'box_to_box_midfielder_ip': 'TT',
    'box_to_box_playmaker_ip': 'OT',
    'defensive_midfielder_oop': 'MD',
    'dropping_defensive_midfielder_oop': 'MDR',
    'pressing_defensive_midfielder_oop': 'MDP',
    'screening_defensive_midfielder_oop': 'MD',
    'wide_covering_defensive_midfielder_oop': 'MDC',
    'central_midfielder_ip': 'MC',
    'wide_central_midfielder_ip': 'MCA',
    'midfield_playmaker_ip': 'MOR',
    'attacking_midfielder_ip': 'MP',
    'advanced_playmaker_ip': 'OAD',
    'channel_midfielder_ip': 'MC',
    'central_midfielder_oop': 'MC',
    'pressing_central_midfielder_oop': 'MC',
    'screening_central_midfielder_oop': 'MC',
    'wide_covering_central_midfielder_oop': 'MC',
    'wide_midfielder_ip': 'MI',
    'winger_ip': 'EXT',
    'inside_winger_ip': 'EXI',
    'playmaking_winger_ip': 'EXI',
    'wide_midfielder_oop': 'MA',
    'tracking_wide_midfielder_oop': 'MI',
    'wide_outlet_wide_midfielder_oop': 'MIE',
    'free_role_ip': 'MP',
    'second_striker_ip': 'SD',
    'attacking_midfielder_oop': 'MP',
    'tracking_attacking_midfielder_oop': 'MP',
    'central_outlet_attacking_midfielder_oop': 'MPE',
    'splitting_outlet_attacking_midfielder_oop': 'MPR',
    'inside_forward_ip': 'DLI',
    'wide_forward_ip': 'MA',
    'winger_oop': 'EXT',
    'tracking_winger_oop': 'EXT',
    'inside_outlet_winger_oop': 'EXS',
    'wide_outlet_winger_oop': 'EXE',
    'deep_lying_forward_ip': 'DLA',
    'centre_forward_ip': 'DLC',
    'target_forward_ip': 'DT',
    'poacher_ip': 'ARI',
    'channel_forward_ip': 'DDA',
    'false_nine_ip': 'FN',
    'centre_forward_oop': 'DLC',
    'tracking_centre_forward_oop': 'DLC',
    'central_outlet_centre_forward_oop': 'DLC',
    'splitting_outlet_centre_forward_oop': 'DLR'
}"""

pattern_role_abbrev = r'ROLE_ABBREV\s*=\s*\{.*?\n\}'
text = re.sub(pattern_role_abbrev, ROLE_ABBREV_DICT, text, flags=re.DOTALL)

fm26_path.write_text(text, encoding='utf-8')
print('fm_app/fm26.py updated successfully!')
