"""FM26 reference vocabulary and explainable recommendations, separate from FM's ratings."""

import json

from pathlib import Path



ENGINE_VERSION=11

CATALOG=json.loads((Path(__file__).parent/'data/fm26_catalog.json').read_text(encoding='utf-8'))

LOCALE=json.loads((Path(__file__).parent/'data/fm26_es419.json').read_text(encoding='utf-8'))

REFERENCES={r['id']:r for r in CATALOG['roles']}

PI={r['id']:r for r in CATALOG['player_instructions']}

TI={r['id']:r for r in CATALOG['team_instructions']}

POSITION_MAP={'GK':['GK'],'D(C)':['DC'],'D(L/R)':['DL','DR'],'WB(L/R)':['WBL','WBR'],

              'DM':['DM'],'M(C)':['MC'],'M(L/R)':['ML','MR'],'AM(C)':['AMC'],'AM(L/R)':['AML','AMR'],'ST':['STC']}

ATTRIBUTE_MAP={'Off The Ball':'off_the_ball','First Touch':'first_touch','Long Shots':'long_shots','Work Rate':'work_rate',

               'Jumping Reach':'jumping_reach','Aerial Reach':'aerial_reach','Command Of Area':'command_of_area',

               'One On Ones':'one_on_ones'}



# Conservative, position-specific subset. Stopping Centre-Back is excluded: conflicting reference data.

IP_POOLS = {
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
}

# Official FM26 Spanish role abbreviations (as shown in match engine and tactical menus)
ROLE_ABBREV = {
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
}


def record(role_id):
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
    }


ROLE_IDS={r+'_'+phase for pools,phase in ((IP_POOLS,'ip'),(OOP_POOLS,'oop')) for values in pools.values() for r in values}

ROLES={key:record(key) for key in sorted(ROLE_IDS)}



TI_SECTIONS = {

    # Con posesión: Vista general

    'passing_directness': ('vista_general', 'Vista general', 'Pases directos y longitud de entrega'),

    'tempo': ('vista_general', 'Vista general', 'Ritmo de circulación colectiva'),

    'attacking_transition_ip': ('vista_general', 'Vista general', 'Conducta de transición ofensiva'),

    'creative_freedom_ip': ('vista_general', 'Vista general', 'Margen de libertad e improvisación'),

    'time_wasting': ('vista_general', 'Vista general', 'Manejo de tiempos y pausas'),

    'play_for_set_pieces_ip': ('vista_general', 'Vista general', 'Buscar jugadas a balón parado'),

    

    # Con posesión: Área de creación de oportunidades / Salida

    'build_up_strategy_ip': ('creacion_oportunidades', 'Área de creación de oportunidades', 'Estrategia de salida ante la presión'),

    'goal_kicks_ip': ('creacion_oportunidades', 'Área de creación de oportunidades', 'Saques de meta del arquero'),

    'gk_distribution_speed_ip': ('creacion_oportunidades', 'Área de creación de oportunidades', 'Velocidad de distribución del portero'),

    'gk_distribution_ip': ('creacion_oportunidades', 'Área de creación de oportunidades', 'Zona o receptor principal del saque'),

    

    # Con posesión: Avance

    'progress_through_ip': ('avance', 'Avance', 'Canal o zona preferente para progresar'),

    'pass_reception_ip': ('avance', 'Avance', 'Recepción de pases de los receptores'),

    'dribbling_ip': ('avance', 'Avance', 'Uso del regate y la conducción individual'),

    'overlap_ip': ('avance', 'Avance', 'Carreras de apoyo por fuera (desdoble)'),

    'underlap_ip': ('avance', 'Avance', 'Carreras de apoyo por dentro (interiores)'),

    

    # Con posesión: Último tercio

    'patience_ip': ('ultimo_tercio', 'Último tercio', 'Paciencia para elaborar y llevar el balón al área'),

    'shots_from_distance_ip': ('ultimo_tercio', 'Último tercio', 'Frecuencia de disparos lejanos'),

    'crossing_style_ip': ('ultimo_tercio', 'Último tercio', 'Estilo y trayectoria de los centros'),

    

    # Sin posesión: Líneas y Bloque

    'line_of_engagement_oop': ('lineas_bloque', 'Líneas y Bloque', 'Altura de la línea de presión'),

    'defensive_line_oop': ('lineas_bloque', 'Líneas y Bloque', 'Altura de la línea defensiva'),

    'defensive_line_behaviour_oop': ('lineas_bloque', 'Líneas y Bloque', 'Comportamiento de la zaga (presionar o retroceder)'),

    

    # Sin posesión: Presión y Recuperación

    'trigger_press_oop': ('presion_recuperacion', 'Presión y Recuperación', 'Activación e insistencia de la presión'),

    'defensive_transition_oop': ('presion_recuperacion', 'Presión y Recuperación', 'Transición defensiva tras pérdida'),

    'short_goalkeeper_distribution_oop': ('presion_recuperacion', 'Presión y Recuperación', 'Impedir saques cortos del portero rival'),

    

    # Sin posesión: Trampas y Centros

    'pressing_trap_oop': ('trampas_centros', 'Trampas y Centros', 'Orientación de la trampa de presión'),

    'cross_engagement_oop': ('trampas_centros', 'Trampas y Centros', 'Compromiso defensivo ante centros rivales'),

}



