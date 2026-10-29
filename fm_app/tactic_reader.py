"""Decode FM26 tactic enums and the team's selected players, independent of club/name."""
import json
from pathlib import Path
import struct

from fm_app.fm26 import ROLES

TACTIC_SCHEMA_VERSION = 2
CODES = json.loads((Path(__file__).parent/'data/tactic_codes.json').read_text(encoding='utf-8'))
POSITION_NAMES = {
    'Goalkeeper':'GK', 'DefenderRight':'DR', 'DefenderLeft':'DL', 'DefenderCentre':'DC',
    'WingBackRight':'WBR', 'WingBackLeft':'WBL', 'DefensiveMidfielderCentre':'DM',
    'MidfielderRight':'MR', 'MidfielderLeft':'ML', 'MidfielderCentre':'MC',
    'AttackingMidfielderRight':'AMR', 'AttackingMidfielderLeft':'AML',
    'AttackingMidfielderCentre':'AMC', 'AttackerCentre':'STC',
}
POSITION_CODES = {CODES['position_masks'][name]: position for name,position in POSITION_NAMES.items()}
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
    if position in ('DC','DM','MC','AMC','STC') and side is None:
        side = 'centre'
    return position, side


def formation_name(rows, phase):
    groups = [('DL','DR','DC'), ('WBL','WBR','DM'), ('ML','MR','MC'), ('AML','AMR','AMC'), ('STC',)]
    counts = [sum(row.get(phase+'_position') in group for row in rows) for group in groups]
    return '-'.join(str(count) for count in counts if count)


def decode_record(record, selection=None):
    """The OOP index joins an OOP slot to its selected player's IP slot.

    The two stored slot lists can have different orders. Never match by player name,
    familiarity, the tactic's label, or by simply zipping the two phase lists.
    """
    slots = record.get('raw', {}).get('slots', [])
    result = {**record, 'lineup':[], 'decode_warnings':[], 'positions_available':False}
    if len(slots) != 11 or sorted(s.get('number', -1) for s in slots) != list(range(11)):
        result['decode_warnings'].append('La copia no contiene once puestos completos.')
        return result
    oop = {s.get('unknown', {}).get('out_of_possession_position_index'):s for s in slots}
    if set(oop) != set(range(11)):
        result['decode_warnings'].append('No se pudo vincular la identidad entre ambas fases.')
        return result
    for slot in sorted(slots, key=lambda s:s['number']):
        index = slot['number']
        row = {'uid':selection[index] if selection and index < len(selection) else None,
               'instructions':{}, 'instruction_scope':'Posición'}
        for phase, source in [('ip',slot), ('oop',oop[index])]:
            prefix = 'in_possession' if phase == 'ip' else 'out_of_possession'
            position, side = decode_position(source.get(prefix+'_mask'))
            bits = source.get('unknown', {}).get(prefix+'_role_bits')
            role = CODES['roles'][phase].get(str(bits), '')
            if role and position not in ROLES[role]['positions']:
                role = ''
            row.update({phase+'_position':position, phase+'_side':side, phase+'_role':role})
            if not position:
                result['decode_warnings'].append(f'Puesto {index+1}: posición {phase.upper()} no compatible.')
            if not role:
                result['decode_warnings'].append(f'Puesto {index+1}: rol {phase.upper()} sin traducir ({bits}).')
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
            _, cursor = _read_text(section, start+4+len(layout.block_marker), end, layout, info.file_name, 'selección')
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
