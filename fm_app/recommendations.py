"""Position-valid FM26 role pairing, assignment, instructions and player explanations."""

from collections import Counter



from fm_app.tactics import ATTRS, STYLES, FORMATIONS, FORMATION_CATALOG, FORMATIONS_BY_ID, parse_tactical_prompt

POS_NAMES_ES = {
    'GK': 'Arquero / Portero (POR)',
    'DL': 'Lateral izquierdo (LTI)',
    'DR': 'Lateral derecho (LTD)',
    'DC': 'Defensa central (DFC)',
    'WBL': 'Carrilero izquierdo (CRI)',
    'WBR': 'Carrilero derecho (CRD)',
    'DM': 'Pivote defensivo (MCD)',
    'MC': 'Mediocentro (MC)',
    'ML': 'Volante izquierdo (MI)',
    'MR': 'Volante derecho (MD)',
    'AMC': 'Mediapunta central (MP)',
    'AML': 'Extremo izquierdo (EXI)',
    'AMR': 'Extremo derecho (EXD)',
    'STC': 'Delantero centro (DLC)',
    'ST': 'Delantero centro (DLC)',
}

POS_CODES_ES = {
    'GK': 'POR', 'DL': 'LTI', 'DR': 'LTD', 'DC': 'DFC',
    'WBL': 'CRI', 'WBR': 'CRD', 'DM': 'MCD', 'MC': 'MC',
    'ML': 'MI', 'MR': 'MD', 'AMC': 'MP', 'AML': 'EXI',
    'AMR': 'EXD', 'STC': 'DLC', 'ST': 'DLC'
}

POS_SHORT_ES = {
    'GK': 'Arquero', 'DL': 'Lateral izq.', 'DR': 'Lateral der.', 'DC': 'Defensa central',
    'WBL': 'Carrilero izq.', 'WBR': 'Carrilero der.', 'DM': 'Pivote defensivo', 'MC': 'Mediocentro',
    'ML': 'Volante izq.', 'MR': 'Volante der.', 'AMC': 'Mediapunta', 'AML': 'Extremo izq.',
    'AMR': 'Extremo der.', 'STC': 'Delantero centro', 'ST': 'Delantero centro'
}

