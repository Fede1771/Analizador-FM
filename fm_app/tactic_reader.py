"""Decode FM26 tactic binary blocks, roles, instructions, and selected players, independent of club/name."""
import json
from pathlib import Path
import struct

from fm_app.fm26 import ROLES, PI, TI, PLAYER_MENU, OBSERVED_CONTEXTS
from fm_app.instruction_rules import check_support_runs_compatibility

TACTIC_SCHEMA_VERSION = 2
CODES = json.loads((Path(__file__).parent / 'data/tactic_codes.json').read_text(encoding='utf-8'))
DUTY_MASK = int(CODES.get('duty_mask', 0x06E00000))
POSITION_NAMES = {
    'Goalkeeper': 'GK', 'DefenderRight': 'DR', 'DefenderLeft': 'DL', 'DefenderCentre': 'DC',
    'WingBackRight': 'WBR', 'WingBackLeft': 'WBL', 'DefensiveMidfielderCentre': 'DM',
    'MidfielderRight': 'MR', 'MidfielderLeft': 'ML', 'MidfielderCentre': 'MC',
    'AttackingMidfielderRight': 'AMR', 'AttackingMidfielderLeft': 'AML',
    'AttackingMidfielderCentre': 'AMC', 'AttackerCentre': 'STC',
}
POSITION_CODES = {CODES['position_masks'][name]: position for name, position in POSITION_NAMES.items()}
LEFT = CODES['position_masks']['LeftSidedPosition']
RIGHT = CODES['position_masks']['RightSidedPosition']


def decode_position(mask):
    if type(mask) is not int or mask < 0:
        return None, None
    code = mask & ~(LEFT | RIGHT)
    position = POSITION_CODES.get(code)
    side = 'left' if mask & LEFT else 'right' if mask & RIGHT else None
    if mask & LEFT and mask & RIGHT:
        return None, None
    if position in ('DC', 'DM', 'MC', 'AMC', 'STC') and side is None:
        side = 'centre'
    return position, side


def formation_name(rows, phase):
    groups = [('DL', 'DR', 'DC'), ('WBL', 'WBR', 'DM'), ('ML', 'MR', 'MC'), ('AML', 'AMR', 'AMC'), ('STC',)]
    counts = [sum(row.get(phase + '_position') in group for row in rows) for group in groups]
    return '-'.join(str(count) for count in counts if count)


def _extract_slot_role_and_mask(source, phase):
    """Extract the active role bitmask and active PlayerInstruction bitmask from a _SlotBlock.

    In FM26's binary _SlotBlock, setting_count 24-byte TacticSettingUnits are followed by a
    12-byte footer whose last 8 bytes hold (active_role_bit | active_duty_bit).
    fmsave 0.5.11 shifts the stream by 8 bytes after consuming role_bits first, placing:
    - entry 0 role bitmask in unknown[prefix + '_role_bits']
    - entry j (j >= 1) role bitmask in settings[j-1].second_bits_middle | (settings[j-1].second_bits_high << 32)
    - entry j PlayerInstruction bitmask in settings[j].head_byte | (settings[j].first_bits << 8)
    - footer active role+duty in settings[-1].second_bits_high | (unknown[prefix + '_trail_bits'] << 32)
    """
    prefix = 'in_possession' if phase == 'ip' else 'out_of_possession'
    unknown = source.get('unknown') or {}
    settings = source.get(prefix + '_settings')
    trail = unknown.get(prefix + '_trail_bits')
    if isinstance(settings, list) and len(settings) > 0 and type(trail) is int:
        active_word = (int(settings[-1].get('second_bits_high', 0)) & 0xFFFFFFFF) | ((int(trail) & 0xFFFFFFFF) << 32)
        active_role_bit = active_word & ~DUTY_MASK
        entry_roles = [int(unknown.get(prefix + '_role_bits', 0))]
        for unit in settings[:-1]:
            low = int(unit.get('second_bits_middle', 0)) & 0xFFFFFFFF
            high = int(unit.get('second_bits_high', 0)) & 0xFFFFFFFF
            entry_roles.append(low | (high << 32))
        pi_mask = None
        for idx, entry_role in enumerate(entry_roles):
            if (entry_role & ~DUTY_MASK) == active_role_bit:
                unit = settings[idx]
                pi_mask = (int(unit.get('head_byte', 0)) & 0xFF) | ((int(unit.get('first_bits', 0)) & 0xFFFFFFFFFFFFFFFF) << 8)
                break
        return active_role_bit, pi_mask
    return unknown.get(prefix + '_role_bits'), None


