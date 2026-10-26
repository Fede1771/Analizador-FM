"""Acceptance test suite for FM26 empirical reconstruction and verification."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import unittest
from fixtures import dataset
from fm_app.current_tactic import audit_tactic
from fm_app.fm26 import ROLES, PI, TI, SCREENSHOT_LOCKS, EDITABLE_GROUPS, PLAYER_MENU, player_instructions
from fm_app.recommendations import simulate_formation, role_score
from fm_app.tactics import STYLES


class FM26ReconstructionAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = dataset()
        cls.proposal_433 = simulate_formation(cls.data, formation_id='433')
        cls.proposal_352 = simulate_formation(cls.data, formation_id='352')

    def make_plan_433(self):
        return {
            'confirmed': True,
            'style': 'possession',
            'name': 'Plan 433',
            'lineup': [
                {
                    'uid': r['uid'],
                    'ip_position': r['in_possession']['position'],
                    'oop_position': r['out_of_possession']['position'],
                    'ip_role': r['in_possession']['id'],
                    'oop_role': r['out_of_possession']['id'],
                    'instructions': {}
                }
                for r in self.proposal_433['lineup']
            ]
        }

    def test_criterion_1_unified_carrilero_organizador(self):
        """1. El catálogo mantiene un único Carrilero organizador CP con varias familias compatibles, evitando duplicados por rótulo."""
        carrilero = ROLES['playmaking_wing_back_ip']
        self.assertEqual(carrilero['name'], 'Carrilero organizador')
        self.assertIn('DL', carrilero['positions'])
        self.assertIn('DR', carrilero['positions'])
        self.assertIn('WBL', carrilero['positions'])
        self.assertIn('WBR', carrilero['positions'])
        # Ensure no duplicate old role exists
        self.assertNotIn('playmaking_wing_back_ip_d_l_r', ROLES)
        self.assertEqual(len(ROLES), 79)

    def test_criterion_2_same_player_dual_phase_retains_identity(self):
        """2. El mismo jugador puede ser MC CP y AMC SP, o AML CP y ML SP, sin duplicar su identidad."""
        plan = self.make_plan_433()
        # Change player 6 (an interior) to MC in CP and AMC in SP
        row = plan['lineup'][6]
        row['ip_position'] = 'MC'
        row['ip_role'] = 'central_midfielder_ip'
        row['oop_position'] = 'MC'
        row['oop_role'] = 'pressing_central_midfielder_oop'

        # Change player 8 (winger) to AML in CP and ML in SP
        row_wing = plan['lineup'][8]
        row_wing['ip_position'] = 'AML'
        row_wing['ip_role'] = 'inside_winger_ip'
        row_wing['oop_position'] = 'ML'
        row_wing['oop_role'] = 'wide_midfielder_oop'

        result = audit_tactic(self.data, plan)
        player_entry = next(e for e in result['lineup'] if e['uid'] == row_wing['uid'])
        self.assertEqual(player_entry['uid'], row_wing['uid'])
        self.assertEqual(player_entry['in_possession']['position'], 'AML')
        self.assertEqual(player_entry['out_of_possession']['position'], 'ML')

    def test_criterion_3_more_direct_passing_directness_valid_end_to_end(self):
        """3. La longitud Más directo se conserva y valida de extremo a extremo."""
        self.assertIn('More Direct', PI['passing_directness_ip']['options'])
        plan = self.make_plan_433()
        plan['lineup'][0]['instructions'] = {'passing_directness_ip': 'More Direct'}
        result = audit_tactic(self.data, plan)
        keeper_plan = result['lineup'][0]
        direct_inst = next(i for i in keeper_plan['in_possession']['instructions'] if i['id'] == 'passing_directness_ip')
        self.assertEqual(direct_inst['value_en'], 'More Direct')
        self.assertEqual(direct_inst['value'], 'Más directo')

    def test_criterion_4_unresolved_locks_remain_none(self):
        """4. Los tres valores antes tapados por ayudas emergentes quedaron confirmados visualmente en No con candado."""
        p = self.data['players'][2]
        for rid in ('wide_centre_back_ip', 'overlapping_centre_back_ip', 'box_to_box_midfielder_ip'):
            r = ROLES[rid]
            instructions = player_instructions(p, r)
            hold = next(i for i in instructions if i['id'] == 'hold_up_ball_ip')
            self.assertTrue(hold['locked'])
            self.assertEqual(hold['locked_value'], 'No')
            self.assertEqual(hold['value_en'], 'No')
            self.assertEqual(hold['value'], 'No')

    def test_criterion_5_marking_targets_validation(self):
        """5. Marca específica requiere rival identificado; Marcar posición requiere puesto rival identificado."""
        plan = self.make_plan_433()
        # Try Mark Specific without target player
        plan['lineup'][2]['instructions'] = {'marking_target_oop': 'Mark Specific'}
        with self.assertRaisesRegex(ValueError, 'rival a marcar'):
            audit_tactic(self.data, plan)

        # Now supply target player
        plan['lineup'][2]['marking_target_player'] = 'Haaland'
        result = audit_tactic(self.data, plan)
        self.assertIsNotNone(result)

        # Try Mark Position without position
        plan['lineup'][2]['instructions'] = {'marking_target_oop': 'Mark Position'}
        with self.assertRaisesRegex(ValueError, 'puesto rival a cubrir'):
            audit_tactic(self.data, plan)

        # Supply target position
        plan['lineup'][2]['marking_target_position'] = 'STC'
        result = audit_tactic(self.data, plan)
        self.assertIsNotNone(result)

    def test_criterion_6_modified_vs_locked_controls(self):
        """6. Un control modificado permanece distinto de un control bloqueado. Las restricciones no se extienden a contextos no comprobados."""
        p = self.data['players'][2]
        # Ball playing goalkeeper locks passing_risk_ip to Take More Risks
        bpg = ROLES['ball_playing_goalkeeper_ip']
        bpg_insts = player_instructions(p, bpg)
        risk = next(i for i in bpg_insts if i['id'] == 'passing_risk_ip')
        self.assertTrue(risk['locked'])
        self.assertFalse(risk['editable'])
        self.assertEqual(risk['value_en'], 'Take More Risks')

        # But passing_directness_ip is verified editable
        direct = next(i for i in bpg_insts if i['id'] == 'passing_directness_ip')
        self.assertFalse(direct['locked'])
        self.assertTrue(direct['editable'])

        # For false_nine_ip, forward_runs_ip is locked while passing_directness_ip is editable
        fn = ROLES['false_nine_ip']
        fn_insts = player_instructions(p, fn)
        fn_runs = next(i for i in fn_insts if i['id'] == 'forward_runs_ip')
        self.assertTrue(fn_runs['locked'])
        self.assertFalse(fn_runs['editable'])
        fn_dir = next(i for i in fn_insts if i['id'] == 'passing_directness_ip')
        self.assertFalse(fn_dir['locked'])
        self.assertTrue(fn_dir['editable'])

        # Context-dependent locks are not universally extended: mock role without context remains unverified
        unverified_mock_role = {'id': 'custom_unverified_role_ip', 'phase': 'in_possession', 'positions': ['STC'], 'player_instructions': []}
        mock_insts = player_instructions(p, unverified_mock_role)
        for i in mock_insts:
            self.assertIsNone(i['locked'])
            self.assertIsNone(i['editable'])
            self.assertIn('Disponibilidad no comprobada', i['availability_source'])

    def test_criterion_7_bpg_and_sweeper_keeper_evidence(self):
        """7. El menú de Portero con salida permite las dos dimensiones editables observadas y conserva las restricciones documentadas. El de Portero líbero no bloquea Entradas por inferencia."""
        p = self.data['players'][2]
        bpg = ROLES['ball_playing_goalkeeper_ip']
        bpg_insts = player_instructions(p, bpg)
        editable_ids = [i['id'] for i in bpg_insts if i['editable']]
        self.assertIn('dribbling_frequency_ip', editable_ids)
        self.assertIn('passing_directness_ip', editable_ids)

        sk = ROLES['sweeper_keeper_oop']
        sk_insts = player_instructions(p, sk)
        tackling = next(i for i in sk_insts if i['id'] == 'tackling_oop')
        # Tackling is not locked on Sweeper Keeper!
        self.assertFalse(tackling['locked'])
        self.assertTrue(tackling['editable'])

    def test_criterion_8_three_cross_concepts_separated(self):
        """8. Centro desde, destino de centros y estilo colectivo de centros son tres conceptos separados."""
        # 1. cross_from_ip: individual, origin of cross
        self.assertIn('Cross From Deep', PI['cross_from_ip']['options'])
        self.assertIn('Byline', PI['cross_from_ip']['options'])

        # 2. crossing_strategy_ip: individual, target destination of cross
        self.assertIn('Far Post', PI['crossing_strategy_ip']['options'])
        self.assertIn('Target Forward', PI['crossing_strategy_ip']['options'])

        # 3. crossing_style_ip: collective team instruction
        self.assertIn('crossing_style_ip', TI)
        self.assertIn('Whipped Crosses', TI['crossing_style_ip']['options'])
        self.assertIn('Low Crosses', TI['crossing_style_ip']['options'])

    def test_criterion_9_spanish_aliases_system(self):
        """9. La UI conserva los alias españoles sin usar la etiqueta traducida como clave de datos."""
        keeper = ROLES['ball_playing_goalkeeper_ip']
        self.assertEqual(keeper['name'], 'Portero con salida')
        alias_texts = [a['text'] for a in keeper['localization']['aliases']]
        self.assertIn('Portero jugador', alias_texts)

        zaguero = ROLES['stopping_centre_back_oop']
        self.assertEqual(zaguero['name'], 'Zaguero')

    def test_criterion_10_transparent_touchline_evaluation_limits(self):
        """10. La evaluación explica qué viene de atributos, qué viene de la táctica y qué es una regla propia."""
        plan = self.make_plan_433()
        result = audit_tactic(self.data, plan)
        self.assertIn('80% CP / 20% SP', result['limits'])
        self.assertIn('propia de Touchline', result['limits'])
        self.assertIn('No representa probabilidades deportivas ni pesos internos', result['limits'])

    def test_criterion_11_subposition_restrictions(self):
        """11. Central abierto y Central que dobla exigen una línea de al menos 3 centrales en FM26."""
        plan = self.make_plan_433()
        # In 4-3-3 there are only 2 CBs
        plan['lineup'][2]['ip_role'] = 'wide_centre_back_ip'
        with self.assertRaisesRegex(ValueError, '3 centrales'):
            audit_tactic(self.data, plan)

        # In 3-5-2 with 3 CBs, wide_centre_back_ip is permitted!
        plan_352 = {
            'confirmed': True,
            'style': 'possession',
            'name': 'Plan 352',
            'lineup': [
                {
                    'uid': r['uid'],
                    'ip_position': r['in_possession']['position'],
                    'oop_position': r['out_of_possession']['position'],
                    'ip_role': r['in_possession']['id'],
                    'oop_role': r['out_of_possession']['id'],
                    'instructions': {}
                }
                for r in self.proposal_352['lineup']
            ]
        }
        # In 3-5-2, slots 1, 2, 3 are DC
        plan_352['lineup'][1]['ip_role'] = 'wide_centre_back_ip'
        result = audit_tactic(self.data, plan_352)
        self.assertIsNotNone(result)
        self.assertEqual(result['lineup'][1]['in_possession']['id'], 'wide_centre_back_ip')

    def test_criterion_12_collective_selectors_quantities_and_options(self):
        """12. 27 selectores colectivos y 28 dimensiones de valor verificadas, con cantidades reales de opciones."""
        self.assertEqual(len(TI), 28)
        # 5 levels
        for key in ('tempo', 'passing_directness', 'attacking_width_ip', 'defensive_line_oop', 'trigger_press_oop'):
            self.assertEqual(len(TI[key]['options']), 5, f"{key} must have 5 levels")
        # 4 crossing styles
        self.assertEqual(len(TI['crossing_style_ip']['options']), 4)
        # 2 play for set pieces options (no standard 3rd value)
        self.assertEqual(len(TI['play_for_set_pieces_ip']['options']), 2)
        self.assertNotIn('Standard', TI['play_for_set_pieces_ip']['options'])

    def test_criterion_13_shared_collective_state_controls(self):
        """13. Regate y Trampa de presión tienen una sola fuente de estado para sus respectivas subfases."""
        from fm_app.fm26 import CATALOG
        cat_rules = CATALOG.get('collective_rules', {})
        shared = {c['control']: c['areas'] for c in cat_rules.get('shared_controls', [])}
        self.assertIn('dribbling_ip', shared)
        self.assertEqual(shared['dribbling_ip'], ['Avance', 'Último tercio'])
        self.assertIn('pressing_trap_oop', shared)
        self.assertEqual(shared['pressing_trap_oop'], ['Presión adelantada', 'Bloque medio'])

    def test_criterion_14_support_runs_two_axes_and_incompatibilities(self):
        """14. Carreras de apoyo tiene dos ejes independientes y valida la matriz completa de 16 combinaciones comprobadas."""
        self.assertIn('overlap_ip', TI)
        self.assertIn('underlap_ip', TI)
        plan = self.make_plan_433()

        allowed_combinations = [
            ('Overlap - Balanced', 'Underlap - Balanced'),
            ('Overlap - Balanced', 'Underlap - Left'),
            ('Overlap - Balanced', 'Underlap - Right'),
            ('Overlap - Balanced', 'Underlap - Both Flanks'),
            ('Overlap - Left', 'Underlap - Balanced'),
            ('Overlap - Left', 'Underlap - Right'),  # costados opuestos coexisten
            ('Overlap - Right', 'Underlap - Balanced'),
            ('Overlap - Right', 'Underlap - Left'),  # costados opuestos coexisten
            ('Overlap - Both Flanks', 'Underlap - Balanced'),
        ]

        blocked_combinations = [
            ('Overlap - Left', 'Underlap - Left'),  # mismo costado excluyente
            ('Overlap - Left', 'Underlap - Both Flanks'),
            ('Overlap - Right', 'Underlap - Right'),  # mismo costado excluyente
            ('Overlap - Right', 'Underlap - Both Flanks'),
            ('Overlap - Both Flanks', 'Underlap - Left'),
            ('Overlap - Both Flanks', 'Underlap - Right'),
            ('Overlap - Both Flanks', 'Underlap - Both Flanks'),
        ]

        # Verify all 9 allowed combinations pass
        for overlap, underlap in allowed_combinations:
            plan['team'] = {'overlap_ip': overlap, 'underlap_ip': underlap}
            res = audit_tactic(self.data, plan)
            self.assertIsNotNone(res, f"Failed for allowed combination ({overlap}, {underlap})")

        # Verify all 7 blocked combinations raise ValueError
        for overlap, underlap in blocked_combinations:
            plan['team'] = {'overlap_ip': overlap, 'underlap_ip': underlap}
            with self.assertRaisesRegex(ValueError, 'Carreras de apoyo', msg=f"Should fail for blocked combination ({overlap}, {underlap})"):
                audit_tactic(self.data, plan)

    def test_criterion_15_opposition_gk_distribution_distinguished_from_own(self):
        """15. La salida del portero rival (prevent_short_gk) se distingue de la distribución propia (gk_distribution)."""
        # Own goalkeeper distribution (CP)
        self.assertEqual(TI['gk_distribution_ip']['category'], 'in_possession')
        self.assertEqual(TI['gk_distribution_speed_ip']['category'], 'in_possession')
        self.assertEqual(TI['goal_kicks_ip']['category'], 'in_possession')

        # Opposition goalkeeper distribution (SP)
        self.assertEqual(TI['short_goalkeeper_distribution_oop']['category'], 'out_of_possession')
        self.assertEqual(TI['short_goalkeeper_distribution_oop']['options'], ['No', 'Yes'])


if __name__ == '__main__':
    unittest.main()
