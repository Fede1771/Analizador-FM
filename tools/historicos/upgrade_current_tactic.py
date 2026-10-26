"""Upgrades fm_app/current_tactic.py with sub-position rules, marking targets, scopes and transparency."""

from pathlib import Path

ct_path = Path(__file__).resolve().parents[2] / 'fm_app' / 'current_tactic.py'
text = ct_path.read_text(encoding='utf-8')

import re

# Update imports from fm26
target_imp = "from fm_app.fm26 import ROLES, PI, TI, PLAYER_MENU, SCREENSHOT_LOCKS, instruction"
replacement_imp = "from fm_app.fm26 import ROLES, PI, TI, PLAYER_MENU, SCREENSHOT_LOCKS, EDITABLE_GROUPS, OBSERVED_CONTEXTS, instruction"

if target_imp in text:
    text = text.replace(target_imp, replacement_imp)

# In audit_tactic, add subposition checks, marking target checks, and behaviors
target_checks = """    for phase in ('ip','oop'):
        for row in rows:
            position=row.get(phase+'_position');role=row.get(phase+'_role')
            if position not in POSITIONS or role not in ROLES or position not in ROLES[role]['positions'] or ROLES[role]['phase']!=('in_possession' if phase=='ip' else 'out_of_possession'):raise ValueError('Confirmá posiciones y roles válidos en las dos fases.')
        if sum(r[phase+'_position']=='GK' for r in rows)!=1:raise ValueError('El once necesita un arquero en cada fase.')"""

replacement_checks = """    for phase in ('ip','oop'):
        for row in rows:
            position=row.get(phase+'_position');role=row.get(phase+'_role')
            if position not in POSITIONS or role not in ROLES or position not in ROLES[role]['positions'] or ROLES[role]['phase']!=('in_possession' if phase=='ip' else 'out_of_possession'):
                raise ValueError('Confirmá posiciones y roles válidos en las dos fases.')
            sub_rule = ROLES[role].get('subposition_rule')
            if sub_rule:
                if 'min_central_defenders' in sub_rule:
                    cbs = sum(1 for r in rows if r.get(phase+'_position') == 'DC')
                    if cbs < sub_rule['min_central_defenders']:
                        raise ValueError(f'{by_id[row["uid"]]["name"]}: {ROLES[role]["name"]} ({sub_rule["description"]})')
                if 'min_defensive_midfielders' in sub_rule:
                    dms = sum(1 for r in rows if r.get(phase+'_position') == 'DM')
                    if dms < sub_rule['min_defensive_midfielders']:
                        raise ValueError(f'{by_id[row["uid"]]["name"]}: {ROLES[role]["name"]} ({sub_rule["description"]})')
        if sum(r[phase+'_position']=='GK' for r in rows)!=1:raise ValueError('El once necesita un arquero en cada fase.')"""

if target_checks in text:
    text = text.replace(target_checks, replacement_checks)

# In audit_tactic, handle marking targets and instruction scopes
target_ins = """        for key,value in supplied.items():
            if key not in PI or value not in PI[key]['options']:raise ValueError('Instrucción individual no válida.')"""

replacement_ins = """        for key,value in supplied.items():
            if key not in PI or value not in PI[key]['options']:
                raise ValueError(f'{p["name"]}: Instrucción individual no válida ({key}={value}).')
        marking_mode = supplied.get('marking_target_oop')
        if marking_mode == 'Mark Specific' and not row.get('marking_target_player') and not row.get('marking_target_player_uid'):
            raise ValueError(f'{p["name"]}: La marca específica requiere indicar el jugador rival a marcar.')
        if marking_mode == 'Mark Position' and not row.get('marking_target_position'):
            raise ValueError(f'{p["name"]}: Marcar posición requiere indicar el puesto rival a cubrir.')"""

if target_ins in text:
    text = text.replace(target_ins, replacement_ins)

# Update plan creation with behaviors, abbreviation, scope
target_plan = """            plan['instructions']=chosen;plan['unconfirmed_instructions']=len(menu)-len(chosen)
            entry[key]=plan"""

replacement_plan = """            plan['instructions']=chosen
            plan['unconfirmed_instructions']=len(menu)-len(chosen)
            plan['behaviors']=r.get('behaviors',[])
            plan['abbreviation']=r.get('abbreviation','ROL')
            plan['scope']=row.get('instruction_scope','Posición')
            entry[key]=plan"""

if target_plan in text:
    text = text.replace(target_plan, replacement_plan)

# Update limits description
target_limits = "'limits':'El índice compara atributos y familiaridad. No mide eficacia del sistema ni predice resultados. Las órdenes sin confirmar no se sustituyen por propuestas. El mapa usa anclas del puesto y comportamiento típico del rol donde faltan instrucciones. Mentalidad, rival y movimientos dinámicos no están modelados.'"
replacement_limits = "'limits':'Ponderación analítica propia de Touchline (80% CP / 20% SP) basada en encaje de atributos y familiaridad posicional. No representa probabilidades deportivas ni pesos internos del motor de partidos de FM26. Las órdenes sin confirmar no se sustituyen por propuestas. Mentalidad, rival y movimientos dinámicos no están modelados.'"

if target_limits in text:
    text = text.replace(target_limits, replacement_limits)

ct_path.write_text(text, encoding='utf-8')
print('Upgraded current_tactic.py successfully!')
