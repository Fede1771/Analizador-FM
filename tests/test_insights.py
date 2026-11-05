from copy import deepcopy
import csv
from html import escape
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import time
import unittest
import urllib.request
import urllib.error

from fixtures import dataset, write_snapshot
from fm_app.insights import HistoryStore, compare_players, performance, squad_insights
from fm_app.table_import import preview, template
from fm_app.jobs import AppState
from fm_app.server import create_app_server
from fm_app.storage import ImportStorage, atomic_json


class InsightsTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = dataset()
        self.params = {'dataset_id':self.data['id'], 'uid':10, 'left_uid':10,'right_uid':11,
                       'role_id':'central_midfielder_ip','position':'MC','style':'possession'}

    def tearDown(self):
        self.temp.cleanup()

    def test_history_is_persistent_deduplicated_and_separated_by_career(self):
        store = HistoryStore(self.root)
        first = store.record(self.data)
        self.assertEqual(first, store.record(self.data))
        changed = deepcopy(self.data);changed['date']='2026-11-24';changed['id']='new'
        changed['players'][9]['attributes']['passing'] += 1
        store.record(changed)
        result = HistoryStore(self.root).evolution(changed,{**self.params,'dataset_id':'new'})
        self.assertEqual(len(result['points']),2)
        self.assertEqual(next(a['delta'] for a in result['attributes'] if a['id']=='passing'),1)
        self.assertGreater(result['score_delta'],0)
        other=deepcopy(changed);other['career_id']='other'
        self.assertEqual(len(store.evolution(other,{**self.params,'dataset_id':'new'})['points']),1)

    def test_earlier_guard_does_not_compare_with_future_and_unknown_baseline_rejected(self):
        store=HistoryStore(self.root);later=deepcopy(self.data);later['date']='2027-01-01';later['id']='later'
        store.record(later)
        result=store.evolution(self.data,self.params)
        self.assertEqual(len(result['points']),1)
        with self.assertRaises(ValueError):store.evolution(self.data,{**self.params,'baseline_id':'bad'})

    def test_retention_cannot_remove_compact_history_and_backfill_reads_old_extractions(self):
        storage=ImportStorage(self.root/'imports');old='a'*32;new='b'*32
        old_data=write_snapshot(storage.folder(old)/'output')
        storage.folder(new).mkdir();atomic_json(storage.folder(new)/'import.json',{})
        storage.publish(new)
        history=HistoryStore(storage.root);history.backfill(storage)
        self.assertEqual(len(history.observations(old_data)),1)
        storage.configure_retention({'max_snapshots':1,'max_total_mb':400});storage.prune()
        self.assertFalse(storage.folder(old).exists())
        self.assertEqual(len(history.observations(old_data)),1)

    def test_comparison_uses_identical_role_position_style_and_unknown_finances(self):
        result=compare_players(self.data,self.params)
        self.assertEqual(result['left']['familiarity'],20)
        self.assertIsNone(result['left']['wage'])
        self.assertEqual(len(result['attributes']),47)
        with self.assertRaises(ValueError):compare_players(self.data,{**self.params,'position':'GK'})
        with self.assertRaises(ValueError):compare_players(self.data,{**self.params,'right_uid':10})
        with self.assertRaises(ValueError):compare_players(self.data,{**self.params,'dataset_id':'old'})
        self.data['players'][9]['positions']={'mc':20}
        unknown=compare_players(self.data,{**self.params,'role_id':'ball_playing_goalkeeper_ip','position':'GK'})
        self.assertIsNone(unknown['left']['familiarity'])
        self.assertIsNone(unknown['left']['score'])
        history=HistoryStore(self.root).evolution(self.data,{**self.params,'role_id':'ball_playing_goalkeeper_ip','position':'GK'})
        self.assertIsNone(history['points'][0]['score'])
        self.assertIsNone(history['score_delta'])

    def test_depth_respects_group_exclusions_and_excludes_goalkeepers_from_axes(self):
        result=squad_insights(self.data,{**self.params,'excluded':[1,2,3]})
        self.assertEqual(result['player_count'],19)
        self.assertEqual(sum(g['count'] for g in result['groups'][:2]),19)
        self.assertEqual(next(p['count'] for p in result['coverage'] if p['position']=='GK'),0)
        self.assertEqual(result['excluded_count'],3)

    def test_performance_suppresses_incomplete_mixed_or_unknown_periods_and_zero_denominators(self):
        players=deepcopy(self.data['players'][:3])
        for i,p in enumerate(players):
            p.update(season_stats={'available':True,'minutes':(i+1)*100,'goals':i,'assists':1},
                     season_stats_scope='overall_club',season_stats_period='2026/27')
        result=performance(players)
        self.assertTrue(result['comparable']);self.assertEqual(result['top11_minutes'],100)
        self.assertEqual(result['top3_contributions'],100)
        players[0]['season_stats_period']=None
        self.assertFalse(performance(players)['comparable'])
        players[0]['season_stats_period']='2026/27';players[0]['season_stats']['minutes']=None
        self.assertIsNone(performance(players)['top11_minutes'])
        for p in players:p['season_stats']={'available':True,'minutes':0,'goals':0,'assists':0}
        self.assertIsNone(performance(players)['scorer_share'])
        players[0]['season_stats']={'available':False}
        self.assertFalse(performance(players)['comparable'])


