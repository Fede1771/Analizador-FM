"""Visible attribute labels, tactical styles and formation templates."""
import re
import unicodedata
ATTRS = {
    'crossing':'Centros', 'dribbling':'Regate', 'finishing':'Remate', 'heading':'Cabeceo',
    'long_shots':'Tiros lejanos', 'marking':'Marcaje', 'off_the_ball':'Desmarques',
    'passing':'Pases', 'penalty_taking':'Penaltis', 'tackling':'Entradas', 'vision':'Visión',
    'handling':'Blocaje', 'aerial_reach':'Alcance aéreo', 'command_of_area':'Mando en el área',
    'communication':'Comunicación', 'kicking':'Saques de puerta', 'throwing':'Saques con la mano',
    'anticipation':'Anticipación', 'decisions':'Decisiones', 'one_on_ones':'Uno contra uno',
    'positioning':'Colocación', 'reflexes':'Reflejos', 'first_touch':'Primer toque',
    'technique':'Técnica', 'flair':'Talento', 'corners':'Córners', 'teamwork':'Trabajo en equipo',
    'work_rate':'Sacrificio', 'long_throws':'Saques largos', 'eccentricity':'Excentricidad',
    'rushing_out':'Salidas', 'punching':'Tendencia a despejar', 'acceleration':'Aceleración',
    'free_kick_taking':'Faltas', 'strength':'Fuerza', 'stamina':'Resistencia', 'pace':'Velocidad',
    'jumping_reach':'Salto', 'leadership':'Liderazgo', 'balance':'Equilibrio', 'bravery':'Valentía',
    'aggression':'Agresividad', 'agility':'Agilidad', 'natural_fitness':'Forma natural',
    'determination':'Determinación', 'composure':'Serenidad', 'concentration':'Concentración',
}

STYLES = {
 'possession': {'name':'Posesión', 'fm26_style':'Tiquitaca', 'fm26_style_alt':'Control de la posesión', 'mentality':'Positiva',
 'description':'Progresar con apoyos y controlar el balón.',
 'weights':{'passing':3,'first_touch':2,'decisions':2,'technique':2,'composure':1},
 'ip':['Pases más cortos y ritmo moderado.','Salir jugando desde la defensa.','Mantener amplitud con los extremos y apoyos por dentro.'],
 'oop':['Bloque medio-alto, sin forzar una línea máxima.','Presionar como unidad y proteger el centro.'],
 'transition':['Tras recuperar, asegurar el primer pase.','Tras perder, presionar cerca del balón si hay cobertura.'],
 'risk':'La salida corta exige decisiones y serenidad; ante una presión eficaz conviene una salida alternativa.'},
 'press': {'name':'Presión alta', 'fm26_style':'Contrapresión', 'fm26_style_alt':'Tiquitaca vertical', 'mentality':'Ofensivo',
 'description':'Recuperar arriba y atacar con intensidad.',
 'weights':{'work_rate':3,'stamina':3,'teamwork':2,'acceleration':2,'anticipation':2},
 'ip':['Ritmo alto con apoyos cercanos.','Atacar el espacio después de recuperar.','Conservar un pivote por detrás del balón.'],
 'oop':['Bloque alto y presión frecuente.','Orientar la presión hacia las bandas.'],
 'transition':['Contrapresión tras pérdida cuando el equipo esté junto.','Buscar profundidad tras recuperar.'],
 'risk':'La intensidad aumenta la exigencia física. Bajar la línea si los centrales quedan expuestos a carreras.'},
 'counter': {'name':'Transiciones', 'fm26_style':'Contrataque directo', 'fm26_style_alt':'Contrataque fluido', 'mentality':'Cauta',
 'description':'Cerrar espacios y acelerar hacia campo rival.',
 'weights':{'pace':3,'acceleration':3,'off_the_ball':2,'anticipation':2,'passing':1},
 'ip':['Pases algo más directos hacia el espacio.','Buscar rápidamente a los atacantes.','Subir un lateral por vez.'],
 'oop':['Bloque medio y líneas compactas.','Proteger el carril central antes de saltar a presionar.'],
 'transition':['Reagruparse tras pérdida.','Contraatacar cuando exista ventaja espacial.'],
 'risk':'Si el rival espera atrás, hará falta una variante paciente para no regalar la posesión.'},
 'wide': {'name':'Juego por bandas', 'fm26_style':'Juego por las bandas', 'fm26_style_alt':'Vía rápida', 'mentality':'Positiva',
 'description':'Amplitud, desequilibrio y llegadas al área.',
 'weights':{'crossing':3,'dribbling':3,'pace':2,'off_the_ball':2,'teamwork':1},
 'ip':['Abrir el campo con los extremos.','Alternar desborde y apoyos del lateral.','Priorizar pases atrás si no hay ventaja aérea.'],
 'oop':['Bloque medio con ayudas de los extremos.','Proteger las espaldas de los laterales.'],
 'transition':['Buscar la banda libre al recuperar.','Replegar por el lado contrario al balón.'],
 'risk':'Dos laterales arriba pueden dejar las bandas abiertas. Mantener cobertura con el pivote.'},
}


