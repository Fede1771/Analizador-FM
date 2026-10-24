"""Position-valid FM26 role pairing, assignment, instructions and player explanations."""

from collections import Counter



from fm_app.tactics import ATTRS, STYLES, FORMATIONS, FORMATION_CATALOG, FORMATIONS_BY_ID, parse_tactical_prompt

from fm_app.fm26 import ROLES, IP_POOLS, OOP_POOLS, player_instructions, team_instructions





def average(player, weights):

    return sum(player['attributes'][k]*w for k,w in weights.items())/sum(weights.values())*5





def role_score(player, role, style='possession', position=None):

    r=ROLES[role]

    if position is not None and position not in r['positions']:

        raise ValueError(f'{role} is unavailable at {position}')

    familiarity=player['positions'].get(position.lower(),1) if position else max(player['positions'].get(p.lower(),1) for p in r['positions'])

    quality=.8*average(player,r['weights'])+.2*average(player,STYLES[style]['weights'])

    return round(quality*(.25+.75*familiarity/20),1)





def choose(player,phase,position,style,kind=None):

    pools=IP_POOLS if phase=='ip' else OOP_POOLS

    ids=[stem+'_'+phase for stem in pools[position]]

    a=player['attributes']

    # Formation policy: an anchor stays behind the ball; one interior can create, the other supports.

    if phase=='ip' and position=='MC' and kind=='cm':

        ids=[r for r in ids if r in ('central_midfielder_ip','channel_midfielder_ip','attacking_midfielder_ip')]

    if phase=='ip' and position=='STC' and kind=='target':

        ids=['target_forward_ip','deep_lying_forward_ip','centre_forward_ip']

    if phase=='ip' and position in ('AML','AMR'):

        allowed={'wide':('winger','wide_forward','inside_winger'),

                 'possession':('winger','inside_winger','playmaking_winger'),

                 'press':('winger','inside_forward','wide_forward'),

                 'counter':('winger','inside_forward','wide_forward')}[style]

        ids=[r for r in ids if r.rsplit('_',1)[0] in allowed]

    if phase=='ip' and kind=='cb':

        ids=[r for r in ids if r!='ball_playing_centre_back_ip']

    if phase=='ip' and position=='GK' and min(a['passing'],a['first_touch'],a['decisions'])<12:

        ids=[r for r in ids if r!='ball_playing_goalkeeper_ip']

    if phase=='oop':

        if style!='press' or min(a['work_rate'],a['stamina'])<13:

            ids=[r for r in ids if not r.startswith('pressing_')]

        if style not in ('counter','wide'):

            ids=[r for r in ids if not r.startswith('central_outlet_')]

    ranked=sorted(((r,role_score(player,r,style,position)) for r in ids),key=lambda x:(-x[1],x[0]))

    return {'id':ranked[0][0],'score':ranked[0][1],'position':position,'alternatives':ranked[1:3]}





PURPOSE={

 'gk':'Participar en la salida con balón sin abandonar la protección de la portería.',

 'dc':'Dar seguridad a la última línea y conservar una salida de pase.',

 'flank':'Dar una opción por banda y conectar con los compañeros cercanos.',

 'dm':'Ofrecer una base por delante de los centrales y sostener el equilibrio.',

 'mc':'Conectar la progresión con el ataque sin duplicar la función del otro interior.',

 'amc':'Recibir entre líneas y generar una ventaja cerca del área.',

 'stc':'Dar una referencia al ataque y amenazar el área rival.',

}

ROLE_PURPOSE={

 'ball_playing_goalkeeper':'Participa en la construcción y se ofrece fuera del arco como opción de pase; vigilar pérdidas cerca del arco.',

 'no_nonsense_goalkeeper':'Juega con prudencia, conserva su posición y reduce los riesgos con los pies al distribuir bajo presión.',

 'goalkeeper':'Distribuye según la estrategia del equipo, sin una especialización fija de construcción.',

 'ball_playing_centre_back':'Mantiene la posición defensiva y utiliza pases más ambiciosos para superar líneas e iniciar ataques.',

 'centre_back':'Conserva su posición en la zaga para proteger al equipo ante una pérdida y evitar riesgos innecesarios.',

 'no_nonsense_center_back':'Mantiene la posición y simplifica al máximo el uso de la pelota, despejando sin comprometerse.',

 'covering_centre_back':'Protege la profundidad y vigila los balones a la espalda de la zaga sin desordenar la línea.',

 'wing_back':'Avanza y se proyecta por la banda para proporcionar amplitud y profundidad al ataque.',

 'full_back':'Ofrece amplitud desde una posición más contenida, equilibrando la subida con la protección de su sector.',

 'holding_full_back':'Conserva su posición y prioriza proteger su sector por delante de sumarse a campo contrario.',

 'pressing_full_back':'Adelanta su intervención para presionar y encimar a los rivales de banda en cuanto reciben.',

 'deep_lying_playmaker':'Organiza desde una posición retrasada y busca pases que hagan progresar al equipo.',

 'defensive_midfielder':'Mantiene una posición de apoyo por delante de la zaga y utiliza la pelota con prudencia y equilibrio.',

 'midfield_playmaker':'Asume la creación desde el centro del campo y busca hacer progresar el juego mediante sus pases.',

 'advanced_playmaker':'Encuentra espacios entre líneas para recibir y crear ocasiones mediante pases filtrados de riesgo.',

 'channel_midfielder':'Ataca los canales y espacios interiores para asociarse con los atacantes de banda y romper líneas.',

 'central_midfielder':'Ofrece apoyo general desde el centro con un cometido equilibrado entre progresión y cobertura.',

 'wide_midfielder':'Conserva una posición abierta en banda para ofrecer apoyo por fuera y conectar con el lateral.',

 'attacking_midfielder':'Actúa entre mediocampo y ataque, buscando espacios entre líneas y aportando amenaza cerca del área.',

 'second_striker':'Se adelanta desde la mediapunta para incorporarse a la línea de ataque y buscar el remate.',

 'free_role':'Dispone de libertad total para encontrar espacios, conducir e influir en la creación; requiere equilibrio detrás.',

 'inside_winger':'Entra hacia dentro con una función principalmente creativa y asociativa para combinar con los medios.',

 'inside_forward':'Se mueve desde la banda hacia el centro para atacar el área y buscar el gol (finalización directa).',

 'wide_forward':'Mantiene amplitud y aporta amenaza de gol directa atacando el segundo palo o la diagonal desde afuera.',

 'winger':'Mantiene la amplitud para generar juego, desbordar por velocidad y enviar centros al área rival.',

 'playmaking_winger':'Se mete hacia zonas interiores para asumir mayor responsabilidad en la organización y creación.',

 'tracking_winger':'Retrocede desde la banda para colaborar con el lateral y reforzar la defensa de su costado.',

 'tracking_wide_midfielder':'Acompaña el repliegue y refuerza las ayudas en la banda.',

 'target_forward':'Sirve de referencia física y aérea adelantada para aguantar balones directos y ganar duelos de segunda jugada.',

 'deep_lying_forward':'Baja a recibir de espaldas, retiene la pelota y enlaza el mediocampo con el ataque para los que llegan de frente.',

 'channel_forward':'Ataca los espacios y canales entre lateral y central para recibir pases profundos y amenazar el arco.',

 'false_nine':'Retrocede hacia la mediapunta para recibir y conectar el juego, arrastrando centrales y liberando espacios.',

 'poacher':'Juega cerca de la última línea y prioriza encontrar oportunidades para definir dentro del área.',

 'centre_forward':'Actúa como amenaza de gol y referencia de ataque desde el centro, capaz de asociarse y definir.',

 'tracking_centre_forward':'Participa en el trabajo defensivo antes de ofrecer una salida en ataque.',

 'central_outlet_centre_forward':'Reduce el repliegue defensivo y permanece adelantado como vía de escape inmediata para lanzar la contra.',

}





