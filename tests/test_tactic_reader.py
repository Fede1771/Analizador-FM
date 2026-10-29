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

    def test_slot_block_footer_active_role_duty_mask_and_pi_mask_decoding(self):
        record = raw_record()
        slots = record['raw']['slots']
        # Slot 9 is STC (16384). Suppose entry 0 has a stale DC role (4),
        # while entry 1 and the active footer have Deep-Lying Forward (1024) + duty bit (0x04000000),
        # and OOP active role is Centre Forward OOP (4398046511104 = 1<<42) + duty bit (0x00400000).
        dlf_with_duty = 1024 | 0x04000000
        cf_oop_with_duty = 4398046511104 | 0x00400000
        # Set PI_PASS_SHORTER (bit 1 -> 1<<1 = 2) and PI_HOLD_UP_BALL (bit 12 -> 1<<12 = 4096) in IP pi_mask:
        ip_pi_mask = (1 << 1) | (1 << 12)
        slots[9]['in_possession_settings'] = [
            {'head_byte': 0, 'first_bits': 0, 'second_bits_low': 0,
             'second_bits_middle': dlf_with_duty & 0xFFFFFFFF, 'second_bits_high': dlf_with_duty >> 32},
            {'head_byte': ip_pi_mask & 0xFF, 'first_bits': ip_pi_mask >> 8,
             'second_bits_low': 0, 'second_bits_middle': 0, 'second_bits_high': dlf_with_duty & 0xFFFFFFFF},
        ]
        slots[9]['out_of_possession_settings'] = [
            {'head_byte': 0, 'first_bits': 0, 'second_bits_low': 0,
             'second_bits_middle': 0, 'second_bits_high': cf_oop_with_duty & 0xFFFFFFFF},
        ]
        slots[9]['unknown'].update({
            'in_possession_role_bits': 4,
            'in_possession_trail_bits': dlf_with_duty >> 32,
            'out_of_possession_role_bits': cf_oop_with_duty,
            'out_of_possession_trail_bits': cf_oop_with_duty >> 32,
        })
        decoded = decode_record(record, list(range(1, 12)))
        stc_row = decoded['lineup'][9]
        self.assertEqual(stc_row['ip_role'], 'deep_lying_forward_ip')
        self.assertEqual(stc_row['oop_role'], 'centre_forward_oop')
        self.assertEqual(stc_row['instructions']['passing_directness_ip'], 'Shorter')
        self.assertEqual(stc_row['instruction_sources']['passing_directness_ip'], 'save')
        self.assertEqual(stc_row['instructions']['hold_up_ball_ip'], 'Yes')
        self.assertEqual(stc_row['instruction_sources']['hold_up_ball_ip'], 'role')
        self.assertEqual(stc_row['instructions']['shoot_ip'], 'Standard')
        self.assertEqual(stc_row['instruction_sources']['shoot_ip'], 'role')

    def test_oop_3_cycle_permutation_follows_target_slot_index(self):
        record = raw_record()
        slots = record['raw']['slots']
        # Configure a 3-cycle on slots 7 (MC_L -> OOP AMC), 8 (AMR -> OOP MR), 10 (AML -> OOP ML):
        # Slot 7 OOP slot is 8 (set to AMC 8192), Slot 8 OOP slot is 10 (set to MR 256), Slot 10 OOP slot is 7 (set to ML 512)
        slots[8]['out_of_possession_mask'] = 8192
        slots[10]['out_of_possession_mask'] = 256
        slots[7]['out_of_possession_mask'] = 512
        slots[7]['unknown']['out_of_possession_position_index'] = 8
        slots[8]['unknown']['out_of_possession_position_index'] = 10
        slots[10]['unknown']['out_of_possession_position_index'] = 7
        slots[8]['unknown']['out_of_possession_role_bits'] = 1073741824     # attacking_midfielder_oop (AMC)
        slots[10]['unknown']['out_of_possession_role_bits'] = 34359738368   # wide_midfielder_oop (MR)
        slots[7]['unknown']['out_of_possession_role_bits'] = 34359738368    # wide_midfielder_oop (ML)
        decoded = decode_record(record, list(range(1, 12)))
        self.assertEqual(decoded['lineup'][7]['ip_position'], 'MC')
        self.assertEqual(decoded['lineup'][7]['oop_position'], 'AMC')
        self.assertEqual(decoded['lineup'][7]['oop_role'], 'attacking_midfielder_oop')
        self.assertEqual(decoded['lineup'][8]['ip_position'], 'AMR')
        self.assertEqual(decoded['lineup'][8]['oop_position'], 'MR')
        self.assertEqual(decoded['lineup'][8]['oop_role'], 'wide_midfielder_oop')
        self.assertEqual(decoded['lineup'][10]['ip_position'], 'AML')
        self.assertEqual(decoded['lineup'][10]['oop_position'], 'ML')
        self.assertEqual(decoded['lineup'][10]['oop_role'], 'wide_midfielder_oop')

    def test_collective_team_instructions_decode_from_raw_bytes_and_stay_empty_when_absent(self):
        record = raw_record()
        decoded_empty = decode_record(record)
        self.assertEqual(decoded_empty['team_instructions'], {})

        raw_bytes = [4, 2, 5, 6, 2, 3, 208, 176, 102, 0, 4, 20, 18, 34, 100, 153, 4, 0, 255]
        record['raw']['unknown'] = {f'team_instruction_{idx:02d}': val for idx, val in enumerate(raw_bytes)}
        decoded = decode_record(record)
        ti = decoded['team_instructions']
        self.assertEqual(len(ti), 28)
        self.assertEqual(ti['passing_directness'], 'Much Shorter')
        self.assertEqual(ti['tempo'], 'Much Lower')
        self.assertEqual(ti['attacking_width_ip'], 'Narrower')
        self.assertEqual(ti['defensive_transition_oop'], 'Counter-Press')
        self.assertEqual(ti['defensive_line_oop'], 'Higher')
        self.assertEqual(ti['line_of_engagement_oop'], 'High Press')
        self.assertEqual(ti['tackling_oop'], 'Get Stuck In')
        self.assertEqual(ti['short_goalkeeper_distribution_oop'], 'Yes')


if __name__ == '__main__':
    unittest.main()