def slot(role, ip, oop, defend=None):
    return {'role':role, 'ip':ip, 'oop':oop, 'defend':defend or role}


FORMATIONS = [
 {'id':'433','name':'4-3-3','defensive':'4-1-4-1','idea':'Un pivote fija la base; los interiores conectan con extremos abiertos.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('lb',[13,66],[15,71]),slot('bpd',[37,74],[38,75]),slot('cb',[63,74],[62,75]),slot('rb',[87,66],[85,71]),
 slot('dm',[50,58],[50,58]),slot('am',[34,42],[35,43],'cm'),slot('cm',[66,42],[65,43]),slot('lw',[15,25],[14,42]),slot('st',[50,19],[50,23]),slot('rw',[85,25],[86,42])]},
 {'id':'4231','name':'4-2-3-1','defensive':'4-4-1-1','idea':'Doble base para cubrir la espalda del creador y conectar con tres atacantes.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('lb',[13,66],[15,73]),slot('bpd',[37,74],[38,76]),slot('cb',[63,74],[62,76]),slot('rb',[87,66],[85,73]),
 slot('dm',[38,55],[38,53],'cm'),slot('d play',[62,55],[62,53],'cm'),slot('am',[50,36],[50,35]),slot('lw',[15,29],[14,51]),slot('st',[50,17],[50,20]),slot('rw',[85,29],[86,51])]},
 {'id':'442','name':'4-4-2','defensive':'4-4-2','idea':'Dos referencias de ataque y dos líneas de cuatro; exige trabajo de los jugadores de banda.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('lb',[13,68],[15,74]),slot('bpd',[37,75],[38,77]),slot('cb',[63,75],[62,77]),slot('rb',[87,68],[85,74]),
 slot('d play',[38,51],[38,52],'cm'),slot('cm',[62,51],[62,52]),slot('lw',[14,44],[14,51]),slot('rw',[86,44],[86,51]),slot('st',[37,21],[37,25]),slot('target',[63,21],[63,25])]},
]