OOP_PURPOSE={

 'goalkeeper':'Protege el arco y responde a remates y centros bajo la organización general del equipo.',

 'sweeper_keeper':'Sale con valentía de su línea para interceptar pases profundos y cortar contragolpes a la espalda de la defensa.',

 'line_holding_keeper':'Permanece cerca del arco sobre la línea de meta, dejando a sus compañeros la cobertura de espacios lejanos.',

 'centre_back':'Cumple la función defensiva general de frenar atacantes, bloquear disparos y proteger el área propia.',

 'covering_centre_back':'Prioriza mantener la línea y reaccionar al peligro profundo sin salir precipitadamente a la marca.',

 'full_back':'Defiende su banda según la organización colectiva y frena el avance del extremo contrario.',

 'holding_full_back':'Conserva su posición con un comportamiento defensivo prudente, priorizando no ser desbordado.',

 'pressing_full_back':'Adelanta su intervención para encimar y presionar a los rivales de banda en la salida.',

 'wing_back':'Defiende el carril exterior dentro de la estructura colectiva coordinando su repliegue.',

 'holding_wing_back':'Mantiene su posición en el carril con un comportamiento defensivo prudente y coberturas.',

 'pressing_wing_back':'Da pasos hacia adelante para intervenir en la presión y acosar la banda rival.',

 'defensive_midfielder':'Protege la zona por delante de los centrales y tapa las líneas de pase interiores.',

 'screening_defensive_midfielder':'Conserva su posición en la zona 14 para tapar pases interiores y bloquear disparos desde la medialuna.',

 'central_midfielder':'Sostiene el bloque central y coordina la presión y las coberturas con sus compañeros.',

 'screening_central_midfielder':'Mantiene su posición para cerrar los pasillos interiores en el centro del campo y evitar filtraciones.',

 'pressing_central_midfielder':'Abandona el bloque para acosar al portador y disputar la pelota más arriba con intensidad.',

 'wide_covering_central_midfielder':'Se desplaza hacia los costados para cubrir espacios y apoyar la defensa de banda junto al lateral.',

 'attacking_midfielder':'Molesta la salida rival y cierra las opciones de pase retrasadas desde la mediapunta.',

 'tracking_attacking_midfielder':'Baja para colaborar con el mediocampo y reforzar la defensa en bloque medio.',

 'winger':'Colabora en la presión y en la protección de su banda desde la línea de medios.',

 'tracking_winger':'Baja y retrocede para ayudar al lateral y reforzar la defensa compacta de su costado.',

 'wide_midfielder':'Defiende desde la banda dentro de la estructura colectiva para sostener la línea de cuatro medios.',

 'tracking_wide_midfielder':'Retrocede para apoyar la defensa y acompañar el repliegue por su banda.',

 'centre_forward':'Inicia el trabajo defensivo sobre la salida de los centrales rivales desde la primera línea.',

 'tracking_centre_forward':'Baja para colaborar con el mediocampo cuando el rival tiene la pelota, compactando al equipo.',

 'central_outlet_centre_forward':'Reduce el retroceso defensivo y permanece adelantado como vía de escape inmediata para lanzar la contra.',

}







