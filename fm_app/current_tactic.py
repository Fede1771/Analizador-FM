"""Stored tactic provenance and evaluation of the user's explicitly confirmed plan."""
from dataclasses import asdict
from fm_app.fm26 import ROLES, PI, TI, PLAYER_MENU, instruction, instruction_availability
from fm_app.instruction_rules import position_context
from fm_app.tactics import STYLES
from fm_app.contracts import check_support_runs_compatibility
from fm_app.recommendations import role_score, explanation
from fm_app.spatial import coverage

MENTALITIES={1:'Muy defensiva',2:'Defensiva',3:'Cauta',4:'Equilibrada',5:'Positiva',6:'Ofensiva',7:'Muy ofensiva'}
POSITIONS={'GK':(50,91),'DL':(13,70),'DR':(87,70),'DC':(50,76),'WBL':(12,58),'WBR':(88,58),'DM':(50,58),'MC':(50,44),'ML':(14,45),'MR':(86,45),'AMC':(50,33),'AML':(15,25),'AMR':(85,25),'STC':(50,19)}


def extract_stored_tactics(career, club_uid):
    records=[]
    for tactic in career.tactics():
        if tactic.club_uid!=club_uid:continue
        records.append({'id':f'{tactic.team_id}:{tactic.index}','team_slot':tactic.team_slot,
            'name':tactic.name or f'Táctica {tactic.index+1}', 'style_name':tactic.style_name,
            'mentality':MENTALITIES.get(tactic.mentality.raw,'Sin identificar'),
            'raw':asdict(tactic)})
    return {'available':True,'records':records,'active_identified':False,
        'limitations':'El lector recupera las copias guardadas y la mentalidad; no identifica la activa, el once, ni traduce posiciones, roles o instrucciones. Nombre y estilo requieren cotejo con el juego.'}


def coordinates(rows, key):
    values=[]
    for row in rows:
        position=row[key];x,y=POSITIONS[position]
        same=[i for i,r in enumerate(rows) if r[key]==position]
        index=same.index(len(values))
        if len(same)>1:
            x+= (index-(len(same)-1)/2)*(24 if position=='DC' else 25)
        values.append([max(5,min(95,x)),y])
    return values


POSITION_ES = {
    'GK': 'POR', 'DL': 'DFI', 'DR': 'DFD', 'DC': 'DFC',
    'WBL': 'CRI', 'WBR': 'CRD', 'DM': 'MCD', 'MC': 'MC',
    'ML': 'MI', 'MR': 'MD', 'AMC': 'MPC', 'AML': 'MPI',
    'AMR': 'MPD', 'STC': 'DLC',
}

POSITION_NAMES_ES = {
    'GK': 'Portero', 'DL': 'Lateral Izquierdo', 'DR': 'Lateral Derecho',
    'DC': 'Defensa Central', 'WBL': 'Carrilero Izquierdo', 'WBR': 'Carrilero Derecho',
    'DM': 'Mediocentro Defensivo', 'MC': 'Mediocentro', 'ML': 'Medio Izquierdo',
    'MR': 'Medio Derecho', 'AMC': 'Mediapunta Central', 'AML': 'Mediapunta Izquierdo',
    'AMR': 'Mediapunta Derecho', 'STC': 'Delantero Centro',
}


