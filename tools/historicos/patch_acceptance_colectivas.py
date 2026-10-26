path = 'tests/test_reconstruction_acceptance.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read().replace('\r\n', '\n')

old_tail = """        self.assertEqual(result['lineup'][1]['in_possession']['id'], 'wide_centre_back_ip')


if __name__ == '__main__':
    unittest.main()"""

new_tail = """        self.assertEqual(result['lineup'][1]['in_possession']['id'], 'wide_centre_back_ip')

    def test_criterion_12_collective_selectors_quantities_and_options(self):
        """ + '"""12. 27 selectores colectivos y 28 dimensiones de valor verificadas, con cantidades reales de opciones."""' + """
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
        """ + '"""13. Regate y Trampa de presión tienen una sola fuente de estado para sus respectivas subfases."""' + """
        from fm_app.fm26 import CATALOG
        cat_rules = CATALOG.get('collective_rules', {})
        shared = {c['control']: c['areas'] for c in cat_rules.get('shared_controls', [])}
        self.assertIn('dribbling_ip', shared)
        self.assertEqual(shared['dribbling_ip'], ['Avance', 'Último tercio'])
        self.assertIn('pressing_trap_oop', shared)
        self.assertEqual(shared['pressing_trap_oop'], ['Presión adelantada', 'Bloque medio'])

    def test_criterion_14_support_runs_two_axes_and_incompatibilities(self):
        """ + '"""14. Carreras de apoyo tiene dos ejes independientes y valida las incompatibilidades comprobadas."""' + """
        self.assertIn('overlap_ip', TI)
        self.assertIn('underlap_ip', TI)
        plan = self.make_plan_433()

        # Incompatibility 1: underlap both flanks + overlap non-balanced
        plan['team'] = {'underlap_ip': 'Underlap - Both Flanks', 'overlap_ip': 'Overlap - Left'}
        with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
            audit_tactic(self.data, plan)

        # Incompatibility 2: overlap both flanks + underlap non-balanced
        plan['team'] = {'overlap_ip': 'Overlap - Both Flanks', 'underlap_ip': 'Underlap - Right'}
        with self.assertRaisesRegex(ValueError, 'Carreras de apoyo'):
            audit_tactic(self.data, plan)

        # Both Balanced is valid
        plan['team'] = {'underlap_ip': 'Underlap - Balanced', 'overlap_ip': 'Overlap - Balanced'}
        res = audit_tactic(self.data, plan)
        self.assertIsNotNone(res)

        # Single flank each (not both flanks) remains unblocked (unverified combinations not extrapolated)
        plan['team'] = {'underlap_ip': 'Underlap - Left', 'overlap_ip': 'Overlap - Right'}
        res = audit_tactic(self.data, plan)
        self.assertIsNotNone(res)

    def test_criterion_15_opposition_gk_distribution_distinguished_from_own(self):
        """ + '"""15. La salida del portero rival (prevent_short_gk) se distingue de la distribución propia (gk_distribution)."""' + """
        # Own goalkeeper distribution (CP)
        self.assertEqual(TI['gk_distribution_ip']['category'], 'in_possession')
        self.assertEqual(TI['gk_distribution_speed_ip']['category'], 'in_possession')
        self.assertEqual(TI['goal_kicks_ip']['category'], 'in_possession')

        # Opposition goalkeeper distribution (SP)
        self.assertEqual(TI['short_goalkeeper_distribution_oop']['category'], 'out_of_possession')
        self.assertEqual(TI['short_goalkeeper_distribution_oop']['options'], ['No', 'Yes'])


if __name__ == '__main__':
    unittest.main()"""

assert old_tail in text, "old_tail not found"
with open(path, 'w', encoding='utf-8') as f:
    f.write(text.replace(old_tail, new_tail))
print('Updated tests/test_reconstruction_acceptance.py with criteria 12-15')
