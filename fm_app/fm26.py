"""FM26 reference vocabulary and explainable recommendations, separate from FM's ratings."""
import json
from pathlib import Path

ENGINE_VERSION=6
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
IP_POOLS={
 'GK':['goalkeeper','ball_playing_goalkeeper','no_nonsense_goalkeeper'],
 'DC':['centre_back','ball_playing_centre_back','no_nonsense_center_back'],
 'DL':['full_back','wing_back'],'DR':['full_back','wing_back'],
 'WBL':['wing_back'],'WBR':['wing_back'],
 'DM':['defensive_midfielder','deep_lying_playmaker'],
 'MC':['central_midfielder','midfield_playmaker','attacking_midfielder','advanced_playmaker','channel_midfielder'],
 'AMC':['attacking_midfielder','advanced_playmaker','second_striker','free_role'],
 'AML':['winger','inside_winger','inside_forward','wide_forward','playmaking_winger'],
 'AMR':['winger','inside_winger','inside_forward','wide_forward','playmaking_winger'],
 'ML':['wide_midfielder','winger','inside_winger','playmaking_winger'],
 'MR':['wide_midfielder','winger','inside_winger','playmaking_winger'],
 'STC':['centre_forward','channel_forward','target_forward','deep_lying_forward','poacher','false_nine'],
}
OOP_POOLS={
 'GK':['goalkeeper','sweeper_keeper','line_holding_keeper'],'DC':['centre_back','covering_centre_back'],
 'DL':['full_back','pressing_full_back','holding_full_back'],'DR':['full_back','pressing_full_back','holding_full_back'],
 'WBL':['wing_back','pressing_wing_back','holding_wing_back'],'WBR':['wing_back','pressing_wing_back','holding_wing_back'],
 'DM':['defensive_midfielder','screening_defensive_midfielder'],
 'MC':['central_midfielder','pressing_central_midfielder','screening_central_midfielder','wide_covering_central_midfielder'],
 'AMC':['attacking_midfielder','tracking_attacking_midfielder'],
 'AML':['winger','tracking_winger'],'AMR':['winger','tracking_winger'],
 'ML':['wide_midfielder','tracking_wide_midfielder'],'MR':['wide_midfielder','tracking_wide_midfielder'],
 'STC':['centre_forward','tracking_centre_forward','central_outlet_centre_forward'],
}


def record(role_id):
    raw=REFERENCES[role_id]
    stem=role_id.rsplit('_',1)[0]
    pos=raw['position'] if isinstance(raw['position'],list) else [raw['position']]
    positions=[p for value in pos for p in POSITION_MAP[value]]
    attrs=[ATTRIBUTE_MAP.get(a,a.lower().replace(' ','_')) for a in raw['key_attributes']]
    local=LOCALE['roles'][stem]
    verified = local.get('runtime_verified', False) or local.get('menu_verified_es', False)
    status = ('Español latinoamericano · verificado en menú de FM26 '+LOCALE['game_version']) if verified else ('Español latinoamericano · archivo de FM26 '+LOCALE['game_version'])
    src = local.get('verified_source', LOCALE['source'])
    return {**raw,'name':local['text'],'positions':positions,'weights':{a:1 for a in attrs},
            'english':raw['role_name'],'spanish_status':status,
            'spanish_source':src,'menu_verified_es':verified,
            'localization':{**local,'locale':LOCALE['locale'],'steam_build':LOCALE['steam_build']}}


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


