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
# Each slot owns both phases. Index order is player identity, never a sort by line.
_POSITIONS = {
 '433': (['GK','DL','DC','DC','DR','DM','MC','MC','AML','STC','AMR'], ['GK','DL','DC','DC','DR','DM','MC','MC','ML','STC','MR']),
 '4231': (['GK','DL','DC','DC','DR','DM','DM','AMC','AML','STC','AMR'], ['GK','DL','DC','DC','DR','MC','MC','AMC','ML','STC','MR']),
 '442': (['GK','DL','DC','DC','DR','MC','MC','ML','MR','STC','STC'], ['GK','DL','DC','DC','DR','MC','MC','ML','MR','STC','STC']),
 '352': (['GK','DC','DC','DC','WBL','DM','MC','MC','WBR','STC','STC'], ['GK','DC','DC','DC','WBL','DM','MC','MC','WBR','STC','STC']),
 '343': (['GK','DC','DC','DC','WBL','MC','MC','WBR','AML','AMR','STC'], ['GK','DC','DC','DC','WBL','MC','MC','WBR','ML','MR','STC']),
 '532': (['GK','DL','DC','DC','DC','DR','DM','MC','MC','STC','STC'], ['GK','DL','DC','DC','DC','DR','DM','MC','MC','STC','STC']),
 '41212': (['GK','DL','DC','DC','DR','DM','MC','MC','AMC','STC','STC'], ['GK','DL','DC','DC','DR','MC','MC','MC','AMC','STC','STC']),
 '3412': (['GK','DC','DC','DC','WBL','MC','MC','WBR','AMC','STC','STC'], ['GK','DC','DC','DC','WBL','MC','MC','WBR','AMC','STC','STC']),
 '424': (['GK','DL','DC','DC','DR','MC','MC','AML','AMR','STC','STC'], ['GK','DL','DC','DC','DR','MC','MC','ML','MR','STC','STC']),
 '523': (['GK','DC','DC','DC','WBL','MC','MC','WBR','AML','AMR','STC'], ['GK','DC','DC','DC','WBL','MC','MC','WBR','ML','MR','STC']),
}
for _form in FORMATION_CATALOG:
    _ip, _oop = _POSITIONS[_form['id']]
    for _index, _slot in enumerate(_form['slots']):
        _slot.update(id=f"{_form['id']}:{_index}", ip_position=_ip[_index], oop_position=_oop[_index])
    if _form['id'] == '41212':
        _form['slots'][5]['oop'] = [50, 48]
FORMATIONS = FORMATION_CATALOG
FORMATIONS_BY_ID = {f['id']: f for f in FORMATION_CATALOG}
del _POSITIONS


def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')


INTENTS = {
 'possession': (r'\b(?:posesion|pelota|balon|control\w*|toques?|pases? cortos?|salir jugando|paciencia|elaborar|asociar|tiki.?taka|circular)\b', 'Control y circulación', '+Posesión'),
 'chances': (r'\b(?:chances?|cahcnes?|ocasiones?|goles?|gol|llegadas?|atacar|ataque|remates?|rematar|peligro|profundidad|crear)\b', 'Generar ocasiones', '+Ocasiones'),
 'defense': (r'(?:evitar.{0,30}remat|no.{0,20}(?:rematen|pateen|lleguen|encajar|recibir goles)|arco en cero|valla invicta|solidez|defensa|cerrar espacios|compact\w*|ordenad\w*|proteger)', 'Proteger el arco', '+Solidez defensiva'),
 'press': (r'\b(?:presion alta|presionar arriba|asfixiar|ahogar|intensidad|gegenpress|contrapresion|recuperar rapido)\b', 'Presionar arriba', '+Presión'),
 'counter': (r'\b(?:contraataques?|contragolpes?|transiciones?|juego directo|pases? directos?|vertical(?:es)?|al espacio)\b', 'Transiciones verticales', '+Transición'),
 'wide': (r'\b(?:bandas?|centros?|centrar|desborde|juego aereo|cabecear|extremos abiertos)\b', 'Amplitud y centros', '+Bandas'),
}