def instruction(kind,key,option,reason,origin='adjustment'):

    if kind not in ('player','team'):

        raise ValueError(f'Invalid FM26 instruction kind {kind}')

    ref=(PI if kind=='player' else TI)[key]

    if option not in ref['options']:

        raise ValueError(f'Invalid FM26 option {key}={option}')

    local=LOCALE[kind][key]

    selected=local['options'][option]

    sec = TI_SECTIONS.get(key) if kind=='team' else None

    res = {'id':key,'property':local['property']['text'],'property_en':ref['label'],

           'value':selected['text'],'value_en':option,

           'phase':ref.get('phase',ref.get('category')),'origin':origin,'reason':reason,

           'source':ref['source'],'menu_verified_es':False,

           'localization':{'locale':LOCALE['locale'],'steam_build':LOCALE['steam_build'],

                           'property':local['property'],'value':selected}}

    if sec:

        res['section_id'] = sec[0]

        res['section_name'] = sec[1]

        res['section_desc'] = sec[2]

    return res





PLAYER_MENU = {
    'in_possession': ['attacking_width_ip', 'dribbling_direction_ip', 'dribbling_frequency_ip', 'forward_runs_ip', 'freedom_of_movement_ip', 'hold_up_ball_ip', 'shoot_ip', 'passing_risk_ip', 'passing_directness_ip', 'cross_from_ip', 'crossing_strategy_ip'],
    'out_of_possession': ['pressing_oop', 'marking_oop', 'tackling_oop', 'marking_target_oop']
}

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
                i['availability_status'] = 'locked_verified'
                i['status_label'] = 'Bloqueado comprobado'
                locked_val = locks[key]
                i['locked_value'] = locked_val
                i['availability_source'] = f"Bloqueo comprobado en capturas FM26 ({ctx.get('evidence', '')})"
                if locked_val is not None:
                    i.update(instruction('player', key, locked_val, 'Valor bloqueado por el rol en las capturas: cambiar el rol para modificarlo.', 'role'))
                else:
                    i['locked_value'] = None
                    i['value_en'] = None
                    i['value'] = 'Desconocido (tapado por ayuda emergente en FM26)'
                    i['origin'] = 'role'
                    i['reason'] = 'Valor bloqueado en el juego pero tapado en las capturas por ayuda emergente (pendiente de certificación).'
            elif key in editable_list:
                i['locked'] = False
                i['editable'] = True
                i['availability_status'] = 'editable_verified'
                i['status_label'] = 'Editable comprobado'
                i['locked_value'] = None
                i['availability_source'] = f"Control editable comprobado en capturas FM26 ({ctx.get('evidence', '')})"
            else:
                i['locked'] = None
                i['editable'] = None
                i['availability_status'] = 'unverified'
                i['status_label'] = 'Disponibilidad no verificada'
                i['locked_value'] = None
                i['availability_source'] = f"Disponibilidad no verificada en FM para este contexto ({ctx.get('evidence', '')})"
        else:
            i['locked'] = None
            i['editable'] = None
            i['availability_status'] = 'unverified'
            i['status_label'] = 'Disponibilidad no verificada'
            i['locked_value'] = None
            i['availability_source'] = 'Disponibilidad no comprobada en las capturas de este rol'

    result.sort(key=lambda item: PLAYER_MENU[phase].index(item['id']))
    return result


