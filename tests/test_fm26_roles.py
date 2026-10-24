from copy import deepcopy
from pathlib import Path
import unittest

from fm_app.analysis import STYLES, analyze
from fm_app.fm26 import ROLES, PI, TI, ENGINE_VERSION, LOCALE, instruction
from fm_app.recommendations import choose, profile
from fm_app.server import ROOT, load_dataset
from test_analysis import player
from fixtures import dataset as fixture_dataset


class FM26RoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=fixture_dataset()

    def test_all_real_players_have_two_explained_phases_in_every_style(self):
        for style in STYLES:
            result=analyze(self.data,style)
            self.assertEqual(len(result['profiles']),len(self.data['players'])+len(self.data['loans']))
            for p in self.data['players']+self.data['loans']:
                prof=result['profiles'][p['uid']]
                for key,phase in [('in_possession','in_possession'),('out_of_possession','out_of_possession')]:
                    r=prof[key]
                    self.assertEqual(ROLES[r['id']]['phase'],phase)
                    self.assertIn(r['position'],ROLES[r['id']]['positions'])
                    self.assertEqual(r['english'],ROLES[r['id']]['english'])
                    self.assertTrue(r['reasons'])
                    self.assertIn('/20',r['reasons'][0])
                    self.assertTrue(r['comparison'])
                    self.assertTrue(r['source'].startswith('https://'))
                    self.assertTrue(r['menu_verified_es'])
                    self.assertTrue(r['localization']['resource_verified'])
                    self.assertTrue(r['localization']['runtime_verified'])
                    self.assertEqual(r['localization']['locale'],'es-419')
                    self.assertEqual(r['name'],r['localization']['text'])
                    for i in r['instructions']:
                        self.assertIn(i['value_en'],PI[i['id']]['options'])
                        self.assertEqual(i['phase'],phase)
                        self.assertEqual(i['localization']['locale'],'es-419')
                        self.assertEqual(i['value'],i['localization']['value']['text'])
                        self.assertEqual(i['property'],i['localization']['property']['text'])

    def test_lineup_roles_match_formation_positions_and_phases(self):
        for style in STYLES:
            result=analyze(self.data,style)
            for t in result['tactics']:
                for l in t['lineup']:
                    for key in ('in_possession','out_of_possession'):
                        r=l[key]
                        self.assertIn(r['position'],ROLES[r['id']]['positions'])
                    # A Winger at AML must become an M(L) role when defending in 4-1-4-1.
                    if t['id']=='433' and l['in_possession']['position']=='AML':
                        self.assertEqual(l['out_of_possession']['position'],'ML')
                        self.assertIn(l['out_of_possession']['id'],('wide_midfielder_oop','tracking_wide_midfielder_oop'))
                for i in t['instructions']:
                    self.assertIn(i['value_en'],TI[i['id']]['options'])
                    self.assertTrue(i['localization']['value']['resource_verified'])
                    self.assertEqual(i['value'],i['localization']['value']['text'])

    def test_latam_roles_keep_distinct_meanings_and_context_variants(self):
        keeper=ROLES['ball_playing_goalkeeper_ip']
        self.assertEqual(keeper['name'],'Portero con salida')
        self.assertEqual(keeper['localization']['key'],688113)
        self.assertTrue(keeper['menu_verified_es'])
        self.assertIn('Portero jugador',[a['text'] for a in keeper['localization']['aliases']])
        self.assertEqual(ROLES['deep_lying_forward_ip']['name'],'Delantero de apoyo')
        self.assertEqual(ROLES['second_striker_ip']['name'],'Segundo delantero')
        for role in ROLES.values():
            self.assertNotIn('[%',role['name'])
            self.assertEqual(role['localization']['token'] & 0xfffffff,role['localization']['key'])
        self.assertEqual(LOCALE['language'],'Español latinoamericano')
        self.assertEqual(len(LOCALE['sha256']['latam']),64)

    def test_instruction_labels_are_specific_to_player_team_and_property(self):
        def ins(kind,key,value):return instruction(kind,key,value,'test')
        self.assertEqual(ins('player','passing_risk_ip','Take More Risks')['property'],'Riesgo en los pases')
        self.assertEqual(ins('player','forward_runs_ip','Make More Runs')['property'],'Carreras hacia adelante')
        self.assertEqual(ins('player','pressing_oop','More Often')['value'],'Más a menudo')
        self.assertEqual(ins('team','trigger_press_oop','More Often')['value'],'Más insistente')
        self.assertEqual(ins('team','tempo','Lower')['value'],'Más bajo')
        self.assertEqual(ins('team','defensive_line_oop','Lower')['value'],'Más baja')
        # LATAM is literally "Alto" at this key; Spain's translation is "Alta".
        self.assertEqual(ins('team','defensive_line_oop','Higher')['value'],'Alto')
        self.assertEqual(ins('player','tackling_oop','Standard')['value'],'Normal')
        self.assertEqual(ins('player','hold_up_ball_ip','Yes')['value'],'Sí')
        self.assertEqual(ins('player','hold_up_ball_ip','No')['value'],'No')
        self.assertEqual(ins('player','hold_up_ball_ip','Yes')['localization']['value']['binding_status'],'context_selected')
        self.assertEqual(ins('player','hold_up_ball_ip','No')['localization']['value']['binding_status'],'context_selected')
        self.assertEqual(ins('team','defensive_line_oop','Standard')['value'],'Estándar')
        for kind in ('player','team'):
            for key,group in LOCALE[kind].items():
                for value in group['options']:
                    output=ins(kind,key,value)
                    self.assertNotIn('[%',output['value'])
                    self.assertFalse(output['menu_verified_es'])
                    self.assertFalse(output['localization']['value']['runtime_verified'])
        with self.assertRaises((KeyError,ValueError)):
            ins('player','passing_risk_ip','Counter-Press')
        with self.assertRaises(ValueError):
            ins('other','tempo','Standard')

    def test_no_old_role_duties_or_conflicting_passing_risk(self):
        result=analyze(self.data)
        for prof in result['profiles'].values():
            r=prof['in_possession']; defaults=ROLES[r['id']]['player_instructions']
            risks=[i for i in r['instructions'] if i['id']=='passing_risk_ip']
            self.assertEqual(len(risks),1)
            if 'Take More Risks' in defaults:
                self.assertEqual(risks[0]['value_en'],'Take More Risks')
                self.assertEqual(risks[0]['origin'],'role')
            if 'Take Fewer Risks' in defaults:
                self.assertEqual(risks[0]['value_en'],'Take Fewer Risks')
        self.assertFalse(any(r.startswith('stopping_centre_back') for r in ROLES))

    def test_weak_goalkeeper_is_not_given_risky_ball_playing_role(self):
        p=player(1,'gk',10)
        chosen=choose(p,'ip','GK','possession')
        self.assertNotEqual(chosen['id'],'ball_playing_goalkeeper_ip')

    def test_pressing_role_requires_physical_capacity(self):
        p=player(1,'mc',16)
        p['attributes']['stamina']=8
        p['attributes']['work_rate']=8
        self.assertNotEqual(choose(p,'oop','MC','press')['id'],'pressing_central_midfielder_oop')

    def test_training_and_reasons_respond_to_changed_player_attributes(self):
        p=player(1,'stc',12,slot=1,age=17)
        before=profile(p,'counter')
        p=deepcopy(p)
        p['attributes'].update(finishing=18,anticipation=18,off_the_ball=18,acceleration=18,composure=18)
        after=profile(p,'counter')
        self.assertGreater(after['score'],before['score'])
        self.assertNotEqual(after['in_possession']['reasons'],before['in_possession']['reasons'])


    def test_tactical_prompt_and_natural_role_comparison(self):
        prompt = 'quiero jugar con mucha posesion e intentar tener muchas cahcnes de gol y evitar que me rematen mucho al arco'
        result = analyze(self.data, prompt=prompt)
        self.assertIsNotNone(result['prompt_analysis'])
        self.assertEqual(len(result['prompt_analysis']['pillars']), 3)
        self.assertEqual(len(result['tactics']), 3)
        for t in result['tactics']:
            self.assertIn(t['rank'], (1, 2, 3))
            self.assertIn(t['id'], {f['id'] for f in self.data['formations_catalog']})
            for l in t['lineup']:
                self.assertTrue(l['natural_role'])
                self.assertIn(l['role_matches_natural'], (True, False))
                self.assertTrue(l['individual_instructions'])
        ti = {i['id']: i['value_en'] for i in result['tactics'][0]['instructions']}
        self.assertEqual(ti['passing_directness'], 'Shorter')
        self.assertEqual(ti['tempo'], 'Lower')
        self.assertEqual(ti['line_of_engagement_oop'], 'Mid Block')


if __name__=='__main__':
    unittest.main()
