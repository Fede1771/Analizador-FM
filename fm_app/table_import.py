"""Offline CSV/HTML import with an explicit preview and no inferred masked attributes."""
import csv
from datetime import date
import hashlib
from html.parser import HTMLParser
import io
import json
import re
import unicodedata

from fm_app.tactics import ATTRS
from fm_app.contracts import clean_player

POSITION_KEYS = ('gk','dl','dc','dr','dm','ml','mc','mr','aml','amc','amr','stc','wbl','wbr')
ALIASES = {'uid': ('id único','id unico','unique id','id'), 'name': ('nombre','name'),
           'age': ('edad',), 'positions': ('familiaridades','familiaridad posicional'),
           'natural_positions': ('posiciones naturales',), 'wage_weekly': ('salario semanal',),
           'contract_end': ('fin contrato','fin de contrato'), 'transfer_value': ('valor estimado',),
           'minutes': ('minutos','mins'), 'goals': ('goles',), 'assists': ('asistencias',),
           'appearances': ('partidos','pj'), 'average_rating': ('media',),
           'first_touch': ('control','control de balón'), 'teamwork': ('juego en equipo',),
           'jumping_reach': ('alcance de salto',), 'corners': ('saques de esquina',),
           'free_kick_taking': ('tiros libres',), 'natural_fitness': ('recuperación física',)}


def key(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(text)).lower() if c.isalnum())


class Tables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.table, self.row, self.cell = [], None, None, None
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'):
            self.skip += 1
        if tag == 'table':
            if self.table is not None:
                raise ValueError('El HTML tiene tablas anidadas; exportá una tabla simple.')
            self.table = []
        elif tag == 'tr' and self.table is not None:
            self.row = []
        elif tag in ('td','th') and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None and not self.skip:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('script','style') and self.skip:
            self.skip -= 1
        if tag in ('td','th') and self.cell is not None:
            self.row.append(''.join(self.cell).strip()); self.cell = None
        elif tag == 'tr' and self.row is not None:
            if self.row: self.table.append(self.row)
            self.row = None
        elif tag == 'table' and self.table is not None:
            if self.table: self.tables.append(self.table)
            self.table = None


def parse_table(text):
    if not isinstance(text, str) or not text.strip() or len(text.encode('utf-8')) > 6*1024*1024:
        raise ValueError('Elegí una tabla CSV o HTML de hasta 6 MB.')
    if re.search(r'<table\b', text, re.I):
        parser = Tables(); parser.feed(text)
        candidates = [t for t in parser.tables if any(key(c) in ('uid','idunico','uniqueid','id') for c in t[0])]
        if len(candidates) != 1:
            raise ValueError('El HTML debe contener una sola tabla de jugadores con ID único.')
        return candidates[0]
    try:
        dialect = csv.Sniffer().sniff(text[:16384], delimiters=',;\t')
        return list(csv.reader(io.StringIO(text.lstrip('\ufeff')), dialect))
    except csv.Error as exc:
        raise ValueError('No se pudo leer el CSV: usá coma, punto y coma o tabulaciones.') from exc


def number(value, label, optional=False, integer=False, money=False):
    value = str(value or '').strip()
    if optional and value in ('','-','—','N/A'):
        return None
    if money:
        value = re.sub(r'[€\s]', '', value)
        if ',' in value and '.' in value:
            value = value.replace('.', '').replace(',', '.') if value.rfind(',')>value.rfind('.') else value.replace(',', '')
        elif re.fullmatch(r'\d{1,3}[.,]\d{3}', value):
            raise ValueError(f'{label}: separador ambiguo. Usá 1000.00 o 1.000,00, sin abreviaturas.')
        elif ',' in value:
            value = value.replace(',', '.')
    elif ',' in value:
        value = value.replace(',', '.')
    if not re.fullmatch(r'\d+(?:\.\d+)?', value):
        raise ValueError(f'{label}: valor ausente, oculto o inválido.')
    result = float(value)
    if result > 1e12 or (integer and not result.is_integer()):
        raise ValueError(f'{label}: número fuera de rango.')
    return int(result) if integer else result


