"""Patch recommendations.py and test_fm26_roles.py for subposition restrictions and stopping_centre_back."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 1. Patch recommendations.py
rec_path = ROOT / 'fm_app' / 'recommendations.py'
rec_text = rec_path.read_text(encoding='utf-8')

target_rec = "    if phase=='ip' and kind=='cb':"
replacement_rec = """    if position == 'DC' and kind not in ('wcb', 'wide_cb'):
        ids = [r for r in ids if not ('wide_centre_back' in r or 'overlapping_centre_back' in r)]
    if position == 'DM' and kind not in ('dm_dual', 'dm_pair', 'box_to_box', 'wide_covering'):
        ids = [r for r in ids if not ('box_to_box' in r or r.startswith('pressing_') or r.startswith('wide_covering_'))]
    if phase=='ip' and kind=='cb':"""

if target_rec in rec_text:
    rec_text = rec_text.replace(target_rec, replacement_rec, 1)
    rec_path.write_text(rec_text, encoding='utf-8')
    print('Updated recommendations.py')

# 2. Patch test_fm26_roles.py line 115
test_roles_path = ROOT / 'tests' / 'test_fm26_roles.py'
test_roles_text = test_roles_path.read_text(encoding='utf-8')

target_test = "self.assertFalse(any(r.startswith('stopping_centre_back') for r in ROLES))"
replacement_test = "self.assertIn('stopping_centre_back_oop', ROLES)\n        self.assertEqual(ROLES['stopping_centre_back_oop']['name'], 'Zaguero')"

if target_test in test_roles_text:
    test_roles_text = test_roles_text.replace(target_test, replacement_test, 1)
    test_roles_path.write_text(test_roles_text, encoding='utf-8')
    print('Updated test_fm26_roles.py')