FORMATION_CATALOG = [
 {'id':'352','name':'3-5-2','defensive':'5-3-2','category':'Línea de 3 / 5','idea':'Tres centrales sólidos, carrileros para toda la banda, trivote en el medio y dos puntas fijando a los zagueros rivales.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('bpd',[27,75],[28,76]),slot('cb',[50,76],[50,78]),slot('cb',[73,75],[72,76]),
 slot('wb',[12,54],[14,72]),slot('dm',[50,58],[50,58]),slot('cm',[35,43],[35,46]),slot('cm',[65,43],[65,46]),
 slot('wb',[88,54],[86,72]),slot('st',[38,20],[38,24]),slot('target',[62,20],[62,24])]},
 {'id':'433','name':'4-3-3','defensive':'4-1-4-1','category':'Línea de 4','idea':'Un pivote fija la base; los interiores conectan con extremos abiertos.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('lb',[13,66],[15,71]),slot('bpd',[37,74],[38,75]),slot('cb',[63,74],[62,75]),slot('rb',[87,66],[85,71]),
 slot('dm',[50,58],[50,58]),slot('am',[34,42],[35,43],'cm'),slot('cm',[66,42],[65,43]),slot('lw',[15,25],[14,42]),slot('st',[50,19],[50,23]),slot('rw',[85,25],[86,42])]},
 {'id':'4231','name':'4-2-3-1','defensive':'4-4-1-1','category':'Línea de 4','idea':'Doble base para cubrir la espalda del creador y conectar con tres atacantes.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('lb',[13,66],[15,73]),slot('bpd',[37,74],[38,76]),slot('cb',[63,74],[62,76]),slot('rb',[87,66],[85,73]),
 slot('dm',[38,55],[38,53],'cm'),slot('d play',[62,55],[62,53],'cm'),slot('am',[50,36],[50,35]),slot('lw',[15,29],[14,51]),slot('st',[50,17],[50,20]),slot('rw',[85,29],[86,51])]},
 {'id':'442','name':'4-4-2','defensive':'4-4-2','category':'Línea de 4','idea':'Dos referencias de ataque y dos líneas de cuatro; exige trabajo de los jugadores de banda.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('lb',[13,68],[15,74]),slot('bpd',[37,75],[38,77]),slot('cb',[63,75],[62,77]),slot('rb',[87,68],[85,74]),
 slot('d play',[38,51],[38,52],'cm'),slot('cm',[62,51],[62,52]),slot('lw',[14,44],[14,51]),slot('rw',[86,44],[86,51]),slot('st',[37,21],[37,25]),slot('target',[63,21],[63,25])]},
 {'id':'343','name':'3-4-3','defensive':'5-4-1','category':'Línea de 3 / 5','idea':'Línea de 3 con carrileros adelantados, doble pivote de equilibrio y dos extremos acompañando al delantero.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('bpd',[27,75],[28,76]),slot('cb',[50,76],[50,78]),slot('cb',[73,75],[72,76]),
 slot('wb',[12,54],[14,72]),slot('cm',[38,52],[38,55]),slot('cm',[62,52],[62,55]),slot('wb',[88,54],[86,72]),
 slot('lw',[22,30],[20,48]),slot('rw',[78,30],[80,48]),slot('st',[50,18],[50,22])]},
 {'id':'532','name':'5-3-2','defensive':'5-3-2','category':'Línea de 3 / 5','idea':'Bloque ultracompacto con 5 defensas, 3 volantes de lucha y salidas directas con dos puntas veloces.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('lb',[13,70],[14,74]),slot('bpd',[32,76],[32,77]),slot('cb',[50,77],[50,79]),
 slot('cb',[68,76],[68,77]),slot('rb',[87,70],[86,74]),slot('dm',[50,57],[50,57]),slot('cm',[34,45],[34,48]),
 slot('cm',[66,45],[66,48]),slot('st',[38,20],[38,24]),slot('target',[62,20],[62,24])]},
 {'id':'41212','name':'4-1-2-1-2 Rombo','defensive':'4-3-1-2','category':'Línea de 4','idea':'Rombo en mediocampo con enganche y pivote; domina la zona interior y da libertad a dos delanteros.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('lb',[13,64],[15,72]),slot('bpd',[37,74],[38,76]),slot('cb',[63,74],[62,76]),
 slot('rb',[87,64],[85,72]),slot('dm',[50,60],[50,60]),slot('cm',[33,45],[33,48]),slot('cm',[67,45],[67,48]),
 slot('am',[50,33],[50,35]),slot('st',[38,19],[38,23]),slot('target',[62,19],[62,23])]},
 {'id':'3412','name':'3-4-1-2','defensive':'5-2-1-2','category':'Línea de 3 / 5','idea':'Carrileros largos, doble pivote de contención, enganche creador entre líneas y dos delanteros centros.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('bpd',[27,75],[28,76]),slot('cb',[50,76],[50,78]),slot('cb',[73,75],[72,76]),
 slot('wb',[12,54],[14,72]),slot('cm',[38,54],[38,56]),slot('cm',[62,54],[62,56]),slot('wb',[88,54],[86,72]),
 slot('am',[50,34],[50,36]),slot('st',[38,20],[38,24]),slot('target',[62,20],[62,24])]},
 {'id':'424','name':'4-2-4','defensive':'4-4-2','category':'Línea de 4','idea':'Ataque agresivo con dos extremos abiertos y dos centrodelanteros presionando en el área contraria.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('lb',[13,67],[15,73]),slot('bpd',[37,74],[38,76]),slot('cb',[63,74],[62,76]),
 slot('rb',[87,67],[85,73]),slot('d play',[38,52],[38,54],'cm'),slot('cm',[62,52],[62,54]),slot('lw',[15,26],[14,50]),
 slot('rw',[85,26],[86,50]),slot('st',[38,19],[38,23]),slot('target',[62,19],[62,23])]},
 {'id':'523','name':'5-2-3','defensive':'5-4-1','category':'Línea de 3 / 5','idea':'Estructura rocosa de tres centrales y carrileros, dos mediocentros de apoyo y tridente veloz en ataque.', 'slots':[
 slot('gk',[50,91],[50,91]),slot('bpd',[27,75],[28,76]),slot('cb',[50,76],[50,78]),slot('cb',[73,75],[72,76]),
 slot('wb',[12,54],[14,72]),slot('cm',[38,54],[38,56]),slot('cm',[62,54],[62,56]),slot('wb',[88,54],[86,72]),
 slot('lw',[18,28],[16,48]),slot('rw',[82,28],[84,48]),slot('st',[50,18],[50,22])]},
]
FORMATIONS_BY_ID = {f['id']: f for f in FORMATION_CATALOG}


