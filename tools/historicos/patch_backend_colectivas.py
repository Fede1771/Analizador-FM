"""Updates fm_app/fm26.py, fm_app/contracts.py, and fm_app/current_tactic.py with collective rules and validation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 1. Update fm_app/fm26.py
fm26_path = ROOT / 'fm_app' / 'fm26.py'
fm26_code = fm26_path.read_text(encoding='utf-8')

# Ensure TI_SECTIONS has attacking_width_ip and tackling_oop
if "'attacking_width_ip'" not in fm26_code:
    fm26_code = fm26_code.replace(
        "'passing_directness': ('vista_general', 'Vista general', 'Pases directos y longitud de entrega'),",
        "'passing_directness': ('vista_general', 'Vista general', 'Pases directos y longitud de entrega'),\n    'attacking_width_ip': ('vista_general', 'Vista general', 'Amplitud del ataque y ocupación de carriles'),"
    )

if "'tackling_oop'" not in fm26_code:
    fm26_code = fm26_code.replace(
        "'short_goalkeeper_distribution_oop': ('presion_recuperacion', 'Presión y Recuperación', 'Impedir saques cortos del portero rival'),",
        "'short_goalkeeper_distribution_oop': ('presion_recuperacion', 'Presión y Recuperación', 'Impedir saques cortos del portero rival'),\n    'tackling_oop': ('presion_recuperacion', 'Presión y Recuperación', 'Compromiso físico al realizar una entrada'),"
    )

# Ensure TEAM_PLANS has defaults for attacking_width_ip and tackling_oop
if "'attacking_width_ip':" not in fm26_code:
    fm26_code = fm26_code.replace(
        "'passing_directness':'Shorter','tempo':'Lower',",
        "'passing_directness':'Shorter','tempo':'Lower','attacking_width_ip':'Standard',"
    ).replace(
        "'trigger_press_oop':'More Often','defensive_transition_oop':'Counter-Press','short_goalkeeper_distribution_oop':'Yes',",
        "'trigger_press_oop':'More Often','defensive_transition_oop':'Counter-Press','short_goalkeeper_distribution_oop':'Yes','tackling_oop':'Standard',"
    )
    # Also update press, counter, wide
    fm26_code = fm26_code.replace(
        "'passing_directness':'Shorter','tempo':'Higher',",
        "'passing_directness':'Shorter','tempo':'Higher','attacking_width_ip':'Standard',"
    ).replace(
        "'passing_directness':'More Direct','tempo':'Higher',",
        "'passing_directness':'More Direct','tempo':'Higher','attacking_width_ip':'Wider',"
    ).replace(
        "'passing_directness':'Standard','tempo':'Standard',",
        "'passing_directness':'Standard','tempo':'Standard','attacking_width_ip':'Much Wider',"
    )
    fm26_code = fm26_code.replace(
        "'trigger_press_oop':'More Often','defensive_transition_oop':'Counter-Press','short_goalkeeper_distribution_oop':'Yes',\n\n     'pressing_trap_oop':'Trap Inside','cross_engagement_oop':'Stop Crosses'\n\n  },\n\n  'counter'",
        "'trigger_press_oop':'More Often','defensive_transition_oop':'Counter-Press','short_goalkeeper_distribution_oop':'Yes','tackling_oop':'Get Stuck In',\n\n     'pressing_trap_oop':'Trap Inside','cross_engagement_oop':'Stop Crosses'\n\n  },\n\n  'counter'"
    ).replace(
        "'trigger_press_oop':'Standard','defensive_transition_oop':'Regroup','short_goalkeeper_distribution_oop':'No',\n\n     'pressing_trap_oop':'Trap Outside','cross_engagement_oop':'Balanced'\n\n  },\n\n  'wide'",
        "'trigger_press_oop':'Standard','defensive_transition_oop':'Regroup','short_goalkeeper_distribution_oop':'No','tackling_oop':'Standard',\n\n     'pressing_trap_oop':'Trap Outside','cross_engagement_oop':'Balanced'\n\n  },\n\n  'wide'"
    ).replace(
        "'trigger_press_oop':'Standard','defensive_transition_oop':'Regroup','short_goalkeeper_distribution_oop':'No',\n\n     'pressing_trap_oop':'Trap Inside','cross_engagement_oop':'Balanced'\n\n  }\n\n}",
        "'trigger_press_oop':'Standard','defensive_transition_oop':'Regroup','short_goalkeeper_distribution_oop':'No','tackling_oop':'Standard',\n\n     'pressing_trap_oop':'Trap Inside','cross_engagement_oop':'Balanced'\n\n  }\n\n}"
    )

# Evidence in team_instructions
if "'attacking_width_ip':" not in fm26_code:
    evidence_target = "'passing_directness': ("
    evidence_replacement = """'attacking_width_ip': (
                'Amplitud abierta para estirar la defensa rival y ensanchar la cancha.'
                if 'Wider' in value else
                'Amplitud equilibrada para mantener apoyos cortos y compactos.'
            ),

            'passing_directness': ("""
    fm26_code = fm26_code.replace(evidence_target, evidence_replacement)

if "'tackling_oop':" not in fm26_code:
    tackling_evidence_target = "'short_goalkeeper_distribution_oop': ("
    tackling_evidence_replacement = """'tackling_oop': (
                'Entradas agresivas para recuperar la posesión con contundencia y frenar avances rivales.'
                if value == 'Get Stuck In' else
                'Mantenerse de pie sin precipitarse para no cometer faltas ni desubicarse.'
            ),

            'short_goalkeeper_distribution_oop': ("""
    fm26_code = fm26_code.replace(tackling_evidence_target, tackling_evidence_replacement)

fm26_path.write_text(fm26_code, encoding='utf-8')
print('Updated fm_app/fm26.py')

# 2. Update fm_app/contracts.py
contracts_path = ROOT / 'fm_app' / 'contracts.py'
contracts_code = contracts_path.read_text(encoding='utf-8')
if 'Incompatibilidad en Carreras de apoyo' not in contracts_code:
    old_validate = """def validate_overrides(value):
    if not isinstance(value, dict) or len(value) > len(TI):
        raise ValueError('Los ajustes tácticos deben ser un objeto.')
    for key, option in value.items():
        if key not in TI or not isinstance(option, str) or option not in TI[key]['options']:
            raise ValueError(f'Instrucción desconocida o valor inválido: {key}.')
    return value"""
    new_validate = """def validate_overrides(value):
    if not isinstance(value, dict) or len(value) > len(TI):
        raise ValueError('Los ajustes tácticos deben ser un objeto.')
    for key, option in value.items():
        if key not in TI or not isinstance(option, str) or option not in TI[key]['options']:
            raise ValueError(f'Instrucción desconocida o valor inválido: {key}.')
    # Support runs verified incompatibilities
    if value.get('underlap_ip') == 'Underlap - Both Flanks' and value.get('overlap_ip') in ('Overlap - Left', 'Overlap - Right', 'Overlap - Both Flanks'):
        raise ValueError('Incompatibilidad en Carreras de apoyo: al doblar por dentro en ambas bandas, doblar por banda debe ser Equilibrado.')
    if value.get('overlap_ip') == 'Overlap - Both Flanks' and value.get('underlap_ip') in ('Underlap - Left', 'Underlap - Right', 'Underlap - Both Flanks'):
        raise ValueError('Incompatibilidad en Carreras de apoyo: al doblar por ambas bandas, doblar por dentro debe ser Equilibrado.')
    return value"""
    contracts_code = contracts_code.replace(old_validate, new_validate)
    contracts_path.write_text(contracts_code, encoding='utf-8')
    print('Updated fm_app/contracts.py')

# 3. Update fm_app/current_tactic.py
current_tactic_path = ROOT / 'fm_app' / 'current_tactic.py'
ct_code = current_tactic_path.read_text(encoding='utf-8')
if 'Incompatibilidad en Carreras de apoyo' not in ct_code:
    old_ct_check = """    for key,value in team.items():
        if key not in TI or value not in TI[key]['options']:raise ValueError('Instrucción de equipo no válida.')"""
    new_ct_check = """    for key,value in team.items():
        if key not in TI or value not in TI[key]['options']:raise ValueError('Instrucción de equipo no válida.')
    if team.get('underlap_ip') == 'Underlap - Both Flanks' and team.get('overlap_ip') in ('Overlap - Left', 'Overlap - Right', 'Overlap - Both Flanks'):
        raise ValueError('Incompatibilidad en Carreras de apoyo: al doblar por dentro en ambas bandas, doblar por banda debe ser Equilibrado.')
    if team.get('overlap_ip') == 'Overlap - Both Flanks' and team.get('underlap_ip') in ('Underlap - Left', 'Underlap - Right', 'Underlap - Both Flanks'):
        raise ValueError('Incompatibilidad en Carreras de apoyo: al doblar por ambas bandas, doblar por dentro debe ser Equilibrado.')
    if team.get('short_goalkeeper_distribution_oop') == 'Yes':
        advice.append({
            'title': 'Impedir salida en corto del portero rival',
            'player_uid': None,
            'player_name': None,
            'phase': 'oop',
            'phase_label': 'Sin posesión (SP)',
            'detail': 'En Sin posesión (SP), tu equipo presiona la salida corta del arquero rival para forzarlo a dividir el balón en largo.',
            'category': 'team_press',
            'severity': 'info',
            'badge': '🧤 Salida rival',
            'action': 'Obligar al portero rival a jugar en largo',
            'chips': ['Fase: Sin posesión (SP)', 'Presión adelantada', 'Impedir salida en corto']
        })"""
    ct_code = ct_code.replace(old_ct_check, new_ct_check)
    current_tactic_path.write_text(ct_code, encoding='utf-8')
    print('Updated fm_app/current_tactic.py')