def audit_tactic(dataset, params):
    if params.get('confirmed') is not True:raise ValueError('Confirmá que el once, las posiciones y los roles coinciden con FM.')
    style=params.get('style','possession')
    if style not in STYLES:raise ValueError('Estilo no válido.')
    rows=params.get('lineup')
    if not isinstance(rows,list) or len(rows)!=11 or not all(isinstance(r,dict) for r in rows):raise ValueError('Confirmá once puestos.')
    by_id={p['uid']:p for p in dataset['players']}
    ids=[r.get('uid') for r in rows]
    if any(type(uid)!=int or uid not in by_id for uid in ids) or len(set(ids))!=11:raise ValueError('Elegí once jugadores del club, sin repeticiones.')
    stored_id=params.get('stored_id','')
    if stored_id and stored_id not in {r['id'] for r in dataset.get('stored_tactics',{}).get('records',[])}:raise ValueError('La táctica guardada cambió: volvé a elegirla.')
    for phase in ('ip','oop'):
        for row in rows:
            position=row.get(phase+'_position');role=row.get(phase+'_role')
            if position not in POSITIONS or role not in ROLES or position not in ROLES[role]['positions'] or ROLES[role]['phase']!=('in_possession' if phase=='ip' else 'out_of_possession'):
                raise ValueError('Confirmá posiciones y roles válidos en las dos fases.')
            sub_rule = ROLES[role].get('subposition_rule')
            if sub_rule:
                if 'min_central_defenders' in sub_rule:
                    cbs = sum(1 for r in rows if r.get(phase+'_position') == 'DC')
                    if cbs < sub_rule['min_central_defenders']:
                        raise ValueError(f'{by_id[row["uid"]]["name"]}: {ROLES[role]["name"]} ({sub_rule["description"]})')
                if 'min_defensive_midfielders' in sub_rule:
                    dms = sum(1 for r in rows if r.get(phase+'_position') == 'DM')
                    if dms < sub_rule['min_defensive_midfielders']:
                        raise ValueError(f'{by_id[row["uid"]]["name"]}: {ROLES[role]["name"]} ({sub_rule["description"]})')
        if sum(r[phase+'_position']=='GK' for r in rows)!=1:raise ValueError('El once necesita un arquero en cada fase.')
    points={phase:coordinates(rows,phase+'_position') for phase in ('ip','oop')}
    lineup=[];advice=[]
    for index,row in enumerate(rows):
        p=by_id[row['uid']];entry={'uid':p['uid'],'ip':points['ip'][index],'oop':points['oop'][index]}
        values=[]
        supplied=row.get('instructions',{})
        if not isinstance(supplied,dict):raise ValueError('Instrucciones individuales no válidas.')
        for key,value in supplied.items():
            if key not in PI or value not in PI[key]['options']:
                raise ValueError(f'{p["name"]}: Instrucción individual no válida ({key}={value}).')
        marking_mode = supplied.get('marking_target_oop')
        if marking_mode == 'Mark Specific' and not row.get('marking_target_player') and not row.get('marking_target_player_uid'):
            raise ValueError(f'{p["name"]}: La marca específica requiere indicar el jugador rival a marcar.')
        if marking_mode == 'Mark Position' and not row.get('marking_target_position'):
            raise ValueError(f'{p["name"]}: Marcar posición requiere indicar el puesto rival a cubrir.')
        for phase,key in [('ip','in_possession'),('oop','out_of_possession')]:
            role_id=row[phase+'_role'];position=row[phase+'_position'];r=ROLES[role_id]
            pos_label = POSITION_ES.get(position, position)
            pos_full = POSITION_NAMES_ES.get(position, position)
            phase_label = 'Con posesión (CP)' if phase == 'ip' else 'Sin posesión (SP)'
            value=role_score(p,role_id,style,position);values.append(value)
            alternatives=sorted([(rid,role_score(p,rid,style,position)) for rid,ref in ROLES.items() if ref['phase']==r['phase'] and position in ref['positions'] and rid!=role_id],key=lambda v:(-v[1],v[0]))[:2]
            context = position_context([r[phase+'_position'] for r in rows], index, row.get('instruction_scope','Posición'))
            plan=explanation(p,{'id':role_id,'score':value,'position':position,'alternatives':[]},style,context)
            plan['comparison']='Rol confirmado por vos. Las alternativas siguientes comparan atributos; revisá su función antes de cambiarlas.'
            plan['alternatives']=[{'id':rid,'name':ROLES[rid]['name'],'score':s} for rid,s in alternatives]
            chosen=[]
            menu=PLAYER_MENU[r['phase']]
            for instruction_id in menu:
                availability = instruction_availability(role_id, instruction_id, context)
                locked = availability['locked_value'] if availability['locked'] else None
                selected=supplied.get(instruction_id)
                if locked is not None and selected is not None and selected!=locked:raise ValueError(f'{p["name"]}: {instruction_id} está bloqueada por el rol.')
                if selected is not None or locked is not None:
                    item = instruction('player',instruction_id,selected if selected is not None else locked,'Valor confirmado por vos.' if selected is not None else 'Valor bloqueado comprobado en las capturas.','confirmed' if selected is not None else 'role')
                    item.update(availability)
                    chosen.append(item)
            plan['instructions']=chosen
            plan['unconfirmed_instructions']=len(menu)-len(chosen)
            plan['behaviors']=r.get('behaviors',[])
            plan['abbreviation']=r.get('abbreviation','ROL')
            plan['scope']=row.get('instruction_scope','Posición')
            entry[key]=plan
            if alternatives and alternatives[0][1]>=value+3:
                alt_role=ROLES[alternatives[0][0]]
                advice.append({
                    'title':f'Rol de {p["name"]}',
                    'player_uid': p['uid'],
                    'player_name': p['name'],
                    'phase': phase,
                    'phase_label': phase_label,
                    'detail':f'En {phase_label}, su rol actual es {r["name"]} en {pos_label} ({value:.1f}). Probar {alt_role["name"]} ({alternatives[0][1]:.1f}) sube su encaje de atributos (+{alternatives[0][1]-value:.1f} pts) conservando al jugador.',
                    'category':'role_alt',
                    'severity':'info',
                    'badge':'🔵 Optimización de rol',
                    'action':f'Probar {alt_role["name"]} en {pos_label} (+{alternatives[0][1]-value:.1f} pts)',
                    'chips':[f'Fase: {phase_label}', f'Puesto: {pos_label}', f'Rol sugerido: {alt_role["name"]}']
                })
            fam=p['positions'].get(position.lower(),1)
            if fam<15:
                natural_positions = p.get('natural_positions', [])
                valid_positions = [pos_code for pos_code in natural_positions if any(ref['phase'] == r['phase'] and pos_code in ref['positions'] for ref in ROLES.values())]
                if not valid_positions:
                    candidates_pos = [(pos_code.upper(), f_val) for pos_code, f_val in p['positions'].items() if f_val >= 15 and any(ref['phase'] == r['phase'] and pos_code.upper() in ref['positions'] for ref in ROLES.values())]
                    best_target = max(candidates_pos, key=lambda x: x[1])[0] if candidates_pos else position
                else:
                    best_target = valid_positions[0]
                best_target_label = POSITION_ES.get(best_target, best_target)
                best_target_full = POSITION_NAMES_ES.get(best_target, best_target)
                target_fam = p['positions'].get(best_target.lower(), 20)
                target_roles = [(rid, role_score(p, rid, style, best_target)) for rid, ref in ROLES.items() if ref['phase'] == r['phase'] and best_target in ref['positions']]
                best_target_role_name = ROLES[max(target_roles, key=lambda x: x[1])[0]]['name'] if target_roles else r['name']
                advice.append({
                    'title': f'Puesto de {p["name"]}',
                    'player_uid': p['uid'],
                    'player_name': p['name'],
                    'phase': phase,
                    'phase_label': phase_label,
                    'current_position': pos_label,
                    'suggested_position': best_target_label,
                    'suggested_role': best_target_role_name,
                    'detail': f'En {phase_label}, juega en {pos_label} ({pos_full}) donde tiene familiaridad regular de {fam}/20. Recomendado cambiar su posición defensiva a {best_target_label} ({best_target_full}, {target_fam}/20 Natural) con el rol de {best_target_role_name} para jugar en su puesto natural sin penalización de rendimiento.',
                    'category': 'familiarity',
                    'severity': 'purple',
                    'badge': '🟣 Posición no natural',
                    'action': f'Cambiar puesto: de {pos_label} ({fam}/20) ➔ a {best_target_label} ({target_fam}/20 Natural)',
                    'chips': [f'Fase: {phase_label}', f'Puesto actual: {pos_label} ({fam}/20)', f'Recomendado: {best_target_label} (Natural)', f'Rol: {best_target_role_name}']
                })
        entry['score']=round(.8*values[0]+.2*values[1],1);lineup.append(entry)
        candidates=[]
        for other in dataset['players']:
            if other['uid'] in ids or other['team_slot']!=dataset['default_primary_slot']:continue
            alternative=.8*role_score(other,row['ip_role'],style,row['ip_position'])+.2*role_score(other,row['oop_role'],style,row['oop_position'])
            if alternative>=entry['score']+3:candidates.append((alternative,other))
        if candidates:
            value,other=max(candidates,key=lambda v:(v[0],-v[1]['uid']))
            advice.append({
                'title':f'Alternativa para {p["name"]}',
                'player_uid': p['uid'],
                'player_name': p['name'],
                'phase': 'both',
                'phase_label': 'Ambas fases',
                'detail':f'{other["name"]} ofrece {value:.1f} frente a {entry["score"]:.1f} en los mismos roles y puestos de ambas fases. Probarlo conserva la estructura.',
                'category':'player_alt',
                'severity':'success',
                'badge':'🟢 Mejor encaje de plantel',
                'action':f'Probar a {other["name"]} ({value:.1f} vs {entry["score"]:.1f})',
                'chips':['Fase: Ambas fases', f'{other["name"]}: {value:.1f}', f'{p["name"]}: {entry["score"]:.1f}']
            })
        if supplied.get('pressing_oop')=='More Often' and supplied.get('marking_oop')=='Mark Tighter' and row['oop_position'] in ('DC','DM'):
            pos_label = POSITION_ES.get(row['oop_position'], row['oop_position'])
            action_text = f'En {p["name"]}: evaluar cambiar Presión a «Normal» para escalonar la zaga y hacer cobertura'
            advice.append({
                'title':f'Cobertura de {p["name"]}',
                'player_uid': p['uid'],
                'player_name': p['name'],
                'phase': 'oop',
                'phase_label': 'Sin posesión (SP)',
                'detail':'En Sin posesión (SP), presionar más y marcar de cerca al mismo tiempo puede sacarlo de zona y dejar la espalda libre. Conviene que uno anticipe y el otro conserve la zona para escalonar la zaga.',
                'category':'coverage',
                'severity':'warning',
                'badge':'🟡 Cobertura defensiva',
                'action': action_text,
                'chips':['Fase: Sin posesión (SP)', 'Presión: Más a menudo', 'Marca: De cerca', f'Puesto: {pos_label}']
            })
        if supplied.get('tackling_oop')=='Tackle Harder':
            if p['attributes']['tackling']<10:
                advice.append({
                    'title':f'Entradas de {p["name"]}',
                    'player_uid': p['uid'],
                    'player_name': p['name'],
                    'phase': 'oop',
                    'phase_label': 'Sin posesión (SP)',
                    'detail':f'En Sin posesión (SP), tiene Entradas {p["attributes"]["tackling"]}/20 y agresividad {p["attributes"]["aggression"]}/20. Con la orden de «Entrar más fuerte» y la orden colectiva de ser agresivos, arriesga tarjetas amarillas y expulsiones tempranas.',
                    'category':'discipline',
                    'severity':'danger',
                    'badge':'🔴 Alto riesgo de tarjetas',
                    'action':f'Cambiar a «Entradas en Normal» (entradas {p["attributes"]["tackling"]}/20)',
                    'chips':['Fase: Sin posesión (SP)', f'Entradas: {p["attributes"]["tackling"]}/20 (baja)', f'Agresividad: {p["attributes"]["aggression"]}/20', 'Orden: Entrar más fuerte']
                })
            else:
                advice.append({
                    'title':f'Entradas de {p["name"]}',
                    'player_uid': p['uid'],
                    'player_name': p['name'],
                    'phase': 'oop',
                    'phase_label': 'Sin posesión (SP)',
                    'detail':f'En Sin posesión (SP), entrar más fuerte aumenta el compromiso en el duelo físico. Con Entradas {p["attributes"]["tackling"]}/20 y agresividad {p["attributes"]["aggression"]}/20, monitorear faltas y tarjetas amarillas.',
                    'category':'discipline',
                    'severity':'warning',
                    'badge':'🟠 Duelo agresivo',
                    'action':'Monitorear faltas y tarjetas amarillas en el partido',
                    'chips':['Fase: Sin posesión (SP)', f'Entradas: {p["attributes"]["tackling"]}/20', f'Agresividad: {p["attributes"]["aggression"]}/20', 'Orden: Entrar más fuerte']
                })
        if supplied.get('shoot_ip')=='Shoot More Often':
            advice.append({
                'title':f'Remates de {p["name"]}',
                'player_uid': p['uid'],
                'player_name': p['name'],
                'phase': 'ip',
                'phase_label': 'Con posesión (CP)',
                'detail':f'En Con posesión (CP), tiene Remate {p["attributes"]["finishing"]}/20 y tiros lejanos {p["attributes"]["long_shots"]}/20. Como el equipo juega con «Llevar el balón al área», evaluar cambiar a Normal para no apresurar remates desde lejos ante bloques cerrados.',
                'category':'shooting',
                'severity':'info',
                'badge':'🎯 Selección de tiro',
                'action':f'Comparar con «Disparos en Normal» (remate {p["attributes"]["finishing"]}/20, lejanos {p["attributes"]["long_shots"]}/20)',
                'chips':['Fase: Con posesión (CP)', f'Remate: {p["attributes"]["finishing"]}/20', f'Tiros lejanos: {p["attributes"]["long_shots"]}/20', 'Orden: Disparar más']
            })
    team=params.get('team',{})
    if not isinstance(team,dict):raise ValueError('Instrucciones de equipo no válidas.')
    for key,value in team.items():
        if key not in TI or value not in TI[key]['options']:raise ValueError('Instrucción de equipo no válida.')
    ok, err = check_support_runs_compatibility(team.get('overlap_ip'), team.get('underlap_ip'))
    if not ok:
        raise ValueError(err)
    if team.get('short_goalkeeper_distribution_oop') == 'Yes':
        advice.append({
            'title': 'Impedir salida en corto del portero rival',
            'player_uid': None,
            'player_name': None,
            'phase': 'oop',
            'phase_label': 'Sin posesión (SP)',
            'detail': 'En Sin posesión (SP), tu equipo presiona la salida corta del arquero rival para forzarlo a dividir el balón en largo.',
            'category': 'team_press',
            'severity': 'info',
            'badge': '🧤 Salida rival',
            'action': 'Obligar al portero rival a jugar en largo',
            'chips': ['Fase: Sin posesión (SP)', 'Presión adelantada', 'Impedir salida en corto']
        })
    defenders=[by_id[r['uid']] for r in rows if r['oop_position']=='DC']
    if team.get('defensive_line_oop') in ('Higher','Much Higher') and any(p['attributes']['pace']<13 for p in defenders):
        advice.append({
            'title':'Espacio a espaldas de la zaga',
            'player_uid': None,
            'player_name': None,
            'phase': 'oop',
            'phase_label': 'Sin posesión (SP)',
            'detail':'En Sin posesión (SP), con línea más adelantada y centrales de ritmo moderado (< 13), conviene bajar un nivel a «Alta» ante delanteros rivales muy veloces.',
            'category':'team_space',
            'severity':'warning',
            'badge':'⚠️ Espacio a la espalda',
            'action':'Bajar línea a «Alta» ante rivales veloces',
            'chips':['Fase: Sin posesión (SP)', 'Línea: Más adelantada', 'Zaga con velocidad moderada']
        })
    if team.get('defensive_transition_oop')=='Counter-Press' and sum(by_id[uid]['attributes']['stamina'] for uid in ids)/11<12:
        advice.append({
            'title':'Carga física de la contrapresión',
            'player_uid': None,
            'player_name': None,
            'phase': 'oop',
            'phase_label': 'Sin posesión (SP)',
            'detail':'En Sin posesión (SP), la resistencia media del once está por debajo de 12. Alternar con «Reagruparse» para cuidar el físico en segundas partes.',
            'category':'team_stamina',
            'severity':'warning',
            'badge':'⚡ Desgaste físico',
            'action':'Alternar con «Reagruparse» para cuidar la estamina',
            'chips':['Fase: Sin posesión (SP)', 'Transición: Contrapresión', 'Cuidado físico']
        })
    count=sum(x[k]['unconfirmed_instructions'] for x in lineup for k in ('in_possession','out_of_possession'))
    return {'dataset_id':dataset['id'],'name':str(params.get('name','Mi táctica'))[:100], 'style':style,
        'score':round(sum(x['score'] for x in lineup)/11,1),'lineup':lineup,'advice':advice,
        'coverage':coverage(lineup,by_id,team),'unconfirmed_player_instructions':count,
        'unconfirmed_team_instructions':len(TI)-len(team),
        'limits':'Ponderación analítica propia de Touchline (80% CP / 20% SP) basada en encaje de atributos y familiaridad posicional. No representa probabilidades deportivas ni pesos internos del motor de partidos de FM26. Las órdenes sin confirmar no se sustituyen por propuestas. Mentalidad, rival y movimientos dinámicos no están modelados.'}