TEAM_PLANS={

 'possession':{

     'passing_directness':'Shorter','tempo':'Lower','attacking_width_ip':'Standard','attacking_transition_ip':'Hold Shape',

     'creative_freedom_ip':'Balanced','time_wasting':'Less Often','play_for_set_pieces_ip':'Play for Set Pieces',

     'build_up_strategy_ip':'Play Through Press','goal_kicks_ip':'Short','gk_distribution_speed_ip':'Distribute Quickly','gk_distribution_ip':'Center-Backs',

     'progress_through_ip':'Balanced','pass_reception_ip':'Pass to Feet','dribbling_ip':'Balanced','overlap_ip':'Overlap - Balanced','underlap_ip':'Underlap - Balanced',

     'patience_ip':'Work Ball Into Box','shots_from_distance_ip':'Discourage','crossing_style_ip':'Low Crosses',

     'line_of_engagement_oop':'Mid Block','defensive_line_oop':'Standard','defensive_line_behaviour_oop':'Step Up More',

     'trigger_press_oop':'More Often','defensive_transition_oop':'Counter-Press','short_goalkeeper_distribution_oop':'Yes','tackling_oop':'Standard',

     'pressing_trap_oop':'Trap Inside','cross_engagement_oop':'Stop Crosses'

 },

 'press':{

     'passing_directness':'Shorter','tempo':'Higher','attacking_width_ip':'Standard','attacking_transition_ip':'Counter-Attack',

     'creative_freedom_ip':'More Expressive','time_wasting':'Less Often','play_for_set_pieces_ip':'Keep Ball in Play',

     'build_up_strategy_ip':'Balanced','goal_kicks_ip':'Short','gk_distribution_speed_ip':'Distribute Quickly','gk_distribution_ip':'Balanced',

     'progress_through_ip':'Balanced','pass_reception_ip':'Pass Into Space','dribbling_ip':'Encourage','overlap_ip':'Overlap - Both Flanks','underlap_ip':'Underlap - Balanced',

     'patience_ip':'Work Ball Into Box','shots_from_distance_ip':'Encourage','crossing_style_ip':'Whipped Crosses',

     'line_of_engagement_oop':'High Press','defensive_line_oop':'Higher','defensive_line_behaviour_oop':'Step Up More',

     'trigger_press_oop':'More Often','defensive_transition_oop':'Counter-Press','short_goalkeeper_distribution_oop':'Yes','tackling_oop':'Standard',

     'pressing_trap_oop':'Trap Inside','cross_engagement_oop':'Stop Crosses'

 },

 'counter':{

     'passing_directness':'More Direct','tempo':'Higher','attacking_width_ip':'Wider','attacking_transition_ip':'Counter-Attack',

     'creative_freedom_ip':'More Disciplined','time_wasting':'Standard','play_for_set_pieces_ip':'Keep Ball in Play',

     'build_up_strategy_ip':'Bypass Press','goal_kicks_ip':'Long','gk_distribution_speed_ip':'Distribute Quickly','gk_distribution_ip':'Over Opposition Defense',

     'progress_through_ip':'Both Flanks','pass_reception_ip':'Pass Into Space','dribbling_ip':'Encourage','overlap_ip':'Overlap - Balanced','underlap_ip':'Underlap - Balanced',

     'patience_ip':'Hit Early Crosses','shots_from_distance_ip':'Encourage','crossing_style_ip':'Whipped Crosses',

     'line_of_engagement_oop':'Mid Block','defensive_line_oop':'Standard','defensive_line_behaviour_oop':'Drop Off More',

     'trigger_press_oop':'Standard','defensive_transition_oop':'Regroup','short_goalkeeper_distribution_oop':'No','tackling_oop':'Standard',

     'pressing_trap_oop':'Trap Outside','cross_engagement_oop':'Balanced'

 },

 'wide':{

     'passing_directness':'Standard','tempo':'Standard','attacking_width_ip':'Much Wider','attacking_transition_ip':'Standard',

     'creative_freedom_ip':'Balanced','time_wasting':'Standard','play_for_set_pieces_ip':'Play for Set Pieces',

     'build_up_strategy_ip':'Balanced','goal_kicks_ip':'Mixed','gk_distribution_speed_ip':'Balanced','gk_distribution_ip':'Flanks',

     'progress_through_ip':'Both Flanks','pass_reception_ip':'Balanced','dribbling_ip':'Encourage','overlap_ip':'Overlap - Both Flanks','underlap_ip':'Underlap - Balanced',

     'patience_ip':'Hit Early Crosses','shots_from_distance_ip':'Balanced','crossing_style_ip':'Floated Crosses',

     'line_of_engagement_oop':'Mid Block','defensive_line_oop':'Standard','defensive_line_behaviour_oop':'Balanced',

     'trigger_press_oop':'Standard','defensive_transition_oop':'Regroup','short_goalkeeper_distribution_oop':'No','tackling_oop':'Standard',

     'pressing_trap_oop':'Trap Inside','cross_engagement_oop':'Balanced'

 },

}





