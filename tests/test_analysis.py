import itertools
import json
from pathlib import Path
import unittest

from fm_app.analysis import ATTRS, ROLES, analyze, assignment, role_score
from fm_app.recommendations import simulate_formation
from fm_app.server import load_dataset, ROOT
from fixtures import dataset as fixture_dataset


def player(uid, position, value=12, slot=0, age=20):
    return {'uid':uid,'name':str(uid),'team_slot':slot,'age':age,
            'attributes':{k:value for k in ATTRS},
            'positions':{p:20 if p==position else 1 for p in ('gk','sw','dl','dc','dr','dm','ml','mc','mr','aml','amc','amr','stc','wbl','wbr')}}


class AnalysisTests(unittest.TestCase):
    def test_assignment_is_global_and_unique(self):
        players=[player(1,'stc',16),player(2,'mc',15),player(3,'gk',14),player(4,'mc',12)]
        slots=[{'role':'centre_forward_ip','defend':'centre_forward_ip'},{'role':'central_midfielder_ip','defend':'central_midfielder_ip'},{'role':'goalkeeper_ip','defend':'goalkeeper_ip'}]
        total,chosen=assignment(players,slots,'possession')
        exhaustive=max(sum(role_score(p,s['role']) for p,s in zip(permutation,slots)) for permutation in itertools.permutations(players,3))
        self.assertAlmostEqual(total,exhaustive)
        self.assertEqual(len({uid for _,uid,_ in chosen}),3)

    def test_unfamiliar_seniors_do_not_inflate_youth_readiness(self):
        senior=player(1,'stc',16)
        other=[player(2,'gk',18),player(3,'dc',18)]
        youth=player(4,'stc',12,slot=1,age=17)
        result=analyze({'players':[senior,*other,youth],'loans':[]})
        entry=result['academy'][0]
        self.assertEqual(len(entry['comparison']),1)
        self.assertLess(entry['gap'],-3)
        self.assertEqual(entry['action'],'Desarrollar en inferiores')

    def test_no_familiar_reference_is_explicit(self):
        result=analyze({'players':[player(1,'gk'),player(2,'stc',slot=1)],'loans':[]})
        self.assertIsNone(result['academy'][0]['gap'])
        self.assertEqual(result['academy'][0]['action'],'Sin referencia')

    def test_insufficient_players_and_exclusions(self):
        rows=[player(i,'mc') for i in range(11)]
        result=analyze({'players':rows,'loans':[]},excluded=[0])
        self.assertEqual(result['tactics'],[])
        self.assertEqual(result['senior_count'],10)

    def test_hidden_data_is_not_exposed_to_frontend(self):
        dataset=fixture_dataset()
        for p in dataset['players']+dataset['loans']:
            self.assertNotIn('ability',p)
            self.assertNotIn('personality',p)
            self.assertNotIn('consistency',p['attributes'])
            self.assertEqual(set(p['attributes']),set(ATTRS))
        self.assertEqual(len(dataset['players']),26)
        self.assertEqual(len(dataset['loans']),3)

    def test_actual_brighton_lineups_and_all_academy_groups(self):
        dataset=fixture_dataset()
        excluded=dataset['players'][0]['uid']
        result=analyze(dataset,excluded=[excluded])
        self.assertEqual(len(result['tactics']),3)
        for tactic in result['tactics']:
            ids=[l['uid'] for l in tactic['lineup']]
            self.assertEqual(len(set(ids)),11)
            self.assertNotIn(excluded,ids)
            self.assertTrue(all(0<=l['score']<=100 for l in tactic['lineup']))
        self.assertEqual({a['uid'] for a in result['academy']},{p['uid'] for p in dataset['players'] if p['team_slot']!=0})

    def test_custom_formation_simulation_and_loan_recalls(self):
        dataset = fixture_dataset()
        sim = simulate_formation(dataset, formation_id='352', style='possession')
        self.assertEqual(sim['formation']['name'], '3-5-2')
        self.assertEqual(sim['formation']['defensive'], '5-3-2')
        self.assertEqual(len(sim['lineup']), 11)
        self.assertGreater(sim['score'], 60.0)
        self.assertIn('fit_summary', sim)
        self.assertIn('reinforcements', sim)
        self.assertTrue(len(sim['reinforcements']) > 0)
        # Check loan recall recommendations
        recalls = [c for r in sim['reinforcements'] for c in r.get('loan_recalls', [])]
        self.assertTrue(len(recalls) > 0)
        first_recall = recalls[0]
        self.assertTrue(first_recall['player_name'])
        self.assertTrue(first_recall['club_name'])
        self.assertIn('reason', first_recall)
        # Verify other custom formations can also simulate cleanly
        for fid in ('343', '532', '41212', '424'):
            res = simulate_formation(dataset, formation_id=fid)
            self.assertEqual(len(res['lineup']), 11)


if __name__=='__main__':
    unittest.main()
