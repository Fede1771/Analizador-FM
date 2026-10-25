from copy import deepcopy
import unittest
from unittest.mock import patch, Mock, MagicMock
from dataclasses import dataclass
import sys

from fixtures import dataset
from fm_app.current_tactic import audit_tactic, extract_stored_tactics
from fm_app.fm26 import ROLES, PI, PLAYER_MENU, SCREENSHOT_LOCKS, player_instructions
from fm_app.recommendations import simulate_formation
from fm_app.spatial import coverage
import app_desktop


class CurrentTacticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=dataset();cls.proposal=simulate_formation(cls.data,formation_id='433')

    def plan(self):
        return {'confirmed':True,'style':'possession','name':'Actual', 'lineup':[{
            'uid':r['uid'],'ip_position':r['in_possession']['position'],'oop_position':r['out_of_possession']['position'],
            'ip_role':r['in_possession']['id'],'oop_role':r['out_of_possession']['id'],'instructions':{}}
            for r in self.proposal['lineup']]}

    def test_audit_keeps_user_players_roles_and_unconfirmed_orders(self):
        plan=self.plan();result=audit_tactic(self.data,plan)
        self.assertEqual([r['uid'] for r in result['lineup']],[r['uid'] for r in plan['lineup']])
        for before,after in zip(plan['lineup'],result['lineup']):
            self.assertEqual(after['in_possession']['id'],before['ip_role'])
            for phase in ('in_possession','out_of_possession'):
                self.assertTrue(all(i['origin']=='role' for i in after[phase]['instructions']))
        self.assertGreater(result['unconfirmed_player_instructions'],0)
        self.assertGreater(result['unconfirmed_team_instructions'],0)

    def test_invalid_or_unconfirmed_plans_are_rejected(self):
        for mutate in (
            lambda p:p.update(confirmed=False),
            lambda p:p['lineup'].pop(),
            lambda p:p['lineup'][1].update(uid=p['lineup'][0]['uid']),
            lambda p:p['lineup'][1].update(ip_role='goalkeeper_ip'),
            lambda p:p['lineup'][1].update(oop_role='centre_back_ip'),
            lambda p:p['lineup'][1].update(instructions={'passing_risk_ip':'invalid'}),
            lambda p:p.update(team={'tempo':'invalid'}),
            lambda p:p.update(stored_id='does-not-exist')):
            with self.subTest(mutate=mutate):
                plan=self.plan();mutate(plan)
                with self.assertRaises(ValueError):audit_tactic(self.data,plan)

    def test_individual_role_locks_cannot_be_contradicted(self):
        plan=self.plan();row=next(r for r in plan['lineup'] if r['ip_position']=='DC')
        row['ip_role']='centre_back_ip';row['instructions']={'forward_runs_ip':'Make More Runs'}
        with self.assertRaisesRegex(ValueError,'bloqueada'):audit_tactic(self.data,plan)

    def test_confirmed_collective_line_height_changes_only_oop_map(self):
        plan=self.plan();a=audit_tactic(self.data,plan)
        plan['team']={'defensive_line_oop':'Higher'};b=audit_tactic(self.data,plan)
        self.assertEqual(a['coverage']['phases']['ip'],b['coverage']['phases']['ip'])
        self.assertNotEqual(a['coverage']['phases']['oop'],b['coverage']['phases']['oop'])

    def test_current_role_is_not_silently_optimized(self):
        plan=self.plan();row=next(r for r in plan['lineup'] if r['ip_position']=='STC')
        row['ip_role']='deep_lying_forward_ip';result=audit_tactic(self.data,plan)
        after=next(r for r in result['lineup'] if r['uid']==row['uid'])
        self.assertEqual(after['in_possession']['id'],'deep_lying_forward_ip')
        self.assertEqual(next(i for i in after['in_possession']['instructions'] if i['id']=='hold_up_ball_ip')['value_en'],'Yes')

    def test_complete_outfield_menu_and_observed_locks(self):
        p=self.data['players'][2]
        for role in ROLES.values():
            instructions=player_instructions(p,role)
            self.assertEqual([i['id'] for i in instructions],PLAYER_MENU[role['phase']])
            for i in instructions:
                self.assertIn(i['value_en'],PI[i['id']]['options'])
            for key,value in SCREENSHOT_LOCKS.get(role['id'],{}).items():
                item=next(i for i in instructions if i['id']==key)
                self.assertTrue(item['locked']);self.assertEqual(item['value_en'],value)

    def test_zone_estimate_responds_to_instructions_and_retains_identity(self):
        plan=self.plan();row=next(r for r in plan['lineup'] if r['ip_position']=='AML')
        row['ip_role']='inside_winger_ip';row['instructions']={'dribbling_direction_ip':'Standard'}
        a=audit_tactic(self.data,plan);row['instructions']['dribbling_direction_ip']='Cut Inside With Ball'
        b=audit_tactic(self.data,plan)
        self.assertNotEqual(a['coverage']['phases']['ip'],b['coverage']['phases']['ip'])
        self.assertEqual(a['coverage']['phases']['oop'],b['coverage']['phases']['oop'])
        allowed={r['uid'] for r in plan['lineup'] if r['ip_position']!='GK'}
        for cells in b['coverage']['phases'].values():
            self.assertEqual(len(cells),25)
            for cell in cells:
                self.assertLessEqual(cell['strength'],100)
                self.assertEqual(len({p['uid'] for p in cell['players']}),len(cell['players']))
                self.assertTrue({p['uid'] for p in cell['players']}<=allowed)

    def test_liverpool_reference_has_all_confirmed_team_instructions(self):
        from fm_app.dataset import LIVERPOOL_REF
        self.assertIsNotNone(LIVERPOOL_REF)
        self.assertEqual(LIVERPOOL_REF['screenshots_count'], 30)
        self.assertEqual(len(LIVERPOOL_REF['team_screenshots']), 8)
        self.assertEqual(len(LIVERPOOL_REF['team']), 26)
        plan = self.plan()
        plan['team'] = dict(LIVERPOOL_REF['team'])
        result = audit_tactic(self.data, plan)
        self.assertEqual(result['unconfirmed_team_instructions'], 0)