TACTICAL_SUMMARY = {

    'ball_playing_goalkeeper_ip': 'Participa en la construcción y se ofrece fuera del arco como opción de pase',

    'goalkeeper_ip': 'Distribuye según la estrategia colectiva sin riesgo de salida',

    'no_nonsense_goalkeeper_ip': 'Conserva su posición y despeja sin arriesgar con los pies',

    'goalkeeper_oop': 'Protección del arco y respuesta a centros y remates',

    'sweeper_keeper_oop': 'Sale de su línea a interceptar pases profundos y cortar a la espalda',

    'line_holding_keeper_oop': 'Permanece bajo palos y no abandona el área chica',

    'ball_playing_centre_back_ip': 'Inicia ataques con pases ambiciosos que rompen líneas',

    'centre_back_ip': 'Conserva la posición para dar equilibrio y proteger ante pérdidas',

    'no_nonsense_center_back_ip': 'Mantiene la línea y despeja de inmediato sin complicaciones',

    'centre_back_oop': 'Frena atacantes y protege el área central sin desordenarse',

    'covering_centre_back_oop': 'Prioriza mantener la línea y reaccionar al peligro profundo',

    'full_back_ip': 'Ofrece amplitud desde una posición contenida y segura',

    'wing_back_ip': 'Se proyecta por la banda para dar máxima amplitud y profundidad',

    'full_back_oop': 'Defiende su banda según la organización colectiva',

    'holding_full_back_oop': 'Lateral de contención: conserva posición y prioriza no ser superado',

    'pressing_full_back_oop': 'Adelanta la marca para presionar al extremo rival al recibir',

    'wing_back_oop': 'Defiende el carril exterior coordinando su repliegue',

    'holding_wing_back_oop': 'Carrilero de contención: repliegue prudente y coberturas',

    'pressing_wing_back_oop': 'Salto hacia adelante para intervenir en la presión por banda',

    'defensive_midfielder_ip': 'Apoyo posicional por delante de la zaga y pase equilibrado',

    'deep_lying_playmaker_ip': 'Organiza desde la base retrasada y filtra pases de progresión',

    'defensive_midfielder_oop': 'Protege el espacio por delante de los centrales y tapa líneas',

    'screening_defensive_midfielder_oop': 'Pantalla en Zona 14: bloquea remates frontales y tapa el centro',

    'central_midfielder_ip': 'Apoyo general y conexión fluida entre líneas',

    'midfield_playmaker_ip': 'Asume la creación desde el centro para hacer avanzar al equipo',

    'advanced_playmaker_ip': 'Encuentra espacios entre líneas para habilitar con pases filtrados',

    'channel_midfielder_ip': 'Ataca los canales interiores (espacios entre central y lateral)',

    'attacking_midfielder_ip': 'Actúa entre líneas y aporta amenaza directa cerca del área',

    'central_midfielder_oop': 'Sostiene el bloque central y coordina la presión colectiva',

    'screening_central_midfielder_oop': 'Cierra pasillos interiores en el centro para evitar filtraciones',

    'pressing_central_midfielder_oop': 'Abandona el bloque para encimar al rival y disputar la pelota arriba',

    'wide_covering_central_midfielder_oop': 'Se desplaza al costado para apoyar la cobertura defensiva del lateral',

    'wide_midfielder_ip': 'Conserva posición abierta para ofrecer apoyo y circulación exterior',

    'winger_ip': 'Mantiene amplitud, desborda por fuera y envía centros al área',

    'inside_winger_ip': 'Conduce hacia dentro con función creativa y asociativa',

    'playmaking_winger_ip': 'Se mete por dentro para asumir la organización y el pase final',

    'inside_forward_ip': 'Diagonal desde banda hacia el área para buscar el remate y el gol',

    'wide_forward_ip': 'Amplitud exterior y amenaza de gol atacando el segundo palo',

    'winger_oop': 'Defiende la banda dentro de la estructura colectiva',

    'tracking_winger_oop': 'Retrocede profundamente para ayudar al lateral en el costado',

    'wide_midfielder_oop': 'Defiende desde la banda para sostener la línea de cuatro medios',

    'tracking_wide_midfielder_oop': 'Acompaña el repliegue y refuerza las ayudas por banda',

    'second_striker_ip': 'Se incorpora desde la mediapunta al área como segundo atacante',

    'free_role_ip': 'Libertad absoluta para flotar, conducir y crear ventajas',

    'attacking_midfielder_oop': 'Molesta la salida rival y cierra líneas de pase retrasadas',

    'tracking_attacking_midfielder_oop': 'Baja a colaborar con el mediocampo compactando el bloque',

    'channel_forward_ip': 'Desmarques en profundidad atacando el canal entre central y lateral',

    'false_nine_ip': 'Falso 9: retrocede a mediapunta, arrastra centrales y abre espacios',

    'deep_lying_forward_ip': 'Aguanta de espaldas, retiene el balón y asiste a quienes llegan de cara',

    'centre_forward_ip': 'Referencia ofensiva equilibrada: fija, combina y busca el remate',

    'poacher_ip': 'Juega al límite del fuera de juego buscando definir dentro del área',

    'target_forward_ip': 'Referencia física y aérea: gana duelos y habilita segundas jugadas',

    'centre_forward_oop': 'Acoso a la salida de los defensas centrales rivales',

    'tracking_centre_forward_oop': 'Baja a campo propio para tapar la salida del mediocentro rival',

    'central_outlet_centre_forward_oop': 'Permanece adelantado sin bajar, como vía de escape al contraataque',

}



TACTICAL_BADGE = {

    'ball_playing_goalkeeper_ip': 'Salida con pies',

    'goalkeeper_ip': 'Portero seguro',

    'no_nonsense_goalkeeper_ip': 'Despeje directo',

    'sweeper_keeper_oop': 'Líbero (anticipación)',

    'goalkeeper_oop': 'Bajo palos',

    'line_holding_keeper_oop': 'Línea de meta',

    'ball_playing_centre_back_ip': 'Pase de salida',

    'centre_back_ip': 'Zaga posicional',

    'no_nonsense_center_back_ip': 'Despeje simple',

    'centre_back_oop': 'Marcaje central',

    'covering_centre_back_oop': 'Cobertura profunda',

    'full_back_ip': 'Apoyo lateral',

    'wing_back_ip': 'Desborde y centro',

    'full_back_oop': 'Defensa de banda',

    'holding_full_back_oop': 'Lateral de contención',

    'pressing_full_back_oop': 'Presión en banda',

    'wing_back_oop': 'Repliegue de carril',

    'holding_wing_back_oop': 'Carrilero contención',

    'pressing_wing_back_oop': 'Presión adelantada',

    'defensive_midfielder_ip': 'Ancla y apoyo',

    'deep_lying_playmaker_ip': 'Organizador retrasado',

    'defensive_midfielder_oop': 'Contención central',

    'screening_defensive_midfielder_oop': 'Pantalla Zona 14',

    'central_midfielder_ip': 'Conector de líneas',

    'midfield_playmaker_ip': 'Creación central',

    'advanced_playmaker_ip': 'Pase filtrado',

    'channel_midfielder_ip': 'Ruptura a canales',

    'attacking_midfielder_ip': 'Llegada frontal',

    'central_midfielder_oop': 'Bloque medio',

    'screening_central_midfielder_oop': 'Tapón interior',

    'pressing_central_midfielder_oop': 'Presión y robo',

    'wide_covering_central_midfielder_oop': 'Cobertura a banda',

    'wide_midfielder_ip': 'Amplitud de banda',

    'winger_ip': 'Desborde y centro',

    'inside_winger_ip': 'Creación interior',

    'playmaking_winger_ip': 'Organizador escorado',

    'inside_forward_ip': 'Diagonal y gol',

    'wide_forward_ip': 'Amenaza de gol exterior',

    'winger_oop': 'Repliegue volante',

    'tracking_winger_oop': 'Ayuda profunda',

    'wide_midfielder_oop': 'Línea de cuatro',

    'tracking_wide_midfielder_oop': 'Repliegue por banda',

    'second_striker_ip': 'Segundo punta',

    'free_role_ip': 'Libre creador',

    'attacking_midfielder_oop': 'Presión mediapunta',

    'tracking_attacking_midfielder_oop': 'Repliegue a medios',

    'channel_forward_ip': 'Ruptura al intervalo',

    'false_nine_ip': 'Falso 9 (arrastra)',

    'deep_lying_forward_ip': 'Apoyo de espaldas',

    'centre_forward_ip': 'Delantero completo',

    'poacher_ip': 'Cazagoles (área)',

    'target_forward_ip': 'Referencia aérea',

    'centre_forward_oop': 'Acoso a centrales',

    'tracking_centre_forward_oop': 'Repliegue defensivo',

    'central_outlet_centre_forward_oop': 'Salida de contra',

}





