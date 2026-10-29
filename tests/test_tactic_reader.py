"""Club-independent decoding: custom shapes, empty selections, phase permutations."""
from copy import deepcopy
from dataclasses import dataclass
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from fm_app.current_tactic import extract_stored_tactics, coordinates
from fm_app.tactic_reader import decode_position, decode_record, CODES


def raw_record():
    # Custom name intentionally gives no hint of the actual shape.
    positions = [1,4,16|2097152,16|1048576,8,128,1024|2097152,1024|1048576,2048,16384,4096]
    slots = [{'number':i,'in_possession_mask':p,'out_of_possession_mask':p,
              'unknown':{'in_possession_role_bits':1,'out_of_possession_role_bits':1,
                         'out_of_possession_position_index':i}} for i,p in enumerate(positions)]
    return {'id':'12:0','name':'Plan propio','team_slot':0,'raw':{'slots':slots}}


class TacticReaderTests(unittest.TestCase):
    def test_enum_positions_and_sides_are_from_game_not_template_order(self):
        self.assertEqual(decode_position(4), ('DR',None))
        self.assertEqual(decode_position(8), ('DL',None))
        self.assertEqual(decode_position(16|2097152), ('DC','right'))
        self.assertEqual(decode_position(16|1048576), ('DC','left'))
        for invalid in (0,2,3,16|1048576|2097152,-1,'16',None):
            self.assertEqual(decode_position(invalid), (None,None))

    def test_any_name_loads_actual_shape_and_keeps_unselected_slots_empty(self):
        record=raw_record()
        selected=[None,2,3,4,5,6,7,8,9,10,11]
        decoded=decode_record(record, selected)
        self.assertTrue(decoded['positions_available'])
        self.assertEqual(decoded['formation_ip'],'4-1-2-2-1')
        self.assertEqual([r['uid'] for r in decoded['lineup']], selected)
        self.assertEqual(decoded['lineup'][1]['ip_position'],'DR')
        self.assertEqual(decoded['lineup'][1]['ip_role'],'')  # incompatible GK never becomes a best-fit role
        self.assertTrue(decoded['decode_warnings'])
        self.assertTrue(all(r['instructions']=={} for r in decoded['lineup']))

    def test_oop_permutation_joins_positions_and_roles_to_player_identity(self):
        record=raw_record()
        slots=record['raw']['slots']
        slots[5]['unknown']['out_of_possession_position_index']=7
        slots[7]['unknown']['out_of_possession_position_index']=5
        slots[5]['unknown']['out_of_possession_role_bits']=32768
        decoded=decode_record(record,list(range(1,12)))
        self.assertEqual(decoded['lineup'][7]['uid'],8)
        self.assertEqual(decoded['lineup'][7]['ip_position'],'MC')
        self.assertEqual(decoded['lineup'][7]['oop_position'],'DM')
        self.assertEqual(decoded['lineup'][7]['oop_role'],'defensive_midfielder_oop')
        self.assertEqual(decoded['lineup'][5]['oop_position'],'MC')

    def test_incomplete_or_unknown_positions_do_not_invent_a_formation(self):
        record=raw_record();record['raw']['slots'].pop()
        self.assertFalse(decode_record(record)['positions_available'])
        record=raw_record();record['raw']['slots'][3]['in_possession_mask']=2
        self.assertFalse(decode_record(record)['positions_available'])
        record=raw_record();record['raw']['slots'][3]['unknown']['out_of_possession_position_index']=2
        self.assertFalse(decode_record(record)['positions_available'])

    def test_loaded_central_defenders_keep_their_actual_side_on_the_pitch(self):
        rows=decode_record(raw_record())['lineup']
        points=coordinates(rows,'ip_position')
        self.assertEqual(points[2],[62,76])
        self.assertEqual(points[3],[38,76])

    def test_lookup_covers_all_catalog_roles_and_no_zero_roles(self):
        from fm_app.fm26 import ROLES
        self.assertEqual(set(CODES['roles']['ip'].values())|set(CODES['roles']['oop'].values()),set(ROLES))
        self.assertNotIn('0',CODES['roles']['ip'])


if __name__ == '__main__':
    unittest.main()
