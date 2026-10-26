import json
from pathlib import Path

survey_dir = Path('docs/relevamiento-fm26-2026-10-25')
vc = json.load(open(survey_dir / 'verificacion-colectivas.json', encoding='utf-8'))
cat = json.load(open('fm_app/data/fm26_catalog.json', encoding='utf-8'))
loc = json.load(open('fm_app/data/fm26_es419.json', encoding='utf-8'))

ti_by_id = {t['id']: t for t in cat.get('team_instructions', [])}
ti_loc = loc.get('team', {})

CONTROL_TO_CAT_ID = {
    'passing_directness': 'passing_directness',
    'tempo': 'tempo',
    'attacking_transition': 'attacking_transition_ip',
    'creative_freedom': 'creative_freedom_ip',
    'time_wasting': 'time_wasting',
    'play_for_set_pieces': 'play_for_set_pieces_ip',
    'dribbling': 'dribbling_ip',
    'patience': 'patience_ip',
    'shots_from_distance': 'shots_from_distance_ip',
    'crossing_style': 'crossing_style_ip',
    'progress_through': 'progress_through_ip',
    'pass_reception': 'pass_reception_ip',
    'build_up_strategy': 'build_up_strategy_ip',
    'goal_kicks': 'goal_kicks_ip',
    'gk_distribution_speed': 'gk_distribution_speed_ip',
    'gk_distribution_target': 'gk_distribution_ip',
    'cross_engagement': 'cross_engagement_oop',
    'line_of_engagement': 'line_of_engagement_oop',
    'defensive_line': 'defensive_line_oop',
    'defensive_line_behavior': 'defensive_line_behaviour_oop',
    'trigger_press': 'trigger_press_oop',
    'defensive_transition': 'defensive_transition_oop',
    'pressing_trap': 'pressing_trap_oop',
    'prevent_short_gk_distribution': 'short_goalkeeper_distribution_oop'
}

for c_key, cat_id in CONTROL_TO_CAT_ID.items():
    vc_ctrl = vc['controls'][c_key]
    ti = ti_by_id.get(cat_id)
    l_entry = ti_loc.get(cat_id, {})
    prop_text = l_entry.get('property', {}).get('text')
    expected_prop = vc_ctrl['label_ui']
    
    # compare options
    cat_opts = ti.get('options', [])
    loc_opts = [l_entry.get('options', {}).get(o, {}).get('text') for o in cat_opts]
    vc_opts = vc_ctrl.get('options_ui', [])
    
    diffs = []
    if prop_text != expected_prop:
        diffs.append(f"Prop mismatch: '{prop_text}' vs expected '{expected_prop}'")
    for o_cat, o_loc, o_vc in zip(cat_opts, loc_opts, vc_opts):
        if o_loc != o_vc:
            diffs.append(f"Opt '{o_cat}': '{o_loc}' vs expected '{o_vc}'")
    
    if diffs:
        print(f"[{c_key}] ({cat_id}):")
        for d in diffs:
            print(f"   {d}")
    else:
        print(f"[{c_key}] OK - Label and all {len(vc_opts)} options match exactly.")

# Also check support_runs (overlap_ip, underlap_ip)
sr = vc['controls']['support_runs']
print("\n[support_runs]:")
for dim_key, cat_id in [('overlap', 'overlap_ip'), ('underlap', 'underlap_ip')]:
    dim_ctrl = sr['dimensions'][dim_key]
    ti = ti_by_id.get(cat_id)
    l_entry = ti_loc.get(cat_id, {})
    prop_text = l_entry.get('property', {}).get('text')
    expected_prop = dim_ctrl['label_ui']
    cat_opts = ti.get('options', [])
    loc_opts = [l_entry.get('options', {}).get(o, {}).get('text') for o in cat_opts]
    vc_opts = dim_ctrl.get('options_ui', [])
    diffs = []
    if prop_text != expected_prop:
        diffs.append(f"Prop: '{prop_text}' vs '{expected_prop}'")
    for o_cat, o_loc, o_vc in zip(cat_opts, loc_opts, vc_opts):
        if o_loc != o_vc:
            diffs.append(f"Opt '{o_cat}': '{o_loc}' vs '{o_vc}'")
    if diffs:
        print(f" {dim_key} ({cat_id}): {diffs}")
    else:
        print(f" {dim_key} ({cat_id}): OK")