def explanation(player,choice,style):

    r=ROLES[choice['id']]; a=player['attributes']; position=choice['position']

    top=sorted(r['weights'],key=lambda k:(-a[k],k))[:3]

    low=sorted(r['weights'],key=lambda k:(a[k],k))[:2]

    familiarity=player['positions'].get(position.lower(),1)

    phase='con balón' if r['phase']=='in_possession' else 'sin balón'

    reasons=[f'{ATTRS[k]} {a[k]}/20 es uno de los atributos de referencia de este rol {phase}.' for k in top]

    reasons.append(f'Familiaridad en {position}: {familiarity}/20; se evalúa esta posición concreta, no otra posición permitida por el mismo rol.')

    purpose=PURPOSE.get(position.lower(),PURPOSE['flank'])

    if r['phase']=='out_of_possession':

        purpose=('Proteger el espacio a la espalda de la defensa.' if position=='GK' else

                 'Recuperar una posición defensiva compatible con la estructura del equipo.')

    stem=r['id'].rsplit('_',1)[0]

    reasons.append(OOP_PURPOSE.get(stem,ROLE_PURPOSE.get(stem,purpose)) if r['phase']=='out_of_possession' else ROLE_PURPOSE.get(stem,purpose))

    reasons.append(f'Se evalúa dentro del plan de {STYLES[style]["name"].lower()}.')

    if position in ('AML','AMR'):reasons.append('El estilo limita los roles de banda candidatos para mantener coherencia con el ataque.')

    if r['id'].startswith('pressing_'):reasons.append('Cumple el umbral propio de sacrificio y resistencia de al menos 13 para salir a presionar.')

    other=choice['alternatives'][0] if choice['alternatives'] else None

    comparison=(f'Supera a {ROLES[other[0]]["name"]} ({other[1]:.1f}) por {choice["score"]-other[1]:.1f} puntos en {position}, entre los roles admitidos para este puesto.' if other and choice['score']>other[1] else f'Empata con {ROLES[other[0]]["name"]} ({other[1]:.1f}); ambas son alternativas comparables.' if other else 'Es el único rol admitido por esta configuración de puesto.')

    warnings=[f'{ATTRS[k]} {a[k]}/20 es un punto a revisar para esta función.' for k in low if a[k]<12]

    if familiarity<15:warnings.append('La familiaridad está por debajo de 15: requiere adaptación o una posición alternativa.')

    if 'Take More Risks' in r['player_instructions'] and min(a['passing'],a['decisions'])<12:

        warnings.append('El rol pide arriesgar y sus pases o decisiones son menores de 12. Probar una alternativa más sencilla si pierde balones.')

    return {'id':r['id'],'name':r['name'],'english':r['english'],'phase':r['phase'],'position':position,

            'score':choice['score'],'source':r['source'],'spanish_status':r['spanish_status'],

            'menu_verified_es':r['menu_verified_es'],'spanish_source':r['spanish_source'],

            'localization':r['localization'],

            'tactical_summary':TACTICAL_SUMMARY.get(r['id'],''),

            'tactical_badge':TACTICAL_BADGE.get(r['id'],''),

            'reasons':reasons,'comparison':comparison,'warnings':warnings,

            'instructions':player_instructions(player,r),

            'behaviours':r['player_instructions'],

            'alternatives':[{'id':key,'name':ROLES[key]['name'],'english':ROLES[key]['english'],'score':value} for key,value in choice['alternatives']]}





def profile(player,style):

    eligible=[p for p in IP_POOLS if player['positions'].get(p.lower(),1)>=15]

    if not eligible:

        best=max((player['positions'].get(p.lower(),1) for p in IP_POOLS),default=1)

        eligible=[p for p in IP_POOLS if player['positions'].get(p.lower(),1)==best]

    candidates=sorted((choose(player,'ip',p,style) for p in eligible),key=lambda c:(-c['score'],c['id'],c['position']))

    ip=candidates[0]; oop=choose(player,'oop',ip['position'],style)

    r=ROLES[ip['id']]; weights=r['weights']

    strengths=sorted(weights,key=lambda k:(-player['attributes'][k],k))[:3]

    priorities=sorted(weights,key=lambda k:(player['attributes'][k],-weights[k],k))[:3]

    alternatives=[(ip['id'],ip['score'])]+ip['alternatives']

    return {'best_role':ip['id'],'position':ip['position'],'role_name':r['name'],'score':ip['score'],

            'strengths':[{'key':k,'name':ATTRS[k],'value':player['attributes'][k]} for k in strengths],

            'focus':[{'key':k,'name':ATTRS[k],'value':player['attributes'][k]} for k in priorities],

            'roles':[{'id':key,'name':ROLES[key]['name'],'english':ROLES[key]['english'],'score':value} for key,value in alternatives],

            'in_possession':explanation(player,ip,style),'out_of_possession':explanation(player,oop,style)}





FORMATION_POSITIONS = {
  '433': (['GK','DL','DC','DC','DR','DM','MC','MC','AML','STC','AMR'], ['GK','DL','DC','DC','DR','DM','MC','MC','ML','STC','MR']),
  '4231': (['GK','DL','DC','DC','DR','DM','DM','AMC','AML','STC','AMR'], ['GK','DL','DC','DC','DR','MC','MC','AMC','ML','STC','MR']),
  '442': (['GK','DL','DC','DC','DR','MC','MC','ML','MR','STC','STC'], ['GK','DL','DC','DC','DR','MC','MC','ML','MR','STC','STC']),
  '352': (['GK','DC','DC','DC','WBL','DM','MC','MC','WBR','STC','STC'], ['GK','WBL','DC','DC','DC','WBR','MC','DM','MC','STC','STC']),
  '343': (['GK','DC','DC','DC','WBL','MC','MC','WBR','AML','AMR','STC'], ['GK','WBL','DC','DC','DC','WBR','ML','MR','MC','MC','STC']),
  '532': (['GK','DL','DC','DC','DC','DR','DM','MC','MC','STC','STC'], ['GK','DL','DC','DC','DC','DR','MC','DM','MC','STC','STC']),
  '41212': (['GK','DL','DC','DC','DR','DM','MC','MC','AMC','STC','STC'], ['GK','DL','DC','DC','DR','MC','DM','MC','AMC','STC','STC']),
  '3412': (['GK','DC','DC','DC','WBL','MC','MC','WBR','AMC','STC','STC'], ['GK','WBL','DC','DC','DC','WBR','MC','MC','AMC','STC','STC']),
  '424': (['GK','DL','DC','DC','DR','MC','MC','AML','AMR','STC','STC'], ['GK','DL','DC','DC','DR','MC','MC','ML','MR','STC','STC']),
  '523': (['GK','DC','DC','DC','WBL','MC','MC','WBR','AML','AMR','STC'], ['GK','WBL','DC','DC','DC','WBR','ML','MC','MC','MR','STC']),
}