class TableImportTests(unittest.TestCase):
    def params(self, text=None):
        return {'text':text or template(),'club':'Club <de prueba>','manager':'Manager','date':'2026-11-04',
                'stats_scope':'overall_club','stats_period':'2026/27','filename':'plantel.csv'}

    def test_csv_and_html_roundtrip_preserve_utf8_and_do_not_execute_markup(self):
        csv_result=preview(self.params())
        rows=list(csv.reader(io.StringIO(template())))
        html='<table>'+''.join('<tr>'+''.join('<td>'+escape(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</table>'
        html_result=preview(self.params(html))
        self.assertEqual(csv_result['players'],html_result['players'])
        self.assertEqual(csv_result['summary']['count'],1)
        self.assertEqual(csv_result['players'][0]['season_stats']['minutes'],900)
        self.assertFalse(csv_result['summary']['linked'])

    def test_masked_attributes_missing_columns_duplicates_and_familiarity_are_rejected(self):
        rows=list(csv.reader(io.StringIO(template())))
        for mutate in [lambda r:r[1].__setitem__(4,'—'),lambda r:r[0].__setitem__(4,'unknown'),
                       lambda r:r[1].__setitem__(3,'{"mc":21}')]:
            changed=deepcopy(rows);mutate(changed);s=io.StringIO();csv.writer(s).writerows(changed)
            with self.assertRaises(ValueError):preview(self.params(s.getvalue()))
        rows.append(rows[1]);s=io.StringIO();csv.writer(s).writerows(rows)
        with self.assertRaises(ValueError):preview(self.params(s.getvalue()))

    def test_explicit_natural_positions_confirmation_and_linking_current_identity(self):
        rows=list(csv.reader(io.StringIO(template())));rows[0][3]='Posiciones naturales';rows[1][3]='MC DM'
        s=io.StringIO();csv.writer(s).writerows(rows)
        with self.assertRaises(ValueError):preview(self.params(s.getvalue()))
        result=preview({**self.params(s.getvalue()),'confirm_natural':True})
        self.assertEqual(result['players'][0]['positions'],{'mc':20,'dm':20})
        data=dataset();p={**self.params(),'club':data['club'],'manager':data['manager'],'dataset_id':data['id'],'link_current':True}
        self.assertEqual(preview(p,data)['report']['external_career_id'],data['career_id'])
        with self.assertRaises(ValueError):preview({**p,'manager':'another'},data)

    def test_external_import_publishes_and_restores_through_existing_lifecycle(self):
        with TemporaryDirectory() as temp:
            state=AppState(Path(temp)/'imports')
            try:
                job=state.reserve('reading','Test');state.import_table(preview(self.params()),job)
                self.assertEqual(state.jobs[job]['status'],'done')
                data=state.dataset
                self.assertFalse(data['stored_tactics']['available'])
                self.assertEqual(data['source']['kind'],'table')
                self.assertEqual(len(state.history.observations(data)),1)
            finally:state.close()
            restored=AppState(Path(temp)/'imports')
            try:self.assertEqual(restored.dataset['id'],data['id'])
            finally:restored.close()

    def test_http_preview_is_read_only_commit_is_single_use_and_stale_is_rejected(self):
        with TemporaryDirectory() as temp:
            server=create_app_server(port=0,storage=Path(temp)/'imports',enable_watcher=False)
            worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
            def request(path,body):
                req=urllib.request.Request(f'http://127.0.0.1:{server.server_port}'+path,data=json.dumps(body).encode(),
                    headers={'Content-Type':'application/json','X-FM-App':'1'})
                try:
                    with urllib.request.urlopen(req,timeout=30) as response:return response.status,json.load(response)
                except urllib.error.HTTPError as error:
                    try:return error.code,json.load(error)
                    finally:error.close()
            try:
                code,value=request('/api/table/preview',self.params())
                self.assertEqual(code,200);self.assertIsNone(server.state.dataset)
                self.assertFalse((server.state.storage/'current.json').exists())
                server.state.dataset=dataset()
                self.assertEqual(request('/api/table/commit',{'token':value['token']})[0],409)
                server.state.dataset=None
                self.assertEqual(request('/api/table/commit',{'token':value['token']})[0],202)
                deadline=time.monotonic()+30
                while server.state.busy() and time.monotonic()<deadline:time.sleep(.05)
                self.assertEqual(request('/api/table/commit',{'token':value['token']})[0],400)
                self.assertIsNotNone(server.state.dataset)
            finally:
                server.shutdown();server.state.close();server.server_close();worker.join(3)
