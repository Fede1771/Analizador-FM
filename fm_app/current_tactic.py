"""Stored tactic provenance and evaluation of the user's explicitly confirmed plan."""
from dataclasses import asdict
from fm_app.fm26 import ROLES, PI, TI, PLAYER_MENU, SCREENSHOT_LOCKS, instruction
from fm_app.tactics import STYLES
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
            if position not in POSITIONS or role not in ROLES or position not in ROLES[role]['positions'] or ROLES[role]['phase']!=('in_possession' if phase=='ip' else 'out_of_possession'):raise ValueError('Confirmá posiciones y roles válidos en las dos fases.')
        if sum(r[phase+'_position']=='GK' for r in rows)!=1:raise ValueError('El once necesita un arquero en cada fase.')
    points={phase:coordinates(rows,phase+'_position') for phase in ('ip','oop')}
    lineup=[];advice=[]
    for index,row in enumerate(rows):
        p=by_id[row['uid']];entry={'uid':p['uid'],'ip':points['ip'][index],'oop':points['oop'][index]}
        values=[]
        supplied=row.get('instructions',{})
        if not isinstance(supplied,dict):raise ValueError('Instrucciones individuales no válidas.')
        for key,value in supplied.items():
            if key not in PI or value not in PI[key]['options']:raise ValueError('Instrucción individual no válida.')
        for phase,key in [('ip','in_possession'),('oop','out_of_possession')]:
            role_id=row[phase+'_role'];position=row[phase+'_position'];r=ROLES[role_id]
            value=role_score(p,role_id,style,position);values.append(value)
            alternatives=sorted([(rid,role_score(p,rid,style,position)) for rid,ref in ROLES.items() if ref['phase']==r['phase'] and position in ref['positions'] and rid!=role_id],key=lambda v:(-v[1],v[0]))[:2]
            plan=explanation(p,{'id':role_id,'score':value,'position':position,'alternatives':[]},style)
            plan['comparison']='Rol confirmado por vos. Las alternativas siguientes comparan atributos; revisá su función antes de cambiarlas.'
            plan['alternatives']=[{'id':rid,'name':ROLES[rid]['name'],'score':s} for rid,s in alternatives]
            # Never pass generated player instructions off as the user's current settings.
            chosen=[]
            menu=PLAYER_MENU[r['phase']]
            for instruction_id in menu:
                locked=SCREENSHOT_LOCKS.get(role_id,{}).get(instruction_id)
                selected=supplied.get(instruction_id)
                if locked is not None and selected is not None and selected!=locked:raise ValueError(f'{p["name"]}: {instruction_id} está bloqueada por el rol.')
                if selected is not None or locked is not None:
                    chosen.append(instruction('player',instruction_id,selected if selected is not None else locked,'Valor confirmado por vos.' if selected is not None else 'Valor bloqueado comprobado en las capturas.','confirmed' if selected is not None else 'role'))
            plan['instructions']=chosen;plan['unconfirmed_instructions']=len(menu)-len(chosen)
            entry[key]=plan
            if alternatives and alternatives[0][1]>=value+3:
                advice.append({'title':p['name'],'detail':f'{r["name"]} en {position}: {value:.1f}. Probar {ROLES[alternatives[0][0]]["name"]} ({alternatives[0][1]:.1f}) conserva al jugador y mejora su encaje de atributos; cambia su función y requiere revisar el equilibrio.'})
            if p['positions'].get(position.lower(),1)<15:advice.append({'title':p['name'],'detail':f'Familiaridad baja en {position}: {p["positions"].get(position.lower(),1)}/20. Revisá la posición antes de cambiar de jugador.'})
        entry['score']=round(.8*values[0]+.2*values[1],1);lineup.append(entry)
        candidates=[]
        for other in dataset['players']:
            if other['uid'] in ids or other['team_slot']!=dataset['default_primary_slot']:continue
            alternative=.8*role_score(other,row['ip_role'],style,row['ip_position'])+.2*role_score(other,row['oop_role'],style,row['oop_position'])
            if alternative>=entry['score']+3:candidates.append((alternative,other))
        if candidates:
            value,other=max(candidates,key=lambda v:(v[0],-v[1]['uid']))
            advice.append({'title':f'Alternativa para {p["name"]}','detail':f'{other["name"]} ofrece {value:.1f} frente a {entry["score"]:.1f} en los mismos roles y posiciones de ambas fases. Probarlo conserva la estructura. Revisá disponibilidad e inscripción en FM; una alternativa no puede cubrir varios puestos a la vez.'})
        if supplied.get('pressing_oop')=='More Often' and supplied.get('marking_oop')=='Mark Tighter' and row['oop_position'] in ('DC','DM'):
            advice.append({'title':f'Cobertura de {p["name"]}','detail':'Presionar más y marcar de cerca puede sacar a este jugador de su zona. Probá primero volver una de esas órdenes a Normal y observá las coberturas, manteniendo el resto.'})
        if supplied.get('tackling_oop')=='Tackle Harder':
            if p['attributes']['tackling']<10:
                advice.append({'title':f'Entradas de {p["name"]}','detail':f'Entradas {p["attributes"]["tackling"]}/20 y agresividad {p["attributes"]["aggression"]}/20 con la orden de entrar más fuerte aumentan las faltas y tarjetas sin asegurar mayor recuperación. Probar entradas en Normal es una mejora razonable para evaluar, conservando por separado su presión.'})
            else:
                advice.append({'title':f'Entradas de {p["name"]}','detail':f'Entrar más fuerte aumenta el compromiso en el duelo; no garantiza recuperar mejor. Entradas {p["attributes"]["tackling"]}/20, agresividad {p["attributes"]["aggression"]}/20: revisar faltas y amarillas antes de mantener la orden.'})
        if supplied.get('shoot_ip')=='Shoot More Often':
            advice.append({'title':f'Remates de {p["name"]}','detail':f'Remate {p["attributes"]["finishing"]}/20 y tiros lejanos {p["attributes"]["long_shots"]}/20. Compará Normal contra disparar más: calidad de ocasión y pérdidas, además del volumen de tiros.'})
    team=params.get('team',{})
    if not isinstance(team,dict):raise ValueError('Instrucciones de equipo no válidas.')
    for key,value in team.items():
        if key not in TI or value not in TI[key]['options']:raise ValueError('Instrucción de equipo no válida.')
    defenders=[by_id[r['uid']] for r in rows if r['oop_position']=='DC']
    if team.get('defensive_line_oop') in ('Higher','Much Higher') and any(p['attributes']['pace']<13 for p in defenders):advice.append({'title':'Espacio a espaldas de la zaga','detail':'Línea alta y un central con velocidad menor a 13: probá bajar un nivel la línea antes de modificar toda la estructura.'})
    if team.get('defensive_transition_oop')=='Counter-Press' and sum(by_id[uid]['attributes']['stamina'] for uid in ids)/11<12:advice.append({'title':'Carga de la contrapresión','detail':'La resistencia media está por debajo de 12. Probá reagruparte o dosificá la presión.'})
    count=sum(x[k]['unconfirmed_instructions'] for x in lineup for k in ('in_possession','out_of_possession'))
    return {'dataset_id':dataset['id'],'name':str(params.get('name','Mi táctica'))[:100], 'style':style,
        'score':round(sum(x['score'] for x in lineup)/11,1),'lineup':lineup,'advice':advice,
        'coverage':coverage(lineup,by_id,team),'unconfirmed_player_instructions':count,
        'unconfirmed_team_instructions':len(TI)-len(team),
        'limits':'El índice compara atributos y familiaridad. No mide eficacia del sistema ni predice resultados. Las órdenes sin confirmar no se sustituyen por propuestas. El mapa usa anclas del puesto y comportamiento típico del rol donde faltan instrucciones. Mentalidad, rival y movimientos dinámicos no están modelados.'}
