import json
from pathlib import Path

survey_dir = Path('docs/relevamiento-fm26-2026-10-25')
vc = json.load(open(survey_dir / 'verificacion-colectivas.json', encoding='utf-8'))
cat = json.load(open('fm_app/data/fm26_catalog.json', encoding='utf-8'))
loc = json.load(open('fm_app/data/fm26_es419.json', encoding='utf-8'))

print('Controls in verificacion-colectivas:', len(vc['controls']))
for k, v in vc['controls'].items():
    opts = len(v.get('options_ui', []))
    dims = list(v.get('dimensions', {}).keys())
    print(f"  {k}: label='{v['label_ui']}', opts={opts}, dims={dims}")

print('\nExisting team_instructions in fm26_catalog.json:', len(cat.get('team_instructions', [])))
for ti in cat.get('team_instructions', []):
    print(f"  {ti['id']}: prop='{ti['instruction_property']}', opts={len(ti['options'])} -> {ti['options']}")
