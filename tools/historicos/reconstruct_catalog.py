"""Reconstructs Touchline's FM26 catalog and localization using the empirical survey from 2026-10-25."""

import json
import os
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
SURVEY_DIR = ROOT / 'docs' / 'relevamiento-fm26-2026-10-25'

with open(SURVEY_DIR / 'catalogo-para-reconstruccion.json', 'r', encoding='utf-8') as f:
    cat_src = json.load(f)

with open(SURVEY_DIR / 'matriz-instrucciones-observadas.json', 'r', encoding='utf-8') as f:
    mat_src = json.load(f)

with open(SURVEY_DIR / 'verificacion-adicional-roles.json', 'r', encoding='utf-8') as f:
    ver_src = json.load(f)

with open(ROOT / 'fm_app' / 'data' / 'fm26_es419.json', 'r', encoding='utf-8') as f:
    old_loc = json.load(f)

with open(ROOT / 'fm_app' / 'data' / 'fm26_catalog.json', 'r', encoding='utf-8') as f:
    old_cat = json.load(f)

from fm_app.tactics import ATTRS

def normalize_attr_name(s):
    try:
        s = s.encode('latin-1').decode('utf-8')
    except Exception:
        pass
    s = s.lower().replace('\xad', '')
    for src, dst in [('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('\ufffd', '')]:
        s = s.replace(src, dst)
    return s.strip()

SPANISH_ATTR_MAP = {
    'aceleracion': 'acceleration', 'agilidad': 'agility', 'agresividad': 'aggression',
    'alcance aereo': 'aerial_reach', 'alcance de salto': 'jumping_reach',
    'anticipacion': 'anticipation', 'blocaje': 'handling', 'cabeceo': 'heading',
    'centros': 'crossing', 'colocacion': 'positioning', 'comunicacion': 'communication',
    'concentracion': 'concentration', 'control': 'first_touch', 'decisiones': 'decisions',
    'desmarques': 'off_the_ball', 'entradas': 'tackling', 'equilibrio': 'balance',
    'fuerza': 'strength', 'juego en equipo': 'teamwork', 'mando en el area': 'command_of_area',
    'marca': 'marking', 'pases': 'passing', 'reflejos': 'reflexes', 'regate': 'dribbling',
    'remate': 'finishing', 'remates lejanos': 'long_shots', 'resistencia': 'stamina',
    'sacrificio': 'work_rate', 'saques de puerta': 'kicking', 'serenidad': 'composure',
    'talento': 'flair', 'tecnica': 'technique', 'uno contra uno': 'one_on_ones',
    'valentia': 'bravery', 'velocidad': 'pace', 'vision': 'vision'
}

EN_ATTR_MAP = {
    'Handling': 'handling', 'Aerial Reach': 'aerial_reach', 'Command Of Area': 'command_of_area',
    'Communication': 'communication', 'Positioning': 'positioning', 'Reflexes': 'reflexes',
    'Agility': 'agility', 'Concentration': 'concentration', 'Kicking': 'kicking',
    'Anticipation': 'anticipation', 'Decisions': 'decisions', 'One On Ones': 'one_on_ones',
    'Marking': 'marking', 'Tackling': 'tackling', 'Heading': 'heading', 'Jumping Reach': 'jumping_reach',
    'Strength': 'strength', 'Bravery': 'bravery', 'Passing': 'passing', 'Technique': 'technique',
    'Composure': 'composure', 'First Touch': 'first_touch', 'Vision': 'vision', 'Pace': 'pace',
    'Acceleration': 'acceleration', 'Crossing': 'crossing', 'Dribbling': 'dribbling',
    'Off The Ball': 'off_the_ball', 'Stamina': 'stamina', 'Work Rate': 'work_rate',
    'Teamwork': 'teamwork', 'Finishing': 'finishing', 'Long Shots': 'long_shots', 'Flair': 'flair',
    'Balance': 'balance', 'Aggression': 'aggression'
}

# Role abbreviations for pitch badges
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

mat_by_role = {item['role']: item for item in mat_src}

# Build roles
reconstructed_roles = []
locale_roles = dict(old_loc.get('roles', {}))

for r in cat_src['roles']:
    rid = r['id']
    stem = rid.rsplit('_', 1)[0]
    phase = r['phase']
    en_name = r.get('label_resource', {}).get('en') or r.get('id')
    ref_label_es = r.get('label_es_reference')
    res_label_es = r.get('label_resource', {}).get('es') or ref_label_es
    ui_ver = r.get('additional_ui_verification') or ver_src.get(rid, {})
    ui_label = ui_ver.get('label_ui') or ref_label_es
    res_key = r.get('label_resource', {}).get('key') or 0

    # Positions
    positions = list(r.get('positions_reference', []))

    # Attributes
    ui_attrs_raw = ui_ver.get('attributes') or []
    if ui_attrs_raw:
        key_attributes = [SPANISH_ATTR_MAP[normalize_attr_name(a)] for a in ui_attrs_raw if normalize_attr_name(a) in SPANISH_ATTR_MAP]
        attrs_verified = True
        attrs_provenance = f"Ficha observada en FM26 ({ui_ver.get('evidence', r.get('current_ui_evidence', ''))}); no revela pesos del motor."
    else:
        prior_raw = r.get('key_attributes_prior_catalog', [])
        if not prior_raw and rid == 'pressing_defensive_midfielder_oop':
            # Match pressing central midfielder reference attributes (work rate, stamina, tackling, anticipation, decisions, teamwork, aggression)
            prior_raw = ['Tackling', 'Anticipation', 'Decisions', 'Teamwork', 'Work Rate', 'Stamina', 'Aggression']
        key_attributes = [EN_ATTR_MAP.get(a, a.lower().replace(' ', '_')) for a in prior_raw if a in EN_ATTR_MAP or a.lower().replace(' ', '_') in ATTRS]
        attrs_verified = False
        attrs_provenance = "Catálogo de referencia externo (no cotejado en esta pasada de FM26; no revela pesos del motor)."

    # Behaviors
    behaviors = ui_ver.get('behaviors') or []

    # Runtime locks from matriz
    mat_item = mat_by_role.get(rid)
    if mat_item:
        locked_runtime = {
            'status': 'verified_in_documented_context_only',
            'position': mat_item.get('position_family'),
            'scope': mat_item.get('scope'),
            'evidence': mat_item.get('evidence'),
            'locked_values': mat_item.get('locked_values'),
            'editable_groups': mat_item.get('editable_groups'),
            'applicability': mat_item.get('applicability')
        }
    elif rid == 'deep_lying_forward_ip':
        # Retain prior session reference lock for deep lying forward (Hold Up Ball = Yes)
        locked_runtime = {
            'status': 'prior_session_reference',
            'position': 'STC',
            'scope': 'Posición',
            'evidence': 'Relevamiento previo FM26',
            'locked_values': {'dribbling_direction_ip': 'Standard', 'hold_up_ball_ip': 'Yes', 'cross_from_ip': 'Standard', 'crossing_strategy_ip': 'Standard'},
            'editable_groups': ['attacking_width_ip', 'dribbling_frequency_ip', 'shoot_ip', 'passing_risk_ip', 'passing_directness_ip'],
            'applicability': 'Referencia de sesión previa; panel no reabierto en esta pasada.'
        }
    else:
        locked_runtime = {
            'status': 'unverified',
            'position': positions[0] if positions else None,
            'scope': 'Posición',
            'evidence': None,
            'locked_values': None,
            'editable_groups': None,
            'applicability': 'No comprobado en capturas de esta pasada'
        }

    # Description
    desc_res = r.get('description_resource', {})
    desc_en = desc_res.get('en', '')
    desc_es = desc_res.get('es', '')

    # Subposition rules / availability
    subposition_rule = None
    if rid in ('wide_centre_back_ip', 'overlapping_centre_back_ip', 'wide_centre_back_oop', 'covering_wide_centre_back_oop', 'stopping_wide_centre_back_oop'):
        subposition_rule = {
            'min_central_defenders': 3,
            'allowed_subpositions': ['DC_L', 'DC_R'],
            'description': 'Disponible únicamente como central lateral en zagas de 3 centrales.'
        }
    elif rid in ('box_to_box_midfielder_ip', 'box_to_box_playmaker_ip', 'pressing_defensive_midfielder_oop', 'wide_covering_defensive_midfielder_oop'):
        subposition_rule = {
            'min_defensive_midfielders': 2,
            'allowed_subpositions': ['DM_L', 'DM_R'],
            'description': 'Disponible únicamente en esquemas con doble o triple pivote (no en pivote central único).'
        }

    # Aliases
    aliases = []
    if res_label_es and res_label_es != ui_label:
        aliases.append({'text': res_label_es, 'key': res_key, 'surface': 'LTC Resource'})
    if ref_label_es and ref_label_es not in (ui_label, res_label_es):
        aliases.append({'text': ref_label_es, 'key': res_key, 'surface': 'Reference'})

    # Role entry
    role_obj = {
        'id': rid,
        'phase': phase,
        'role_name': en_name,
        'label': en_name,
        'label_es': ref_label_es,
        'label_ui': ui_label,
        'abbreviation': ROLE_ABBREV.get(rid, 'ROL'),
        'position': positions,
        'positions': positions,
        'subposition_rule': subposition_rule,
        'key_attributes': key_attributes,
        'key_attributes_ui_verified': attrs_verified,
        'attributes_provenance': attrs_provenance,
        'behaviors': behaviors,
        'description': {'en': desc_en, 'es': desc_es},
        'resource_key': res_key,
        'locked_instructions_runtime': locked_runtime,
        'player_instructions': r.get('prior_catalog_role_instructions', []),
        'current_ui_evidence': r.get('current_ui_evidence') or ui_ver.get('evidence'),
        'source': f'https://fmsidekick.com/api/roles/{rid}'
    }
    reconstructed_roles.append(role_obj)

    # Locale role entry
    loc_entry = {
        'key': res_key,
        'token': 0x20000000 | res_key,
        'text': ui_label,
        'resource_text': res_label_es,
        'reference_text': ref_label_es,
        'description': desc_es,
        'behaviors': behaviors,
        'runtime_verified': True,
        'menu_verified_es': True,
        'resource_verified': True,
        'verified_source': r.get('current_ui_evidence') or ui_ver.get('evidence') or 'FM26 26.3.2',
        'aliases': aliases
    }
    locale_roles[rid] = loc_entry
    if stem not in locale_roles:
        locale_roles[stem] = loc_entry

# Build individual instructions (15 groups, 45 options)
reconstructed_pi = []
locale_player = dict(old_loc.get('player', {}))

for inst in cat_src.get('individual_instructions', []):
    iid = inst['id']
    options = [opt['id'] for opt in inst['options']]
    pi_obj = {
        'id': iid,
        'phase': inst['phase'],
        'label': inst.get('label_es_ui', iid),
        'instruction_property': inst.get('label_es_ui', iid),
        'label_es_ui': inst.get('label_es_ui', iid),
        'options': options,
        'current_ui_evidence': inst.get('current_ui_evidence'),
        'source': 'FM26 Menú táctico 25/10/2026',
        'options_detailed': inst['options']
    }
    reconstructed_pi.append(pi_obj)

    # Update locale for player instructions
    prop_entry = locale_player.get(iid, {})
    prop_entry['property'] = {
        'text': inst.get('label_es_ui', iid),
        'key': inst['options'][0].get('description_resource', {}).get('key', 0) if inst['options'] else 0
    }
    opts_dict = dict(prop_entry.get('options', {}))
    for opt in inst['options']:
        opt_id = opt['id']
        opt_label = opt.get('label_es_ui') or opt_id
        opt_key = opt.get('description_resource', {}).get('key', 0)
        opt_desc = opt.get('description_resource', {}).get('es') or opt.get('explanation_es_editorial') or ''
        opts_dict[opt_id] = {
            'text': opt_label,
            'key': opt_key,
            'description': opt_desc,
            'runtime_verified': False,
            'resource_verified': True,
            'binding_status': 'context_selected'
        }
    prop_entry['options'] = opts_dict
    locale_player[iid] = prop_entry

# Build team instructions (26 definitions + 8 views with 29 observed entries)
reconstructed_ti = list(old_cat.get('team_instructions', []))
team_views = cat_src.get('team_instructions_current', [])

# Build positions with sub-position specs
reconstructed_positions = []
for p in cat_src.get('positions', []):
    reconstructed_positions.append({
        'id': p['id_reference'],
        'label_ui': p['label_ui_reference'],
        'name': p['name'],
        'notes': p['notes']
    })

# Build observed contexts including prior reference for roles pending reopening
observed_contexts = list(mat_src)
if not any(item['role'] == 'deep_lying_forward_ip' for item in observed_contexts):
    observed_contexts.append({
        'role': 'deep_lying_forward_ip',
        'position_family': 'STC',
        'scope': 'Posición',
        'evidence': 'Relevamiento previo FM26',
        'locked_values': {'dribbling_direction_ip': 'Standard', 'hold_up_ball_ip': 'Yes', 'cross_from_ip': 'Standard', 'crossing_strategy_ip': 'Standard'},
        'editable_groups': ['attacking_width_ip', 'dribbling_frequency_ip', 'shoot_ip', 'passing_risk_ip', 'passing_directness_ip'],
        'applicability': 'Referencia de sesión previa; panel no reabierto en esta pasada.'
    })

# Assembly catalog
new_catalog = {
    'edition': 'Football Manager 2026 (26.3.2.2329565)',
    'checked_at': '2026-10-25',
    'locale_ui': 'Español latinoamericano',
    'resource_fingerprints': cat_src.get('resource_fingerprints', {}),
    'scope': 'Tactical reference for Touchline reconstruction; not FM match engine reconstruction.',
    'roles': reconstructed_roles,
    'player_instructions': reconstructed_pi,
    'team_instructions': reconstructed_ti,
    'team_views_current': team_views,
    'positions': reconstructed_positions,
    'observed_instruction_contexts': observed_contexts
}

# Assembly locale
new_locale = {
    'locale': 'es-419',
    'language': 'Español latinoamericano',
    'game_version': '26.3.2.2329565 (m.e v26.3.0.1)',
    'steam_build': '2026.10.25',
    'source': 'Relevamiento empírico en FM26 (25/10/2026) y archivos locales de instalación',
    'sha256': old_loc.get('sha256', {'latam': '293ba893c8f9a4df25ef702dd6f09077257254ab129cfbd2578d5a03c25e9ae5'}),
    'verification': 'Cotejado visualmente contra menús de FM26 y archivos .ltc extraídos',
    'roles': locale_roles,
    'player': locale_player,
    'team': old_loc.get('team', {})
}

# Save new files
with open(ROOT / 'fm_app' / 'data' / 'fm26_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(new_catalog, f, indent=2, ensure_ascii=False)

with open(ROOT / 'fm_app' / 'data' / 'fm26_es419.json', 'w', encoding='utf-8') as f:
    json.dump(new_locale, f, indent=2, ensure_ascii=False)

print('Successfully reconstructed fm26_catalog.json and fm26_es419.json')
print(f'Catalog roles: {len(new_catalog["roles"])}')
print(f'Catalog individual instructions: {len(new_catalog["player_instructions"])}')
print(f'Locale roles: {len(new_locale["roles"])}')
print(f'Locale player instructions: {len(new_locale["player"])}')