class DesktopTests(unittest.TestCase):
    def test_second_launch_activates_without_opening_browser(self):
        with patch.object(sys,'argv',['app_desktop.py']),patch.object(app_desktop,'configure_logging'),patch.object(app_desktop,'check_existing_instance',return_value=True),patch.object(app_desktop,'activate_existing_instance') as activate,patch.object(app_desktop.webbrowser,'open') as browser,patch.object(app_desktop,'create_app_server') as server:
            app_desktop.main();activate.assert_called_once_with(8765);browser.assert_not_called();server.assert_not_called()

    def test_native_profile_preserves_local_tactic_drafts(self):
        server=Mock();server.server_port=8765;server.watcher=None
        webview=MagicMock()
        with patch.object(sys,'argv',['app_desktop.py']),patch.object(sys,'platform','test'),patch.object(app_desktop,'configure_logging'),patch.object(app_desktop,'check_existing_instance',return_value=False),patch.object(app_desktop,'find_free_port',return_value=8765),patch.object(app_desktop,'create_app_server',return_value=server),patch.dict(sys.modules,{'webview':webview}):
            app_desktop.main()
            self.assertFalse(webview.start.call_args.kwargs['private_mode'])
            self.assertEqual(webview.start.call_args.kwargs['storage_path'],str(app_desktop.ROOT/'data/webview'))

    def test_webview_failure_does_not_open_an_additional_browser(self):
        server=Mock();server.server_port=8765;server.watcher=None
        webview=Mock();webview.create_window.side_effect=RuntimeError('WebView failed')
        with patch.object(sys,'argv',['app_desktop.py']),patch.object(sys,'platform','test'),patch.object(app_desktop,'configure_logging'),patch.object(app_desktop,'check_existing_instance',return_value=False),patch.object(app_desktop,'find_free_port',return_value=8765),patch.object(app_desktop,'create_app_server',return_value=server),patch.object(app_desktop.webbrowser,'open') as browser,patch.dict(sys.modules,{'webview':webview}):
            with self.assertRaisesRegex(RuntimeError,'WebView failed'):app_desktop.main()
            browser.assert_not_called();server.state.close.assert_called_once()


if __name__=='__main__':unittest.main()