def formation_slots(form):
    ip, oop = FORMATION_POSITIONS.get(form['id'], FORMATION_POSITIONS['433'])
    return [dict(s, ip_position=ip[i], oop_position=oop[i]) for i, s in enumerate(form['slots'])]





def slot_choices(player,spec,style):

    if spec['role'] in ROLES:  # Explicit role pairs are useful to verify the assignment solver.

        ip={'id':spec['role'],'score':role_score(player,spec['role'],style),'position':ROLES[spec['role']]['positions'][0],'alternatives':[]}

        oop={'id':spec['defend'],'score':role_score(player,spec['defend'],style),'position':ROLES[spec['defend']]['positions'][0],'alternatives':[]}

    else:

        ip=choose(player,'ip',spec['ip_position'],style,spec['role'])

        oop=choose(player,'oop',spec['oop_position'],style,spec['defend'])

    return ip,oop,round(.8*ip['score']+.2*oop['score'],2)





def assignment(players,slots,style):

    n=len(slots)

    if len(players)<n:return None

    dp={0:(0.0,())}

    for p in players:

        scores=[slot_choices(p,s,style)[2] for s in slots]

        updates={}

        for mask,(value,chosen) in dp.items():

            for i in range(n):

                if mask&(1<<i):continue

                newmask=mask|(1<<i); candidate=value+scores[i]

                if candidate>max(dp.get(newmask,(-1,()))[0],updates.get(newmask,(-1,()))[0]):

                    updates[newmask]=(candidate,chosen+((i,p['uid'],round(scores[i],1)),))

        dp.update(updates)

    return dp[(1<<n)-1]