PROMPT_REASONS = {

    'passing_directness': 'Recomendado por tu planteo: Pases más cortos para asegurar la posesión y evitar pérdidas en salida.',

    'tempo': 'Recomendado por tu planteo: Ritmo más bajo para elaborar con paciencia y desgastar al rival.',

    'build_up_strategy_ip': 'Recomendado por tu planteo: Salir jugando superando la presión desde la primera línea.',

    'pass_reception_ip': 'Recomendado por tu planteo: Pases al pie para facilitar el control y la asociación.',

    'attacking_transition_ip': 'Recomendado por tu planteo: Mantener el dibujo ofensivo para no precipitarse ni desordenar las líneas.',

    'line_of_engagement_oop': 'Recomendado por tu planteo: Bloque medio/alto para reducir espacios y evitar remates en la frontal.',

    'defensive_line_oop': 'Recomendado por tu planteo: Línea defensiva estándar para mantener la zaga protegida y no regalar la espalda.',

    'trigger_press_oop': 'Recomendado por tu planteo: Activar presión para incomodar el avance rival e impedir tiros a puerta.',

    'defensive_transition_oop': 'Recomendado por tu planteo: Contrapresión tras pérdida para recuperar de inmediato en campo rival.'

}



def team_instructions(players,style,overrides=None):

    if not players:

        return []

    def avg(key):return sum(p['attributes'][key] for p in players)/len(players)

    selected=dict(TEAM_PLANS[style])

    if overrides:

        selected.update({k:v for k,v in overrides.items() if k in selected})

    defenders=[p for p in players if p['positions'].get('dc',1)>=15]

    slow=defenders and min(p['attributes']['pace'] for p in defenders)<13

    if slow and selected['defensive_line_oop']=='Higher' and not (overrides and 'defensive_line_oop' in overrides):

        selected['defensive_line_oop']='Standard'

    if avg('stamina')<12 and not (overrides and 'trigger_press_oop' in overrides):

        selected['trigger_press_oop']='Standard'

        if selected['defensive_transition_oop']=='Counter-Press' and not (overrides and 'defensive_transition_oop' in overrides):

            selected['defensive_transition_oop']='Standard'

    if avg('passing')<12 and selected['build_up_strategy_ip']=='Play Through Press' and not (overrides and 'build_up_strategy_ip' in overrides):

        selected['build_up_strategy_ip']='Balanced'

    output=[]

    for key,value in selected.items():

        is_override = bool(overrides and key in overrides)

        evidence = {

            'passing_directness': (

                f'Pases cortos para dominar la posesión; primer toque medio {avg("first_touch"):.1f} y pase {avg("passing"):.1f}.'

                if 'Short' in value else

                f'Pases directos para transiciones verticales rápidas (técnica media {avg("technique"):.1f}).'

            ),

            'tempo': (

                f'Ritmo controlado para desgastar al rival con posesión paciente; decisiones medias {avg("decisions"):.1f} y serenidad {avg("composure"):.1f}.'

                if 'Lower' in value else

                f'Ritmo alto para sorprender al bloque rival; aceleración media {avg("acceleration"):.1f} y resistencia {avg("stamina"):.1f}.'

            ),

            'attacking_transition_ip': (

                'Conserva la estructura táctica tras recuperar para asegurar la posesión y evitar contraataques rivales desprotegidos.'

                if value == 'Hold Shape' else

                'Transición ofensiva rápida: busca atacar los espacios inmediatos antes de que el rival se reorganice defensivamente.'

            ),

            'creative_freedom_ip': (

                f'Equilibrio entre rigor táctico y libertad de movimientos; decisiones medias {avg("decisions"):.1f}.'

                if value == 'Balanced' else

                f'Mayor libertad e inventiva en tres cuartos de cancha; talento medio {avg("flair"):.1f} y visión {avg("vision"):.1f}.'

                if 'Expressive' in value else

                'Máxima disciplina táctica para que cada jugador mantenga su función sin correr riesgos innecesarios.'

            ),

            'time_wasting': (

                'Mantiene la fluidez del juego y la intensidad competitiva sin especular ni frenar el ritmo.'

                if 'Less' in value else

                'Ralentiza las reanudaciones para pausar el trámite del partido y asegurar el resultado favorable.'

            ),

            'play_for_set_pieces_ip': (

                f'Busca faltas y córners para explotar el juego aéreo del equipo; remate de cabeza medio {avg("heading"):.1f}.'

                if 'Play for' in value else

                'Prioriza la continuidad del juego dinámico con pelota en movimiento.'

            ),

            'build_up_strategy_ip': (

                f'Atrae la presión rival y sale jugando limpio desde el fondo; pases medios {avg("passing"):.1f} y serenidad {avg("composure"):.1f}.'

                if 'Play Through' in value else

                'Supera la primera línea de presión con pases largos o directos hacia los volantes y extremos.'

            ),

            'goal_kicks_ip': (

                'Saque en corto para mantener el control del balón y construir el ataque con los centrales abiertos.'

                if value == 'Short' else

                'Distribución mixta o larga según la presión alta que ejerza el rival.'

            ),

            'gk_distribution_speed_ip': (

                '💡 Recomendación: Con ritmo bajo y pases cortos, apurar al arquero puede causar pérdidas si la zaga aún no tomó amplitud. Evaluá pausar la salida.'

                if 'Quickly' in value else

                'El arquero toma dos segundos antes de jugar para que los laterales ganen la banda y los centrales se ubiquen.'

            ),

            'gk_distribution_ip': (

                'Salida con centrales abiertos para iniciar la fase de construcción desde el fondo con superioridad.'

                if 'Center-Backs' in value or 'Centre-Backs' in value else

                'Distribución dirigida a los costados para activar inmediatamente a los laterales en campo propio.'

                if 'Full-Backs' in value or 'Flanks' in value else

                'Distribución hacia el organizador para que tome la manija de la creación desde el primer pase.'

            ),

            'progress_through_ip': (

                'Progresión equilibrada: utiliza tanto las bandas como el carril interior según los espacios libres.'

                if value == 'Balanced' else

                'Concentra los avances por los costados para generar superioridad con laterales y extremos.'

                if 'Flanks' in value else

                'Canaliza la progresión por el centro para conectar con los mediocampistas organizadores.'

            ),

            'pass_reception_ip': (

                f'Pases al pie para asegurar el control y reducir pérdidas; primer toque medio {avg("first_touch"):.1f}.'

                if 'Feet' in value or 'to Feet' in value else

                f'Pases al espacio aprovechando la velocidad y aceleración de los atacantes (media {avg("pace"):.1f}).'

            ),

            'dribbling_ip': (

                'Privilegia la circulación de balón y los apoyos colectivos por sobre la conducción individual.'

                if 'Discourage' in value else

                f'Fomenta el uno contra uno de los extremos y mediapuntas; regate medio {avg("dribbling"):.1f}.'

            ),

            'overlap_ip': (

                '💡 Consejo táctico: Activar "Doblar por fuera" permite que tus laterales desdoblen a los extremos y abran defensas replegadas 2 vs 1.'

                if 'Balanced' in value else

                'Los laterales se proyectan por la banda para generar centros constantes y desdoblar a los extremos.'

            ),

            'underlap_ip': (

                'Los laterales trazan diagonales hacia el centro para generar superioridad interior en tres cuartos.'

                if 'Underlap' in value else

                'Mantiene los desdoblamientos equilibrados según la situación de la jugada.'

            ),

            'patience_ip': (

                f'Paciencia para entrar al área: elabora la jugada hasta encontrar remates claros de alto xG (serenidad {avg("composure"):.1f}).'

                if 'Work Ball' in value else

                'Busca centros tempranos para sorprender a la zaga rival antes de que se posicione.'

            ),

            'shots_from_distance_ip': (

                f'Desalienta los tiros de larga distancia para no desperdiciar posesiones en remates de bajo porcentaje (tiros lejanos {avg("long_shots"):.1f}).'

                if 'Discourage' in value else

                f'Alienta a probar al arquero desde afuera del área; remates lejanos medios {avg("long_shots"):.1f}.'

            ),

            'crossing_style_ip': (

                'Centros rasos al primer palo o punto penal, ideales para delanteros dinámicos y llegadores desde segunda línea.'

                if 'Low' in value else

                f'Centros colgados o tensos para aprovechar la envergadura y potencia aérea de los atacantes (salto {avg("jumping_reach"):.1f}).'

            ),

            'line_of_engagement_oop': (

                '💡 Recomendación: Con contrapresión insistente, el bloque medio puede dividir al equipo. Si buscás dominar arriba, subí a "Bloque alto".'

                if value == 'Mid Block' else

                'Bloque alto: asfixia la salida del rival en su propio campo forzando errores y recuperaciones cercanas al arco.'

                if 'High' in value else

                'Bloque bajo: protege el área propia y reduce los espacios a espaldas de la defensa.'

            ),

            'defensive_line_oop': (

                ('Hay un central con velocidad menor de 13: se evita subir más la línea.' if slow else f'Revisar la respuesta de los centrales a balones a su espalda (velocidad media {sum(p["attributes"]["pace"] for p in defenders)/len(defenders):.1f}).')

                if value == 'Standard' else

                'Línea defensiva adelantada para achicar la distancia con el mediocampo y asfixiar al rival.'

            ),

            'defensive_line_behaviour_oop': (

                'La zaga da un paso al frente para provocar el fuera de juego del atacante y achicar espacios entre líneas.'

                if 'Step Up' in value else

                'La zaga retrocede con cautela protegiendo el espacio a su espalda ante balones largos rivales.'

            ),

            'trigger_press_oop': (

                f'Resistencia media {avg("stamina"):.1f} y sacrificio {avg("work_rate"):.1f}. Presión insistente sobre el portador.'

                if 'More' in value else

                'Presión equilibrada para dosificar el esfuerzo físico y conservar las líneas compactas.'

            ),

            'defensive_transition_oop': (

                f'Resistencia media {avg("stamina"):.1f}; la contrapresión se modera si es menor de 12. Recuperación inmediata tras pérdida.'

                if 'Counter-Press' in value else

                'Reagrupamiento defensivo inmediato tras perder el balón para proteger el arco propio ordenadamente.'

            ),

            'short_goalkeeper_distribution_oop': (

                'Tapa las opciones de pase corto del portero rival forzándolo a despejar en largo y dividir la pelota.'

                if value in ('Yes', True) else

                'Permite la salida rival para esperarlo ordenadamente en campo propio.'

            ),

            'pressing_trap_oop': (

                'Trampa hacia dentro: orienta la presión para forzar al rival a jugar por el medio, donde el doble pivote y centrales recuperan balones.'

                if 'Inside' in value else

                'Trampa hacia fuera: empuja el juego rival hacia la banda para acorralarlo contra la línea de cal.'

            ),

            'cross_engagement_oop': (

                'Los laterales y extremos enciman rápidamente al portador de la pelota para tapar centros al área.'

                if 'Stop' in value else

                'Invita los centros rivales confiando en la superioridad aérea y despejes de los centrales.'

            )

        }

        reason = (PROMPT_REASONS.get(key, 'Ajustado específicamente según tu planteo táctico personalizado.') if is_override else evidence.get(key, f'Instrucción coordinada con el estilo {style}.'))

        output.append(instruction('team',key,value,reason,origin='prompt' if is_override else 'style'))

    return output



# Official FM26 Spanish role abbreviations (as shown in match engine and tactical menus)
