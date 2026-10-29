"""Rebuild the small FM26 enum lookup from an installed Unity metadata file.

Only enum names/numbers are exported; no game binary or metadata is distributed.
Metadata layout: Perfare/Il2CppDumper, Il2Cpp/MetadataClass.cs (v31).
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]


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

    enums = {}
    for offset in range(types_at, types_at + types_size, 88):
        values = struct.unpack_from('<16i8H2I', data, offset)
        label = name(values[0])
        if label not in ('PositionMask', 'InPossessionRole', 'OutOfPossessionRole'):
            continue
        enum = {}
        for field in range(values[8], values[8] + values[18]):
            if field not in defaults:
                continue
            key = name(struct.unpack_from('<I', data, fields + field * 12)[0])
            pos = values_at + defaults[field]
            enum[key] = uint(pos) if label == 'PositionMask' else struct.unpack_from('<Q', data, pos)[0]
        enums[label] = enum
    if len(enums) != 3:
        raise ValueError('Missing tactic enums.')
    return enums, hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('metadata', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'fm_app/data/tactic_codes.json')
    args = parser.parse_args()
    enums, digest = extract(args.metadata)
    catalog = json.loads((ROOT/'fm_app/data/fm26_catalog.json').read_text(encoding='utf-8'))
    normalize = lambda value: re.sub('[^a-z]', '', value.lower())
    roles = {normalize(r['role_name']): r['id'] for r in catalog['roles']}
    # FM keeps older internal enum names for several renamed FM26 roles.
    aliases = {
        'CentralDefender':'centre_back', 'Libero':'advanced_centre_back',
        'BallPlayingDefender':'ball_playing_centre_back', 'NoNonsenseCentreBack':'no_nonsense_center_back',
        'InvertedWingBack':'inside_wing_back', 'InvertedFullBack':'inside_full_back',
        'InvertedWinger':'inside_winger', 'WidePlaymaker':'playmaking_winger',
        'TargetMan':'target_forward', 'FalseNumberNine':'false_nine', 'ShadowStriker':'second_striker',
        'Trequartista':'free_role', 'OPCentralOutletMidfielder':'central_outlet_attacking_midfielder',
        'OPLineKeeper':'line_holding_keeper', 'OPAtackingMidfielder':'attacking_midfielder',
        'OPTrackingAtackingMidfielder':'tracking_attacking_midfielder',
        'OPSplittingOutletAtackingMidfielder':'splitting_outlet_attacking_midfielder',
        'OPInvertingOutletWinger':'inside_outlet_winger',
        'OPWideCoverDefensiveMidfielder':'wide_covering_defensive_midfielder',
        'OPWideCoverCentralMidfielder':'wide_covering_central_midfielder',
    }
    result = {'metadata_version':31, 'metadata_sha256':digest,
        'source':'FM26 Unity enums: PositionMask, FM.UI.InPossessionRole, FM.UI.OutOfPossessionRole',
        'position_masks':enums['PositionMask'], 'roles':{}}
    for phase, enum in [('ip','InPossessionRole'),('oop','OutOfPossessionRole')]:
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
    print({phase:len(rows) for phase,rows in result['roles'].items()})


if __name__ == '__main__':
    main()