def analyze(dataset,style='possession',primary_slot=0,excluded=(),prompt=None):

    parsed_prompt = parse_tactical_prompt(prompt) if prompt else None

    if parsed_prompt:

        style = parsed_prompt['recommended_style']

        team_overrides = parsed_prompt['team_overrides']

    else:

        team_overrides = None

    if style not in STYLES:raise ValueError('Estilo desconocido.')

    excluded=set(excluded); players=dataset['players']

    seniors=[p for p in players if p['team_slot']==primary_slot and p['uid'] not in excluded]

    byid={p['uid']:p for p in players+dataset['loans']}

    profiles={p['uid']:profile(p,style) for p in players+dataset['loans']}

    tactics=[]

    for form in FORMATIONS:

        slots=formation_slots(form); solution=assignment(seniors,slots,style)

        if solution is None:continue

        total,picked=solution; lineup=[];risks=[]

        for i,uid,score in sorted(picked):

            p=byid[uid]; spec=slots[i]; ip,oop,_=slot_choices(p,spec,style)

            ip_ex=explanation(p,ip,style);oop_ex=explanation(p,oop,style)

            prof=profiles[uid]

            familiarity=min(p['positions'].get(ip['position'].lower(),1),p['positions'].get(oop['position'].lower(),1))

            lineup.append({'uid':uid,'role':ip_ex['name'],'role_id':ip['id'],'score':score,

                           'ip':spec['ip'],'oop':spec['oop'],'in_possession':ip_ex,'out_of_possession':oop_ex,

                           'without_ball':oop_ex['name'],'reason':ip_ex['comparison'],'familiarity':familiarity,

                           'natural_role':prof['role_name'],'natural_role_id':prof['best_role'],

                           'natural_position':prof['position'],'natural_score':prof['score'],

                           'role_matches_natural':(ip['id']==prof['best_role']),

                           'tactical_summary':ip_ex.get('tactical_summary',''),

                           'tactical_badge':ip_ex.get('tactical_badge',''),

                           'tactical_summary_oop':oop_ex.get('tactical_summary',''),

                           'tactical_badge_oop':oop_ex.get('tactical_badge',''),

                           'individual_instructions':[*ip_ex['instructions'],*oop_ex['instructions']]})

            if familiarity<15:risks.append(f'{p["name"]}: familiaridad menor a 15 en una de las dos fases; revisar {ip["position"]} → {oop["position"]}.')

        chosen_ids={l['uid'] for l in lineup}

        bench=sorted((p for p in seniors if p['uid'] not in chosen_ids),key=lambda p:profiles[p['uid']]['score'],reverse=True)[:9]

        pos_map = {

            'GK': ['gk'], 'DL': ['dl', 'wbl'], 'DC': ['dc'], 'DR': ['dr', 'wbr'],

            'DM': ['dm'], 'CM': ['mc'], 'AM': ['amc'], 'LW': ['aml', 'ml'],

            'RW': ['amr', 'mr'], 'ST': ['stc'], 'STC': ['stc'], 'AML': ['aml', 'ml'], 'AMR': ['amr', 'mr'], 'MC': ['mc']

        }

        bench_replacements = []

        for bp in bench:

            bprof = profiles[bp['uid']]

            best_target = None

            best_eff = -999.0

            best_gap = 0.0

            for l in lineup:

                pos = l['in_possession']['position'].upper()

                mapped = pos_map.get(pos, [pos.lower()])

                fam = max(bp['positions'].get(k, 1) for k in mapped)

                eff = bprof['score'] * (0.25 + 0.75 * fam / 20.0)

                gap = eff - l['score']

                if fam >= 10 and eff > best_eff:

                    best_eff = eff

                    best_target = l

                    best_gap = gap

            target_p = byid[best_target['uid']] if best_target else None

            quality = 'starter_level' if best_gap >= -1.5 else 'reliable' if best_gap >= -4.5 else 'rotation'

            quality_label = 'Nivel titular directo' if best_gap >= -1.5 else 'Recambio de garantías' if best_gap >= -4.5 else 'Opción de rotación'

            beaten = [

                {'uid': l['uid'], 'name': byid[l['uid']]['name'], 'position': l['in_possession']['position'], 'score': l['score']}

                for l in lineup if bprof['score'] > l['score']

            ]

            beaten.sort(key=lambda x: x['score'])

            bench_replacements.append({

                'uid': bp['uid'],

                'name': bp['name'],

                'age': bp.get('age'),

                'natural_positions': bp.get('natural_positions', []),

                'score': bprof['score'],

                'role_name': bprof['role_name'],

                'replaces_uid': best_target['uid'] if best_target else None,

                'replaces_name': target_p['name'] if target_p else None,

                'replaces_position': best_target['in_possession']['position'] if best_target else None,

                'replaces_role': best_target['role'] if best_target else None,

                'replacement_score': round(best_eff, 1) if best_target else bprof['score'],

                'gap': round(best_gap, 1) if best_target else 0.0,

                'quality': quality,

                'quality_label': quality_label,

                'better_than_starters': beaten

            })

        tactics.append({'id':form['id'],'name':form['name'],'defensive':form['defensive'],'idea':form['idea'],

                       'fm26_style':STYLES[style].get('fm26_style','Tiquitaca'),'fm26_style_alt':STYLES[style].get('fm26_style_alt','Control de la posesión'),'fm26_mentality':(parsed_prompt.get('recommended_mentality') if parsed_prompt else STYLES[style].get('mentality','Positiva')),

                       'score':round(total/11,1),'lineup':lineup,'bench':[p['uid'] for p in bench],

                       'bench_replacements':bench_replacements,

                       'risks':risks+[STYLES[style]['risk']],

                       'tactical_recommendations': [

                           {

                               'type': 'warning',

                               'title': 'Salida del arquero vs Ritmo pausado',

                               'detail': 'Con pases cortos y ritmo bajo, apurar al arquero a distribuir rápido puede forzar pérdidas si los laterales aún no se abrieron. Recomendamos "Ralentizar el juego" o distribución equilibrada para salir limpios.'

                           },

                           {

                               'type': 'warning',

                               'title': 'Coordinación entre Bloque y Contrapresión',

                               'detail': 'Con bloque medio y contrapresión muy insistente, los atacantes van a asfixiar arriba pero la defensa espera en mitad de cancha, dejando un hueco entre líneas. Para dominar y presionar arriba, subí a "Bloque alto"; si preferís cuidar el fondo, moderá a "Reagruparse".'

                           },

                           {

                               'type': 'tip',

                               'title': 'Desdoblamientos por banda ante defensas replegadas',

                               'detail': 'Al jugar con paciencia para entrar al área y centros rasos, los rivales suelen cerrar el centro. Activar "Doblar por fuera" en las carreras de apoyo permite que tus laterales desdoblen a los extremos y generen superioridad 2 vs 1 en las bandas.'

                           }

                       ],

                       'instructions':team_instructions([byid[l['uid']] for l in lineup],style,team_overrides)})

    tactics.sort(key=lambda t:t['score'],reverse=True)

    for idx, t in enumerate(tactics):

        t['rank'] = idx + 1

        t['rank_badge'] = 'MEJOR ENCAJE' if idx == 0 else f'ALTERNATIVA #{idx + 1}'

    academy=[]

    for p in players:

        if p['team_slot']==primary_slot:continue

        prof=profiles[p['uid']]; position=prof['position']

        comparable=[q for q in seniors if q['positions'].get(position.lower(),1)>=15]

        comparisons=sorted(((q,role_score(q,prof['best_role'],style,position)) for q in comparable),key=lambda x:x[1],reverse=True)

        benchmark=comparisons[min(2,len(comparisons)-1)][1] if comparisons else None

        gap=round(prof['score']-benchmark,1) if benchmark is not None else None

        if gap is None:action='Sin referencia';plan='No hay una opción familiar en esta posición para comparar. Evaluar el puesto dentro del club.'

        elif gap>=-3:action='Probar con el primer equipo';plan='Integrar entrenamientos y evaluar minutos de rotación; confirmar rendimiento y disponibilidad en FM.'

        elif p['age'] is not None and p['age']<18:action='Desarrollar en inferiores';plan='Priorizar entrenamiento y minutos juveniles. Revisar la evolución antes de subir la exigencia.'

        else:action='Evaluar minutos o cesión';plan='Si no tiene minutos adecuados en el club, evaluar una cesión con participación y entrenamiento suficientes.'

        academy.append({'uid':p['uid'],'benchmark':benchmark,'gap':gap,'action':action,'plan':plan,

                        'comparison':[{'uid':q['uid'],'name':q['name'],'score':v} for q,v in comparisons[:3]],

                        'development':f'Entrenar {prof["role_name"]} en {position}; priorizar '+', '.join(f'{a["name"]} ({a["value"]})' for a in prof['focus'][:2])+'. No garantiza crecimiento.'})

    academy.sort(key=lambda x:x['gap'] if x['gap'] is not None else -999,reverse=True)

    formations_catalog = [{'id': f['id'], 'name': f['name'], 'category': f.get('category', 'Formación'), 'defensive': f['defensive'], 'idea': f['idea']} for f in FORMATION_CATALOG]
    requested_tactic = None
    if parsed_prompt and parsed_prompt.get('requested_formation'):
        rf_id = parsed_prompt['requested_formation']
        try:
            requested_tactic = simulate_formation(dataset, formation_id=rf_id, style=style, primary_slot=primary_slot, excluded=excluded, prompt=prompt)
        except Exception:
            requested_tactic = None

    return {'style':style,'profiles':profiles,'tactics':tactics,'academy':academy,'senior_count':len(seniors),
            'excluded_count':len(excluded),'actions':dict(Counter(a['action'] for a in academy)),
            'prompt_analysis':parsed_prompt,'custom_prompt':prompt or '',
            'formations_catalog':formations_catalog, 'requested_tactic':requested_tactic}




