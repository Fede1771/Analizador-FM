import json
from pathlib import Path

survey_dir = Path('docs/relevamiento-fm26-2026-10-25')
vc = json.load(open(survey_dir / 'verificacion-colectivas.json', encoding='utf-8'))
cat = json.load(open('fm_app/data/fm26_catalog.json', encoding='utf-8'))
loc = json.load(open('fm_app/data/fm26_es419.json', encoding='utf-8'))

ti_by_id = {t['id']: t for t in cat.get('team_instructions', [])}
ti_loc = loc.get('team', {})

print(f"{'CONTROL':<30} | {'CAT_ID':<32} | {'OPTS MATCH?':<12} | {'LOCALE?':<8}")
print("-" * 88)

# Mapping between verificacion-colectivas control key and catalog team instruction id
CONTROL_TO_CAT_ID = {
    'passing_directness': 'passing_directness',
    'tempo': 'tempo',
    'attacking_width': 'attacking_width_ip', # or attacking_width
    'attacking_transition': 'attacking_transition_ip',
    'creative_freedom': 'creative_freedom_ip',
    'time_wasting': 'time_wasting',
    'play_for_set_pieces': 'play_for_set_pieces_ip',
    'dribbling': 'dribbling_ip',
    'patience': 'patience_ip',
    'shots_from_distance': 'shots_from_distance_ip',
    'crossing_style': 'crossing_style_ip',
    'support_runs': 'support_runs', # dimensions: overlap_ip, underlap_ip
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
    'tackling': 'tackling_oop',
    'pressing_trap': 'pressing_trap_oop',
    'prevent_short_gk_distribution': 'short_goalkeeper_distribution_oop'
}

for c_key, c_val in vc['controls'].items():
    cat_id = CONTROL_TO_CAT_ID.get(c_key, c_key)
    if c_key == 'support_runs':
        # Check both overlap_ip and underlap_ip
        o_exists = 'overlap_ip' in ti_by_id
        u_exists = 'underlap_ip' in ti_by_id
        print(f"{c_key:<30} | overlap_ip & underlap_ip       | {str(o_exists and u_exists):<12} | {str('overlap_ip' in ti_loc and 'underlap_ip' in ti_loc):<8}")
        continue
    
    ti = ti_by_id.get(cat_id) or ti_by_id.get(c_key)
    actual_id = ti['id'] if ti else 'MISSING'
    opts_ok = 'N/A'
    if ti:
        cat_opts = ti.get('options', [])
        vc_opts = c_val.get('options_ui', [])
        opts_ok = f"{len(cat_opts)}=={len(vc_opts)}"
    has_loc = str((cat_id in ti_loc) or (c_key in ti_loc))
    print(f"{c_key:<30} | {actual_id:<32} | {opts_ok:<12} | {has_loc:<8}")
