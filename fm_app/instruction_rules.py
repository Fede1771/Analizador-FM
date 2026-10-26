"""Observed instruction constraints; unknown contexts never imply a lock."""
import re
import unicodedata


SUPPORT_RUNS_SIDES = {
    f'{axis} - {value}': frozenset(sides)
    for axis in ('Overlap', 'Underlap')
    for value, sides in (('Balanced', ()), ('Left', ('L',)),
                         ('Right', ('R',)), ('Both Flanks', ('L', 'R')))
}


def check_support_runs_compatibility(overlap, underlap):
    conflict = SUPPORT_RUNS_SIDES.get(overlap, frozenset()) & SUPPORT_RUNS_SIDES.get(underlap, frozenset())
    if not conflict:
        return True, None
    if len(conflict) == 2:
        return False, 'Incompatibilidad en Carreras de apoyo: al seleccionar ambas bandas en un eje, el otro debe ser Equilibrado.'
    side = 'izquierda' if 'L' in conflict else 'derecha'
    return False, f'Incompatibilidad en Carreras de apoyo: no es posible doblar por banda y por dentro en la banda {side} simultáneamente.'


def normalized_scope(value):
    # Some historical observations contain mojibake or a replacement character.
    value = str(value or '')
    try:
        value = value.encode('latin-1').decode('utf-8')
    except (UnicodeError, ValueError):
        pass
    value = ''.join(c for c in unicodedata.normalize('NFD', value.lower()) if c.isascii() and c.isalpha())
    if value in ('posicion', 'posicin', 'position', 'positionpanel'):
        return 'position'
    if value in ('personalizada', 'jugador', 'player'):
        return 'player'
    return None


def observation_requirements(observation):
    label = str(observation.get('position', observation.get('position_family', ''))).lower()
    match = re.match(r'([a-z]+)', label)
    position = match[1].upper() if match else None
    if position == 'ST':
        position = 'STC'
    side = ('left' if 'left' in label or 'izquierda' in label else
            'right' if 'right' in label or 'derecha' in label else None)
    count = (3 if 'of-three' in label else
             2 if any(s in label for s in ('double', 'doble', 'pareja')) else
             1 if 'single' in label else None)
    return {'position': position, 'scope': normalized_scope(observation.get('scope')),
            'side': side, 'count': count}


def position_context(positions, index, scope='Posición', xs=None):
    """Same-position rows are displayed left to right in the current editor."""
    position = positions[index]
    peers = [i for i, p in enumerate(positions) if p == position]
    if xs is not None:
        peers.sort(key=lambda i: xs[i])
    rank = peers.index(index)
    side = None if len(peers) == 1 else 'left' if rank == 0 else 'right' if rank == len(peers) - 1 else 'centre'
    return {'position': position, 'scope': normalized_scope(scope), 'side': side, 'count': len(peers)}


def context_matches(observation, context):
    if not observation or not context:
        return False
    required = observation.get('requirements') or observation_requirements(observation)
    actual_scope = context.get('scope')
    if actual_scope not in ('position', 'player'):
        actual_scope = normalized_scope(actual_scope)
    if not required['position'] or not required['scope']:
        return False
    return (required['position'] == context.get('position') and required['scope'] == actual_scope
            and (required['side'] is None or required['side'] == context.get('side'))
            and (required['count'] is None or required['count'] == context.get('count')))