import re
import unicodedata

def normalize(text):
    text = unicodedata.normalize('NFD', text.lower())
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text

def parse_tactical_prompt(text):
    if not text or not text.strip():
        return None
    raw = text.strip()
    norm = normalize(raw)
    
    pillars = []
    style_votes = {'possession': 0, 'press': 0, 'counter': 0, 'wide': 0}
    team_overrides = {}
    player_instructions_guide = []
    
    # Pillar 1: Posesión / Dominio / Salir jugando
    possession_matches = re.findall(r'(posesion|pelota|balon|control|toque|pases? cortos?|salir jugando|paciencia|elabora|asociar|tiki.?taka|circular)', norm)
    if possession_matches:
        style_votes['possession'] += len(possession_matches) * 2
        team_overrides['passing_directness'] = 'Shorter'
        team_overrides['tempo'] = 'Lower'
        team_overrides['build_up_strategy_ip'] = 'Play Through Press'
        team_overrides['pass_reception_ip'] = 'Pass to Feet'
        pillars.append({
            'id': 'possession',
            'title': 'Control y circulación con posesión',
            'badge': '+Posesión',
            'color': '#38bdf8',
            'summary': 'Progresión limpia desde el fondo con pases cortos y ritmo pausado para desgastar al rival.',
            'fm26_instruction': 'Con balón: Pases más cortos, Ritmo más bajo, Salir jugando ante la presión y Pases al pie.'
        })
        player_instructions_guide.append({
            'line': 'Salida limpia desde el fondo y apoyos',
            'tip': 'Priorizá Portero con salida y Central con salida para no rifar el balón. Con laterales, podés usar Lateral interior para formar línea de 3 en salida, o Extremo invertido para sumar creación asociativa por dentro.',
            'guide_ref': 'Guía capturas: el lateral interior cierra a la línea de centrales; el extremo invertido asume una función creativa interior.'
        })
        
    # Pillar 2: Ocasiones de gol / Ataque / Remates
    chances_matches = re.findall(r'(chances?|cahcnes?|ocasion|ocasiones|goles?|gol|llegadas?|atacar?|ataque|remates?|rematar|peligro|ofensiv|profundidad|definir|crear|arco rival)', norm)
    if chances_matches:
        style_votes['press'] += 1
        style_votes['possession'] += 1
        team_overrides['attacking_transition_ip'] = 'Counter-Attack' if 'contra' in norm else 'Hold Shape'
        pillars.append({
            'id': 'chances',
            'title': 'Generación de ocasiones y finalización',
            'badge': '+Ocasiones',
            'color': '#34d399',
            'summary': 'Desmarques continuos hacia el área, habilitaciones al espacio y presencia de varios hombres en zona de remate.',
            'fm26_instruction': 'Transición ofensiva: Atacar espacios libres y dar libertad de llegada a extremos y delanteros.'
        })
        player_instructions_guide.append({
            'line': 'Extremos y atacantes con llegada y gol',
            'tip': 'Asigná Delantero interior (Inside Forward) si querés que tus extremos ataquen el área buscando el gol directo, o Delantero entre líneas (Channel Forward) para atacar los canales entre central y lateral.',
            'guide_ref': 'Guía capturas: el Delantero interior busca el gol y remate directo (a diferencia del Extremo invertido asociativo); el Channel Forward rompe en el intervalo central-lateral.'
        })
        
    # Pillar 3: Evitar remates / Solidez defensiva / No encajar
    defense_matches = re.findall(r'(evitar.*remat|no.*rematen|pocos.*remates|no.*pateen|no.*lleguen|arco en cero|valla invicta|no encajar|solidez|defensa|cerrar espacios|compact|ordenad|sin goles|proteger)', norm)
    if defense_matches:
        style_votes['possession'] += 1
        style_votes['counter'] += 1
        team_overrides['line_of_engagement_oop'] = 'Mid Block'
        team_overrides['defensive_line_oop'] = 'Standard'
        team_overrides['trigger_press_oop'] = 'More Often'
        team_overrides['defensive_transition_oop'] = 'Counter-Press' if ('posesion' in norm or 'recuperar' in norm) else 'Regroup'
        pillars.append({
            'id': 'defense',
            'title': 'Protección del arco y reducción de remates rivales',
            'badge': '+Solidez defensiva',
            'color': '#f472b6',
            'summary': 'Bloque medio compacto sin huecos entre líneas, pivote defensivo que tapa la frontal del área (Zona 14) y entradas limpias.',
            'fm26_instruction': 'Sin balón: Bloque medio, Línea estándar y pivote como pantalla en zona de remate.'
        })
        player_instructions_guide.append({
            'line': 'Pantalla en Zona 14 y coberturas defensivas',
            'tip': 'Configurá Mediocentro fijo (Screening DM) o Mediocampista fijo para proteger el espacio delante de los centrales y tapar disparos lejanos. En la zaga, Defensa central de cobertura para no saltar en falso.',
            'guide_ref': 'Guía capturas: el rol fijo/screening se planta en la medialuna para bloquear remates frontales y cortar balones sueltos.'
        })

    # Pillar 4: Presión alta
    press_matches = re.findall(r'(presi[oó]n alta|presionar arriba|asfixiar|ahogar|intensidad|gegenpress|recuperar r[aá]pido)', norm)
    if press_matches:
        style_votes['press'] += len(press_matches) * 2
        team_overrides['line_of_engagement_oop'] = 'High Press'
        team_overrides['trigger_press_oop'] = 'More Often'
        team_overrides['defensive_line_oop'] = 'Higher'
        team_overrides['defensive_transition_oop'] = 'Counter-Press'
        pillars.append({
            'id': 'press',
            'title': 'Presión alta y contrapresión inmediata',
            'badge': '+Presión',
            'color': '#f59e0b',
            'summary': 'Acoso continuo a los centrales rivales y salto coordinado del bloque.',
            'fm26_instruction': 'Sin balón: Bloque alto, Línea defensiva más alta y Contrapresión tras pérdida.'
        })
        player_instructions_guide.append({
            'line': 'Salto coordinado de presión alta',
            'tip': 'Usá Lateral presionante, Mediocentro presionante y Delantero centro con retroceso para acosar la salida rival en su propio campo.',
            'guide_ref': 'Guía capturas: los roles presionantes adelantan su intervención para disputar la pelota de inmediato.'
        })

    # Pillar 5: Contraataque / Transición rápida
    counter_matches = re.findall(r'(contraataque|contra|transici[oó]n|r[aá]pid|direct|velocidad|espacios?|v[eé]rtigo)', norm)
    if counter_matches:
        style_votes['counter'] += len(counter_matches) * 2
        team_overrides['attacking_transition_ip'] = 'Counter-Attack'
        team_overrides['passing_directness'] = 'More Direct'
        team_overrides['tempo'] = 'Higher'
        team_overrides['defensive_transition_oop'] = 'Regroup'
        pillars.append({
            'id': 'counter',
            'title': 'Transiciones verticales al espacio',
            'badge': '+Transición',
            'color': '#a78bfa',
            'summary': 'Salidas vertiginosas apenas se recupera el balón atacando la espalda de la defensa contraria.',
            'fm26_instruction': 'Transición: Contraataque tras recuperar; Pases más directos hacia los atacantes.'
        })
        player_instructions_guide.append({
            'line': 'Vías de escape en ataque (Roles Outlet)',
            'tip': 'Asigná Delantero centro estacionario o Extremo estacionario para que no retrocedan en repliegue y queden como vía de escape inmediata.',
            'guide_ref': 'Guía capturas: los roles estacionarios (outlets) reducen el retroceso y quedan preparados para lanzar la contra.'
        })

    # Pillar 6: Bandas y centros
    wide_matches = re.findall(r'(bandas?|centros?|centrar|desborde|a[eé]re|cabez|extremos abiertos)', norm)
    if wide_matches:
        style_votes['wide'] += len(wide_matches) * 2
        pillars.append({
            'id': 'wide',
            'title': 'Juego por bandas y centros al área',
            'badge': '+Bandas',
            'color': '#38bdf8',
            'summary': 'Amplitud con extremos y laterales con centros dirigidos a las referencias en el área.',
            'fm26_instruction': 'Con balón: Abrir el campo y buscar centros a las referencias de área.'
        })
        player_instructions_guide.append({
            'line': 'Amplitud exterior y remate aéreo',
            'tip': 'Combiná Extremo o Carrilero con Delantero torre (Target Forward) para ganar juego aéreo y segundas pelotas.',
            'guide_ref': 'Guía capturas: el Delantero torre sirve de referencia física y aérea adelantada.'
        })

    # Formación solicitada (ej. 3-5-2, 343, 5-3-2, etc.)
    requested_formation = None
    form_patterns = [
        (r'\b(3[- ]?5[- ]?2)\b', '352'),
        (r'\b(3[- ]?4[- ]?3)\b', '343'),
        (r'\b(5[- ]?3[- ]?2)\b', '532'),
        (r'\b(4[- ]?1[- ]?2[- ]?1[- ]?2|rombo|diamante)\b', '41212'),
        (r'\b(3[- ]?4[- ]?1[- ]?2)\b', '3412'),
        (r'\b(4[- ]?2[- ]?4)\b', '424'),
        (r'\b(5[- ]?2[- ]?3)\b', '523'),
        (r'\b(4[- ]?3[- ]?3)\b', '433'),
        (r'\b(4[- ]?2[- ]?3[- ]?1)\b', '4231'),
        (r'\b(4[- ]?4[- ]?2)\b', '442'),
    ]
    for pattern, fid in form_patterns:
        if re.search(pattern, norm):
            requested_formation = fid
            break
    if requested_formation and requested_formation in FORMATIONS_BY_ID:
        target_f = FORMATIONS_BY_ID[requested_formation]
        pillars.insert(0, {
            'id': 'formation_' + requested_formation,
            'title': f'Alineación solicitada: {target_f["name"]}',
            'badge': f'Formación {target_f["name"]}',
            'color': '#10b981',
            'summary': f'Optimizado específicamente para el dibujo {target_f["name"]} ({target_f["defensive"]} sin balón). {target_f["idea"]}',
            'fm26_instruction': f'Estructura con posesión {target_f["name"]} y repliegue en {target_f["defensive"]}.'
        })

    best_style = max(style_votes.items(), key=lambda x: x[1])[0] if any(style_votes.values()) else 'possession'
    
    if not pillars:
        pillars.append({
            'id': 'balanced',
            'title': 'Planteo equilibrado',
            'badge': 'Equilibrado',
            'color': '#94a3b8',
            'summary': 'Estructura equilibrada basada en los mejores atributos de tu plantilla.',
            'fm26_instruction': 'Mantener instrucciones estándar y ajustar según el rival.'
        })

    # Determine recommended mentality from the 7 FM26 official options:
    # ['Muy defensiva', 'Defensivo', 'Cauta', 'Equilibrada', 'Positiva', 'Ofensivo', 'Muy ofensiva']
    if re.search(r'(muy ofensiv|a por todo|con todo|arriesgar al maximo|a matar)', norm):
        rec_mentality = 'Muy ofensiva'
    elif re.search(r'(muy defensiv|autobus|colgarse del travesa|todos atras)', norm):
        rec_mentality = 'Muy defensiva'
    elif re.search(r'(defensiv|solidez extrema|no recibir goles|blindar|cerrar el arco)', norm) and 'posesion' not in norm:
        rec_mentality = 'Defensivo'
    elif re.search(r'(caut[ao]|precavid[ao]|esperar|cerrado)', norm):
        rec_mentality = 'Cauta'
    elif re.search(r'(equilibrad[ao]|balance)', norm):
        rec_mentality = 'Equilibrada'
    elif re.search(r'(ofensiv|muchos goles|atacar con todo|asfixiar|agresiv)', norm) and 'posesion' not in norm:
        rec_mentality = 'Ofensivo'
    else:
        rec_mentality = STYLES[best_style].get('mentality', 'Positiva')

    return {
        'original_prompt': raw,
        'pillars': pillars,
        'recommended_style': best_style,
        'recommended_mentality': rec_mentality,
        'team_overrides': team_overrides,
        'player_guides': player_instructions_guide,
        'requested_formation': requested_formation,
    }
