"""Transparent spatial estimate; these are not FM engine occupation probabilities."""
import math


def coverage(lineup, by_id, team=None):
    team=team or {}
    output={}
    for phase, key in [('ip','in_possession'),('oop','out_of_possession')]:
        players=[]
        for slot in lineup:
            role=slot[key]
            if role['position']=='GK':
                continue
            x,y=slot[phase]
            stem=role['id'].rsplit('_',1)[0] if role.get('id') else ''
            instructions={i['id']:i['value_en'] for i in role.get('instructions',[])}
            # Role shape is a fallback only; confirmed individual instructions take precedence.
            direction=instructions.get('dribbling_direction_ip')
            if phase=='ip':
                if direction=='Cut Inside With Ball' or (direction is None and stem in ('inside_winger','inside_forward','playmaking_winger')):
                    x+=(50-x)*.32
                if instructions.get('attacking_width_ip')=='Sit Narrower':x+=(50-x)*.18
                if instructions.get('attacking_width_ip')=='Stay Wider':x=10 if x<50 else 90
                runs=instructions.get('forward_runs_ip')
                if runs=='Make More Runs' or (runs is None and stem in ('wing_back','second_striker','channel_forward')):y-=8
                if runs=='Make Fewer Runs':y+=5
                if stem in ('deep_lying_forward','false_nine'):y+=10
            else:
                if stem.startswith('pressing_'):y-=6
                if role['position'] in ('DC','DL','DR','WBL','WBR'):
                    y+={'Much Lower':10,'Lower':5,'Standard':0,'Higher':-5,'Much Higher':-10}.get(team.get('defensive_line_oop'),0)
                else:
                    y+={'High Press':-6,'Mid Block':0,'Low Block':6}.get(team.get('line_of_engagement_oop'),0)
            a=by_id[slot['uid']]['attributes']
            ability=sum(a[k] for k in (('off_the_ball','decisions','anticipation') if phase=='ip' else ('positioning','anticipation','work_rate')))/3*5
            familiarity=by_id[slot['uid']]['positions'].get(role['position'].lower(),1)
            ability*=.25+.75*familiarity/20
            players.append((slot['uid'],x,y,ability))
        cells=[]
        for row in range(5):
            for col in range(5):
                cx,cy=10+col*20,10+row*20
                ranked=[]
                for uid,x,y,ability in players:
                    distance=math.hypot(cx-x,cy-y)
                    value=round(ability*math.exp(-.5*(distance/24)**2),1)
                    ranked.append({'uid':uid,'name':by_id[uid]['name'],'score':value,'distance':round(distance,1)})
                ranked.sort(key=lambda p:(-p['score'],p['uid']))
                strength=ranked[0]['score'] if ranked else 0
                cells.append({'row':row,'col':col,'strength':strength,
                    'level':'high' if strength>=50 else 'medium' if strength>=25 else 'low',
                    'players':ranked[:3]})
        output[phase]=cells
    return {'phases':output,'method':'Anclas posicionales ajustadas por rol e instrucciones; influencia = atributos de movimiento × familiaridad × exp(−0,5 × (distancia/24)²). Línea defensiva: ±5 por nivel para defensores; bloque alto/bajo: ∓6 para el resto, solo si esas órdenes están confirmadas. Cada celda muestra hasta tres apoyos; color según el mayor índice (verde ≥50, amarillo ≥25, rojo <25). No predice ocupación real, probabilidades ni estrellas de FM. El arquero se excluye de los apoyos de campo.'}