MONTHS_ES = ['', 'ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

def format_date_es(date_str):
    if not date_str:
        return 'Fin de temporada'
    try:
        parts = str(date_str).split('-')
        if len(parts) == 3:
            y, m, d = parts
            return f"{int(d)} {MONTHS_ES[int(m)]} {y}"
    except Exception:
        pass
    return str(date_str)


from fm_app.fm26 import ROLES, ROLE_ABBREV, IP_POOLS, OOP_POOLS, player_instructions, team_instructions





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
            'role_abbrev':ROLE_ABBREV.get(r['id'],'JUG'),
            'position_es':POS_CODES_ES.get(position.upper(),position),

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





def formation_slots(form):
    return form['slots']


def slot_choices(player,spec,style):

    if spec['role'] in ROLES:  # Explicit role pairs are useful to verify the assignment solver.

        ip={'id':spec['role'],'score':role_score(player,spec['role'],style),'position':ROLES[spec['role']]['positions'][0],'alternatives':[]}

        oop={'id':spec['defend'],'score':role_score(player,spec['defend'],style),'position':ROLES[spec['defend']]['positions'][0],'alternatives':[]}

    else:

        ip=choose(player,'ip',spec['ip_position'],style,spec['role'])

        oop=choose(player,'oop',spec['oop_position'],style,spec['defend'])

    return ip,oop,round(.8*ip['score']+.2*oop['score'],2)





def assignment(players,slots,style,evaluate=None):

    n=len(slots)

    if len(players)<n:return None

    dp={0:(0.0,())}

    for p in players:

        scores=[(evaluate(p,s) if evaluate else slot_choices(p,s,style))[2] for s in slots]

        updates={}

        for mask,(value,chosen) in dp.items():

            for i in range(n):

                if mask&(1<<i):continue

                newmask=mask|(1<<i); candidate=value+scores[i]

                if candidate>max(dp.get(newmask,(-1,()))[0],updates.get(newmask,(-1,()))[0]):

                    updates[newmask]=(candidate,chosen+((i,p['uid'],round(scores[i],1)),))

        dp.update(updates)

    return dp[(1<<n)-1]





def analyze(dataset, style='possession', primary_slot=0, excluded=(), prompt=None, overrides=None):
    context = AnalysisContext(dataset, style, primary_slot, excluded, prompt, overrides)
    style = context.style
    players, seniors, profiles = context.players, context.seniors, context.profiles
    excluded = set(excluded)
    tactics = [context.build(form) for form in FORMATION_CATALOG] if len(seniors) >= 11 else []
    tactics.sort(key=lambda t: (-t['score'], t['id']))
    for index, tactic in enumerate(tactics):
        tactic.update(rank=index + 1, rank_badge='MEJOR ENCAJE' if index == 0 else f'ALTERNATIVA #{index + 1}')
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

    requested = next((t for t in tactics if context.parsed and t['id'] == context.parsed.get('requested_formation')), None)
    return {'style': style, 'profiles': profiles, 'tactics': tactics[:3],
            'formation_rankings': [{'id': t['id'], 'name': t['name'], 'score': t['score'], 'defensive': t['defensive']} for t in tactics],
            'evaluated_formations': len(tactics), 'academy': academy, 'senior_count': len(seniors),
            'excluded_count': len(excluded), 'actions': dict(Counter(a['action'] for a in academy)),
            'prompt_analysis': context.parsed, 'custom_prompt': prompt or '',
            'formations_catalog': [{k: f[k] for k in ('id','name','category','defensive','idea')} for f in FORMATION_CATALOG],
            'requested_tactic': requested, 'effective_overrides': context.overrides}


def evaluate_formation_reinforcements(lineup, seniors, loans, form, style, profiles, byid=None):
    """
    Evaluates squad depth and weaknesses for a specific formation in Spanish.
    Identifies weak positions (low rating or adapting) and missing squad backups.
    Evaluates whether any loaned player can be recalled (repescar cesión) to fill
    the position without transfer fees, or outlines the target market scouting profile.
    """
    if byid is None:
        byid = {p['uid']: p for p in seniors + loans}

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

    slots = formation_slots(form)
    starter_uids = {l['uid'] for l in lineup}
    relative_floor = sum(x['score'] for x in lineup) / len(lineup) - 8
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
            if any(min(bp['positions'].get(slots[x['slot_index']]['ip_position'].lower(), 1),
                       bp['positions'].get(slots[x['slot_index']]['oop_position'].lower(), 1)) >= 15
                   for x in pos_starters)
        ]

        issues = []
        worst_starter = min(pos_starters, key=lambda x: x['score'])
        starter_p = byid.get(worst_starter['uid'])
        starter_name = starter_p['name'] if starter_p else 'Titular del once'
        pos_es = POS_NAMES_ES.get(pos, pos)
        pos_code = POS_CODES_ES.get(pos, pos)
        pos_short = POS_SHORT_ES.get(pos, pos)

        if worst_starter['familiarity'] < 15:
            issues.append(f"El titular {starter_name} adapta de puesto (familiaridad {worst_starter['familiarity']}/20 en {pos_es}).")
        if worst_starter['score'] < relative_floor:
            issues.append(f"Puntuación baja de titular ({worst_starter['score']}/100 para {starter_name}) respecto del nivel del once.")
        if len(backups) < len(pos_starters):
            issues.append(f"Falta de recambio natural en el plantel ({len(backups)} suplente{'s' if len(backups)!=1 else ''} para {len(pos_starters)} puesto{'s' if len(pos_starters)!=1 else ''} en {pos_es}).")

        if issues:
            urgency = 'Alta' if (worst_starter['score'] < relative_floor - 4 or worst_starter['familiarity'] < 14 or len(backups) == 0) else 'Media'

            loan_candidates = []
            for lp in loans:
                spec = slots[worst_starter['slot_index']]
                lfam = min(lp['positions'].get(spec['ip_position'].lower(), 1), lp['positions'].get(spec['oop_position'].lower(), 1))
                if lfam >= 14:
                    candidate_score = slot_choices(lp, spec, style)[2]
                    stats = lp.get('loan_stats', {})
                    pj = stats.get('appearances')
                    loan_candidates.append({
                        'uid': lp['uid'],
                        'name': lp['name'],
                        'age': lp.get('age'),
                        'natural_positions': lp.get('natural_positions', []),
                        'natural_positions_es': [POS_CODES_ES.get(np.upper(), np) for np in lp.get('natural_positions', [])],
                        'club_name': lp.get('club_name') or 'Club cesión',
                        'loan_end': lp.get('loan_end'),
                        'score': round(candidate_score, 1),
                        'familiarity': lfam,
                        'stats': stats,
                        'rating': stats.get('average_rating'),
                        'goals': stats.get('goals'),
                        'assists': stats.get('assists'),
                        'appearances': pj
                    })

            loan_candidates.sort(key=lambda x: (x['familiarity'] >= 18, x['familiarity'], x['appearances'] or 0, x['score']), reverse=True)

            loan_recommendations = []
            for cand in loan_candidates[:2]:
                st = cand['stats']
                pj = cand['appearances']
                goles = cand['goals']
                media = cand['rating']
                vence = cand['loan_end']
                exp_date_str = format_date_es(vence)

                perf_str = f"{pj} PJ" if pj is not None else "partidos sin verificar"
                if goles is not None and goles > 0: perf_str += f", {goles} goles"
                if media and media != '—': perf_str += f", media {media}"

                reason = (
                    f"Evaluá el regreso de {cand['name']} (cedido en {cand['club_name']}, vence el {exp_date_str}). "
                    f"{'Registra participaciones' if pj else 'Rodaje sin confirmar'} ({perf_str}) y tiene encaje estimado como {pos_es} con índice {cand['score']}/100. "
                    f"Confirmá en FM la cláusula de repesca, las fechas, los costos y la inscripción. Es una alternativa para este puesto; no puede cubrir varios a la vez."
                )

                loan_recommendations.append({
                    'player_uid': cand['uid'],
                    'player_name': cand['name'],
                    'age': cand['age'],
                    'club_name': cand['club_name'],
                    'loan_end': cand['loan_end'],
                    'loan_end_formatted': exp_date_str,
                    'appearances': pj,
                    'goals': goles,
                    'assists': cand['assists'],
                    'rating': media,
                    'score': cand['score'],
                    'position_es': pos_code,
                    'position_label': pos_es,
                    'reason': reason
                })

            market_profile = None
            if not loan_recommendations:
                req_attrs = key_attrs_by_pos.get(pos, ['passing', 'work_rate', 'stamina', 'teamwork'])
                attr_labels = [ATTRS.get(a, a) for a in req_attrs[:4]]
                market_profile = {
                    'target_position': pos_code,
                    'target_position_label': pos_es,
                    'role_label': f"Especialista en {pos_es} para {form['name']}",
                    'key_attributes': attr_labels,
                    'scouting_note': f"Buscar en el mercado de fichajes un futbolista para {pos_es}. Atributos clave recomendados en FM26: {', '.join(attr_labels)}. Priorizar jugadores con sacrificio físico y comprensión táctica."
                }

            weak_positions.append({
                'position': pos_code,
                'position_raw': pos,
                'position_label': pos_es,
                'position_short': pos_short,
                'urgency': urgency,
                'current_starter': worst_starter['uid'],
                'current_starter_name': starter_name,
                'starter_score': worst_starter['score'],
                'issues': issues,
                'has_loan_recall': len(loan_recommendations) > 0,
                'recall_verified': False,
                'loan_recalls': loan_recommendations,
                'market_profile': market_profile
            })

    return weak_positions

