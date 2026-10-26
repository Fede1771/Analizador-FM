from copy import deepcopy
import unittest

from fixtures import dataset
from fm_app.contracts import analysis_parameters, validate_preferences
from fm_app.current_tactic import audit_tactic
from fm_app.fm26 import ROLES, OBSERVED_CONTEXTS, player_instructions, team_instructions
from fm_app.instruction_rules import context_matches, position_context
from fm_app.recommendations import simulate_formation


class InstructionContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = dataset()
        proposal = simulate_formation(cls.data, '433')
        cls.plan = {'confirmed': True, 'style': 'possession', 'lineup': [{
            'uid': r['uid'], 'ip_position': r['in_possession']['position'],
            'oop_position': r['out_of_possession']['position'],
            'ip_role': r['in_possession']['id'], 'oop_role': r['out_of_possession']['id'],
            'instructions': {}} for r in proposal['lineup']]}

    def test_partial_overrides_are_checked_after_merging_style_and_prompt(self):
        base = {'dataset_id': self.data['id'], 'style': 'press', 'overrides': {'underlap_ip': 'Underlap - Left'}}
        with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
            analysis_parameters(base, self.data)
        with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
            validate_preferences(base, self.data)
        with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
            simulate_formation(self.data, '433', style='press', overrides=base['overrides'])
        with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
            team_instructions(self.data['players'][:11], 'press', base['overrides'])
        with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
            analysis_parameters({**base, 'style': 'possession', 'prompt': 'Presión alta, recuperar rápido'}, self.data)
        valid = {**base, 'overrides': {'overlap_ip': 'Overlap - Right', 'underlap_ip': 'Underlap - Left', 'tempo': 'Lower'}}
        self.assertEqual(analysis_parameters(valid, self.data)['overrides'], valid['overrides'])

    def test_role_evidence_does_not_certify_other_positions_or_scopes(self):
        role = ROLES['playmaking_wing_back_ip']
        player = self.data['players'][4]
        for position, scope, locked in [('DR', 'Posición', True), ('WBL', 'Posición', None), ('DR', 'Personalizada', None)]:
            with self.subTest(position=position, scope=scope):
                context = position_context([position], 0, scope)
                item = next(i for i in player_instructions(player, role, context) if i['id'] == 'hold_up_ball_ip')
                self.assertIs(item['locked'], locked)
                self.assertEqual(item['availability_status'], 'locked_verified' if locked else 'unverified')
        self.assertTrue(all(i['availability_status'] == 'unverified' for i in player_instructions(player, role)))

    def test_side_and_number_of_players_are_part_of_the_observation(self):
        observed = OBSERVED_CONTEXTS['wide_centre_back_ip']
        self.assertTrue(context_matches(observed, position_context(['DC']*3, 2)))
        self.assertFalse(context_matches(observed, position_context(['DC']*3, 0)))
        self.assertFalse(context_matches(observed, position_context(['DC']*2, 1)))
        dm = OBSERVED_CONTEXTS['box_to_box_midfielder_ip']
        self.assertTrue(context_matches(dm, position_context(['DM']*2, 1)))
        self.assertFalse(context_matches(dm, position_context(['DM'], 0)))

    def test_current_audit_preserves_unverified_custom_values(self):
        plan = deepcopy(self.plan)
        row = plan['lineup'][4]
        row.update(ip_position='WBL', ip_role='playmaking_wing_back_ip', instruction_scope='Personalizada',
                   instructions={'hold_up_ball_ip': 'Yes'})
        result = audit_tactic(self.data, plan)
        item = next(i for i in result['lineup'][4]['in_possession']['instructions'] if i['id'] == 'hold_up_ball_ip')
        self.assertEqual(item['value_en'], 'Yes')
        self.assertEqual(item['availability_status'], 'unverified')
        row.update(ip_position='DR', instruction_scope='Posición')
        with self.assertRaisesRegex(ValueError, 'bloqueada'):
            audit_tactic(self.data, plan)
        row['instructions'] = {}
        result = audit_tactic(self.data, plan)
        item = next(i for i in result['lineup'][4]['in_possession']['instructions'] if i['id'] == 'hold_up_ball_ip')
        self.assertEqual(item['value_en'], 'No')
        self.assertEqual(item['availability_status'], 'locked_verified')

    def test_unverified_context_does_not_fill_in_missing_orders(self):
        plan = deepcopy(self.plan)
        row = plan['lineup'][4]
        row.update(ip_position='WBL', ip_role='playmaking_wing_back_ip', instruction_scope='Posición')
        result = audit_tactic(self.data, plan)
        self.assertEqual(result['lineup'][4]['in_possession']['instructions'], [])


if __name__ == '__main__':
    unittest.main()
