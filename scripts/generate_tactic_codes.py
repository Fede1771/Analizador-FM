"""Rebuild the FM26 tactical enum and bitmask lookup from an installed Unity metadata file.

Only enum names/numbers and bitmask mappings are exported; no game binary or metadata is distributed.
Metadata layout: Perfare/Il2CppDumper, Il2Cpp/MetadataClass.cs (v31).
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]

DUTY_MASK = 0x06E00000

PLAYER_INSTRUCTION_MAP = {
    'PI_PASS_SHORTER': ('passing_directness_ip', 'Shorter'),
    'PI_PASS_MORE_DIRECT': ('passing_directness_ip', 'More Direct'),
    'PI_TAKE_MORE_RISKS': ('passing_risk_ip', 'Take More Risks'),
    'PI_TAKE_FEWER_RISKS': ('passing_risk_ip', 'Take Fewer Risks'),
    'PI_CROSS_FROM_DEEP': ('cross_from_ip', 'Cross From Deep'),
    'PI_CROSS_FROM_BYLINE': ('cross_from_ip', 'Byline'),
    'PI_CROSS_TO_NEAR_POST': ('crossing_strategy_ip', 'Near Post'),
    'PI_CROSS_TO_FAR_POST': ('crossing_strategy_ip', 'Far Post'),
    'PI_CROSS_TO_CENTRE': ('crossing_strategy_ip', 'Centre'),
    'PI_CROSS_TO_TARGET_MAN': ('crossing_strategy_ip', 'Target Forward'),
    'PI_DRIBBLE_MORE': ('dribbling_frequency_ip', 'Dribble More'),
    'PI_DRIBBLE_LESS': ('dribbling_frequency_ip', 'Dribble Less'),
    'PI_RUN_WIDE_WITH_BALL': ('dribbling_direction_ip', 'Run Wide With Ball'),
    'PI_CUT_INSIDE_WITH_BALL': ('dribbling_direction_ip', 'Cut Inside With Ball'),
    'PI_HOLD_UP_BALL': ('hold_up_ball_ip', 'Yes'),
    'PI_SHOOT_MORE': ('shoot_ip', 'Shoot More Often'),
    'PI_SHOOT_LESS': ('shoot_ip', 'Shoot Less Often'),
    'PI_GET_FORWARD_OFTEN': ('forward_runs_ip', 'Make More Runs'),
    'PI_HOLD_POSITION': ('forward_runs_ip', 'Make Fewer Runs'),
    'PI_ROAM_FROM_POSITION': ('freedom_of_movement_ip', 'Roam From Position'),
    'PI_STAY_WIDER': ('attacking_width_ip', 'Stay Wider'),
    'PI_PLAY_NARROW': ('attacking_width_ip', 'Sit Narrower'),
    'PI_MOVE_INTO_CHANNELS': ('attacking_width_ip', 'Move Into Channels'),
    'PI_HIGHER_PRESSING_INTENSITY': ('pressing_oop', 'More Often'),
    'PI_LOWER_PRESSING_INTENSITY': ('pressing_oop', 'Less Often'),
    'PI_GET_STUCK_IN': ('tackling_oop', 'Tackle Harder'),
    'PI_STAY_ON_FEET': ('tackling_oop', 'Ease Off Tackles'),
    'PI_MARK_TIGHTER': ('marking_oop', 'Mark Tighter'),
    'PI_MARK_SPECIFIC_PLAYER': ('marking_target_oop', 'Mark Specific'),
    'PI_MARK_SPECIFIC_POSITION': ('marking_target_oop', 'Mark Position'),
}

PLAYER_INSTRUCTION_DEFAULTS = {
    'attacking_width_ip': 'Standard',
    'dribbling_direction_ip': 'Standard',
    'dribbling_frequency_ip': 'Standard',
    'forward_runs_ip': 'Standard',
    'freedom_of_movement_ip': 'Follow Tactical Position',
    'hold_up_ball_ip': 'No',
    'shoot_ip': 'Standard',
    'passing_risk_ip': 'Standard',
    'passing_directness_ip': 'Standard',
    'cross_from_ip': 'Standard',
    'crossing_strategy_ip': 'Standard',
    'pressing_oop': 'Standard',
    'marking_oop': 'Standard',
    'tackling_oop': 'Standard',
    'marking_target_oop': 'Standard',
}

# Verified against game_plugin.dll category table at 0x4373818 & option bit table at 0x4373964
# (evaluated by native readers at 0x3cd750 and 0x3d6aa0 against team_instructions[6..17]).
TEAM_INSTRUCTION_MAP = {
    'passing_directness': {
        'enum_name': 'PassingDirectness',
        'default': 'Standard',
        'bits': [
            {'bit': 4, 'value': 'Much Shorter'},
            {'bit': 3, 'value': 'Shorter'},
            {'bit': 2, 'value': 'More Direct'},
            {'bit': 1, 'value': 'Much More Direct'},
        ],
    },
    'tempo': {
        'enum_name': 'Tempo',
        'default': 'Standard',
        'bits': [
            {'bit': 49, 'value': 'Much Lower'},
            {'bit': 48, 'value': 'Lower'},
            {'bit': 47, 'value': 'Higher'},
            {'bit': 46, 'value': 'Much Higher'},
        ],
    },
    'attacking_transition_ip': {
        'enum_name': 'AttackingTransition',
        'default': 'Standard',
        'bits': [
            {'bit': 55, 'value': 'Hold Shape'},
            {'bit': 54, 'value': 'Counter-Attack'},
        ],
    },
    'attacking_width_ip': {
        'enum_name': 'TeamWidth',
        'default': 'Standard',
        'bits': [
            {'bit': 53, 'value': 'Much Narrower'},
            {'bit': 52, 'value': 'Narrower'},
            {'bit': 51, 'value': 'Wider'},
            {'bit': 50, 'value': 'Much Wider'},
        ],
    },
    'creative_freedom_ip': {
        'enum_name': 'CreativeFreedom',
        'default': 'Balanced',
        'bits': [
            {'bit': 20, 'value': 'More Disciplined'},
            {'bit': 19, 'value': 'More Expressive'},
        ],
    },
    'play_for_set_pieces_ip': {
        'enum_name': 'PlayForSetPieces',
        'default': 'Keep Ball in Play',
        'bits': [
            {'bit': 18, 'value': 'Play for Set Pieces'},
        ],
    },
    'time_wasting': {
        'enum_name': 'TimeWasting',
        'default': 'Standard',
        'bits': [
            {'bit': 79, 'value': 'Less Often'},
            {'bit': 78, 'value': 'More Often'},
        ],
    },
    'line_of_engagement_oop': {
        'enum_name': 'LineOfEngagement',
        'default': 'Mid Block',
        'bits': [
            {'bit': 63, 'value': 'Low Block'},
            {'bit': 62, 'value': 'Mid Block'},
            {'bit': 61, 'value': 'High Press'},
        ],
    },
    'defensive_line_oop': {
        'enum_name': 'DefensiveLine',
        'default': 'Standard',
        'bits': [
            {'bit': 59, 'value': 'Much Lower'},
            {'bit': 58, 'value': 'Lower'},
            {'bit': 57, 'value': 'Higher'},
            {'bit': 56, 'value': 'Much Higher'},
        ],
    },
    'trigger_press_oop': {
        'enum_name': 'PressingTrigger',
        'default': 'Standard',
        'bits': [
            {'bit': 68, 'value': 'Much Less Often'},
            {'bit': 67, 'value': 'Less Often'},
            {'bit': 66, 'value': 'More Often'},
            {'bit': 65, 'value': 'Much More Often'},
        ],
    },
    'defensive_transition_oop': {
        'enum_name': 'DefensiveTransition',
        'default': 'Standard',
        'bits': [
            {'bit': 71, 'value': 'Regroup'},
            {'bit': 70, 'value': 'Counter-Press'},
        ],
    },
    'tackling_oop': {
        'enum_name': 'Tackling',
        'default': 'Standard',
        'bits': [
            {'bit': 73, 'value': 'Stay On Feet'},
            {'bit': 72, 'value': 'Get Stuck In'},
        ],
    },
    'defensive_line_behaviour_oop': {
        'enum_name': 'DefensiveLineBehaviour',
        'default': 'Balanced',
        'bits': [
            {'bit': 76, 'value': 'Step Up More'},
            {'bit': 77, 'value': 'Drop Off More'},
        ],
    },
    'gk_distribution_ip': {
        'enum_name': 'GoalkeeperDistributionTarget',
        'default': 'Balanced',
        'bits': [
            {'bit': 35, 'value': 'Center-Backs'},
            {'bit': 36, 'value': 'Full-Backs'},
            {'bit': 37, 'value': 'Flanks'},
            {'bit': 39, 'value': 'Playmaker'},
            {'bit': 40, 'value': 'Target Forward'},
            {'bit': 38, 'value': 'Over Opposition Defense'},
        ],
    },
    'gk_distribution_speed_ip': {
        'enum_name': 'GoalkeeperDistributionSpeed',
        'default': 'Balanced',
        'bits': [
            {'bit': 43, 'value': 'Slow Pace Down'},
            {'bit': 42, 'value': 'Distribute Quickly'},
        ],
    },
    'patience_ip': {
        'enum_name': 'Patience',
        'default': 'Standard',
        'bits': [
            {'bit': 9, 'value': 'Hit Early Crosses'},
            {'bit': 17, 'value': 'Work Ball Into Box'},
        ],
    },
    'dribbling_ip': {
        'enum_name': 'Dribbling',
        'default': 'Balanced',
        'bits': [
            {'bit': 14, 'value': 'Discourage'},
            {'bit': 13, 'value': 'Encourage'},
        ],
    },
    'pass_reception_ip': {
        'enum_name': 'PassReception',
        'default': 'Balanced',
        'bits': [
            {'bit': 6, 'value': 'Pass to Feet'},
            {'bit': 5, 'value': 'Pass Into Space'},
        ],
    },
    'cross_engagement_oop': {
        'enum_name': 'CrossEngagement',
        'default': 'Balanced',
        'bits': [
            {'bit': 82, 'value': 'Stop Crosses'},
            {'bit': 83, 'value': 'Invite Crosses'},
        ],
    },
    'short_goalkeeper_distribution_oop': {
        'enum_name': 'PreventShortGKDistribution',
        'default': 'No',
        'bits': [
            {'bit': 69, 'value': 'Yes'},
        ],
    },
    'build_up_strategy_ip': {
        'enum_name': 'BuildUpStrategy',
        'default': 'Balanced',
        'bits': [
            {'bit': 7, 'value': 'Play Through Press'},
            {'bit': 8, 'value': 'Bypass Press'},
        ],
    },
    'pressing_trap_oop': {
        'enum_name': 'PressingTrap',
        'default': 'Balanced',
        'bits': [
            {'bit': 80, 'value': 'Trap Inside'},
            {'bit': 81, 'value': 'Trap Outside'},
        ],
    },
    'crossing_style_ip': {
        'enum_name': 'CrossingStyle',
        'default': 'Balanced',
        'bits': [
            {'bit': 10, 'value': 'Floated Crosses'},
            {'bit': 11, 'value': 'Whipped Crosses'},
            {'bit': 12, 'value': 'Low Crosses'},
        ],
    },
    'shots_from_distance_ip': {
        'enum_name': 'ShotsFromDistance',
        'default': 'Balanced',
        'bits': [
            {'bit': 16, 'value': 'Discourage'},
            {'bit': 15, 'value': 'Encourage'},
        ],
    },
    'underlap_ip': {
        'enum_name': 'SupportingRuns',
        'default': 'Underlap - Balanced',
        'bits': [
            {'bit': 29, 'value': 'Underlap - Left'},
            {'bit': 30, 'value': 'Underlap - Right'},
            {'bit': 28, 'value': 'Underlap - Both Flanks'},
        ],
    },
    'goal_kicks_ip': {
        'enum_name': 'GoalKicks',
        'default': 'Mixed',
        'bits': [
            {'bit': 44, 'value': 'Short'},
            {'bit': 45, 'value': 'Long'},
        ],
    },
    'progress_through_ip': {
        'enum_name': 'ProgressThrough',
        'default': 'Balanced',
        'bits': [
            {'bit': 23, 'value': 'Middle'},
            {'bit': 21, 'value': 'Left'},
            {'bit': 22, 'value': 'Right'},
            {'bit': 24, 'value': 'Both Flanks'},
        ],
    },
    'overlap_ip': {
        'enum_name': 'SupportingRunsSecondary',
        'default': 'Overlap - Balanced',
        'bits': [
            {'bit': 26, 'value': 'Overlap - Left'},
            {'bit': 27, 'value': 'Overlap - Right'},
            {'bit': 25, 'value': 'Overlap - Both Flanks'},
        ],
    },
}


def extract(metadata):
    data = metadata.read_bytes()
    if struct.unpack_from('<II', data) != (0xFAB11BAF, 31):
        raise ValueError('Expected Unity metadata version 31.')

    def table(index):
        return struct.unpack_from('<II', data, 8 + index * 8)

    strings, _ = table(2)
    fields, _ = table(11)
    defaults_at, defaults_size = table(7)
    values_at, _ = table(8)
    types_at, types_size = table(19)
    defaults = {field: offset for field, _, offset in struct.iter_unpack(
        '<iii', data[defaults_at:defaults_at + defaults_size])}

    def name(index):
        start = strings + index
        return data[start:data.index(b'\0', start)].decode('utf-8')

    def uint(offset):
        first = data[offset]
        if first < 0x80:
            return first
        if first < 0xC0:
            return ((first & 0x3F) << 8) | data[offset + 1]
        if first < 0xE0:
            return ((first & 0x1F) << 24) | int.from_bytes(data[offset + 1:offset + 4], 'big')
        if first == 0xF0:
            return struct.unpack_from('<I', data, offset + 1)[0]
        raise ValueError('Unexpected enum constant encoding.')

    target_enums = (
        'PositionMask',
        'InPossessionRole',
        'OutOfPossessionRole',
        'PlayerInstruction',
        'TacticTeamInstructions',
    )
    enums = {}
    for offset in range(types_at, types_at + types_size, 88):
        values = struct.unpack_from('<16i8H2I', data, offset)
        label = name(values[0])
        if label not in target_enums:
            continue
        enum = {}
        for field in range(values[8], values[8] + values[18]):
            if field not in defaults:
                continue
            key = name(struct.unpack_from('<I', data, fields + field * 12)[0])
            pos = values_at + defaults[field]
            if label in ('InPossessionRole', 'OutOfPossessionRole'):
                enum[key] = struct.unpack_from('<Q', data, pos)[0]
            elif label == 'PositionMask':
                enum[key] = uint(pos)
            else:
                raw_u = uint(pos)
                enum[key] = (raw_u >> 1) ^ -(raw_u & 1)
        enums[label] = enum
    if len(enums) != len(target_enums):
        raise ValueError(f'Missing tactic enums: {set(target_enums) - set(enums)}')
    return enums, hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('metadata', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'fm_app/data/tactic_codes.json')
    args = parser.parse_args()
    enums, digest = extract(args.metadata)
    catalog = json.loads((ROOT / 'fm_app/data/fm26_catalog.json').read_text(encoding='utf-8'))
    normalize = lambda value: re.sub('[^a-z]', '', value.lower())
    roles = {normalize(r['role_name']): r['id'] for r in catalog['roles']}
    # FM keeps older internal enum names for several renamed FM26 roles.
    aliases = {
        'CentralDefender': 'centre_back', 'Libero': 'advanced_centre_back',
        'BallPlayingDefender': 'ball_playing_centre_back', 'NoNonsenseCentreBack': 'no_nonsense_center_back',
        'InvertedWingBack': 'inside_wing_back', 'InvertedFullBack': 'inside_full_back',
        'InvertedWinger': 'inside_winger', 'WidePlaymaker': 'playmaking_winger',
        'TargetMan': 'target_forward', 'FalseNumberNine': 'false_nine', 'ShadowStriker': 'second_striker',
        'Trequartista': 'free_role', 'OPCentralOutletMidfielder': 'central_outlet_attacking_midfielder',
        'OPLineKeeper': 'line_holding_keeper', 'OPAtackingMidfielder': 'attacking_midfielder',
        'OPTrackingAtackingMidfielder': 'tracking_attacking_midfielder',
        'OPSplittingOutletAtackingMidfielder': 'splitting_outlet_attacking_midfielder',
        'OPInvertingOutletWinger': 'inside_outlet_winger',
        'OPWideCoverDefensiveMidfielder': 'wide_covering_defensive_midfielder',
        'OPWideCoverCentralMidfielder': 'wide_covering_central_midfielder',
    }
    pi_decoded = {}
    for label, bit_index in enums['PlayerInstruction'].items():
        if label in PLAYER_INSTRUCTION_MAP:
            inst_id, opt_val = PLAYER_INSTRUCTION_MAP[label]
            pi_decoded[str(bit_index)] = {'id': inst_id, 'value': opt_val, 'enum': label}

    ti_enum = enums['TacticTeamInstructions']
    ti_decoded = {}
    for ti_id, spec in TEAM_INSTRUCTION_MAP.items():
        enum_name = spec['enum_name']
        ti_decoded[ti_id] = {
            'enum_id': ti_enum.get(enum_name),
            'enum_name': enum_name,
            'default': spec['default'],
            'bits': spec['bits'],
        }

    result = {
        'metadata_version': 31,
        'metadata_sha256': digest,
        'source': 'FM26 Unity enums & game_plugin.dll: PositionMask, FM.UI.InPossessionRole, FM.UI.OutOfPossessionRole, FM.UI.PlayerInstruction, FM.UI.TacticTeamInstructions',
        'duty_mask': DUTY_MASK,
        'position_masks': enums['PositionMask'],
        'roles': {},
        'player_instructions': pi_decoded,
        'player_instruction_defaults': PLAYER_INSTRUCTION_DEFAULTS,
        'team_instructions': ti_decoded,
    }
    for phase, enum in [('ip', 'InPossessionRole'), ('oop', 'OutOfPossessionRole')]:
        decoded = {}
        for label, value in enums[enum].items():
            target = aliases.get(label)
            if not target:
                target = roles.get(normalize(label.removeprefix('OP')))
            if target:
                # Catalog ids contain the phase suffix; aliases do not.
                target = re.sub('_(ip|oop)$', '', target) + '_' + phase
                if any(r['id'] == target for r in catalog['roles']):
                    decoded[str(value)] = target
        result['roles'][phase] = decoded
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print({
        'ip_roles': len(result['roles']['ip']),
        'oop_roles': len(result['roles']['oop']),
        'player_instructions': len(result['player_instructions']),
        'team_instructions': len(result['team_instructions']),
    })


if __name__ == '__main__':
    main()