class AnalysisContext:
    """One request-scoped set of profiles, slot evaluations and result construction."""
    def __init__(self, dataset, style, primary_slot, excluded, prompt, overrides=None):
        if style not in STYLES:
            raise ValueError('Estilo desconocido.')
        self.dataset = dataset
        self.parsed = parse_tactical_prompt(prompt) if prompt else None
        self.style = self.parsed['recommended_style'] if self.parsed else style
        self.overrides = dict(self.parsed['team_overrides']) if self.parsed else {}
        self.overrides.update(overrides or {})
        self.players = dataset['players']
        self.loans = dataset.get('loans', [])
        self.seniors = [p for p in self.players if p['team_slot'] == primary_slot and p['uid'] not in excluded]
        self.byid = {p['uid']: p for p in self.players + self.loans}
        self.profiles = {uid: profile(p, self.style) for uid, p in self.byid.items()}
        self.choices = {}

    def evaluate(self, player, spec):
        key = (player['uid'], spec['ip_position'], spec['oop_position'], spec['role'], spec['defend'])
        if key not in self.choices:
            self.choices[key] = slot_choices(player, spec, self.style)
        return self.choices[key]

    def build(self, form):
        slots = formation_slots(form)
        solution = assignment(self.seniors, slots, self.style, evaluate=self.evaluate)
        if solution is None:
            raise ValueError(f"No hay suficientes jugadores para completar {form['name']}.")
        total, picked = solution
        lineup, risks = [], []
        for index, uid, _ in sorted(picked):
            p, spec, prof = self.byid[uid], slots[index], self.profiles[uid]
            ip, oop, value = self.evaluate(p, spec)
            ip_ex, oop_ex = explanation(p, ip, self.style), explanation(p, oop, self.style)
            fam = min(p['positions'].get(spec['ip_position'].lower(), 1), p['positions'].get(spec['oop_position'].lower(), 1))
            lineup.append({'uid': uid, 'slot_id': spec['id'], 'slot_index': index,
                'role': ip_ex['name'], 'role_id': ip['id'], 'score': round(value, 1),
                'ip': spec['ip'], 'oop': spec['oop'], 'in_possession': ip_ex, 'out_of_possession': oop_ex,
                'without_ball': oop_ex['name'], 'reason': ip_ex['comparison'], 'familiarity': fam,
                'natural_role': prof['role_name'], 'natural_role_id': prof['best_role'],
                'natural_position': prof['position'], 'natural_score': prof['score'],
                'role_matches_natural': ip['id'] == prof['best_role'],
                'tactical_summary': ip_ex['tactical_summary'], 'tactical_badge': ip_ex['tactical_badge'],
                'tactical_summary_oop': oop_ex['tactical_summary'], 'tactical_badge_oop': oop_ex['tactical_badge'],
                'individual_instructions': ip_ex['instructions'] + oop_ex['instructions']})
            if fam < 15:
                risks.append(f"{p['name']}: requiere adaptación ({spec['ip_position']} → {spec['oop_position']}, {fam}/20).")
        bench, replacements = self.build_bench(lineup, slots)
        reinforcements = evaluate_formation_reinforcements(lineup, self.seniors, self.loans, form, self.style, self.profiles, self.byid)
        recalls = {c['player_uid'] for r in reinforcements for c in r['loan_recalls']}
        natural = sum(x['familiarity'] >= 18 for x in lineup)
        verdict = f"{form['name']}: {natural}/11 titulares con familiaridad alta. "
        if reinforcements:
            verdict += f"Hay {len(reinforcements)} posiciones que requieren atención. "
            verdict += f"Se identificaron {len(recalls)} cedidos distintos como alternativas; verificá sus condiciones de regreso en FM." if recalls else 'Revisá el mercado o las inferiores para ampliar la cobertura.'
        else:
            verdict += 'No se detectaron carencias respecto del nivel de este plantel.'
        instructions = team_instructions([self.byid[l['uid']] for l in lineup], self.style, self.overrides)
        selected = {i['id']: i['value_en'] for i in instructions}
        advice = []
        if selected.get('defensive_line_oop') in ('Higher','Much Higher') and any(self.byid[x['uid']]['attributes']['pace'] < 13 for x in lineup if x['in_possession']['position'] == 'DC'):
            advice.append({'type': 'warning', 'title': 'Espacio detrás de la defensa', 'detail': 'La línea alta expone a centrales con velocidad menor a 13. Probá bajar la línea y revisá el rival.'})
        if selected.get('defensive_transition_oop') == 'Counter-Press' and sum(self.byid[x['uid']]['attributes']['stamina'] for x in lineup) / 11 < 12:
            advice.append({'type': 'warning', 'title': 'Exigencia de la contrapresión', 'detail': 'La resistencia media es menor a 12. Considerá reagruparte o moderar la intensidad.'})
        result = {'id': form['id'], 'name': form['name'], 'defensive': form['defensive'], 'idea': form['idea'],
            'formation': {k: form[k] for k in ('id','name','defensive','category','idea')},
            'style': self.style, 'fm26_style': STYLES[self.style]['fm26_style'],
            'fm26_style_alt': STYLES[self.style]['fm26_style_alt'],
            'fm26_mentality': self.parsed['recommended_mentality'] if self.parsed else STYLES[self.style]['mentality'],
            'score': round(total / 11, 1), 'lineup': lineup, 'bench': [p['uid'] for p in bench],
            'bench_replacements': replacements, 'risks': risks + [STYLES[self.style]['risk']],
            'reinforcements': reinforcements, 'tactical_recommendations': advice, 'instructions': instructions,
            'fit_summary': {'overall_score': round(total / 11, 1), 'natural_count': natural, 'adapted_count': 11 - natural,
                            'weak_count': len(reinforcements), 'recalls_count': len(recalls), 'verdict': verdict}}
        return result

    def build_bench(self, lineup, slots):
        starters = {x['uid'] for x in lineup}
        candidates = [p for p in self.seniors if p['uid'] not in starters]
        coverage = {}
        for p in candidates:
            entries = []
            for l in lineup:
                spec = slots[l['slot_index']]
                fam = min(p['positions'].get(spec['ip_position'].lower(), 1), p['positions'].get(spec['oop_position'].lower(), 1))
                if fam >= 10:
                    entries.append((l, self.evaluate(p, spec)[2], fam))
            coverage[p['uid']] = entries
        bench, covered = [], set()
        # Reserve a goalkeeper place before greedily covering the remaining tactical slots.
        keepers = [p for p in candidates if p['positions'].get('gk', 1) >= 15]
        if keepers:
            keeper = max(keepers, key=lambda p: (self.evaluate(p, slots[0])[2], -p['uid']))
            bench.append(keeper); covered.add(0)
        while len(bench) < min(9, len(candidates)):
            remaining = [p for p in candidates if p not in bench]
            def priority(p):
                matches = coverage[p['uid']]
                return (sum(1 for l, v, fam in matches if l['slot_index'] not in covered and fam >= 15),
                        max((v for _, v, _ in matches), default=0), len(matches), -p['uid'])
            chosen = max(remaining, key=priority)
            bench.append(chosen)
            covered.update(l['slot_index'] for l, _, fam in coverage[chosen['uid']] if fam >= 15)
        replacements = []
        for p in bench:
            matches = coverage[p['uid']]
            target = max(matches, key=lambda x: (x[1] - x[0]['score'], x[1])) if matches else None
            l, effective, fam = target if target else (None, None, None)
            gap = round(effective - l['score'], 1) if l else None
            quality = 'unavailable' if l is None else 'starter_level' if gap >= -1.5 else 'reliable' if gap >= -4.5 else 'rotation'
            label = {'unavailable': 'Sin reemplazo compatible', 'starter_level': 'Nivel titular en este puesto', 'reliable': 'Recambio de garantías', 'rotation': 'Opción de rotación'}[quality]
            replacements.append({'uid': p['uid'], 'name': p['name'], 'age': p.get('age'),
                'natural_positions': p.get('natural_positions', []),
                'natural_positions_es': [POS_CODES_ES.get(x.upper(), x) for x in p.get('natural_positions', [])],
                'score': self.profiles[p['uid']]['score'], 'role_name': self.profiles[p['uid']]['role_name'],
                'replaces_uid': l['uid'] if l else None, 'replaces_name': self.byid[l['uid']]['name'] if l else None,
                'replaces_position': l['in_possession']['position'] if l else None,
                'replaces_position_es': POS_CODES_ES.get(l['in_possession']['position']) if l else None,
                'replaces_role': l['role'] if l else None, 'replacement_score': round(effective, 1) if l else None,
                'gap': gap, 'quality': quality, 'quality_label': label,
                'coverage': [x['slot_id'] for x, _, _ in matches],
                'better_than_starters': [{'uid': x['uid'], 'name': self.byid[x['uid']]['name'],
                    'position': x['in_possession']['position'], 'position_es': POS_CODES_ES.get(x['in_possession']['position']),
                    'score': x['score']} for x, v, _ in matches if v > x['score']]})
        return bench, replacements


def simulate_formation(dataset, formation_id='352', style='possession', primary_slot=0, excluded=(), prompt=None, overrides=None):
    if formation_id not in FORMATIONS_BY_ID:
        raise ValueError('Formación desconocida.')
    return AnalysisContext(dataset, style, primary_slot, excluded, prompt, overrides).build(FORMATIONS_BY_ID[formation_id])