def parse_tactical_prompt(text):
    """Deterministic rules with clause-local negation and explicit conflict resolution."""
    if not text or not text.strip():
        return None
    raw = text.strip()
    norm = normalize(raw)
    active, denied, last = {}, {}, {}
    warnings = []
    for key, (pattern, title, badge) in INTENTS.items():
        for match in re.finditer(pattern, norm):
            prefix = re.split(r'[,;.!?]|\b(?:pero|aunque|y)\b', norm[:match.start()])[-1]
            negated = key != 'defense' and bool(re.search(r'\b(?:no|sin|evitar|evita|nunca)\b(?:\s+\w+){0,6}\s*$', prefix))
            # A defensive request such as "evitar remates" is not an attacking request.
            if key == 'chances' and re.search(r'(?:evitar|no|pocos).{0,35}$', prefix):
                continue
            active[key] = not negated
            denied[key] = negated
            last[key] = match.start()
    votes = {k: 0 for k in STYLES}
    for key in ('possession','press','counter','wide'):
        if active.get(key):
            votes[key] += 3
    if active.get('chances') or active.get('defense'):
        votes['possession'] += 1
    best = max(votes, key=lambda k: (votes[k], last.get(k, -1))) if any(votes.values()) else 'possession'
    overrides = {}
    if active.get('possession'):
        overrides.update(passing_directness='Shorter', tempo='Lower', build_up_strategy_ip='Play Through Press', pass_reception_ip='Pass to Feet')
    if active.get('chances'):
        overrides['attacking_transition_ip'] = 'Hold Shape'
    if active.get('defense'):
        overrides.update(line_of_engagement_oop='Mid Block', defensive_line_oop='Standard', trigger_press_oop='More Often', defensive_transition_oop='Counter-Press' if active.get('possession') else 'Regroup')
    if active.get('counter'):
        overrides['attacking_transition_ip'] = 'Counter-Attack'
        if not active.get('possession') or last['counter'] > last['possession']:
            overrides.update(passing_directness='More Direct', tempo='Higher')
        overrides['defensive_transition_oop'] = 'Regroup'
    if active.get('press'):
        overrides.update(line_of_engagement_oop='High Press', defensive_line_oop='Higher', trigger_press_oop='More Often', defensive_transition_oop='Counter-Press')
    if denied.get('press'):
        overrides.update(line_of_engagement_oop='Mid Block', defensive_line_oop='Standard', trigger_press_oop='Standard', defensive_transition_oop='Regroup')
    if denied.get('counter'):
        overrides['attacking_transition_ip'] = 'Hold Shape'
    if denied.get('possession'):
        overrides.update(passing_directness='More Direct', build_up_strategy_ip='Balanced')
    if active.get('possession') and active.get('counter'):
        warnings.append('Pediste control y transiciones: se conserva el contraataque tras recuperar; el último pedido determina pases y ritmo.')
    if active.get('press') and active.get('defense'):
        warnings.append('La presión alta tiene prioridad sobre el bloque medio; revisá el espacio a la espalda de la defensa.')
    if denied.get('wide'):
        overrides['progress_through_ip'] = 'Balanced'
        warnings.append('Se evitó elegir el estilo de bandas. La amplitud concreta depende de la formación y de los roles.')
    requested = None
    for form in sorted(FORMATION_CATALOG, key=lambda f: -len(f['id'])):
        digits = r'[- ]?'.join(form['id'])
        match = re.search(r'\b' + digits + r'\b', norm)
        if match and not re.search(r'\b(?:no|sin|evitar)\b.{0,25}$', norm[:match.start()]):
            requested = form['id']
            break
    if requested is None and re.search(r'\b(?:rombo|diamante)\b', norm) and not re.search(r'(?:no|sin|evitar).{0,20}(?:rombo|diamante)', norm):
        requested = '41212'
    if not any(active.values()) and not any(denied.values()) and requested is None:
        warnings.append('No reconocimos una intención concreta. Se conserva una base de posesión; podés ajustar el estilo y las instrucciones.')
    mentality = STYLES[best]['mentality']
    for pattern, value in ((r'\bmuy ofensiv\w*', 'Muy ofensiva'), (r'\b(?:muy defensiv\w*|autobus)', 'Muy defensiva'), (r'\bdefensiv\w*', 'Defensivo'), (r'\bcaut[ao]\b', 'Cauta'), (r'\b(?:equilibrad[ao]|balance)\b', 'Equilibrada'), (r'\bofensiv\w*', 'Ofensivo')):
        match = re.search(pattern, norm)
        if match and not re.search(r'\b(?:no|sin|evitar)\b.{0,20}$', norm[:match.start()]):
            mentality = value
            break
    pillars = [{'id': k, 'title': INTENTS[k][1], 'badge': INTENTS[k][2], 'color': '#38bdf8',
                'summary': 'Pedido reconocido y aplicado mediante reglas explícitas.',
                'fm26_instruction': 'Revisá los ajustes aplicados antes de llevarlos al juego.'} for k in INTENTS if active.get(k)]
    return {'original_prompt': raw, 'pillars': pillars, 'recommended_style': best,
            'recommended_mentality': mentality, 'team_overrides': overrides, 'player_guides': [],
            'requested_formation': requested, 'warnings': warnings,
            'recognized': [k for k in INTENTS if active.get(k)],
            'avoided': [k for k in INTENTS if denied.get(k)]}
