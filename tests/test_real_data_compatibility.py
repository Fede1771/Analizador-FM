"""Compatibility verification using isolated copies of real imported FM26 career data.

Original files in data/imports/ and data/ are never modified or overwritten.
All operations run inside an isolated temporary directory.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fm_app.dataset import load_dataset
from fm_app.recommendations import analyze, simulate_formation
from fm_app.current_tactic import audit_tactic
from fm_app.contracts import validate_overrides
from fm_app.fm26 import TI, ROLES


class RealDataCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real_import_dir = ROOT / 'data' / 'imports' / 'f3e1b2a01d114dec8357197394a9810f'
        if not cls.real_import_dir.exists():
            # Fallback to any directory in data/imports/ with output/validation.json
            candidates = list((ROOT / 'data' / 'imports').glob('*/output/validation.json'))
            if candidates:
                cls.real_import_dir = candidates[0].parent.parent
            else:
                cls.real_import_dir = None

    def setUp(self):
        if not self.real_import_dir or not self.real_import_dir.exists():
            self.skipTest('No real import folder found in data/imports/')
        # Create an isolated temporary directory for copy
        self.temp_dir = tempfile.TemporaryDirectory(prefix='touchline-real-compat-')
        self.isolated_path = Path(self.temp_dir.name)
        # Copy output folder and import.json safely
        source_output = self.real_import_dir / 'output'
        target_output = self.isolated_path / 'output'
        shutil.copytree(source_output, target_output)
        if (self.real_import_dir / 'import.json').exists():
            shutil.copy2(self.real_import_dir / 'import.json', self.isolated_path / 'import.json')

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_real_dataset_load_and_data_integrity(self):
        """Verifies loading real user dataset copy without modifying original."""
        dataset = load_dataset(self.isolated_path / 'output')
        self.assertEqual(dataset['club'], 'Liverpool')
        self.assertGreater(len(dataset['players']), 20)
        self.assertEqual(dataset['career_id'], '051db1d54748fb7778ca3ec1')
        self.assertEqual(dataset['date'], '2028-09-14')

        # Check loan players loaded
        self.assertIn('loans', dataset)
        self.assertIsInstance(dataset['loans'], list)

        # Check stored tactics loaded
        self.assertIn('stored_tactics', dataset)
        self.assertTrue(dataset['stored_tactics']['available'])
        self.assertGreater(len(dataset['stored_tactics']['records']), 0)

        # Check collective instruction options has all 28 dimensions
        self.assertEqual(len(dataset['instruction_options']), 28)
        self.assertEqual(len(dataset['tactic_editor']['team_properties']), 28)

    def test_real_dataset_analysis_and_simulation(self):
        """Verifies analysis engine on real Liverpool squad produces valid proposals."""
        dataset = load_dataset(self.isolated_path / 'output')
        result = analyze(dataset, style='possession')
        self.assertIn('tactics', result)
        self.assertEqual(len(result['tactics']), 3)

        top_tactic = result['tactics'][0]
        self.assertEqual(len(top_tactic['lineup']), 11)
        self.assertGreater(top_tactic['score'], 50.0)

        # 25 coverage zones calculated in both phases
        self.assertEqual(len(top_tactic['coverage']['phases']['ip']), 25)
        self.assertEqual(len(top_tactic['coverage']['phases']['oop']), 25)

        # Instructions list has all 28 dimensions
        self.assertEqual(len(top_tactic['instructions']), 28)

        # Simulation on alternative formation (e.g. 433)
        sim = simulate_formation(dataset, '433', style='press')
        self.assertEqual(len(sim['lineup']), 11)
        self.assertEqual(len(sim['instructions']), 28)

    def test_real_dataset_custom_tactic_draft_audit_and_persistence(self):
        """Verifies auditing and persisting a real tactic using real Liverpool player UIDs."""
        dataset = load_dataset(self.isolated_path / 'output')
        squad = dataset['players']

        # Pick 11 real players from the Liverpool squad
        eleven = squad[:11]
        lineup = []
        for i, p in enumerate(eleven):
            lineup.append({
                'uid': p['uid'],
                'ip_position': 'GK' if i == 0 else ('DC' if i in (1, 2) else ('DL' if i == 3 else ('DR' if i == 4 else ('MC' if i in (5, 6, 7) else 'STC')))),
                'oop_position': 'GK' if i == 0 else ('DC' if i in (1, 2) else ('DL' if i == 3 else ('DR' if i == 4 else ('MC' if i in (5, 6, 7) else 'STC')))),
                'ip_role': 'goalkeeper_ip' if i == 0 else ('centre_back_ip' if i in (1, 2) else ('full_back_ip' if i in (3, 4) else ('central_midfielder_ip' if i in (5, 6, 7) else 'centre_forward_ip'))),
                'oop_role': 'goalkeeper_oop' if i == 0 else ('centre_back_oop' if i in (1, 2) else ('full_back_oop' if i in (3, 4) else ('central_midfielder_oop' if i in (5, 6, 7) else 'centre_forward_oop'))),
                'instructions': {}
            })

        plan = {
            'confirmed': True,
            'name': 'Mi Táctica Liverpool Real',
            'style': 'possession',
            'lineup': lineup,
            'team': {
                'tempo': 'Lower',
                'passing_directness': 'Shorter',
                'attacking_width_ip': 'Standard',
                'overlap_ip': 'Overlap - Balanced',
                'underlap_ip': 'Underlap - Balanced',
                'tackling_oop': 'Standard'
            }
        }

        # Audit tactic on real squad
        result = audit_tactic(dataset, plan)
        self.assertEqual(result['name'], 'Mi Táctica Liverpool Real')
        self.assertEqual(len(result['lineup']), 11)
        self.assertGreater(result['score'], 0)

        # Save audited draft to isolated temp file and re-read
        draft_file = self.isolated_path / 'tactic_draft_real.json'
        draft_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

        reopened = json.loads(draft_file.read_text(encoding='utf-8'))
        self.assertEqual(reopened['name'], result['name'])
        self.assertEqual(len(reopened['lineup']), 11)
        self.assertEqual(reopened['score'], result['score'])

    def test_real_dataset_collective_restrictions_and_overrides(self):
        """Verifies collective instruction restrictions and overrides against real squad."""
        dataset = load_dataset(self.isolated_path / 'output')

        # Valid overrides
        valid_overrides = {
            'tempo': 'Much Lower',
            'passing_directness': 'Much Shorter',
            'attacking_width_ip': 'Much Narrower',
            'underlap_ip': 'Underlap - Both Flanks',
            'overlap_ip': 'Overlap - Balanced'
        }
        checked = validate_overrides(valid_overrides)
        self.assertEqual(checked['underlap_ip'], 'Underlap - Both Flanks')

        # Incompatible overrides
        invalid_overrides = {
            'underlap_ip': 'Underlap - Both Flanks',
            'overlap_ip': 'Overlap - Both Flanks'
        }
        with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
            validate_overrides(invalid_overrides)


if __name__ == '__main__':
    unittest.main()
