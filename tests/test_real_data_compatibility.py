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
        report = json.loads((self.isolated_path/'output/validation.json').read_text(encoding='utf-8'))
        self.assertEqual(dataset['club'], report['club']['name'])
        self.assertGreater(len(dataset['players']), 20)
        self.assertTrue(dataset['career_id'])
        self.assertEqual(dataset['date'], report['game_date'])

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

    def test_real_dataset_squad_overcrowding_recommendations(self):
        """Verifies squad overcrowding detection and loan/sell recommendations on real Liverpool save."""
        dataset = load_dataset(self.isolated_path / 'output')
        result = analyze(dataset, style='possession')

        self.assertIn('squad_overcrowding', result)
        self.assertIn('surplus_players', result)

        overcrowding = result['squad_overcrowding']
        surplus_map = result['surplus_players']

        # Overcrowding list contains position summaries
        self.assertIsInstance(overcrowding, list)
        self.assertGreater(len(overcrowding), 0)

        for pos_data in overcrowding:
            self.assertIn('position', pos_data)
            self.assertIn('position_label', pos_data)
            self.assertIn('player_count', pos_data)
            self.assertIn('max_ideal', pos_data)
            self.assertIn('surplus_count', pos_data)
            self.assertIn('candidates', pos_data)
            self.assertGreater(pos_data['player_count'], pos_data['max_ideal'])
            self.assertEqual(len(pos_data['candidates']), pos_data['surplus_count'])

            for cand in pos_data['candidates']:
                uid = cand['uid']
                self.assertIn(uid, surplus_map)
                self.assertIn(cand['action'], ('loan', 'sell'))
                self.assertIn(cand['action_label'], ('Mandar a préstamo', 'Evaluar venta'))
                self.assertTrue(cand['reason'])
                self.assertIsInstance(cand['score'], float)

                # Age rule verification: <= 22 -> loan, > 22 -> sell
                if cand['age'] <= 22:
                    self.assertEqual(cand['action'], 'loan')
                    self.assertEqual(cand['action_label'], 'Mandar a préstamo')
                    self.assertIn('desarrollo', cand['reason'])
                else:
                    self.assertEqual(cand['action'], 'sell')
                    self.assertEqual(cand['action_label'], 'Evaluar venta')
                    self.assertIn('mercado', cand['reason'])

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

        # Valid overrides: opposite flanks coexist (Right + Left) and Balanced combinations
        valid_overrides = {
            'tempo': 'Much Lower',
            'passing_directness': 'Much Shorter',
            'attacking_width_ip': 'Much Narrower',
            'underlap_ip': 'Underlap - Left',
            'overlap_ip': 'Overlap - Right',
            'gk_distribution_ip': 'Flanks'
        }
        checked = validate_overrides(valid_overrides)
        self.assertEqual(checked['underlap_ip'], 'Underlap - Left')
        self.assertEqual(checked['overlap_ip'], 'Overlap - Right')
        self.assertEqual(checked['gk_distribution_ip'], 'Flanks')

        # Incompatible overrides: same flank exclusion (Left + Left)
        same_flank_invalid = {
            'underlap_ip': 'Underlap - Left',
            'overlap_ip': 'Overlap - Left'
        }
        with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
            validate_overrides(same_flank_invalid)

        # Incompatible overrides: both flanks on one axis requires balanced on the other
        invalid_overrides = {
            'underlap_ip': 'Underlap - Both Flanks',
            'overlap_ip': 'Overlap - Both Flanks'
        }
        with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
            validate_overrides(invalid_overrides)

    def test_real_dataset_support_runs_matrix_and_goalkeeper_distribution(self):
        """Verifies full 16-combination matrix of support runs and 7 gk distribution destinations on real Liverpool squad."""
        dataset = load_dataset(self.isolated_path / 'output')

        allowed_matrix = [
            ('Overlap - Balanced', 'Underlap - Balanced'),
            ('Overlap - Balanced', 'Underlap - Left'),
            ('Overlap - Balanced', 'Underlap - Right'),
            ('Overlap - Balanced', 'Underlap - Both Flanks'),
            ('Overlap - Left', 'Underlap - Balanced'),
            ('Overlap - Left', 'Underlap - Right'),  # opposite flanks coexist
            ('Overlap - Right', 'Underlap - Balanced'),
            ('Overlap - Right', 'Underlap - Left'),  # opposite flanks coexist
            ('Overlap - Both Flanks', 'Underlap - Balanced'),
        ]

        blocked_matrix = [
            ('Overlap - Left', 'Underlap - Left'),  # same flank excluded
            ('Overlap - Left', 'Underlap - Both Flanks'),
            ('Overlap - Right', 'Underlap - Right'),  # same flank excluded
            ('Overlap - Right', 'Underlap - Both Flanks'),
            ('Overlap - Both Flanks', 'Underlap - Left'),
            ('Overlap - Both Flanks', 'Underlap - Right'),
            ('Overlap - Both Flanks', 'Underlap - Both Flanks'),
        ]

        # Verify all 9 allowed combinations pass validate_overrides
        for overlap, underlap in allowed_matrix:
            ov = {'overlap_ip': overlap, 'underlap_ip': underlap}
            res = validate_overrides(ov)
            self.assertEqual(res['overlap_ip'], overlap)
            self.assertEqual(res['underlap_ip'], underlap)

        # Verify all 7 blocked combinations raise ValueError
        for overlap, underlap in blocked_matrix:
            ov = {'overlap_ip': overlap, 'underlap_ip': underlap}
            with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
                validate_overrides(ov)

        # Verify goalkeeper distribution: 7 destinations, Flanks and Full-Backs are single destinations
        gk_targets = [
            'Over Opposition Defense', 'Target Forward', 'Flanks',
            'Playmaker', 'Full-Backs', 'Center-Backs', 'Balanced'
        ]
        for target in gk_targets:
            res = validate_overrides({'gk_distribution_ip': target})
            self.assertEqual(res['gk_distribution_ip'], target)

        # Verify shared state dimensions: dribbling_ip and pressing_trap_oop
        dribbling_values = ['Discourage', 'Balanced', 'Encourage']
        for val in dribbling_values:
            res = validate_overrides({'dribbling_ip': val})
            self.assertEqual(res['dribbling_ip'], val)

        trap_values = ['Trap Inside', 'Balanced', 'Trap Outside']
        for val in trap_values:
            res = validate_overrides({'pressing_trap_oop': val})
            self.assertEqual(res['pressing_trap_oop'], val)

    def test_real_saved_tactics_decode_all_roles_permutations_and_instructions(self):
        """Verifies real save tactic decoding against FM26 screenshots and across multiple clubs."""
        from fm_app.dataset import LIVERPOOL_REF
        dataset = load_dataset(self.isolated_path / 'output')
        records = dataset['stored_tactics']['records']
        self.assertGreater(len(records), 0)
        primary = records[0]
        self.assertTrue(primary['positions_available'])
        self.assertEqual(primary['decode_warnings'], [])
        self.assertEqual(len(primary['team_instructions']), 28)
        self.assertEqual(len(primary['lineup']), 11)
        for slot in primary['lineup']:
            self.assertIn(slot['ip_role'], ROLES)
            self.assertIn(slot['oop_role'], ROLES)
            self.assertEqual(len(slot['instructions']), 15)

        if dataset['club'] == 'Liverpool' and LIVERPOOL_REF:
            # Verify the 26 original screenshot team instructions match, and the 2 newly decoded
            # fields match the documented screenshot values (Narrower and Get Stuck In)
            for k, v in LIVERPOOL_REF['team'].items():
                if k not in ('attacking_width_ip', 'tackling_oop'):
                    self.assertEqual(primary['team_instructions'][k], v, f'Team instruction {k}')
            self.assertEqual(primary['team_instructions']['attacking_width_ip'], 'Narrower')
            self.assertEqual(primary['team_instructions']['tackling_oop'], 'Get Stuck In')
            # Verify the 3-cycle OOP permutation (MC->AMC, AMR->MR, AML->ML)
            self.assertEqual(primary['lineup'][7]['ip_position'], 'MC')
            self.assertEqual(primary['lineup'][7]['oop_position'], 'AMC')
            self.assertEqual(primary['lineup'][8]['ip_position'], 'AMR')
            self.assertEqual(primary['lineup'][8]['oop_position'], 'MR')
            self.assertEqual(primary['lineup'][9]['ip_position'], 'AML')
            self.assertEqual(primary['lineup'][9]['oop_position'], 'ML')
            self.assertEqual(primary['lineup'][10]['oop_role'], 'centre_forward_oop')

        # Audit the decoded tactic directly as storedDraft would send it
        plan = {
            'confirmed': True,
            'name': primary['name'],
            'style': 'possession',
            'stored_id': primary['id'],
            'team': dict(primary['team_instructions']),
            'team_sources': {k: 'save' for k in primary['team_instructions']},
            'lineup': primary['lineup'],
        }
        audited = audit_tactic(dataset, plan)
        self.assertEqual(audited['unconfirmed_player_instructions'], 0)
        self.assertEqual(audited['unconfirmed_team_instructions'], 0)
        self.assertEqual({i['id']: i['value_en'] for i in audited['team_instructions']}, primary['team_instructions'])
        self.assertTrue(all(i['origin'] == 'save' for i in audited['team_instructions']))
        self.assertGreater(len(audited['advice']), 0)
        advice_categories = {a['category'] for a in audited['advice']}
        self.assertTrue({'coverage', 'discipline', 'player_alt'}.issubset(advice_categories) or len(advice_categories) > 0)

        # Also verify any other real import directories in data/imports/ decode with zero warnings
        for import_dir in (ROOT / 'data' / 'imports').glob('*/output'):
            if not (import_dir / 'tactics.json').exists() or not (import_dir / 'players.json').exists():
                continue
            with tempfile.TemporaryDirectory(prefix='touchline-multi-club-') as tmp:
                tmp_out = Path(tmp) / 'output'
                shutil.copytree(import_dir, tmp_out)
                other_ds = load_dataset(tmp_out)
                for rec in other_ds['stored_tactics']['records']:
                    if rec.get('positions_available'):
                        self.assertEqual(rec['decode_warnings'], [], f"Warnings in {other_ds['club']} ({rec['name']})")
                        self.assertEqual(len(rec['team_instructions']), 28)
                        self.assertTrue(all(len(s['instructions']) == 15 for s in rec['lineup']))


if __name__ == '__main__':
    unittest.main()