def evaluate_formation_reinforcements(lineup, seniors, loans, form, style, profiles):
    """
    Evaluates squad depth and weaknesses for a specific formation.
    Identifies weak positions (low rating or adapting) and missing squad backups.
    Evaluates whether any loaned player can be recalled (repescar cesión) to fill
    the position without transfer fees, or outlines the target market scouting profile.
    """
    pos_map = {
        'GK': ['gk'], 'DL': ['dl', 'wbl'], 'DC': ['dc'], 'DR': ['dr', 'wbr'],
        'WBL': ['wbl', 'dl'], 'WBR': ['wbr', 'dr'],
        'DM': ['dm'], 'MC': ['mc'], 'AMC': ['amc'],
        'AML': ['aml', 'ml'], 'AMR': ['amr', 'mr'],
        'ML': ['ml', 'aml'], 'MR': ['mr', 'amr'],
        'STC': ['stc'], 'ST': ['stc']
    }

    key_attrs_by_pos = {
        'GK': ['handling', 'reflexes', 'one_on_ones', 'command_of_area', 'kicking'],
        'DC': ['heading', 'marking', 'tackling', 'positioning', 'jumping_reach', 'bravery'],
        'DL': ['tackling', 'pace', 'stamina', 'positioning', 'crossing', 'work_rate'],
        'DR': ['tackling', 'pace', 'stamina', 'positioning', 'crossing', 'work_rate'],
        'WBL': ['stamina', 'pace', 'crossing', 'work_rate', 'dribbling', 'tackling'],
        'WBR': ['stamina', 'pace', 'crossing', 'work_rate', 'dribbling', 'tackling'],
        'DM': ['tackling', 'positioning', 'teamwork', 'work_rate', 'passing', 'anticipation'],
        'MC': ['passing', 'vision', 'first_touch', 'decisions', 'teamwork', 'work_rate'],
        'AMC': ['vision', 'passing', 'technique', 'flair', 'dribbling', 'decisions'],
        'AML': ['dribbling', 'pace', 'acceleration', 'crossing', 'flair', 'off_the_ball'],
        'AMR': ['dribbling', 'pace', 'acceleration', 'crossing', 'flair', 'off_the_ball'],
        'ML': ['crossing', 'work_rate', 'stamina', 'passing', 'teamwork', 'pace'],
        'MR': ['crossing', 'work_rate', 'stamina', 'passing', 'teamwork', 'pace'],
        'STC': ['finishing', 'off_the_ball', 'composure', 'acceleration', 'pace', 'heading']
    }

    starter_uids = {l['uid'] for l in lineup}
    bench_seniors = [p for p in seniors if p['uid'] not in starter_uids]

    weak_positions = []
    seen_positions = set()

    for l in lineup:
        pos = l['in_possession']['position'].upper()
        if pos in seen_positions:
            continue
        seen_positions.add(pos)

        pos_starters = [x for x in lineup if x['in_possession']['position'].upper() == pos]
        mapped_keys = pos_map.get(pos, [pos.lower()])

        backups = [
            bp for bp in bench_seniors
            if any(bp['positions'].get(k, 1) >= 14 for k in mapped_keys)
        ]

        issues = []
        worst_starter = min(pos_starters, key=lambda x: x['score'])
        if worst_starter['familiarity'] < 15:
            issues.append(f"El titular adapta de puesto (familiaridad {worst_starter['familiarity']}/20).")
        if worst_starter['score'] < 72.0:
            issues.append(f"Puntuación baja de titular ({worst_starter['score']}/100) para la exigencia del esquema.")
        if len(backups) < len(pos_starters):
            issues.append(f"Falta de recambio natural en el plantel ({len(backups)} suplente{'s' if len(backups)!=1 else ''} para {len(pos_starters)} puesto{'s' if len(pos_starters)!=1 else ''}).")

        if issues:
            urgency = 'Alta' if (worst_starter['score'] < 68.0 or worst_starter['familiarity'] < 14 or len(backups) == 0) else 'Media'

            loan_candidates = []
            for lp in loans:
                lfam = max((lp['positions'].get(k, 1) for k in mapped_keys), default=1)
                is_nat = any(k.upper() in [np.upper() for np in lp.get('natural_positions', [])] for k in mapped_keys)
                if lfam >= 14 or is_nat:
                    lprof = profiles.get(lp['uid'], profile(lp, style))
                    stats = lp.get('loan_stats', {})
                    pj = (stats.get('starts', 0) or 0) + (stats.get('subs', 0) or 0)
                    loan_candidates.append({
                        'uid': lp['uid'],
                        'name': lp['name'],
                        'age': lp.get('age'),
                        'natural_positions': lp.get('natural_positions', []),
                        'club_name': lp.get('club_name') or 'Club cesión',
                        'loan_end': lp.get('loan_end'),
                        'score': lprof['score'],
                        'familiarity': lfam,
                        'stats': stats,
                        'rating': stats.get('rating'),
                        'goals': stats.get('goals', 0),
                        'assists': stats.get('assists', 0),
                        'appearances': pj
                    })

            loan_candidates.sort(key=lambda x: (x['familiarity'] >= 18, x['familiarity'], x['appearances'], x['score']), reverse=True)

            loan_recommendations = []
            for cand in loan_candidates[:2]:
                st = cand['stats']
                pj = cand['appearances']
                goles = cand['goals']
                media = cand['rating']
                vence = cand['loan_end']

                perf_str = f"{pj} PJ"
                if goles > 0: perf_str += f", {goles} goles"
                if media and media != '—': perf_str += f", media {media}"

                exp_date_str = vence if vence else "Fin de temporada"

                reason = (
                    f"Podés repescar a {cand['name']} (cedido en {cand['club_name']}, vence el {exp_date_str}). "
                    f"Acumula rodaje oficial ({perf_str}) y encaja de forma natural en {pos} con índice {cand['score']}/100. "
                    f"Cubre la posición de inmediato sin gastar presupuesto de fichajes."
                )

                loan_recommendations.append({
                    'player_uid': cand['uid'],
                    'player_name': cand['name'],
                    'age': cand['age'],
                    'club_name': cand['club_name'],
                    'loan_end': cand['loan_end'],
                    'appearances': pj,
                    'goals': goles,
                    'assists': cand['assists'],
                    'rating': media,
                    'score': cand['score'],
                    'reason': reason
                })

            market_profile = None
            if not loan_recommendations:
                req_attrs = key_attrs_by_pos.get(pos, ['passing', 'work_rate', 'stamina', 'teamwork'])
                attr_labels = [ATTRS.get(a, a) for a in req_attrs[:4]]
                market_profile = {
                    'target_position': pos,
                    'role_label': f"Especialista en {pos} para {form['name']}",
                    'key_attributes': attr_labels,
                    'scouting_note': f"Buscar en el mercado un jugador para {pos}. Atributos clave recomendados en FM26: {', '.join(attr_labels)}. Priorizar jugadores con sacrificio físico y comprensión táctica."
                }

            weak_positions.append({
                'position': pos,
                'position_label': f"Puesto: {pos}",
                'urgency': urgency,
                'current_starter': worst_starter['uid'],
                'current_starter_name': worst_starter['in_possession']['name'],
                'starter_score': worst_starter['score'],
                'issues': issues,
                'has_loan_recall': len(loan_recommendations) > 0,
                'loan_recalls': loan_recommendations,
                'market_profile': market_profile
            })

    return weak_positions