def player_instructions(player,role):
    a=player['attributes']; phase=role['phase']; stem=role['id'].rsplit('_',1)[0]
    builtin=role['player_instructions']
    result=[]
    def add(key,value,why,base=False):
        result.append(instruction('player',key,value,why,'role' if base else 'standard' if value in ('Standard','Follow Tactical Position','No') else 'adjustment'))
    if phase=='in_possession':
        more='Take More Risks' in builtin; fewer='Take Fewer Risks' in builtin
        value='Take More Risks' if more else 'Take Fewer Risks' if fewer or min(a['passing'],a['decisions'])<11 else 'Standard'
        add('passing_risk_ip',value,f'Pases {a["passing"]}, visión {a["vision"]} y decisiones {a["decisions"]}. '+('El rol ya pide ese nivel de riesgo; no agregar la orden contraria.' if more or fewer else 'Se limita el riesgo si pases o decisiones están por debajo de 11; en el resto se mantiene el comportamiento del rol.'),more or fewer)
        if 'GK' not in role['positions']:
            dribble='Dribble More' if ('Dribble More Often' in builtin or (stem in ('winger','inside_winger','inside_forward','wide_forward') and min(a['dribbling'],a['acceleration'])>=13)) else 'Dribble Less' if a['dribbling']<11 or any('dribble less' in s.lower() for s in builtin) else 'Standard'
            add('dribbling_frequency_ip',dribble,f'Regate {a["dribbling"]} y aceleración {a["acceleration"]}: '+('aprovechar el uno contra uno.' if dribble=='Dribble More' else 'reducir pérdidas en la conducción.' if dribble=='Dribble Less' else 'conservar la elección de conducción del rol.'),'Dribble More Often' in builtin or any('dribble less' in s.lower() for s in builtin))
            shoot='Shoot Less Often' if a['finishing']<11 and a['long_shots']<12 else 'Standard'
            add('shoot_ip',shoot,f'Remate {a["finishing"]} y tiros lejanos {a["long_shots"]}: '+('priorizar una opción de pase antes que forzar el tiro.' if shoot!='Standard' else 'mantener la selección de tiro del rol; no forzar remates lejanos.'))
            if 'Get Further Forward' in builtin:
                add('forward_runs_ip','Make More Runs',f'Desmarques {a["off_the_ball"]} y resistencia {a["stamina"]}. La llegada forma parte de este rol.',True)
            if 'Hold Up Ball' in builtin:
                add('hold_up_ball_ip','Yes',f'Fuerza {a["strength"]} y primer toque {a["first_touch"]}: el rol recibe de espaldas para conectar apoyos.',True)
            if 'Roam From Position' in builtin:
                add('freedom_of_movement_ip','Roam From Position',f'Decisiones {a["decisions"]} y desmarques {a["off_the_ball"]}: movilidad propia del rol; vigilar el espacio que abandona.',True)
    elif 'GK' not in role['positions']:
        press='More Often' if 'Trigger Press More Often' in builtin else 'Less Often' if 'Trigger Press Less Often' in builtin else 'Standard'
        add('pressing_oop',press,f'Sacrificio {a["work_rate"]}, resistencia {a["stamina"]} y anticipación {a["anticipation"]}: '+('el rol sale a presionar; necesita cobertura detrás.' if press=='More Often' else 'proteger la posición antes de perseguir al portador.' if press=='Less Often' else 'coordinar la presión con el bloque.'),press!='Standard')
        ease=a['tackling']<11 or a['aggression']>=16
        add('tackling_oop','Ease Off Tackles' if ease else 'Standard',f'Entradas {a["tackling"]} y agresividad {a["aggression"]}: '+('evitar entradas precipitadas; no elimina el riesgo de faltas.' if ease else 'mantener la dureza normal; no sumar agresividad sin necesidad.'))
    return result