def _decode_phase_instructions(phase, role_id, pi_mask):
    """Decode individual instructions for one phase when the active role's pi_mask is present."""
    if not role_id or pi_mask is None:
        return {}, {}
    phase_key = 'in_possession' if phase == 'ip' else 'out_of_possession'
    menu = PLAYER_MENU[phase_key]
    pi_lookup = CODES.get('player_instructions', {})
    pi_defaults = CODES.get('player_instruction_defaults', {})
    locked_values = OBSERVED_CONTEXTS.get(role_id, {}).get('locked_values', {})

    instructions = {}
    sources = {}

    for bit_str, spec in pi_lookup.items():
        bit_idx = int(bit_str)
        if (pi_mask >> bit_idx) & 1:
            inst_id = spec['id']
            val = spec['value']
            if inst_id in PI and PI[inst_id]['phase'] == phase_key and val in PI[inst_id]['options']:
                instructions[inst_id] = val
                sources[inst_id] = 'save'

    for inst_id, locked_val in locked_values.items():
        if locked_val is not None and inst_id in PI and PI[inst_id]['phase'] == phase_key:
            instructions[inst_id] = locked_val
            sources[inst_id] = 'role'

    for inst_id in menu:
        if inst_id not in instructions:
            default_val = pi_defaults.get(inst_id)
            if default_val and default_val in PI[inst_id]['options']:
                instructions[inst_id] = default_val
                sources[inst_id] = 'role'

    return instructions, sources