def preview(params, current=None):
    club, manager = str(params.get('club','')).strip(), str(params.get('manager','')).strip()
    game_date = params.get('date','')
    try:
        game_date = date.fromisoformat(game_date).isoformat()
    except (ValueError, TypeError):
        raise ValueError('Indicá la fecha del juego como AAAA-MM-DD.')
    if not club or not manager or len(club)>100 or len(manager)>100:
        raise ValueError('Indicá club y manager (hasta 100 caracteres cada uno).')
    rows = parse_table(params.get('text'))
    if not 2 <= len(rows) <= 2001:
        raise ValueError('La tabla debe tener entre 1 y 2000 jugadores.')
    names = {key(k): k for k in (*ATTRS, 'uid','name','age','positions','natural_positions','wage_weekly',
              'contract_end','transfer_value','minutes','goals','assists','appearances','average_rating', *('pos_'+p for p in POSITION_KEYS))}
    names.update({key(v): k for k, v in ATTRS.items()})
    names.update({key(alias): k for k, aliases in ALIASES.items() for alias in aliases})
    columns = [names.get(key(c)) for c in rows[0]]
    recognized = [c for c in columns if c]
    if len(set(recognized)) != len(recognized):
        raise ValueError('Hay columnas duplicadas o dos etiquetas para el mismo dato.')
    missing = [k for k in ('uid','name',*ATTRS) if k not in columns]
    if missing:
        raise ValueError('Faltan columnas necesarias: '+', '.join(ATTRS.get(k,k) for k in missing)+'. Usá la plantilla de Touchline y valores visibles de 1 a 20.')
    has_positions = 'positions' in columns or any('pos_'+p in columns for p in POSITION_KEYS)
    if not has_positions and not ('natural_positions' in columns and params.get('confirm_natural') is True):
        raise ValueError('Incluí familiaridades numéricas (positions JSON o pos_dc, pos_mc, etc.) o posiciones naturales con confirmación explícita. Una columna genérica Posición no acredita familiaridad.')
    scope = params.get('stats_scope')
    period = str(params.get('stats_period','')).strip()
    if any(k in columns for k in ('minutes','goals','assists')) and (scope not in ('overall_club','league') or not period or len(period)>60):
        raise ValueError('Indicá ámbito y temporada de las estadísticas exportadas.')
    players = []
    for index, row in enumerate(rows[1:], 2):
        if not any(str(c).strip() for c in row): continue
        if len(row) != len(columns):
            raise ValueError(f'Fila {index}: cantidad de columnas incorrecta.')
        values = {k: v.strip() for k, v in zip(columns, row) if k}
        try:
            attributes = {k: number(values[k], ATTRS[k], integer=True) for k in ATTRS}
            positions = json.loads(values['positions']) if values.get('positions') else {
                p: number(values['pos_'+p], 'Familiaridad '+p, integer=True) for p in POSITION_KEYS if values.get('pos_'+p)}
            if not positions and values.get('natural_positions') and params.get('confirm_natural') is True:
                declared = re.split(r'[,;| ]+', values['natural_positions'].lower())
                if any(p not in POSITION_KEYS for p in declared):
                    raise ValueError('Posiciones naturales: usá códigos GK, DC, MC, STC, etc.')
                positions = {p: 20 for p in declared}
            if not isinstance(positions, dict) or any(k not in POSITION_KEYS for k in positions):
                raise ValueError('Código de posición desconocido.')
            end = values.get('contract_end') or None
            if end: date.fromisoformat(end)
            raw = {'uid': number(values['uid'],'ID único',integer=True), 'name':values['name'],
                   'age':number(values.get('age'),'Edad',optional=True,integer=True), 'team_slot':0,
                   'positions':positions, 'attributes':attributes, 'club_name':club,
                   'natural_positions':[p.upper() for p, f in positions.items() if f==20],
                   'accomplished_positions':[p.upper() for p, f in positions.items() if 15<=f<20],
                   'transfer_value':number(values.get('transfer_value'),'Valor',optional=True,money=True),
                   'contract':{'wage':number(values.get('wage_weekly'),'Salario semanal',optional=True,money=True), 'end':end}}
            if raw['uid'] <= 0 or (raw['age'] is not None and not 10<=raw['age']<=100):
                raise ValueError('ID o edad fuera de rango.')
            raw['season_stats'] = {k:number(values.get(k),k,optional=True,integer=k!='average_rating') for k in ('minutes','goals','assists','appearances','average_rating')}
            raw['season_stats']['available'] = any(v is not None for v in raw['season_stats'].values())
            raw.update(season_stats_scope=scope, season_stats_period=period)
            players.append(clean_player(raw))
        except (ValueError, TypeError) as exc:
            raise ValueError(f'Fila {index}: {exc}') from exc
    if not players or len({p['uid'] for p in players}) != len(players):
        raise ValueError('No hay jugadores o hay IDs únicos repetidos.')
    link = params.get('link_current') is True
    if link and (not current or params.get('dataset_id') != current['id'] or club != current['club'] or manager != current.get('manager')):
        raise ValueError('Para vincular, conservá el club y manager de la partida actual y recargá si cambió.')
    identity = 'table:'+key(club)+':'+key(manager)
    career = current['career_id'] if link else hashlib.sha256(identity.encode()).hexdigest()[:24]
    club_uid = current.get('club_uid',0) if link else 0
    manager_uid = current.get('manager_uid',0) if link else 0
    digest = hashlib.sha256(json.dumps([career,game_date,players],sort_keys=True).encode()).hexdigest()
    partial_familiarities = sum(len(p['positions'])<len(POSITION_KEYS) for p in players)
    warnings = ['Tabla importada: solo incluye las filas y columnas del archivo. No contiene táctica guardada ni prueba la disponibilidad de instrucciones.']
    if partial_familiarities:
        warnings.append('Faltan familiaridades en la tabla: Propuestas aplica la penalización mínima del modelo a puestos sin dato. Comparar y Evolución dejan esos encajes desconocidos. Completá las columnas pos_* para evaluarlos con datos.')
    report = {'club':{'uid':club_uid,'name':club}, 'managed_clubs':[{'club_uid':club_uid,
              'manager_staff_uid':manager_uid,'manager_name':manager}], 'external_career_id':career,
              'game_date':game_date,'build':'FM26 · exportación de tabla','save_sha256':digest,
              'sanity_errors':[], 'missing_required_fields':{}, 'slot_labels':{'0':'Plantel exportado'},
              'reader_warnings':warnings}
    return {'players':players, 'report':report, 'base_dataset_id':current['id'] if current else None,
            'filename':str(params.get('filename','Plantel.csv')).replace('\\','/').rsplit('/',1)[-1][:200],
            'summary':{'count':len(players),'club':club,'date':game_date,'linked':link,
                       'recognized_columns':recognized,'ignored_columns':[c for c,k in zip(rows[0],columns) if not k],
                       'partial_familiarities':partial_familiarities,
                       'stats_count':sum(p['season_stats']['available'] for p in players),
                       'sample':[{'uid':p['uid'],'name':p['name']} for p in players[:5]]}}


def template():
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(['uid','name','age','positions',*ATTRS,'wage_weekly','contract_end','minutes','goals','assists'])
    # Example row is explicitly labelled. No fabricated personal player attributes.
    writer.writerow([1,'EJEMPLO - reemplazar',24,json.dumps({'mc':20}),*([10]*len(ATTRS)),1000,'2028-06-30',900,1,2])
    return stream.getvalue()