TEAM_PLANS={
 'possession':{
     'passing_directness':'Shorter','tempo':'Lower','attacking_transition_ip':'Hold Shape',
     'creative_freedom_ip':'Balanced','time_wasting':'Less Often','play_for_set_pieces_ip':'Play for Set Pieces',
     'build_up_strategy_ip':'Play Through Press','goal_kicks_ip':'Short','gk_distribution_speed_ip':'Distribute Quickly','gk_distribution_ip':'Center-Backs',
     'progress_through_ip':'Balanced','pass_reception_ip':'Pass to Feet','dribbling_ip':'Balanced','overlap_ip':'Overlap - Balanced',
     'patience_ip':'Work Ball Into Box','shots_from_distance_ip':'Discourage','crossing_style_ip':'Low Crosses',
     'line_of_engagement_oop':'Mid Block','defensive_line_oop':'Standard','defensive_line_behaviour_oop':'Step Up More',
     'trigger_press_oop':'More Often','defensive_transition_oop':'Counter-Press','short_goalkeeper_distribution_oop':'Yes',
     'pressing_trap_oop':'Trap Inside','cross_engagement_oop':'Stop Crosses'
 },
 'press':{
     'passing_directness':'Shorter','tempo':'Higher','attacking_transition_ip':'Counter-Attack',
     'creative_freedom_ip':'More Expressive','time_wasting':'Less Often','play_for_set_pieces_ip':'Keep Ball in Play',
     'build_up_strategy_ip':'Balanced','goal_kicks_ip':'Short','gk_distribution_speed_ip':'Distribute Quickly','gk_distribution_ip':'Balanced',
     'progress_through_ip':'Balanced','pass_reception_ip':'Pass Into Space','dribbling_ip':'Encourage','overlap_ip':'Overlap - Both Flanks',
     'patience_ip':'Work Ball Into Box','shots_from_distance_ip':'Encourage','crossing_style_ip':'Whipped Crosses',
     'line_of_engagement_oop':'High Press','defensive_line_oop':'Higher','defensive_line_behaviour_oop':'Step Up More',
     'trigger_press_oop':'More Often','defensive_transition_oop':'Counter-Press','short_goalkeeper_distribution_oop':'Yes',
     'pressing_trap_oop':'Trap Inside','cross_engagement_oop':'Stop Crosses'
 },
 'counter':{
     'passing_directness':'More Direct','tempo':'Higher','attacking_transition_ip':'Counter-Attack',
     'creative_freedom_ip':'More Disciplined','time_wasting':'Standard','play_for_set_pieces_ip':'Keep Ball in Play',
     'build_up_strategy_ip':'Bypass Press','goal_kicks_ip':'Long','gk_distribution_speed_ip':'Distribute Quickly','gk_distribution_ip':'Over Opposition Defense',
     'progress_through_ip':'Both Flanks','pass_reception_ip':'Pass Into Space','dribbling_ip':'Encourage','overlap_ip':'Overlap - Balanced',
     'patience_ip':'Hit Early Crosses','shots_from_distance_ip':'Encourage','crossing_style_ip':'Whipped Crosses',
     'line_of_engagement_oop':'Mid Block','defensive_line_oop':'Standard','defensive_line_behaviour_oop':'Drop Off More',
     'trigger_press_oop':'Standard','defensive_transition_oop':'Regroup','short_goalkeeper_distribution_oop':'No',
     'pressing_trap_oop':'Trap Outside','cross_engagement_oop':'Balanced'
 },
 'wide':{
     'passing_directness':'Standard','tempo':'Standard','attacking_transition_ip':'Standard',
     'creative_freedom_ip':'Balanced','time_wasting':'Standard','play_for_set_pieces_ip':'Play for Set Pieces',
     'build_up_strategy_ip':'Balanced','goal_kicks_ip':'Mixed','gk_distribution_speed_ip':'Balanced','gk_distribution_ip':'Flanks',
     'progress_through_ip':'Both Flanks','pass_reception_ip':'Balanced','dribbling_ip':'Encourage','overlap_ip':'Overlap - Both Flanks',
     'patience_ip':'Hit Early Crosses','shots_from_distance_ip':'Balanced','crossing_style_ip':'Floated Crosses',
     'line_of_engagement_oop':'Mid Block','defensive_line_oop':'Standard','defensive_line_behaviour_oop':'Balanced',
     'trigger_press_oop':'Standard','defensive_transition_oop':'Regroup','short_goalkeeper_distribution_oop':'No',
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
        evidence={'passing_directness':f'Pases medios {avg("passing"):.1f} y primer toque {avg("first_touch"):.1f}.',
                  'tempo':f'Decisiones medias {avg("decisions"):.1f} y resistencia {avg("stamina"):.1f}.',
                  'defensive_line_oop':('Hay un central con velocidad menor de 13: se evita subir más la línea.' if slow else 'Revisar la respuesta de los centrales a balones a su espalda.'),
                  'trigger_press_oop':f'Resistencia media {avg("stamina"):.1f} y sacrificio {avg("work_rate"):.1f}.',
                  'defensive_transition_oop':f'Resistencia media {avg("stamina"):.1f}; la contrapresión se modera si es menor de 12.'}
        reason = (PROMPT_REASONS.get(key, 'Ajustado específicamente según tu planteo táctico personalizado.') if is_override else evidence.get(key,'Coordina esta fase con el estilo elegido; comprobar su funcionamiento ante el rival.'))
        output.append(instruction('team',key,value,reason,origin='prompt' if is_override else 'style'))
    return output
