"""Assemble the auditable FM26 UI/resource handoff; no production data changes."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/relevamiento-fm26-2026-10-25'

# id | reference Spanish name | position families | description key | name key | current UI evidence
# These are application reference IDs, NOT decoded FM save identifiers.
ROLE_ROWS = '''
goalkeeper_ip|Portero|GK|690521|688068|001
ball_playing_goalkeeper_ip|Portero con salida|GK|690523|688113|003
no_nonsense_goalkeeper_ip|Portero práctico|GK|690522|688114|002
goalkeeper_oop|Portero|GK|690561|688068|007
sweeper_keeper_oop|Portero líbero|GK|690562|688070|008
line_holding_keeper_oop|Portero entre palos|GK|690560|688069|007
centre_back_ip|Central / Defensa central|DC|690525|688071|013
advanced_centre_back_ip|Central avanzado|DC|690527|688115|013
ball_playing_centre_back_ip|Central con salida|DC|690524|688116|014
no_nonsense_center_back_ip|Central práctico|DC|690526|688129|013
wide_centre_back_ip|Central abierto|DC|690528|688117|
overlapping_centre_back_ip|Central que dobla|DC|690529|688118|
centre_back_oop|Central / Defensa central|DC|690563|688071|040
stopping_centre_back_oop|Zaguero|DC|696068|688073|040
covering_centre_back_oop|Defensa central de cobertura|DC|690564|688072|040
wide_centre_back_oop|Central abierto|DC|690513|688076|
covering_wide_centre_back_oop|Central de cobertura abierta|DC|690511|688074|
stopping_wide_centre_back_oop|Zaguero abierto|DC|696071|688075|
full_back_ip|Lateral|DL,DR|690530|688077|011
wing_back_ip|Carrilero|DL,DR,WBL,WBR|690534|688080|011
inside_wing_back_ip|Carrilero interior|DL,DR,WBL,WBR|690532|688142|011
inside_full_back_ip|Lateral interior|DL,DR|690531|688107|011
playmaking_wing_back_ip|Carrilero organizador|DL,DR,WBL,WBR|690533|688143|011
advanced_wing_back_ip|Carrilero avanzado|WBL,WBR|690535|688136|
full_back_oop|Lateral / Lateral defensivo|DL,DR|690514|688077|041
holding_full_back_oop|Lateral de contención|DL,DR|690515|688078|041
pressing_full_back_oop|Lateral presionante|DL,DR|690516|688079|041
wing_back_oop|Carrilero|WBL,WBR|690518|688080|
holding_wing_back_oop|Carrilero de contención|WBL,WBR|690517|688081|
pressing_wing_back_oop|Carrilero presionante|WBL,WBR|690519|688082|
defensive_midfielder_ip|Mediocentro defensivo|DM|690536|688083|015
deep_lying_playmaker_ip|Organizador defensivo / Organizador retrasado|DM|690540|688119|015
half_back_ip|Medio cierre|DM|690537|688133|015
box_to_box_midfielder_ip|Mediocampista todoterreno|DM|690538|688121|
box_to_box_playmaker_ip|Organizador todoterreno|DM|690539|688145|
defensive_midfielder_oop|Mediocentro defensivo|DM|690493|688083|038
dropping_defensive_midfielder_oop|Mediocentro de repliegue|DM|690494|688084|038
pressing_defensive_midfielder_oop|Mediocentro presionante|DM|690497|688085|038
screening_defensive_midfielder_oop|Mediocentro fijo|DM|690495|688086|039
wide_covering_defensive_midfielder_oop|Mediocampista defensivo de cobertura abierta|DM|690496|688087|039
central_midfielder_ip|Mediocampista / Centrocampista|MC|690541|688088|016
wide_central_midfielder_ip|Mediocampista abierto|MC|690543|688123|017
midfield_playmaker_ip|Mediocampista organizador / Mediocentro organizador|MC|690542|688146|017
attacking_midfielder_ip|Mediapunta|MC,AMC|690544|688095|016
advanced_playmaker_ip|Organizador adelantado|MC,AMC|696046|688125|016
channel_midfielder_ip|Mediocampista entre líneas|MC,AMC|690549|688111|017
central_midfielder_oop|Mediocampista|MC|690499|688088|
pressing_central_midfielder_oop|Mediocampista presionante|MC|690501|688089|
screening_central_midfielder_oop|Mediocampista fijo|MC|690498|688090|
wide_covering_central_midfielder_oop|Mediocampista de cobertura abierta|MC|690500|688091|
wide_midfielder_ip|Mediocampista abierto|ML,MR|690545|688108|
winger_ip|Extremo|ML,MR,AML,AMR|690548|688102|018
inside_winger_ip|Extremo invertido|ML,MR,AML,AMR|690546|688110|018
playmaking_winger_ip|Extremo organizador|ML,MR,AML,AMR|690547|688141|018
wide_midfielder_oop|Mediocampista abierto|ML,MR|690503|688093|029
tracking_wide_midfielder_oop|Mediocampista abierto con retroceso|ML,MR|690502|688092|029
wide_outlet_wide_midfielder_oop|Mediocampista abierto estacionario|ML,MR|690504|688094|029
free_role_ip|Mediapunta libre|AMC|690550|688131|
second_striker_ip|Segundo delantero|AMC|690551|688140|
attacking_midfielder_oop|Mediapunta|AMC|690506|688095|037
tracking_attacking_midfielder_oop|Mediapunta con retroceso|AMC|690505|688098|037
central_outlet_attacking_midfielder_oop|Mediapunta estacionario|AMC|690507|688096|037
splitting_outlet_attacking_midfielder_oop|Mediapunta de ruptura con salida (nombre de recurso)|AMC|690508|688097|
inside_forward_ip|Delantero interior|AML,AMR|690552|688109|018
wide_forward_ip|Delantero abierto|AML,AMR|690553|696156|018
winger_oop|Extremo|AML,AMR|690492|688102|
tracking_winger_oop|Extremo con retroceso|AML,AMR|690509|688100|
inside_outlet_winger_oop|Extremo de salida invertida|AML,AMR|696094|696138|
wide_outlet_winger_oop|Extremo estacionario|AML,AMR|696097|688101|
deep_lying_forward_ip|Delantero de apoyo|STC|690556|688112|043
centre_forward_ip|Delantero centro|STC|690554|688103|042
target_forward_ip|Delantero torre|STC|690559|688126|042
poacher_ip|Ariete|STC|690558|688127|042
channel_forward_ip|Delantero entre líneas|STC|690555|688635|042
false_nine_ip|Falso nueve|STC|690557|688139|042
centre_forward_oop|Delantero centro|STC|690489|688103|036
tracking_centre_forward_oop|Delantero centro con retroceso|STC|690490|688104|036
central_outlet_centre_forward_oop|Delantero centro estacionario|STC|690488|688105|036
splitting_outlet_centre_forward_oop|Delantero centro de ruptura con salida (nombre de recurso)|STC|690487|688106|
'''

POSITIONS = [
 ('GK','POR','Portero','Zona del arco.'),
 ('DL','DF (I)','Defensa izquierdo / lateral','Banda de la línea defensiva.'),
 ('DR','DF (D)','Defensa derecho / lateral','Banda de la línea defensiva.'),
 ('DC','DF (C)','Defensa central','Distinguir puesto central y puestos laterales de una zaga; no perder el subpuesto.'),
 ('WBL','CR (I)','Carrilero izquierdo','Altura de carrilero; no equivale a lateral aunque comparta roles CP.'),
 ('WBR','CR (D)','Carrilero derecho','Altura de carrilero; no equivale a lateral aunque comparta roles CP.'),
 ('DM','MD','Mediocampista defensivo / mediocentro','Distinguir pivote central único y subpuestos de doble/triple pivote.'),
 ('MC','ME (C)','Mediocampista central','Distinguir centro e interiores a sus costados.'),
 ('ML','ME (I)','Mediocampista izquierdo','Banda a altura de mediocampo.'),
 ('MR','ME (D)','Mediocampista derecho','Banda a altura de mediocampo.'),
 ('AMC','MP (C)','Mediapunta central','Distinguir centro y medias puntas en los canales.'),
 ('AML','MP (I)','Mediapunta izquierdo / extremo','Banda adelantada.'),
 ('AMR','MP (D)','Mediapunta derecho / extremo','Banda adelantada.'),
 ('STC','DL (C)','Delantero centro','Distinguir punta central y puntas de los canales.'),
]

# Complete option sets observed in the current individual-instruction menus.
# Long descriptions come from installed resource keys, not invented engine rules.
INSTRUCTIONS = [
 ('attacking_width_ip','Amplitud del ataque','020',[
  ('Stay Wider','Abrirse a banda',703124),('Sit Narrower','Situarse más cerrado',706686),
  ('Move Into Channels','Moverse entre líneas',703125),('Standard','Estándar',683095)]),
 ('dribbling_direction_ip','Dirección del regate','026',[
  ('Run Wide With Ball','Abrirse con el balón',706661),('Cut Inside With Ball','Recortar hacia dentro',706660),('Standard','Estándar',683096)]),
 ('dribbling_frequency_ip','Frecuencia del regate','005',[
  ('Dribble More','Regatear más',703139),('Dribble Less','Regatear menos',703138),('Standard','Estándar',683097)]),
 ('forward_runs_ip','Carreras hacia adelante','021',[
  ('Make More Runs','Hacer más desmarques',706566),('Standard','Estándar',703134),('Make Fewer Runs','Hacer menos carreras',683145)]),
 ('freedom_of_movement_ip','Libertad de movimientos','022',[
  ('Roam From Position','Variar la posición',683144),('Follow Tactical Position','Sigue posición táctica',683143)]),
 ('hold_up_ball_ip','Aguantar el balón','027',[
  ('Yes','Sí',683166),('No','No',683167)]),
 ('shoot_ip','Disparos','025',[
  ('Shoot More Often','Disparar con más frecuencia',704617),('Shoot Less Often','Disparar con menos frecuencia',706455),('Standard','Normal',703157)]),
 ('passing_risk_ip','Riesgo en los pases','024',[
  ('Take More Risks','Tomar más riesgos',706523),('Take Fewer Risks','Tomar menos riesgos',703155),('Standard','Normal',703151)]),
 ('passing_directness_ip','Estrategia de pase','006',[
  ('Shorter','Más corto',706457),('More Direct','Más directo',706456),('Standard','Normal',703169)]),
 ('cross_from_ip','Centro desde','023',[
  ('Cross From Deep','Centro desde atrás',706459),('Byline','Línea de fondo',706453),('Standard','Normal',703144)]),
 ('crossing_strategy_ip','Estrategia de centros','028',[
  ('Far Post','Segundo palo',706448),('Centre','Centro',706446),('Near Post','Primer poste',706447),
  ('Target Forward','Delantero torre',703166),('Standard','Normal',703163)]),
 ('pressing_oop','Presión alta','031',[
  ('More Often','Más a menudo',703077),('Less Often','Menos a menudo',706458),('Standard','Normal',703084)]),
 ('marking_oop','Marca','032',[
  ('Mark Tighter','Marca más férrea',703086),('Standard','Normal',703094)]),
 ('tackling_oop','Entradas','033',[
  ('Tackle Harder','Entrar más fuerte',706568),('Ease Off Tackles','No entrar fuerte',706567),('Standard','Normal',703095)]),
 ('marking_target_oop','Objetivo de marca','034',[
  ('Mark Specific','Marca específica',706460),('Mark Position','Marcar posición',706454),('Standard','Normal',703115)]),
]

# Editorial Spanish explanations where the selected new resource key is missing
# from the installed es-419 LTC or still contains English. Never label these official.
EXPLANATIONS_ES = {
 706686:'Ocupar una posición más estrecha al atacar para acortar las distancias de pase con los compañeros.',
 706661:'Conducir hacia las bandas para ensanchar la jugada y estirar al rival.',
 706660:'Conducir hacia zonas centrales, entrando por dentro del defensor y orientándose hacia el arco.',
 706566:'Hacer más desmarques ofensivos al espacio para sumar amenazas y sobrecargar a la defensa rival.',
 704617:'Aumentar los intentos de remate cuando surge una oportunidad, en lugar de priorizar otro pase.',
 706455:'Conservar la pelota y esperar una ocasión clara antes de rematar.',
 706523:'Intentar más pases difíciles y pases al espacio, aceptando fallos a cambio de la posibilidad de romper la defensa.',
 706457:'Jugar pases más cortos que los del resto del equipo y simplificar el uso del balón.',
 706456:'Jugar pases más largos que los del resto del equipo para llevar la pelota hacia adelante con mayor rapidez.',
 706459:'Centrar en cuanto aparezca la ocasión, sin esperar a llegar a una zona más avanzada.',
 706453:'Avanzar con el balón por la banda antes de intentar el centro al área.',
 706448:'Dirigir los centros al segundo palo cuando sea posible.',
 706446:'Dirigir los centros hacia la zona central del área cuando sea posible.',
 706447:'Dirigir los centros al primer palo cuando sea posible.',
 706458:'Presionar con más paciencia y esperar una oportunidad adecuada para entrar al rival.',
 706568:'Disputar el balón de forma más agresiva y usar el físico y las entradas para recuperarlo.',
 706567:'Mantenerse firme, por el lado del arco propio, y orientar al rival lejos del peligro en vez de lanzarse a la entrada.',
 706460:'Seguir a un jugador rival concreto para limitar su participación. Esta instrucción se refiere al juego abierto y no cambia el marcaje en jugadas de balón parado.',
 706454:'Seguir al rival que ocupe el puesto seleccionado. Esta instrucción se refiere al juego abierto y no cambia el marcaje en jugadas de balón parado.',
}

TEAM_CURRENT = [
 ('CP','Vista general','Pases directos','Mucho más corto','044'),
 ('CP','Vista general','Ritmo de juego','Mucho más bajo','044'),
 ('CP','Vista general','Amplitud del ataque','Más estrecho','044'),
 ('CP','Vista general','Transición ofensiva','Normal','044'),
 ('CP','Vista general','Libertad creativa','Equilibrado','044'),
 ('CP','Vista general','Perder tiempo','Menos a menudo','044'),
 ('CP','Vista general','Jugar buscando el balón parado','Buscar jugadas de balón parado','044'),
 ('CP','Último tercio','Regate','Animar','045'),
 ('CP','Último tercio','Paciencia','Intentar llevar el balón hasta el área','045'),
 ('CP','Último tercio','Disparos lejanos','Alentar','045'),
 ('CP','Último tercio','Estilo de centros','Centros rasos','045'),
 ('CP','Avance','Carreras de apoyo','Equilibrado','046'),
 ('CP','Avance','Regate','Animar','046'),
 ('CP','Avance','Avance','Izquierda','046'),
 ('CP','Avance','Recepción de pase','Pase al pie','046'),
 ('CP','Área de creación de oportunidades','Estrategia previa','Jugar superando la presión','047'),
 ('CP','Área de creación de oportunidades','Saques de meta','En corto','047'),
 ('CP','Área de creación de oportunidades','Distribución del portero (velocidad)','Distribuir con rapidez','047'),
 ('CP','Área de creación de oportunidades','Distribución del portero','Equilibrado','047'),
 ('SP','Vista general','Línea de presión','Presión adelantada','049'),
 ('SP','Vista general','Línea defensiva','Más adelantada','049'),
 ('SP','Vista general','Comportamiento de la línea defensiva','Presionar más arriba','049'),
 ('SP','Vista general','Activar presión','Más insistente','049'),
 ('SP','Vista general','Transición defensiva','Contrapresión','049'),
 ('SP','Vista general','Realizando una entrada','Ser agresivos','049'),
 ('SP','Presión adelantada','Trampa de presión','Equilibrado','050'),
 ('SP','Presión adelantada','Distribución del portero en corto','Sí','050'),
 ('SP','Bloque medio','Trampa de presión','Equilibrado','051'),
 ('SP','Bloque bajo','Compromiso de centros','Evitar centros','052'),
]

LINEUP_CURRENT = [
 ('Bart Verbruggen','GK','GK','ball_playing_goalkeeper_ip','sweeper_keeper_oop','PCS / POL'),
 ('Djed Spence','DR','DR','wing_back_ip','full_back_oop','CR / LAT'),
 ('Luka Vušković','DC','DC','ball_playing_centre_back_ip','centre_back_oop','CCS / DFC'),
 ('Pau Cubarsí','DC','DC','ball_playing_centre_back_ip','centre_back_oop','CCS / DFC'),
 ('Miloš Kerkez','DL','DL','wing_back_ip','full_back_oop','CR / LAT'),
 ('Aleksandar Pavlović','DM','DM','deep_lying_playmaker_ip','defensive_midfielder_oop','ORD / MD'),
 ('Yasin Ayari','MC','AMC','advanced_playmaker_ip','attacking_midfielder_oop','OAD / MP'),
 ('Adam Wharton','MC','DM','midfield_playmaker_ip','defensive_midfielder_oop','MOR / MD'),
 ('Dominik Szoboszlai','AMR','MR','inside_winger_ip','wide_midfielder_oop','EXI / MA'),
 ('Florian Wirtz','AML','ML','inside_winger_ip','wide_midfielder_oop','EXI / MA'),
 ('Hugo Ekitiké','STC','STC','deep_lying_forward_ip','centre_forward_oop','DDA / DLC'),
]


def dump(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    source = json.loads((OUT/'textos-instalacion.json').read_text(encoding='utf-8'))
    resources = {r['key']: r for r in source['records']}
    raw_ui = json.loads((OUT/'observaciones-ui.json').read_text(encoding='utf-8'))
    # Last capture of an ID supersedes earlier captures taken during an animation.
    observations = list({r['id']: r for r in raw_ui}.values())
    # The UI helper returns JPEG payloads; match the archived file extension.
    capture_root = (OUT/'capturas').resolve()
    for row in observations:
        capture = (OUT/row['file']).resolve()
        if capture.parent != capture_root:
            raise ValueError('Unexpected capture path outside report capture directory')
        if capture.suffix == '.png' and capture.read_bytes().startswith(b'\xff\xd8\xff'):
            destination = capture.with_suffix('.jpg')
            if destination.exists():
                raise FileExistsError(destination)
            capture.rename(destination)
            row['file'] = destination.relative_to(OUT.resolve()).as_posix()
    corrections = {
      '006':'Estrategia de pase: Más corto, Más directo, Normal.',
      '009':'Al abrir instrucciones desde la ficha SP se muestra inicialmente la pestaña CP del portero.',
      '012':'Dibujo táctico: el primer clic cerró el menú anterior; NO es evidencia del menú central.',
      '015':'Mediocentro central CP: Mediocentro defensivo, Organizador defensivo, Medio cierre.',
      '017':'MC CP, parte inferior: Mediocampista abierto, Mediocampista entre líneas, Mediocampista organizador.',
      '021':'Carreras: Hacer más desmarques, Estándar, Hacer menos carreras.',
      '022':'Libertad de movimientos: Variar la posición, Sigue posición táctica.',
      '023':'Centro desde: Centro desde atrás, Línea de fondo, Normal.',
      '024':'Riesgo en los pases: Tomar más riesgos, Tomar menos riesgos, Normal.',
      '028':'Estrategia de centros indica DESTINO: Segundo palo, Centro, Primer poste, Delantero torre, Normal.',
      '032':'Marca: Marca más férrea, Normal.',
      '033':'Entradas: Entrar más fuerte, No entrar fuerte, Normal.',
      '034':'Objetivo de marca: Marca específica, Marcar posición, Normal.',
      '037':'AMC central SP: Mediapunta, Mediapunta con retroceso, Mediapunta estacionario; tres opciones visibles.',
      '040':'Central SP: Defensa central, Zaguero, Defensa central de cobertura.',
      '041':'Lateral SP: Lateral defensivo, Lateral presionante, Lateral de contención.',
      '043':'Delantero de apoyo CP; instrucción resumida: Mantener el balón.',
      '048':'Al pasar a SP se conserva la última subvista: Bloque bajo, Evitar centros.',
      '059':'Estado del juego: primera pestaña Mánager; la versión se ve en 060.',
      '061':'El botón de puesto abre selección de jugador; se cerró sin confirmar sustituciones.',
    }
    for row in observations:
        row['note'] = corrections.get(row['id'][:3], row['note'])
        row['sha256'] = hashlib.sha256((OUT/row['file']).read_bytes()).hexdigest()
    dump('observaciones-ui.json', observations)
    evidence = {r['id'][:3]: r for r in observations}

    def resource(key):
        r = resources[key]
        return {'key': key, 'template_line': r['template_line'], 'context': r['context'],
                'en': (r['en'] or [r['template_english']])[0],
                'es': (r['es'] or [''])[0], 'es_variants': r['es'],
                'language_fallback': not r['es'] or r['es'][0] == (r['en'] or [r['template_english']])[0]}

    def shot(number):
        r = evidence.get(number)
        return f"[{number}]({r['file']})" if r else 'Sin captura actual'

    old_catalog = json.loads((ROOT/'fm_app/data/fm26_catalog.json').read_text(encoding='utf-8'))
    old_roles = {r['id']:r for r in old_catalog['roles']}
    roles = []
    for line in ROLE_ROWS.strip().splitlines():
        rid, label, positions, desc, label_key, ui = line.split('|')
        old = old_roles.get(rid, {})
        label_resource = resource(int(label_key))
        roles.append({'id': rid, 'phase': 'in_possession' if rid.endswith('_ip') else 'out_of_possession',
          'label_es_reference': label, 'label_resource': label_resource,
          'positions_reference': positions.split(','),
          'position_availability_status': 'family_reference_not_full_runtime_matrix',
          'description_resource': resource(int(desc)),
          'current_ui_evidence': evidence[ui]['file'] if ui else None,
          'current_ui_scope': 'role_seen_in_one_menu_context' if ui else 'not_revisited_in_current_ui',
          'key_attributes_prior_catalog': old.get('key_attributes', []),
          'attributes_provenance': 'Existing third-party catalog; not engine weights; not fully checked this session.',
          'prior_catalog_role_instructions': old.get('player_instructions', []),
          'locked_instructions_runtime': None})
    assert len(roles) == 79 and len({r['id'] for r in roles}) == 79
    role_by_id = {r['id']:r for r in roles}
    additional_path = OUT/'verificacion-adicional-roles.json'
    additional = json.loads(additional_path.read_text(encoding='utf-8')) if additional_path.exists() else {}
    mechanics_path = OUT/'verificacion-adicional-mecanicas.json'
    mechanics = json.loads(mechanics_path.read_text(encoding='utf-8')) if mechanics_path.exists() else {}
    for rid, facts in additional.items():
        role = role_by_id[rid]
        if facts.get('evidence'):
            role['current_ui_evidence'] = facts['evidence']
            role['current_ui_scope'] = 'role_seen_in_one_menu_context'
        role['additional_ui_verification'] = facts
        if facts.get('label_ui'):
            role['label_es_ui_verified'] = facts['label_ui']
        if facts.get('attributes'):
            role['key_attributes_ui_verified'] = facts['attributes']
    instructions = []
    for iid, label, ui, options in INSTRUCTIONS:
        instructions.append({'id':iid,'phase':'in_possession' if iid.endswith('_ip') else 'out_of_possession',
          'label_es_ui': label,'current_ui_evidence':evidence[ui]['file'],
          'options':[{'id':oid,'label_es_ui':name,'description_resource':resource(key),
            'explanation_es_editorial':EXPLANATIONS_ES.get(key)} for oid,name,key in options],
          'all_options_available_for_all_roles':False,
          'availability_requires':['phase','position_subslot','role','scope','context'],
          'marking_target_requires_reference':iid=='marking_target_oop'})
    assert len(instructions)==15 and sum(len(i['options']) for i in instructions)==45
    bundle = {'schema_version':1,'date':'2026-10-25','game_version_ui':'26.3.2.2329565 (m.e v26.3.0.1)',
      'locale_ui':'Español latinoamericano','resource_fingerprints':source['sha256'],
      'scope':'Tactical reference for reconstructing Touchline; not FM engine reconstruction.',
      'roles':roles,'individual_instructions':instructions,
      'positions':[dict(zip(('id_reference','label_ui_reference','name','notes'),p)) for p in POSITIONS],
      'lineup_snapshot_current':[dict(zip(('name','ip_position_family','oop_position_family','ip_role_reference','oop_role_reference','ui_role_abbreviations'),r)) for r in LINEUP_CURRENT],
      'observed_instruction_contexts':[
        {'role':'ball_playing_goalkeeper_ip','position_family':'GK','scope':'position_panel',
         'evidence':evidence['004']['file'],
         'locked_values':{'attacking_width_ip':'Standard','dribbling_direction_ip':'Standard',
           'forward_runs_ip':'Standard','freedom_of_movement_ip':'Follow Tactical Position',
           'hold_up_ball_ip':'No','shoot_ip':'Standard','passing_risk_ip':'Take More Risks',
           'cross_from_ip':'Standard','crossing_strategy_ip':'Standard'},
         'editable_groups':['dribbling_frequency_ip','passing_directness_ip'],
         'applicability':'Observed context only; no generalization to other roles.'},
        {'role':'sweeper_keeper_oop','position_family':'GK','scope':'position_panel',
         'evidence':evidence['010']['file'],
         'locked_values':{'pressing_oop':'Standard','marking_oop':'Standard','marking_target_oop':'Standard'},
         'editable_groups':['tackling_oop'],
         'applicability':'Observed context only; no generalization to other goalkeeper roles.'},
        {'role':'inside_winger_ip','position_family':'AML','scope':'position_panel',
         'evidence':evidence['020']['file'],'instruction':'attacking_width_ip',
         'unavailable_option':'Move Into Channels',
         'reason_ui':'Esta instrucción no está disponible ya que es incompatible con la posición de este jugador.',
         'applicability':'Cannot yet attribute this to position alone across all roles.'}],
      'team_instructions_current':[dict(zip(('phase','area','name','value','ui_evidence_id'),r)) for r in TEAM_CURRENT],
      'runtime_matrix_complete':False,'source_record_count':len(resources),
      'resource_keys_are_save_identifiers':False}
    for rid, facts in additional.items():
        if facts.get('instruction_context'):
            context = dict(facts['instruction_context'])
            context['role'] = rid
            context['applicability'] = 'Solo el subpuesto, fase y alcance documentados; no es una regla universal del rol.'
            # Normalize the observation vocabulary to the instruction option IDs above.
            for key, value in context.get('locked_values', {}).items():
                if key == 'forward_runs_ip' and value == 'Get Further Forward':
                    context['locked_values'][key] = 'Make More Runs'
                if key == 'freedom_of_movement_ip' and value == 'Hold Position':
                    context['locked_values'][key] = 'Follow Tactical Position'
            bundle['observed_instruction_contexts'].append(context)
    bundle['additional_mechanics_verification'] = mechanics
    panels = {c['role']: c for c in bundle['observed_instruction_contexts']
              if 'locked_values' in c and 'editable_groups' in c}
    missing_panels = [r for r in roles if r['id'] not in panels]
    missing_attributes = [r for r in roles if not r.get('key_attributes_ui_verified')]
    unresolved_values = [dict(role=rid, instruction=iid, evidence=c['evidence'])
                         for rid,c in panels.items()
                         for iid,value in c['locked_values'].items() if value is None]
    coverage = {'total_roles':len(roles), 'roles_with_instruction_panel':len(panels),
                'roles_with_verified_attribute_list':len(roles)-len(missing_attributes),
                'missing_instruction_panels':[r['id'] for r in missing_panels],
                'missing_attribute_lists':[r['id'] for r in missing_attributes],
                'unresolved_locked_values':unresolved_values,
                'all_position_role_scope_combinations_verified':False,
                'all_team_instruction_variants_verified':False}
    bundle['verification_coverage'] = coverage
    dump('cobertura-y-pendientes.json',coverage)
    dump('matriz-instrucciones-observadas.json',list(panels.values()))
    for rid,c in panels.items():
        role_by_id[rid]['locked_instructions_runtime'] = {
            'status':'verified_in_documented_context_only',
            'position':c.get('position',c.get('position_family')),
            'scope':c['scope'], 'evidence':c['evidence'],
            'locked_values':c['locked_values'], 'editable_groups':c['editable_groups']}
    bundle['lineup_snapshot_initial'] = bundle.pop('lineup_snapshot_current')
    continuation_lineup = [
        ('Bart Verbruggen','GK','ball_playing_goalkeeper_ip','sweeper_keeper_oop'),
        ('Djed Spence','DR','inside_full_back_ip','full_back_oop'),
        ('Luka Vušković','DC-right','ball_playing_centre_back_ip','centre_back_oop'),
        ('Pau Cubarsí','DC-left','ball_playing_centre_back_ip','centre_back_oop'),
        ('Miloš Kerkez','DL','wing_back_ip','full_back_oop'),
        ('Aleksandar Pavlović','DM','deep_lying_playmaker_ip','screening_defensive_midfielder_oop'),
        ('Yasin Ayari','MC-right','advanced_playmaker_ip','pressing_central_midfielder_oop'),
        ('Adam Wharton','MC-left','channel_midfielder_ip','pressing_central_midfielder_oop'),
        ('Dominik Szoboszlai','AMR','inside_forward_ip','winger_oop'),
        ('Hugo Ekitiké','AMC','channel_midfielder_ip','central_outlet_attacking_midfielder_oop'),
        ('Florian Wirtz','AML','inside_forward_ip','winger_oop'),
    ]
    bundle['lineup_snapshot_continuation'] = [dict(zip(('name','position_both_phases','ip_role_reference','oop_role_reference'), row)) for row in continuation_lineup]
    bundle['continuation_state'] = {
        'tactic_at_start':'flick barcelona 26',
        'mentality':'Ofensivo',
        'baseline_evidence':evidence['062']['file'],
        'restored_lineup_evidence':evidence['162']['file'],
        'backup_title':'Respaldo relevamiento 2026-10-25 flick barcelona 26',
        'last_observed_state_evidence':evidence['275']['file'],
        'restoration_required':False,
        'note':'La captura 162 documenta una restauración intermedia. Después el usuario autorizó usar esta partida de prueba sin devolver jugadores ni roles a su estado original. La captura 275 es el último estado observado: central que dobla CP en el puesto exterior derecho de una línea de tres; formación CP 3-2-4-1 y SP 4-2-2-2 ancho con mediocampista defensivo. Los cambios de formación renombraron automáticamente la táctica. No se avanzó fecha ni se guardó la partida durante el relevamiento.'}
    dump('catalogo-para-reconstruccion.json',bundle)

    report = ['# FM26: posiciones, roles e instrucciones para reconstruir Touchline',
      '\nRelevamiento del 25 de octubre de 2026. Idioma **Español latinoamericano**, comprobado en Preferencias. Versión visible **26.3.2.2329565 (m.e v26.3.0.1)**. Fecha de la partida: 14/9/2028, 13:15. Evidencia: '+shot('054')+', '+shot('060')+'.',
      '\n## 1. Qué contiene y cómo interpretar la evidencia',
      f'\nEste paquete reúne **79 definiciones de rol por fase**, **14 familias de posición**, **15 grupos de instrucciones individuales y sus 45 opciones**, ocho vistas colectivas y {len(observations)} capturas actuales. Se adjuntan {len(resources)} registros tácticos seleccionados de la instalación, con claves, contexto del traductor y huellas de los archivos.',
      '\n**La revisión visual completa de todas las combinaciones puesto × rol × fase × alcance no está terminada.** Los 15 menús individuales sí se abrieron y sus conjuntos de opciones se leyeron. Las descripciones completas de los 79 roles se obtuvieron de los recursos instalados. Las familias de compatibilidad combinan el catálogo previo y los menús observados; no constituyen una matriz oficial de disponibilidad.',
      '\nCada ficha distingue `current_ui_evidence` de `description_resource`. Una captura prueba lo mostrado en ese contexto, no todas las variantes del rol. Una cadena instalada prueba que existe ese texto, no que esté habilitado en un menú actual. El anexo conserva textos antiguos y variantes; no deben habilitarse roles solo porque exista su nombre.',
      '\nLas lecturas de recursos se hicieron con el lector Python local FMF/LTC. No son trazas de ejecución, descompilación del motor ni registros REA. Los IDs de este paquete son IDs de referencia para la aplicación. **Una clave KEY de localización no es el número de rol dentro de la partida.**',
      '\nLa navegación no avanzó la fecha ni guardó la partida. Se creó una copia local de la táctica para el relevamiento. La captura 162 documenta una restauración intermedia; después el usuario autorizó usar esta partida de prueba sin restaurar jugadores ni roles. El último estado observado conserva roles de prueba: CP 3-2-4-1 y SP 4-2-2-2 ancho con mediocampista defensivo. Los cambios de formación renombraron automáticamente la táctica. '+shot('062')+', '+shot('106')+', '+shot('162')+', '+shot('244')+', '+shot('275')+'.',
      f'\n**Actualización de la segunda pasada:** los {sum(bool(r["current_ui_evidence"]) for r in roles)} de 79 roles tienen ahora evidencia visual de menú/ficha. Se cerraron los 24 roles que antes estaban pendientes. Hay {len(bundle["observed_instruction_contexts"])} observaciones de instrucciones, incluidas restricciones parciales; esto no equivale a todas las combinaciones posibles. Los detalles nuevos están en `verificacion-adicional-roles.json` y `verificacion-adicional-mecanicas.json`.',
      f'\n**Cierre actualizado:** {len(panels)}/79 roles tienen panel de instrucciones registrado en al menos un contexto; {len(roles)-len(missing_attributes)}/79 tienen lista de atributos clave cotejada en la ficha. Quedan {len(missing_panels)} paneles, {len(missing_attributes)} listas de atributos y {len(unresolved_values)} valores bloqueados sin transcribir. La última continuación completó los 13 paneles solicitados y confirmó los tres valores antes ocultos. Ver `PENDIENTES.md` y `cobertura-y-pendientes.json` para los límites que siguen abiertos.',
      '\n## 2. Modelo táctico observado',
      '\nEl mismo jugador tiene una posición y un rol con posesión (CP) y otra posición y otro rol sin posesión (SP). El once conserva la identidad de sus jugadores al cambiar de fase. La vista combina ambas asignaciones, o permite ver CP, SP y ambos dibujos. La táctica actual se anuncia como **4-1-2-3 MD Amplio CP y 4-4-1-1 2MD SP** en la ayuda interna. '+shot('056')+'.',
      '\nUn rol tiene comportamientos inherentes además de las órdenes editables. FMPedia explica que modifica la posición base con el tiempo y entre fases, y da el ejemplo de un extremo abierto que tiende a regatear más. Por eso un rol no se reconstruye únicamente como una colección de selectores de instrucciones. '+shot('057')+'.',
      '\nLas tarjetas muestran nombre, adecuación en estrellas, rasgos de comportamiento, descripción, atributos clave, órdenes resumidas y una animación. Las estrellas y los números de atributos corresponden al jugador contextual: no son constantes del rol. Al recorrer el selector de puestos, no asumir que la ficha cambió automáticamente al jugador que ocupa ese otro puesto.',
      '\nSe ofrecen alcances **Posición / Personalizada** en roles y **Posición / Jugador** en instrucciones. El modelo debe guardar el alcance y la identidad del jugador para los ajustes personales. Una captura del alcance Posición no basta para certificar todos los valores efectivos de un jugador con personalización.',
      '\n### Once de la primera pasada',
      '\nAsignaciones leídas en la tabla y los dibujos actuales. Las familias de posición son la convención del informe; no IDs decodificados de la partida. '+shot('053')+', '+shot('056')+'.',
      '\n| Jugador | Puesto CP → SP | Rol CP | Rol SP | Abreviaturas vistas CP / SP |\n|---|---|---|---|---|',
      *['| '+r[0]+' | '+r[1]+' → '+r[2]+' | '+role_by_id[r[3]]['label_es_reference']+' | '+role_by_id[r[4]]['label_es_reference']+' | '+r[5]+' |' for r in LINEUP_CURRENT],
      '\n### Once de la continuación: flick barcelona 26',
      '\nEl usuario tenía otra táctica abierta al retomar. Esta tabla conserva la referencia inicial de la continuación y la restauración intermedia; no representa los roles de prueba del último estado observado. '+shot('062')+', '+shot('162')+'.',
      '\n| Jugador | Puesto CP y SP | Rol CP | Rol SP |\n|---|---|---|---|',
      *['| '+r[0]+' | '+r[1]+' | '+role_by_id[r[2]]['label_es_reference']+' | '+role_by_id[r[3]]['label_es_reference']+' |' for r in continuation_lineup],
      '\n## 3. Posiciones y subpuestos',
      '\nLos siguientes códigos son la convención del programa actual. Las abreviaturas españolas varían entre la ficha del futbolista y el dibujo. No se han descifrado aquí los IDs de puestos del archivo `.fm`.',
      '\n| Código de referencia | Rótulo de referencia | Posición | Distinción necesaria |\n|---|---|---|---|']
    report += ['| '+' | '.join(p)+' |' for p in POSITIONS]
    report += ['\nLa familia central necesita subpuesto: centro, centro-izquierda o centro-derecha, según la línea. Conservar también el dibujo y los vecinos. No representar todo como un simple `DC`, `DM`, `AMC` o `STC` si eso hace perder restricciones reales.',
      '\nObservaciones actuales de disponibilidad:',
      '\n- En un central de la línea de dos se ven cuatro roles CP: Central, Central avanzado, Central con salida y Central práctico. No aparecen Central abierto ni Central que dobla en ese contexto. '+shot('013')+'.',
      '- En el pivote central único CP se ven Mediocentro defensivo, Organizador defensivo y Medio cierre; el catálogo de referencia incluye además los dos todoterreno para otros subpuestos/contextos. '+shot('015')+'.',
      '- En el doble pivote SP aparecen cinco variantes, incluida cobertura abierta. '+shot('038')+', '+shot('039')+'.',
      '- En una línea de tres centrales se comprobaron Central abierto y Central que dobla CP, y Central abierto, Zaguero abierto y Central de cobertura abierta SP. '+shot('123')+', '+shot('126')+', '+shot('134')+', '+shot('139')+'.',
      '- En doble pivote CP se comprobaron los dos todoterreno que no aparecían en el pivote central único. '+shot('128')+', '+shot('129')+', '+shot('131')+'.',
      '- Un AMC central SP y un punta central único SP muestran tres roles cada uno. Al pasar a dos jugadores en la línea se comprobaron Mediapunta estacionario con salida y Delantero centro estacionario con salida. Se verificó el caso de pareja; no se deduce de ello una regla para todo dibujo. '+shot('037')+', '+shot('109')+', '+shot('114')+'.',
      '\n## 4. Catálogo de roles por posición y fase',
      '\nLa siguiente tabla es la unión de familias de referencia, **no una orden de habilitar todos los roles en todos los subpuestos**. Los costados se agrupan cuando comparten catálogo; todavía se debe validar la matriz contextual.',
      '\n| Familia | Con posesión | Sin posesión |\n|---|---|---|']
    groups=[('Portero',['GK']),('Centrales',['DC']),('Laterales',['DL','DR']),('Carrileros',['WBL','WBR']),
      ('Mediocentros',['DM']),('Mediocampistas centrales',['MC']),('Medios de banda',['ML','MR']),
      ('Mediapunta central',['AMC']),('Extremos / mediapuntas de banda',['AML','AMR']),('Delanteros',['STC'])]
    for name,pos in groups:
        cells=[]
        for phase in ('in_possession','out_of_possession'):
            cells.append('; '.join(r['label_es_reference'] for r in roles if r['phase']==phase and set(pos)&set(r['positions_reference'])))
        report.append('| '+name+' | '+' | '.join(cells)+' |')
    report += ['\n### Descripciones completas de los 79 roles',
      '\nTexto de los recursos instalados. Se conserva la traducción del recurso aunque difiera del rótulo del menú. Los nombres de referencia sin captura actual no deben presentarse como transcripción actual verificada. En JSON están también el inglés y las variantes españolas.']
    for n,r in enumerate(roles,1):
        d=r['description_resource']; phase='CP' if r['phase']=='in_possession' else 'SP'
        report += [f"\n#### {n}. {r['label_es_reference']} · {phase}",
          f"\nID de referencia: `{r['id']}`. Familias: {', '.join(r['positions_reference'])}. Nombre inglés: {r['label_resource']['en']}. Descripción: KEY-{d['key']}.",
          '\nRevisión visual actual: '+(f"[menú/ficha]({r['current_ui_evidence']})" if r['current_ui_evidence'] else '**pendiente para este rol**')+'.',
          '\n'+(d['es'] or d['en'])]
        if d['language_fallback']: report.append('\nEl recurso seleccionado conserva texto en inglés; no se inventó una traducción oficial.')
        label_es=r['label_resource']['es']
        if label_es and label_es.lower() not in r['label_es_reference'].lower():
            report.append(f'\nAlias del recurso KEY-{r["label_resource"]["key"]}: **{label_es}**. No reemplazar automáticamente el rótulo visto en el menú.')
        if r['key_attributes_prior_catalog']:
            report.append('\nAtributos de referencia del catálogo previo (sin pesos oficiales; no cotejados íntegramente ahora): '+', '.join(r['key_attributes_prior_catalog'])+'.')
        facts = additional.get(r['id'], {})
        if facts.get('label_ui'):
            report.append('\nRótulo verificado en esta pasada: **'+facts['label_ui']+'**.')
        if 'attributes' in facts:
            report.append('\nAtributos clave leídos en la ficha actual: '+', '.join(facts['attributes'])+'. No se registran los valores personales como constantes del rol.')
        if 'behaviors' in facts:
            report.append('\nComportamientos mostrados: '+('; '.join(facts['behaviors']) or 'sin etiquetas')+'.')
        if 'role_instructions_ui' in facts:
            report.append('\nResumen de instrucciones en la ficha: '+('; '.join(facts['role_instructions_ui']) or 'sin órdenes listadas')+'. Este resumen no sustituye el panel de candados.')
        if facts.get('ui_discrepancy'):
            report.append('\n**Discrepancia observada:** '+facts['ui_discrepancy'])
        context = panels.get(r['id'])
        if context:
            report.append('\nContexto de instrucciones comprobado: '+context.get('position',context.get('position_family','desconocido'))+', alcance '+context['scope']+'. [Panel]('+context['evidence']+').')
            report.append('\nControles bloqueados: '+('; '.join(k+' = '+(str(v) if v is not None else 'valor tapado por tooltip, no transcrito') for k,v in context.get('locked_values',{}).items()) or 'ninguno')+'.')
            report.append('\nControles editables: '+', '.join(context.get('editable_groups',[]))+'. No extrapolar a otros subpuestos o alcances.')
    report += ['\n## 5. Instrucciones individuales: los 15 grupos y sus 45 opciones',
      '\nLos nombres siguientes se leyeron en los menús actuales. Las explicaciones largas se vinculan con claves del recurso instalado; estas vinculaciones son por significado/contexto, no identificadores extraídos de la partida. La app debe permitir una sola opción por grupo y conservar los valores desconocidos como desconocidos.',
      '\nAlgunas claves nuevas no tienen traducción en el LTC instalado o todavía devuelven inglés. En esos casos se incluye una explicación en español escrita para este informe y se conserva el original inglés por separado. Esa explicación no es una transcripción oficial del juego.',
      '\n`Estándar` aparece en amplitud, regate y carreras. `Normal` aparece en disparos, pases, centros y SP. No normalizar indiscriminadamente los rótulos españoles. Un valor estándar sigue dependiendo del rol, estrategia colectiva y preferencias personales; no equivale a apagar el comportamiento.']
    for i in instructions:
        phase='CP' if i['phase']=='in_possession' else 'SP'
        report += [f"\n### {i['label_es_ui']} · {phase}",f"\nID de referencia: `{i['id']}`. [Menú actual]({i['current_ui_evidence']})."]
        for opt in i['options']:
            d=opt['description_resource']
            report += [f"\n**{opt['label_es_ui']}** (`{opt['id']}`; KEY-{d['key']})."]
            if d['language_fallback'] and opt['explanation_es_editorial']:
                report += ['\nExplicación en español (redacción del informe): '+opt['explanation_es_editorial'],
                  '\nOriginal de referencia en inglés: '+d['en']]
            else:
                report.append('\n'+(d['es'] or d['en']))
    report += ['\n### Distinciones que afectan al software',
      '\n- **Amplitud** modifica dónde se ofrece sin balón; **dirección del regate** modifica la conducción con balón. Pueden combinarse; no son el mismo control.',
      '- **Carreras hacia adelante** y **libertad de movimientos** son dimensiones distintas.',
      '- **Riesgo en los pases** es distinto de **Estrategia de pase**. Arriesgar más no equivale a jugar más largo.',
      '- **Centro desde** define el origen de los centros. **Estrategia de centros** define su destino: segundo palo, centro, primer poste o delantero torre. No es un selector de frecuencia. El **estilo** de centro —raso, alto, etc.— aparece entre las instrucciones colectivas.',
      '- **Marca** establece proximidad. **Objetivo de marca** agrega una referencia a un jugador o puesto rival. Guardar solo el enum “Marca específica” pierde el objetivo necesario.',
      '- “Sí” en **Distribución del portero en corto**, dentro de la presión colectiva SP, pide impedir la salida corta del **arquero rival**. No ordenar al propio arquero distribuir corto por esa casilla.',
      '\n### Disponibilidad, bloqueos y modificaciones',
      '\nEl icono de candado se explica como **Instrucción no disponible**. El indicador turquesa se explica como **Instrucción modificada**. Un bloqueo puede deberse al rol o al puesto; no asumir una sola causa universal.',
      '\nEn el extremo izquierdo CP, “Moverse entre líneas” está deshabilitado y el panel dice expresamente que es incompatible con la posición del jugador. '+shot('020')+'.',
      '\nEn Portero con salida CP se ven candados en amplitud, dirección del regate, carreras, libertad, aguantar, disparos, riesgo en pases, centro desde y estrategia de centros. Frecuencia del regate y estrategia de pase quedan editables en la vista inspeccionada. Riesgo muestra Tomar más riesgos. '+shot('004')+'.',
      '\nEn Portero líbero SP, presión, marca y objetivo tienen candado y muestran Normal. **Entradas no tiene candado**. La pantalla no muestra que el rol obligue a “Más a menudo” en presión individual; esa inferencia sería incorrecta. '+shot('010')+'.',
      '\nPara el resto, mantener `unknown` donde no haya captura del bloqueo en ese contexto. No convertir una orden resumida en una prueba de bloqueo. Para certificar el estado efectivo de un jugador, relevar también el alcance Jugador y sus personalizaciones.',
      '\n## 6. Instrucciones de equipo: ocho vistas revisadas',
      '\nValores de la táctica actual; no son recomendaciones universales. Hay 29 apariciones de controles en estas ocho vistas: Regate aparece en dos subfases CP y Trampa de presión aparece en dos bloques SP. No contar cada aparición como un parámetro independiente sin verificar cómo comparte estado.',
      '\n| Fase | Área | Instrucción | Valor visto | Captura |\n|---|---|---|---|---|']
    report += ['| '+' | '.join((*r[:4],shot(r[4])))+' |' for r in TEAM_CURRENT]
    report += ['\nEl anexo de recursos conserva opciones, descripciones y reacciones del cuerpo técnico de las instrucciones colectivas. En esta sesión se revisaron sus ocho vistas; **no se abrieron todas las variantes de cada selector colectivo**. No elevar el contenido del archivo a una matriz de controles confirmados.',
      '\n## 7. Diferencias concretas con el programa actual',
      '\n1. `fm_app/data/fm26_catalog.json` tiene 74 registros de rol. Hay un registro específico de Carrilero organizador para laterales además del general. Al unificar ese duplicado quedan 73 definiciones; este paquete agrega seis ausentes y llega a **79**: Central abierto CP, Central que dobla CP, Central abierto SP, Central de cobertura abierta SP, Zaguero abierto SP y Mediocentro presionante SP. Su inclusión final debe respetar los subpuestos y la evidencia.',
      '2. `passing_directness_ip` solo declara `Standard` y `Shorter` en el catálogo actual. El menú muestra también **Más directo**; la descripción de instalación está en KEY-706456. Hay que incorporarlo al contrato, validación, UI, persistencia y análisis, no solo al rótulo.',
      '3. La aplicación guarda 14 familias de puesto. Esa estructura necesita conservar subpuesto o contexto para no ofrecer roles que el menú no permite en un pivote central único o un punta central único.',
      '4. El español de `fm26_es419.json` no garantiza el rótulo de cada superficie del juego. Por ejemplo KEY-688113 dice “Portero jugador”, mientras el menú muestra “Portero con salida”; KEY-688119 y algunos textos dicen “pivote organizador”, pero las pantallas usan Organizador defensivo y ORD. Guardar alias por clave/superficie/idioma; no reemplazar globalmente por una traducción.',
      '5. `SCREENSHOT_LOCKS` conserva bloqueos del relevamiento previo. Debe evolucionar hacia reglas con puesto, fase y alcance. Una clave vacía no prueba por sí sola disponibilidad en todas las posiciones posibles.',
      '6. El código pondera roles CP/SP con **80/20** y añade reglas propias de atributos y zonas. Son decisiones de Touchline. Nada de esta revisión prueba que sean pesos del motor de FM ni probabilidades de éxito.',
      '7. La referencia histórica de Liverpool no coincide íntegramente con la táctica abierta: ahora ambos centrales muestran CCS CP; Ayari pasa de OAD CP a MP SP y Wharton de MOR CP a MD SP. No usar capturas históricas como estado actual automático.',
      '\n## 8. Especificación de reconstrucción propuesta',
      '\nEsta sección propone diseño de software; no atribuye estas estructuras al código interno de FM.',
      '\n### Entidades y procedencia',
      '\n- `RoleDefinition`: id de referencia estable, fase, nombre base y alias por idioma/superficie, descripción, comportamientos inherentes, atributos de referencia y procedencia.',
      '- `PositionSlot`: familia, lado/subpuesto, coordenada base por fase, identidad de puesto en el dibujo y contexto de vecinos. Los códigos de archivo aún desconocidos se conservan aparte.',
      '- `InstructionDefinition`: grupo, fase, opciones válidas, descripción por opción y objetivos adicionales cuando correspondan.',
      '- `InstructionSetting`: opción explícita o valor desconocido, alcance posición/jugador, target rival cuando exista, fuente, estado de modificación y disponibilidad conocida/desconocida.',
      '- `AvailabilityRule`: fase + puesto/subpuesto + rol + contexto + alcance, estado permitido/no disponible/desconocido, causa y evidencia.',
      '- `Tactic`: mismo once con dos asignaciones de fase; instrucciones colectivas y personales separadas; versión y huellas de la referencia.',
      '\nNo representar un desconocido como `Normal`, `No`, cero o un candado. No reemplazar una selección del usuario al recalcular sugerencias. Mantener claramente separados valor observado, restricción observada e interpretación del analizador.',
      '\n### Comportamiento de interfaz esperado',
      '\nSeleccionar fase → puesto concreto → rol compatible → instrucciones. Mostrar por qué una opción está deshabilitada, incluyendo “aún no verificada” si no hay evidencia. Permitir alternar alcance Posición/Jugador. Mostrar el movimiento entre las dos fases manteniendo el mismo futbolista. Describir cambios de forma verificable y no prometer resultados deportivos.',
      '\n### Pruebas de aceptación significativas',
      '\n1. El catálogo mantiene un único Carrilero organizador CP con varias familias compatibles, evitando duplicados por rótulo.',
      '2. El mismo jugador puede ser MC CP y AMC SP, o AML CP y ML SP, sin duplicar su identidad.',
      '3. La longitud Más directo se conserva y valida de extremo a extremo.',
      '4. Una asignación desconocida sigue desconocida al guardar, recargar y recomendar.',
      '5. Marca específica requiere rival identificado; Marcar posición requiere puesto rival identificado.',
      '6. Un control modificado permanece distinto de un control bloqueado. Las restricciones no se extienden a contextos no comprobados.',
      '7. El menú de Portero con salida permite las dos dimensiones editables observadas y conserva las restricciones documentadas. El de Portero líbero no bloquea Entradas por inferencia.',
      '8. Centro desde, destino de centros y estilo colectivo de centros son tres conceptos separados.',
      '9. La UI conserva los alias españoles sin usar la etiqueta traducida como clave de datos.',
      '10. La evaluación explica qué viene de atributos, qué viene de la táctica y qué es una regla propia. Cambiar un dato de entrada invalida los resultados dependientes.',
      '\n## 9. Pendientes explícitos de verificación',
      '\n- La reapertura visual de los 24 roles antes pendientes quedó cerrada: los 79 roles tienen captura de menú/ficha. Esto acredita presencia en al menos un contexto, no selección individual de todas las fichas de la primera pasada.',
      f'- Hay paneles registrados para {len(panels)} roles y listas de atributos cotejadas para {len(roles)-len(missing_attributes)}. La lista exacta de los {len(missing_panels)} paneles y {len(missing_attributes)} listas pendientes está en `PENDIENTES.md`; los IDs están también en `cobertura-y-pendientes.json`.',
      '- Los tres valores antes tapados de Aguantar el balón quedaron confirmados visualmente en **No**, con candado: Central abierto CP, Central que dobla CP y Mediocampista todoterreno CP. '+shot('273')+', '+shot('274')+', '+shot('275')+'.',
      '- La matriz completa de subpuesto, rol, fase y alcance Posición/Jugador sigue sin certificarse. Priorizar únicamente los contextos que necesite la reconstrucción; la partida de prueba puede modificarse con autorización del usuario.',
      '- Los destinos de Marca específica y Marcar posición ya se abrieron: 25 puestos de campo más Ninguna, o lista dinámica de 10 rivales de campo más Ninguna en el prepartido observado. Queda comprobar cómo varían durante el partido y ante cambios rivales. '+shot('118')+', '+shot('120')+'.',
      '- Abrir todas las opciones colectivas para verificar disponibilidad y si los controles repetidos por subfase comparten valor.',
      '- Las 79 listas de atributos fueron cotejadas visualmente. Ninguna lista observada revela pesos numéricos del motor.',
      '- Decodificar, si se desea automatizar la lectura, posiciones, roles e instrucciones de la partida y cotejarlos contra estos menús. Las cadenas de traducción no proporcionan ese mapeo.',
      '\n## 10. Archivos para la otra IA',
      '\n- `REPORTE.md`: este informe, con todas las fichas y opciones.',
      '- `catalogo-para-reconstruccion.json`: catálogo normalizado, descripciones, nombres, procedencia y límites.',
      '- `textos-instalacion.json`: registros originales seleccionados y huellas de instalación.',
      '- `ANEXO-TEXTOS-INSTRUCCIONES.md`: textos de ayuda, opciones y reacciones con sus contextos, conservando variantes y ambigüedades.',
      '- `observaciones-ui.json` y `capturas/`: evidencia visual actual, con SHA-256.',
      '- `verificacion-adicional-roles.json`: fichas, atributos, comportamientos y controles comprobados en la continuación.',
      '- `verificacion-adicional-mecanicas.json`: destinos de marcaje y otras mecánicas comprobadas.',
      '- `PROMPT-PARA-OTRA-IA.md`: pedido de implementación listo para adjuntar.',
      '- `matriz-instrucciones-observadas.json`: un panel representativo por cada rol comprobado, con valores bloqueados y grupos editables.',
      '- `PENDIENTES.md` y `cobertura-y-pendientes.json`: cobertura final y faltantes exactos.',
      '\nFuentes del proyecto consultadas: `README.md`, `docs/fm26-reference.md`, `docs/tactica-actual-y-zonas.md`, `docs/screenshots/Guia de roles FM - capturas.md`, `fm_app/data/fm26_catalog.json`, `fm_app/data/fm26_es419.json`, `fm_app/fm26.py` y `fm_app/current_tactic.py`. El reporte histórico no se trató como comprobación actual.']
    (OUT/'REPORTE.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    pending = ['# Cobertura final y verificaciones pendientes',
      f'\n79/79 roles identificados visualmente y con descripción completa de los recursos instalados. {len(panels)}/79 con panel individual registrado; {len(roles)-len(missing_attributes)}/79 con atributos cotejados. 15 grupos individuales y 45 opciones documentados. Ocho vistas colectivas revisadas.',
      '\n## Paneles individuales pendientes',
      ('\nEstos roles aún necesitan un panel completo en un contexto concreto.' if missing_panels else '\nNinguno: los 79 roles tienen un panel completo registrado en al menos un contexto. Esto no certifica todas las combinaciones de puesto y alcance.'),
      ('\n| Fase | Rol de referencia | ID |\n|---|---|---|' if missing_panels else ''),
      *['| '+('CP' if r['phase']=='in_possession' else 'SP')+' | '+r.get('label_es_ui_verified',r['label_es_reference'])+' | `'+r['id']+'` |' for r in missing_panels],
      '\n## Atributos pendientes de cotejo visual',
      ('\n'+ '; '.join(r.get('label_es_ui_verified',r['label_es_reference'])+' ('+('CP' if r['phase']=='in_possession' else 'SP')+')' for r in missing_attributes)+'.' if missing_attributes else '\nNinguno: las 79 listas están cotejadas en ficha.'),
      '\n## Valores tapados',
      ('\n'+ '; '.join(role_by_id[x['role']]['label_es_reference']+': Aguantar el balón, [captura]('+x['evidence']+')' for x in unresolved_values)+'. Conservar null; no deducir el valor.' if unresolved_values else '\nNinguno de los tres pendientes anteriores: Aguantar el balón es No y está bloqueado en Central abierto CP, Central que dobla CP y Mediocampista todoterreno CP. Evidencia: '+shot('273')+', '+shot('274')+', '+shot('275')+'.'),
      '\n## Límites de verificación',
      '\n- No se probaron todas las combinaciones de subpuesto, costado, formación y personalizaciones de jugador. Cada panel acredita su contexto, no disponibilidad universal.',
      '- Las ocho vistas colectivas están leídas, pero falta abrir todas las variantes, ayudas y restricciones de cada selector y comprobar qué controles repetidos comparten estado.',
      '- Los destinos de marca se verificaron en el prepartido observado. Falta su actualización durante un partido o ante cambios rivales.',
      '- No se decodificaron IDs de roles/posiciones/instrucciones de la partida ni pesos del motor. Solo hace falta ese trabajo si se quiere automatizar su lectura.',
      '\n## Entrega a otra IA',
      '\nAdjuntar el ZIP y usar PROMPT-PARA-OTRA-IA.md. Empezar por el catálogo y la matriz observada; usar unknown/null en los contextos pendientes. La partida fue autorizada para pruebas y no requiere restauración. No se implementaron cambios en el software de producción.']
    (OUT/'PENDIENTES.md').write_text('\n'.join(pending)+'\n',encoding='utf-8')

    appendix=['# Anexo de textos de instrucciones de la instalación',
      '\nSelección por contexto del traductor. Son recursos, no una lista de opciones actualmente habilitadas. Incluye variantes y textos antiguos. El contexto permite diferenciar nombre, descripción, ventaja y desventaja. No derivar reglas numéricas ni bloqueos de estas frases.\n']
    for row in source['records']:
        ctx=row['context'].lower().replace('_',' ')
        if 'player instruction' not in ctx and 'team instruction' not in ctx and 'individual player instruction' not in ctx:
            continue
        appendix += [f"\n## KEY-{row['key']}", '\nContexto: '+row['context'],
          '\nInglés: '+(row['en'] or [row['template_english']])[0],
          '\nEspañol: '+((row['es'] or ['**Sin traducción en este registro**'])[0])]
    (OUT/'ANEXO-TEXTOS-INSTRUCCIONES.md').write_text('\n'.join(appendix)+'\n',encoding='utf-8')
    prompt='''# Pedido para la IA que va a reconstruir el software

Quiero que reconstruyas/mejores Touchline, mi analizador local de Football Manager 26, usando este relevamiento de mi instalación como referencia táctica. No te pido recrear el motor de partidos de FM.

Primero leé REPORTE.md y catalogo-para-reconstruccion.json. Consultá las capturas y los registros de textos para resolver detalles. El idioma actual es Español latinoamericano y la versión visible es 26.3.2.2329565 (m.e v26.3.0.1). No confundas claves de idioma con IDs de la partida ni textos instalados con comportamiento comprobado.

El catálogo reúne 79 definiciones por fase, 14 familias de puesto y 15 grupos individuales con 45 opciones. Los 79 roles tienen evidencia visual, panel individual registrado y lista de atributos cotejada. Se completaron los 13 paneles de la última tanda y los tres valores ocultos quedaron confirmados en No. Consultá verificacion-adicional-roles.json y matriz-instrucciones-observadas.json para estos datos, y verificacion-adicional-mecanicas.json para los destinos de marca. La matriz completa de disponibilidad por subpuesto, fase y alcance sigue pendiente: respetá la procedencia y los desconocidos. No afirmes que se verificaron todas las combinaciones.

Revisá la arquitectura existente antes de modificarla. Conservá el lector de partidas y los datos reales que ya funcionan. Evitá datos de ejemplo en los análisis de mi equipo. Separá posiciones/subpuestos, roles CP/SP, comportamientos inherentes, instrucciones de posición y personales, y órdenes colectivas.

Contrastá el estado actual del código con los problemas identificados en la revisión: Más directo en passing_directness_ip, seis definiciones ausentes, duplicado de Carrilero organizador, alias de español, restricciones dependientes del puesto y objetivo adicional requerido por las marcas específicas. Corregí lo que siga vigente; el software puede haber cambiado desde la primera inspección. No conviertas valores desconocidos en Normal y no extrapoles candados de una captura a todos los contextos.

Las fórmulas 80/20, umbrales de atributos, riesgos y mapas de zonas son reglas propias de Touchline; explicalas y no las atribuyas a FM. Una descripción de rol no revela pesos internos ni una probabilidad de ganar.

Implementá de extremo a extremo: catálogo y contratos, validación, persistencia, cálculo, interfaz, exportación y pruebas significativas. Preservá la configuración de la carrera y la identidad del mismo jugador en ambas fases. Mostrá qué cambió, por qué, qué quedó pendiente y cómo se verificó.
'''
    prompt += f'\nCobertura al cierre: {len(panels)}/79 paneles y {len(roles)-len(missing_attributes)}/79 listas de atributos cotejadas. Leé PENDIENTES.md antes de asumir cobertura completa. Usá matriz-instrucciones-observadas.json como fuente directa de restricciones en el contexto observado. La ficha del Zaguero contradice su panel activo: conservá la discrepancia y priorizá el panel de instrucciones para ese valor.\n'
    prompt += '''

## Encargo ampliado: interfaz y organización de información

El proyecto local está en `C:\\Users\\feder\\Documents\\Codigos varios y emprendimientos\\Analizador FM`. La documentación está en `docs/relevamiento-fm26-2026-10-25/` dentro del proyecto. Si recibiste el ZIP en otro equipo, extraelo y usá la carpeta equivalente; el ZIP contiene documentación y evidencias, no todo el repositorio del programa.

Empezá por INFORME-INTEGRAL.md y leé también MEJORAS-DE-INTERFAZ.md. Implementá las mejoras tácticas y de interfaz en el proyecto existente. Contrastá cada hallazgo con el código actual: hay trabajo previo y puede haber correcciones posteriores al análisis. Conservá las modificaciones existentes y resolvé únicamente los problemas que sigan vigentes.

Prioridad 1: recomendaciones vigentes y coherentes entre checklist, tarjetas, copia y HUD; eliminar nombres y cantidades fijas ajenos al resultado; sustituir «100% optimizada» por un estado que describa lo marcado por el usuario; distinguir propuesta y táctica actual. Comprobá que los metadatos y acciones del HUD correspondan al contexto desde donde se abre.

Prioridad 2: integrar las restricciones tácticas documentadas y simplificar el flujo visual. Mostrar antes la cancha y hasta tres prioridades, unificar la entrada de formación y de idea de juego, reducir botones duplicados y abrir explicaciones y ajustes extensos bajo demanda. Conservar la identidad oscura con verde menta, unificar nombres e iconos y separar colores de fase y gravedad. Adaptar las ventanas angostas y verificar teclado, foco y contraste.

Seguí los criterios de aceptación de MEJORAS-DE-INTERFAZ.md. Preservá el lector de partidas, los datos reales, la configuración por carrera, la identidad del jugador entre fases, las órdenes desconocidas y los cambios pendientes al navegar. No presentes las capturas de prueba de referencias-interfaz/ como datos del equipo. No inventes opciones o reglas para cubrir lo que falta: dejá esos contextos explícitos y preparados para incorporar evidencia posterior.

Implementá y validá el flujo completo con pruebas significativas y capturas de escritorio y ventana angosta. Entregá qué cambió, cómo se verificó y qué queda pendiente. Si no tenés acceso al código del programa, usá el paquete para preparar una especificación concreta y señalá que la implementación necesita el repositorio; no afirmes haberlo modificado.
'''
    (OUT/'PROMPT-PARA-OTRA-IA.md').write_text(prompt,encoding='utf-8')
    from actualizar_colectivas_fm26 import apply_team_review
    team_review_stats = apply_team_review(OUT)
    # Retain the exact tooling used alongside the report.
    for script in ('relevar_textos_fm26.py','crear_reporte_relevamiento_fm26.py','actualizar_colectivas_fm26.py'):
        (OUT/script).write_bytes((ROOT/'scripts'/script).read_bytes())
    stats={'roles':len(roles),'roles_seen_in_current_ui':sum(bool(r['current_ui_evidence']) for r in roles),
      'additional_role_records':len(additional),
      'role_attribute_lists_verified_in_continuation':sum('attributes' in r for r in additional.values()),
      'observed_instruction_context_records':len(bundle['observed_instruction_contexts']),
      'roles_with_instruction_panel':len(panels),
      'roles_missing_instruction_panel':len(missing_panels),
      'roles_missing_verified_attributes':len(missing_attributes),
      'unresolved_locked_values':len(unresolved_values),
      'position_families':len(POSITIONS),'individual_groups':len(instructions),
      'individual_options':sum(len(i['options']) for i in instructions),
      'current_team_control_appearances':len(TEAM_CURRENT),'current_ui_captures':len(observations),
      'resource_records':len(resources),'report_words':len(('\n'.join(report)).split())}
    stats.update(team_review_stats)
    stats['report_words'] = len((OUT/'REPORTE.md').read_text(encoding='utf-8').split())
    dump('resumen-verificacion.json',stats)
    manifest=[]
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.name!='MANIFIESTO-SHA256.json':
            manifest.append({'file':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,
              'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    dump('MANIFIESTO-SHA256.json',manifest)
    archive=ROOT/'docs/Relevamiento-FM26-2026-10-25.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in OUT.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(OUT.parent))
    print(json.dumps({**stats,'zip_bytes':archive.stat().st_size},ensure_ascii=False))


if __name__=='__main__':
    main()