def simulate_formation(dataset, formation_id='352', style='possession', primary_slot=0, excluded=(), prompt=None):
    """
    Simulates a specific formation from the catalog (e.g. 3-5-2, 3-4-3, 5-3-2, etc.).
    Returns the Starting 11, bench, instructions, and deep reinforcement/loan evaluation.
    """
    form = FORMATIONS_BY_ID.get(formation_id, FORMATION_CATALOG[0])
    parsed_prompt = parse_tactical_prompt(prompt) if prompt else None
    if parsed_prompt:
        style = parsed_prompt['recommended_style']
        team_overrides = parsed_prompt['team_overrides']
    else:
        team_overrides = None

    excluded = set(excluded)
    players = dataset['players']
    seniors = [p for p in players if p['team_slot'] == primary_slot and p['uid'] not in excluded]
    byid = {p['uid']: p for p in players + dataset['loans']}
    profiles = {p['uid']: profile(p, style) for p in players + dataset['loans']}

    slots = formation_slots(form)
    solution = assignment(seniors, slots, style)
    if solution is None:
        raise ValueError(f"No hay suficientes jugadores disponibles para completar el esquema {form['name']}.")

    total, picked = solution
    lineup = []
    risks = []

    for i, uid, score in sorted(picked):
        p = byid[uid]
        spec = slots[i]
        ip, oop, _ = slot_choices(p, spec, style)
        ip_ex = explanation(p, ip, style)
        oop_ex = explanation(p, oop, style)
        prof = profiles[uid]
        familiarity = min(p['positions'].get(ip['position'].lower(), 1), p['positions'].get(oop['position'].lower(), 1))
        lineup.append({
            'uid': uid, 'role': ip_ex['name'], 'role_id': ip['id'], 'score': score,
            'ip': spec['ip'], 'oop': spec['oop'], 'in_possession': ip_ex, 'out_of_possession': oop_ex,
            'without_ball': oop_ex['name'], 'reason': ip_ex['comparison'], 'familiarity': familiarity,
            'natural_role': prof['role_name'], 'natural_role_id': prof['best_role'],
            'natural_position': prof['position'], 'natural_score': prof['score'],
            'role_matches_natural': (ip['id'] == prof['best_role']),
            'tactical_summary': ip_ex.get('tactical_summary', ''),
            'tactical_badge': ip_ex.get('tactical_badge', ''),
            'tactical_summary_oop': oop_ex.get('tactical_summary', ''),
            'tactical_badge_oop': oop_ex.get('tactical_badge', ''),
            'individual_instructions': [*ip_ex['instructions'], *oop_ex['instructions']]
        })
        if familiarity < 15:
            risks.append(f"{p['name']}: familiaridad menor a 15 en una de las dos fases ({ip['position']} → {oop['position']}).")

    chosen_ids = {l['uid'] for l in lineup}
    bench = sorted((p for p in seniors if p['uid'] not in chosen_ids), key=lambda p: profiles[p['uid']]['score'], reverse=True)[:9]

    pos_map = {
        'GK': ['gk'], 'DL': ['dl', 'wbl'], 'DC': ['dc'], 'DR': ['dr', 'wbr'],
        'WBL': ['wbl', 'dl'], 'WBR': ['wbr', 'dr'],
        'DM': ['dm', 'mc'], 'MC': ['mc'], 'AMC': ['amc'], 'AML': ['aml', 'ml'],
        'AMR': ['amr', 'mr'], 'ML': ['ml', 'aml'], 'MR': ['mr', 'amr'],
        'ST': ['stc'], 'STC': ['stc']
    }
    bench_replacements = []
    for bp in bench:
        bprof = profiles[bp['uid']]
        best_target = None
        best_eff = -999.0
        best_gap = 0.0
        for l in lineup:
            pos = l['in_possession']['position'].upper()
            mapped = pos_map.get(pos, [pos.lower()])
            fam = max((bp['positions'].get(k, 1) for k in mapped), default=1)
            eff = bprof['score'] * (0.25 + 0.75 * fam / 20.0)
            gap = eff - l['score']
            if fam >= 10 and eff > best_eff:
                best_eff = eff
                best_target = l
                best_gap = gap
        target_p = byid[best_target['uid']] if best_target else None
        quality = 'starter_level' if best_gap >= -1.5 else 'reliable' if best_gap >= -4.5 else 'rotation'
        quality_label = 'Nivel titular directo' if best_gap >= -1.5 else 'Recambio de garantías' if best_gap >= -4.5 else 'Opción de rotación'
        beaten = [
            {'uid': l['uid'], 'name': byid[l['uid']]['name'], 'position': l['in_possession']['position'], 'score': l['score']}
            for l in lineup if bprof['score'] > l['score']
        ]
        beaten.sort(key=lambda x: x['score'])
        bench_replacements.append({
            'uid': bp['uid'],
            'name': bp['name'],
            'age': bp.get('age'),
            'natural_positions': bp.get('natural_positions', []),
            'score': bprof['score'],
            'role_name': bprof['role_name'],
            'replaces_uid': best_target['uid'] if best_target else None,
            'replaces_name': target_p['name'] if target_p else None,
            'replaces_position': best_target['in_possession']['position'] if best_target else None,
            'replaces_role': best_target['role'] if best_target else None,
            'replacement_score': round(best_eff, 1) if best_target else bprof['score'],
            'gap': round(best_gap, 1) if best_target else 0.0,
            'quality': quality,
            'quality_label': quality_label,
            'better_than_starters': beaten
        })

    reinforcements = evaluate_formation_reinforcements(lineup, seniors, dataset['loans'], form, style, profiles)

    natural_count = sum(1 for l in lineup if l['familiarity'] >= 18)
    adapted_count = 11 - natural_count
    recalls_count = sum(len(r['loan_recalls']) for r in reinforcements)
    weak_count = len(reinforcements)

    verdict = (
        f"Esquema {form['name']} con {natural_count}/11 titulares naturales. "
        f"{f'Se detectaron {weak_count} puestos a reforzar. Podés resolverlos repescando a {recalls_count} cedidos sin costo de traspaso.' if recalls_count else 'Plantel con cobertura equilibrada para este planteo.'}"
    )

    return {
        'formation': {
            'id': form['id'],
            'name': form['name'],
            'defensive': form['defensive'],
            'category': form.get('category', 'Formación'),
            'idea': form['idea']
        },
        'style': style,
        'fm26_style': STYLES[style].get('fm26_style', 'Tiquitaca'),
        'fm26_mentality': (parsed_prompt.get('recommended_mentality') if parsed_prompt else STYLES[style].get('mentality', 'Positiva')),
        'score': round(total / 11, 1),
        'lineup': lineup,
        'bench': [p['uid'] for p in bench],
        'bench_replacements': bench_replacements,
        'risks': risks + [STYLES[style]['risk']],
        'reinforcements': reinforcements,
        'fit_summary': {
            'overall_score': round(total / 11, 1),
            'natural_count': natural_count,
            'adapted_count': adapted_count,
            'weak_count': weak_count,
            'recalls_count': recalls_count,
            'verdict': verdict
        },
        'instructions': team_instructions([byid[l['uid']] for l in lineup], style, team_overrides)
    }