def decode_team_instructions(raw):
    """Decode the 28 collective team instructions from team_instruction_00..18 (bytes 6..17 bitmask)."""
    if not isinstance(raw, dict):
        return {}, []
    unknown = raw.get('unknown') or {}
    ti_bytes = [unknown.get(f'team_instruction_{i:02d}') for i in range(19)]
    if not all(type(b) is int and 0 <= b <= 255 for b in ti_bytes):
        return {}, []
    ti_specs = CODES.get('team_instructions', {})
    team = {}
    warnings = []
    for ti_id, spec in ti_specs.items():
        if ti_id not in TI:
            continue
        chosen = spec.get('default')
        for entry in spec.get('bits', []):
            bit = int(entry['bit'])
            byte_idx = 6 + (bit // 8)
            bit_offset = bit % 8
            if 6 <= byte_idx < 18 and ((ti_bytes[byte_idx] >> bit_offset) & 1):
                chosen = entry['value']
                break
        if chosen in TI[ti_id]['options']:
            team[ti_id] = chosen
    ok, err = check_support_runs_compatibility(team.get('overlap_ip'), team.get('underlap_ip'))
    if not ok and err:
        warnings.append(err)
    return team, warnings


def decode_record(record, selection=None):
    """The OOP index joins an IP slot to its corresponding OOP slot in slots.

    The two stored slot lists can have different orders. Never match by player name,
    familiarity, the tactic's label, or by simply zipping the two phase lists.
    """
    raw = record.get('raw') or {}
    slots = raw.get('slots', [])
    team_instructions, ti_warnings = decode_team_instructions(raw)
    result = {
        **record,
        'lineup': [],
        'team_instructions': team_instructions,
        'decode_warnings': list(ti_warnings),
        'positions_available': False,
    }
    if len(slots) != 11 or sorted(s.get('number', -1) for s in slots) != list(range(11)):
        result['decode_warnings'].append('La copia no contiene once puestos completos.')
        return result
    by_number = {s['number']: s for s in slots}
    oop_targets = [s.get('unknown', {}).get('out_of_possession_position_index') for s in slots]
    if set(oop_targets) != set(range(11)):
        result['decode_warnings'].append('No se pudo vincular la identidad entre ambas fases.')
        return result
    for slot in sorted(slots, key=lambda s: s['number']):
        index = slot['number']
        oop_index = slot['unknown']['out_of_possession_position_index']
        oop_slot = by_number[oop_index]
        row = {
            'uid': selection[index] if selection and index < len(selection) else None,
            'instructions': {},
            'instruction_sources': {},
            'instruction_scope': 'Posición',
        }
        for phase, source in [('ip', slot), ('oop', oop_slot)]:
            prefix = 'in_possession' if phase == 'ip' else 'out_of_possession'
            position, side = decode_position(source.get(prefix + '_mask'))
            bits, pi_mask = _extract_slot_role_and_mask(source, phase)
            role = CODES['roles'][phase].get(str(bits), '')
            if role and position not in ROLES[role]['positions']:
                role = ''
            row.update({phase + '_position': position, phase + '_side': side, phase + '_role': role})
            if not position:
                result['decode_warnings'].append(f'Puesto {index + 1}: posición {phase.upper()} no compatible.')
            if not role:
                result['decode_warnings'].append(f'Puesto {index + 1}: rol {phase.upper()} sin traducir ({bits}).')
            phase_insts, phase_sources = _decode_phase_instructions(phase, role, pi_mask)
            row['instructions'].update(phase_insts)
            row['instruction_sources'].update(phase_sources)
        marking_mode = row['instructions'].get('marking_target_oop')
        if marking_mode in ('Mark Specific', 'Mark Position'):
            result['decode_warnings'].append(
                f'Puesto {index + 1}: la orden {marking_mode} requiere indicar el jugador o puesto rival en el editor.'
            )
        result['lineup'].append(row)
    result['positions_available'] = all(r['ip_position'] and r['oop_position'] for r in result['lineup'])
    result['formation_ip'] = formation_name(result['lineup'], 'ip')
    result['formation_oop'] = formation_name(result['lineup'], 'oop')
    return result


def read_team_selections(career, tactics):
    """Small adapter to fmsave 0.5.11's checked section layout and selector index.

    Keep empty slots in place. fmsave's public table filters them out, which would
    shift every following player. Its public tactics() checks must run first.
    """
    from fmsave.readers.tactics import find_tactics_layout, _block_starts, _read_selection_part, _read_text
    context = career._context
    info = context.info
    layout = find_tactics_layout(info.section_schemas.get('tactics_man'), info.build)
    if layout.selection_slot_count != 26 or layout.slot_count != 11:
        raise ValueError('Formato de selección de equipo no compatible.')
    index = context.player_records()
    players = {p.uid for p in career.players()}
    result = {}
    with context.section('tactics_man') as section:
        starts = _block_starts(section, sorted({t.team_id for t in tactics}), layout)
        for team_id, start in starts.items():
            end = min((offset for offset in starts.values() if offset > start), default=len(section))
            _read_selection_part(section, start, end, layout, info.file_name)
            _, cursor = _read_text(section, start + 4 + len(layout.block_marker), end, layout, info.file_name, 'selección')
            selectors = struct.unpack_from('<26I', section, cursor)
            selected = []
            for selector in selectors[:11]:
                at = index.position_by_pindex.get(selector - 1)
                uid = int(index.uids[at]) if at is not None else None
                selected.append(uid if uid in players else None)
            # A repeated starter cannot be an unambiguous team selection.
            present = [uid for uid in selected if uid is not None]
            if len(present) != len(set(present)):
                raise ValueError('La selección contiene jugadores repetidos.')
            result[team_id] = selected
    return result
