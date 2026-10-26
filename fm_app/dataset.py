"""Validated visible dataset and stable club/manager preference identity."""
import hashlib
import json
from fm_app.tactics import ATTRS, STYLES, FORMATION_CATALOG
from fm_app.fm26 import ROLES, CATALOG, LOCALE, TI, PI, PLAYER_MENU, SCREENSHOT_LOCKS, EDITABLE_GROUPS, OBSERVED_CONTEXTS, instruction
from fm_app.contracts import clean_player, get_transfer_window_status
from pathlib import Path
from fm_app.current_tactic import POSITIONS

LIVERPOOL_REF = json.loads((Path(__file__).parent / 'data/liverpool_reference.json').read_text(encoding='utf-8'))


def load_dataset(folder):
    report=json.loads((folder/'validation.json').read_text(encoding='utf-8'))
    if not isinstance(report, dict) or not isinstance(report.get('club'), dict) or not isinstance(report.get('managed_clubs'), list):
        raise ValueError('Informe de extracción inválido.')
    if report.get('sanity_errors') or report.get('missing_required_fields'):
        raise ValueError('La extracción no superó los controles de consistencia.')
    # Compatibility with earlier, genuinely imported snapshots; new imports use generic names.
    squad_file=folder/('squad_full.json' if (folder/'squad_full.json').exists() else 'brighton_full.json')
    loans_file=folder/('loaned_out.json' if (folder/'loaned_out.json').exists() else 'brighton_loaned_out.json')
    players=[clean_player(p) for p in json.loads(squad_file.read_text(encoding='utf-8'))]
    loans_raw = json.loads(loans_file.read_text(encoding='utf-8'))
    loans = []
    game_date_str = report.get('game_date')
    for lp in loans_raw:
        cl = clean_player(lp)
        cl['loan_window'] = get_transfer_window_status(game_date_str, cl.get('loan_end'))
        loans.append(cl)
    if not players:
        raise ValueError('La partida no contiene jugadores para el club detectado.')
    manager=next((m for m in report['managed_clubs'] if m['club_uid']==report['club']['uid']),{})
    metadata_path=folder.parent/'import.json'
    source=json.loads(metadata_path.read_text(encoding='utf-8')) if metadata_path.exists() else {'filename':'Partida importada anteriormente'}
    slots=sorted({p['team_slot'] for p in players if p['team_slot'] is not None})
    if not slots:
        raise ValueError('No se identificaron grupos de plantilla para analizar.')
    primary=slots[0]
    raw_labels=report.get('slot_labels') or {}
    slot_labels={}
    for s in slots:
        if str(s) in raw_labels:
            slot_labels[s]=raw_labels[str(s)]
        elif s==primary:
            slot_labels[s]='Primer equipo'
        else:
            slot_p=[p for p in players if p.get('team_slot')==s]
            ages=[p['age'] for p in slot_p if p.get('age') is not None]
            if ages:
                max_a=max(ages)
                slot_labels[s]='Sub-18' if max_a<=18 else 'Sub-21' if max_a<=21 else 'Sub-23' if max_a<=23 else f'Grupo {s}'
            else:
                slot_labels[s]=f'Grupo {s}'
    identity = f"{report['club']['uid']}:{manager.get('manager_staff_uid', manager.get('manager_name', ''))}"
    career_id = hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]
    if len({p['uid'] for p in players + loans}) != len(players + loans):
        raise ValueError('Identificadores de jugadores duplicados.')

    game_date_str = report.get('game_date')
    contract_alerts = []
    if game_date_str:
        from datetime import datetime
        try:
            g_dt = datetime.fromisoformat(game_date_str)
            for p in players:
                c = p.get('contract') or {}
                c_end = c.get('end')
                if c_end:
                    e_dt = datetime.fromisoformat(c_end)
                    days_left = (e_dt - g_dt).days
                    months_left = max(0, round(days_left / 30.4))
                    urgency = 'danger' if months_left <= 10 else ('warning' if months_left <= 22 else 'info')
                    badge = '🔴 Vence en < 10 meses' if months_left <= 10 else ('🟡 Vence en 1-2 años' if months_left <= 22 else '🟢 En término')
                    action = 'Renovar urgente o vender: entra a los últimos meses y puede firmar libre.' if months_left <= 10 else ('Iniciar negociaciones para blindar su valor.' if months_left <= 22 else 'Situación contractual estable.')
                    if c.get('has_extension_option'):
                        action += ' (El club tiene opción de extensión unilateral por 1 año más).'
                    contract_alerts.append({
                        'player_uid': p['uid'],
                        'player_name': p['name'],
                        'team_slot': p.get('team_slot'),
                        'wage': c.get('wage'),
                        'contract_end': c_end,
                        'months_remaining': months_left,
                        'days_remaining': days_left,
                        'has_extension_option': c.get('has_extension_option', False),
                        'urgency': urgency,
                        'badge': badge,
                        'action': action,
                        'transfer_value': p.get('transfer_value')
                    })
            contract_alerts.sort(key=lambda x: (x['days_remaining'], -(x['transfer_value'] or 0)))
        except Exception:
            contract_alerts = []

    scouting_file = folder / 'scouting.json'
    shared_scouting = folder.parent.parent / 'scouting_cache.json'
    if not scouting_file.exists():
        import shutil
        if shared_scouting.exists():
            try:
                shutil.copy2(shared_scouting, scouting_file)
            except Exception:
                pass
        else:
            for other_imp in folder.parent.glob('*/output/scouting.json'):
                if other_imp.exists():
                    try:
                        shutil.copy2(other_imp, scouting_file)
                        shutil.copy2(other_imp, shared_scouting)
                        break
                    except Exception:
                        pass
    scouting = json.loads(scouting_file.read_text(encoding='utf-8')) if scouting_file.exists() else (
        json.loads(shared_scouting.read_text(encoding='utf-8')) if shared_scouting.exists() else []
    )

    return {'id':report['save_sha256'][:16], 'career_id':career_id, 'club':report['club']['name'],
            'contract_alerts': contract_alerts, 'scouting': scouting,
            'manager':manager.get('manager_name'), 'source':source,'default_primary_slot':slots[0],
            'date':report['game_date'],'build':report['build'], 'players':players,'loans':loans,
            'slots':slots, 'slot_labels':slot_labels,
            'warnings':report.get('reader_warnings',[]),'source_verified':False,
            'attributes':ATTRS,'styles':STYLES,
            'fm26_reference':{'edition':'FM26','checked_at':CATALOG['checked_at'],
                              'role_count':len(ROLES),'available_reference_roles':len(CATALOG['roles']),
                              'spanish_note':'Etiquetas extraídas de Español latinoamericano de FM26 26.3.2. Se conservan variantes por contexto; las vinculaciones con cada vista del menú no están todas comprobadas visualmente.',
                              'localization':{k:LOCALE[k] for k in ('locale','language','game_version','steam_build','source','sha256','verification')},
                              'sources':['https://fmsidekick.com/database/roles','https://fmsidekick.com/database/player_instructions','https://fmsidekick.com/database/team_instructions','https://fm.guidetofootball.com/fm26/roles/']},
            'stored_tactics':json.loads((folder/'tactics.json').read_text(encoding='utf-8')) if (folder/'tactics.json').exists() else {'available':False,'records':[],'limitations':'Esta importación todavía no contiene la lectura táctica. Volvé a sincronizar el guardado para recuperarla. Podés confirmar tu táctica manualmente.'},
            'liverpool_reference': LIVERPOOL_REF if report['club']['name'] == 'Liverpool' else None,
            'tactic_editor':{'positions':list(POSITIONS),
                'formations':FORMATION_CATALOG,'locks':SCREENSHOT_LOCKS,
                'observed_contexts':OBSERVED_CONTEXTS,
                'team_views_current':CATALOG.get('team_views_current', []),
                'roles':{key:{
                    'name':r['name'],
                    'phase':r['phase'],
                    'positions':r['positions'],
                    'abbreviation':r.get('abbreviation', 'ROL'),
                    'behaviors':r.get('behaviors', []),
                    'subposition_rule':r.get('subposition_rule'),
                    'english':r.get('english', ''),
                    'spanish_status':r.get('spanish_status', '')
                } for key,r in ROLES.items()},
                'team_properties':{k:instruction('team',k,v['options'][0],'')['property'] for k,v in TI.items()},
                'player_options':{k:{'label':instruction('player',k,v['options'][0],'')['property'],
                    'phase':v['phase'],'options':[{'value':o,'label':instruction('player',k,o,'')['value']} for o in v['options']]} for k,v in PI.items()}},
            'instruction_options':{k:[{'value':o,'label':instruction('team',k,o,'')['value']} for o in v['options']] for k,v in TI.items()},
            'formations_catalog': [{'id': f['id'], 'name': f['name'], 'category': f.get('category', 'Formación'), 'defensive': f['defensive'], 'idea': f['idea']} for f in FORMATION_CATALOG],
            'methodology':{'formula':'80% atributos de la función + 20% atributos del estilo, multiplicado por (0,25 + 0,75 × familiaridad/20). Ambos promedios se llevan a escala 0–100.',
                           'lineup':'Se maximiza la suma del encaje de los once, sin repetir jugadores. Cada puesto pondera 80% función con balón y 20% función defensiva. Se evalúan las diez estructuras del catálogo y se presentan las tres de mayor encaje. El banco prioriza cobertura y compara ambas fases con la misma fórmula.',
                           'academy':'Se compara el mejor encaje actual del juvenil contra la tercera opción disponible del primer equipo con familiaridad de al menos 15/20 en una posición de esa función. Si hay menos de tres opciones, se usa la última disponible. Sin opciones, no se recomienda promoción. Una diferencia de hasta −3 puntos permite sugerir una prueba. No predice potencial ni evolución.',
                           'roles':{key:{
                               'name':v['name'],
                               'english':v['english'],
                               'positions':v['positions'],
                               'phase':v['phase'],
                               'weights':v['weights'],
                               'source':v['source'],
                               'abbreviation':v.get('abbreviation', 'ROL'),
                               'behaviors':v.get('behaviors', []),
                               'subposition_rule':v.get('subposition_rule'),
                               'key_attributes_ui_verified':v.get('key_attributes_ui_verified', False)
                           } for key,v in ROLES.items()}}}
