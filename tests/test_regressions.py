from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from fm_app.tactics import FORMATION_CATALOG, FORMATIONS_BY_ID, parse_tactical_prompt
from fm_app.recommendations import analyze, simulate_formation, slot_choices, formation_slots
from fm_app.contracts import normalize_stats, cache_key
from fm_app.storage import ImportStorage, atomic_json
from fixtures import dataset, player


class EngineRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=dataset()

    def test_three_center_backs_keep_identity_when_defending(self):
        for fid in ('352','343','3412','523'):
            with self.subTest(formation=fid):
                slots=formation_slots(FORMATIONS_BY_ID[fid])
                self.assertEqual([s['oop_position'] for s in slots[1:4]],['DC']*3)
                self.assertEqual(slots[4]['oop_position'],'WBL')
                right=next(s for s in slots if s['ip_position']=='WBR')
                self.assertEqual(right['oop_position'],'WBR')

    def test_all_formations_have_unique_slot_ids_and_valid_geometry(self):
        for form in FORMATION_CATALOG:
            self.assertEqual(len(form['slots']),11)
            self.assertEqual(len({s['id'] for s in form['slots']}),11)
            for s in form['slots']:
                self.assertTrue(all(0<x<100 for x in s['ip']+s['oop']))
                if s['oop_position'].endswith('L'):self.assertLess(s['oop'][0],50)
                if s['oop_position'].endswith('R'):self.assertGreater(s['oop'][0],50)

    def test_top_three_are_ranked_across_ten_formations(self):
        result=analyze(self.data)
        self.assertEqual(result['evaluated_formations'],10)
        self.assertEqual(len(result['formation_rankings']),10)
        self.assertEqual([t['id'] for t in result['tactics']],[t['id'] for t in result['formation_rankings'][:3]])

    def test_simulator_and_recommendation_use_the_same_builder(self):
        a=analyze(self.data)
        for t in a['tactics']:
            sim=simulate_formation(self.data,t['id'])
            for key in ('score','lineup','bench','bench_replacements','instructions','fit_summary'):
                self.assertEqual(t[key],sim[key])

    def test_bench_scores_are_for_the_actual_target_slot(self):
        sim=simulate_formation(self.data,'352');byid={p['uid']:p for p in self.data['players']}
        for b in sim['bench_replacements']:
            if b['replaces_uid'] is None:
                self.assertIsNone(b['gap']);self.assertEqual(b['quality'],'unavailable');continue
            target=next(x for x in sim['lineup'] if x['uid']==b['replaces_uid'])
            expected=slot_choices(byid[b['uid']],formation_slots(FORMATIONS_BY_ID['352'])[target['slot_index']],'possession')[2]
            self.assertAlmostEqual(b['replacement_score'],round(expected,1))
        self.assertTrue(any(byid[uid]['positions']['gk']>=15 for uid in sim['bench']))

    def test_loan_stats_and_unique_recall_count(self):
        sim=simulate_formation(self.data,'352')
        recalls=[c for r in sim['reinforcements'] for c in r['loan_recalls']]
        self.assertTrue(recalls)
        for c in recalls:
            self.assertEqual(c['appearances'],7);self.assertEqual(c['rating'],7.1)
        self.assertEqual(sim['fit_summary']['recalls_count'],len({c['player_uid'] for c in recalls}))

    def test_no_loans_does_not_erase_weaknesses(self):
        sim=simulate_formation({**self.data,'loans':[]},'352')
        self.assertGreater(sim['fit_summary']['weak_count'],0)
        self.assertNotIn('equilibrada',sim['fit_summary']['verdict'])

    def test_negations_and_conflicting_requests(self):
        for prompt in ('No quiero presión alta','Sin presión alta','Quiero evitar presión alta'):
            parsed=parse_tactical_prompt(prompt)
            self.assertNotEqual(parsed['recommended_style'],'press')
            self.assertNotEqual(parsed['team_overrides'].get('line_of_engagement_oop'),'High Press')
        self.assertNotEqual(parse_tactical_prompt('No quiero jugar por bandas')['recommended_style'],'wide')
        self.assertEqual(parse_tactical_prompt('Presión alta, recuperar rápido')['team_overrides']['defensive_transition_oop'],'Counter-Press')
        self.assertEqual(parse_tactical_prompt('Control del balón sin contraataques')['team_overrides']['attacking_transition_ip'],'Hold Shape')

    def test_unknown_stats_are_distinct_from_zero(self):
        self.assertIsNone(normalize_stats({})['goals'])
        self.assertEqual(normalize_stats({'goals':0})['goals'],0)
        self.assertEqual(normalize_stats({'starts':4,'substitutes':3})['appearances'],7)

    def test_unknown_formation_is_rejected(self):
        with self.assertRaises(ValueError):simulate_formation(self.data,'unknown')


class StorageRegressions(unittest.TestCase):
    def test_retention_preserves_active_and_unrelated_files(self):
        with TemporaryDirectory() as tmp:
            store=ImportStorage(tmp);unrelated=Path(tmp)/'notes';unrelated.mkdir();(unrelated/'keep').write_text('ok')
            for letter in 'abc':
                folder=store.folder(letter*32);folder.mkdir();(folder/'save.fm').write_text('copy')
            store.publish('a'*32);store.configure_retention({'max_snapshots':1,'max_total_mb':400});store.prune()
            self.assertTrue(store.folder('a'*32).exists());self.assertTrue((unrelated/'keep').exists())
            self.assertFalse(store.folder('b'*32).exists());self.assertFalse(store.folder('c'*32).exists())

    def test_import_pointer_cannot_escape_storage(self):
        with TemporaryDirectory() as tmp:
            store=ImportStorage(tmp);atomic_json(Path(tmp)/'current.json',{'folder':'../outside'})
            with self.assertRaises(ValueError):store.current()
