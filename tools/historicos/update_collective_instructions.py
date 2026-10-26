"""Integrates the 27 collective selectors (28 dimensions) and verified options from FM26 empirical survey."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SURVEY_DIR = ROOT / 'docs' / 'relevamiento-fm26-2026-10-25'

vc = json.load(open(SURVEY_DIR / 'verificacion-colectivas.json', encoding='utf-8'))
cat = json.load(open(ROOT / 'fm_app' / 'data' / 'fm26_catalog.json', encoding='utf-8'))
loc = json.load(open(ROOT / 'fm_app' / 'data' / 'fm26_es419.json', encoding='utf-8'))

ti_list = cat.setdefault('team_instructions', [])
ti_map = {t['id']: t for t in ti_list}

# 1. Ensure attacking_width_ip exists in catalog
if 'attacking_width_ip' not in ti_map:
    width_entry = {
        'id': 'attacking_width_ip',
        'instruction_property': 'Attacking Width',
        'label': 'Attacking Width',
        'category': 'in_possession',
        'phase': 'in_possession',
        'options': ['Much Narrower', 'Narrower', 'Standard', 'Wider', 'Much Wider'],
        'source': 'FM26 Menú táctico 25/10/2026 capturas/278-colectiva-amplitud.jpg'
    }
    ti_list.insert(2, width_entry)
    ti_map['attacking_width_ip'] = width_entry

# 2. Ensure tackling_oop exists in catalog
if 'tackling_oop' not in ti_map:
    tackling_entry = {
        'id': 'tackling_oop',
        'instruction_property': 'Tackling',
        'label': 'Tackling',
        'category': 'out_of_possession',
        'phase': 'out_of_possession',
        'options': ['Stay On Feet', 'Standard', 'Get Stuck In'],
        'source': 'FM26 Menú táctico 25/10/2026 capturas/304-colectiva-entradas.jpg'
    }
    ti_list.append(tackling_entry)
    ti_map['tackling_oop'] = tackling_entry

if 'progress_through_ip' in ti_map:
    ti_map['progress_through_ip']['options'] = ['Balanced', 'Left', 'Middle', 'Right', 'Both Flanks']

if 'gk_distribution_ip' in ti_map:
    ti_map['gk_distribution_ip']['options'] = ['Over Opposition Defense', 'Target Forward', 'Flanks', 'Playmaker', 'Full-Backs', 'Center-Backs', 'Balanced']

# 3. Update team locale in fm26_es419.json
team_loc = loc.setdefault('team', {})

def make_opt(text, key):
    return {
        'text': text,
        'key': key,
        'runtime_verified': False,
        'resource_verified': True,
        'binding_status': 'context_selected'
    }

# Exact translations mapping from verificacion-colectivas.json
RAW_TRANSLATIONS = {
    'passing_directness': {
        'property': {'text': 'Pases directos', 'key': 247808},
        'options': {
            'Much Shorter': ('Mucho más corto', 683807),
            'Shorter': ('Más corto', 683809),
            'Standard': ('Estándar', 683811),
            'More Direct': ('Más directo', 683813),
            'Much More Direct': ('Mucho más directo', 683815)
        }
    },
    'tempo': {
        'property': {'text': 'Ritmo de juego', 'key': 247805},
        'options': {
            'Much Lower': ('Mucho más bajo', 683827),
            'Lower': ('Bajo', 683829),
            'Standard': ('Estándar', 683831),
            'Higher': ('Alto', 683833),
            'Much Higher': ('Mucho más alto', 683835)
        }
    },
    'attacking_width_ip': {
        'property': {'text': 'Amplitud del ataque', 'key': 683122},
        'options': {
            'Much Narrower': ('Mucho más estrecho', 683817),
            'Narrower': ('Más estrecho', 683819),
            'Standard': ('Estándar', 683821),
            'Wider': ('Más ancho', 683823),
            'Much Wider': ('Mucho más ancho', 683825)
        }
    },
    'attacking_transition_ip': {
        'property': {'text': 'Transición ofensiva', 'key': 247802},
        'options': {
            'Hold Shape': ('Mantener dibujo', 683801),
            'Standard': ('Normal', 683803),
            'Counter-Attack': ('Contraataque', 683805)
        }
    },
    'creative_freedom_ip': {
        'property': {'text': 'Libertad creativa', 'key': 247806},
        'options': {
            'More Disciplined': ('Más disciplinados', 683837),
            'Balanced': ('Equilibrado', 683839),
            'More Expressive': ('Ser más expresivos', 683841)
        }
    },
    'time_wasting': {
        'property': {'text': 'Perder tiempo', 'key': 247800},
        'options': {
            'Less Often': ('Menos a menudo', 683843),
            'Standard': ('Normal', 683845),
            'More Often': ('Más a menudo', 683847)
        }
    },
    'play_for_set_pieces_ip': {
        'property': {'text': 'Jugar buscando el balón parado', 'key': 247807},
        'options': {
            'Keep Ball in Play': ('Mantener el balón en juego', 683849),
            'Play for Set Pieces': ('Buscar jugadas de balón parado', 683851)
        }
    },
    'dribbling_ip': {
        'property': {'text': 'Regate', 'key': 683123},
        'options': {
            'Discourage': ('Desanimar', 683863),
            'Balanced': ('Equilibrado', 683865),
            'Encourage': ('Animar', 683867)
        }
    },
    'patience_ip': {
        'property': {'text': 'Paciencia', 'key': 247810},
        'options': {
            'Hit Early Crosses': ('Hacer centros rápidos', 683869),
            'Standard': ('Estándar', 683871),
            'Work Ball Into Box': ('Intentar llevar el balón hasta el área', 683873)
        }
    },
    'shots_from_distance_ip': {
        'property': {'text': 'Disparos lejanos', 'key': 247812},
        'options': {
            'Discourage': ('Desalentar', 683875),
            'Balanced': ('Equilibrada', 683877),
            'Encourage': ('Alentar', 683879)
        }
    },
    'crossing_style_ip': {
        'property': {'text': 'Estilo de centros', 'key': 247811},
        'options': {
            'Balanced': ('Equilibrada', 683881),
            'Floated Crosses': ('Centros colgados', 683883),
            'Whipped Crosses': ('Centros tocados', 683885),
            'Low Crosses': ('Centros rasos', 683887)
        }
    },
    'overlap_ip': {
        'property': {'text': 'Doblar por banda', 'key': 247813},
        'options': {
            'Overlap - Balanced': ('Equilibrado', 683889),
            'Overlap - Left': ('Izquierda', 683891),
            'Overlap - Right': ('Derecha', 683893),
            'Overlap - Both Flanks': ('Doblar por ambas bandas', 683895)
        }
    },
    'underlap_ip': {
        'property': {'text': 'Doblar por dentro', 'key': 247814},
        'options': {
            'Underlap - Balanced': ('Equilibrado', 683897),
            'Underlap - Left': ('Izquierda', 683899),
            'Underlap - Right': ('Derecha', 683901),
            'Underlap - Both Flanks': ('Doblar por dentro en ambas bandas', 683903)
        }
    },
    'progress_through_ip': {
        'property': {'text': 'Avance', 'key': 247815},
        'options': {
            'Balanced': ('Equilibrado', 683905),
            'Left': ('Izquierda', 683909),
            'Middle': ('Centro', 683907),
            'Right': ('Derecha', 683911),
            'Both Flanks': ('Ambas bandas', 683913)
        }
    },
    'pass_reception_ip': {
        'property': {'text': 'Recepción de pase', 'key': 247816},
        'options': {
            'Pass to Feet': ('Pase al pie', 683915),
            'Balanced': ('Equilibrado', 683917),
            'Pass Into Space': ('Pasar al espacio', 683919)
        }
    },
    'build_up_strategy_ip': {
        'property': {'text': 'Estrategia previa', 'key': 247817},
        'options': {
            'Play Through Press': ('Jugar superando la presión', 683921),
            'Balanced': ('Equilibrada', 683923),
            'Bypass Press': ('Evitar la presión', 683925)
        }
    },
    'goal_kicks_ip': {
        'property': {'text': 'Saques de meta', 'key': 247818},
        'options': {
            'Short': ('En corto', 683927),
            'Mixed': ('Mixto', 683929),
            'Long': ('Largo', 683931)
        }
    },
    'gk_distribution_speed_ip': {
        'property': {'text': 'Distribución del portero (velocidad)', 'key': 247819},
        'options': {
            'Slow Pace Down': ('Ralentizar el juego', 683933),
            'Balanced': ('Equilibrada', 683935),
            'Distribute Quickly': ('Distribuir con rapidez', 683937)
        }
    },
    'gk_distribution_ip': {
        'property': {'text': 'Distribución del portero', 'key': 247820},
        'options': {
            'Over Opposition Defense': ('Por encima de la línea defensiva rival', 683951),
            'Target Forward': ('Delantero torre', 683949),
            'Flanks': ('Bandas', 683945),
            'Playmaker': ('Organizador', 683947),
            'Full-Backs': ('Laterales', 683943),
            'Center-Backs': ('Centrales', 683941),
            'Balanced': ('Equilibrado', 683939)
        }
    },
    'cross_engagement_oop': {
        'property': {'text': 'Compromiso de centros', 'key': 247821},
        'options': {
            'Stop Crosses': ('Evitar centros', 683953),
            'Balanced': ('Equilibrada', 683955),
            'Invite Crosses': ('Permitir centros', 683957)
        }
    },
    'line_of_engagement_oop': {
        'property': {'text': 'Línea de presión', 'key': 247822},
        'options': {
            'Low Block': ('Bloque bajo', 683959),
            'Mid Block': ('Bloque medio', 683961),
            'High Press': ('Presión adelantada', 683963)
        }
    },
    'defensive_line_oop': {
        'property': {'text': 'Línea defensiva', 'key': 247823},
        'options': {
            'Much Lower': ('Mucho más baja', 683965),
            'Lower': ('Más retrasada', 683967),
            'Standard': ('Estándar', 683969),
            'Higher': ('Más adelantada', 683971),
            'Much Higher': ('Mucho más alta', 683973)
        }
    },
    'defensive_line_behaviour_oop': {
        'property': {'text': 'Comportamiento de la línea defensiva', 'key': 247824},
        'options': {
            'Step Up More': ('Presionar más arriba', 683975),
            'Balanced': ('Equilibrada', 683977),
            'Drop Off More': ('Replegarse más', 683979)
        }
    },
    'trigger_press_oop': {
        'property': {'text': 'Activar presión', 'key': 247825},
        'options': {
            'Much Less Often': ('Mucho menos insistente', 683981),
            'Less Often': ('Menos insistente', 683983),
            'Standard': ('Estándar', 683985),
            'More Often': ('Más insistente', 683987),
            'Much More Often': ('Mucho más insistente', 683989)
        }
    },
    'defensive_transition_oop': {
        'property': {'text': 'Transición defensiva', 'key': 247826},
        'options': {
            'Regroup': ('Reagruparse', 683991),
            'Standard': ('Estándar', 683993),
            'Counter-Press': ('Contrapresión', 683995)
        }
    },
    'tackling_oop': {
        'property': {'text': 'Realizando una entrada', 'key': 703100},
        'options': {
            'Stay On Feet': ('Mantenerse de pie', 703104),
            'Standard': ('Estándar', 706482),
            'Get Stuck In': ('Ser agresivos', 703101)
        }
    },
    'pressing_trap_oop': {
        'property': {'text': 'Trampa de presión', 'key': 247827},
        'options': {
            'Trap Inside': ('Trampa en el interior', 683997),
            'Balanced': ('Equilibrado', 683999),
            'Trap Outside': ('Presionar fuera', 684001)
        }
    },
    'short_goalkeeper_distribution_oop': {
        'property': {'text': 'Distribución del portero en corto', 'key': 247828},
        'options': {
            'No': ('No', 684003),
            'Yes': ('Sí', 684005)
        }
    }
}

for k, val in RAW_TRANSLATIONS.items():
    prop = dict(val['property'])
    opts = {o_k: make_opt(o_v[0], o_v[1]) for o_k, o_v in val['options'].items()}
    team_loc[k] = {'property': prop, 'options': opts}

# 4. Attach collective rules to catalog
cat['collective_rules'] = {
    'total_unique_selectors': 27,
    'total_dimensions': 28,
    'shared_controls': [
        {
            'control': 'dribbling_ip',
            'label': 'Regate',
            'areas': ['Avance', 'Último tercio'],
            'evidence': 'capturas/285-regate-compartido-subfases.jpg'
        },
        {
            'control': 'pressing_trap_oop',
            'label': 'Trampa de presión',
            'areas': ['Presión adelantada', 'Bloque medio'],
            'evidence': 'capturas/308-trampa-compartida-subfases.jpg'
        }
    ],
    'support_runs_restrictions': [
        {
            'when': {'underlap_ip': 'Underlap - Both Flanks'},
            'disabled_options': {'overlap_ip': ['Overlap - Left', 'Overlap - Right', 'Overlap - Both Flanks']},
            'allowed_options': {'overlap_ip': ['Overlap - Balanced']},
            'evidence': 'capturas/289-colectiva-carreras-apoyo.jpg'
        },
        {
            'when': {'overlap_ip': 'Overlap - Both Flanks'},
            'disabled_options': {'underlap_ip': ['Underlap - Left', 'Underlap - Right', 'Underlap - Both Flanks']},
            'allowed_options': {'underlap_ip': ['Underlap - Balanced']},
            'evidence': 'capturas/291-doblar-ambas-bandas.jpg'
        },
        {
            'when': {'underlap_ip': 'Underlap - Balanced', 'overlap_ip': 'Overlap - Balanced'},
            'enabled': 'All options available on both axes',
            'evidence': 'capturas/290-carreras-interiores-equilibradas.jpg'
        }
    ]
}

# 5. Save updated catalog and locale
with open(ROOT / 'fm_app' / 'data' / 'fm26_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(cat, f, indent=2, ensure_ascii=False)

with open(ROOT / 'fm_app' / 'data' / 'fm26_es419.json', 'w', encoding='utf-8') as f:
    json.dump(loc, f, indent=2, ensure_ascii=False)

print('Updated catalog and locale successfully with runtime and resource flags.')
