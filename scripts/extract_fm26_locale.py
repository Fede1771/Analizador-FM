"""Extract a small, auditable es-419 vocabulary from an owned FM26 installation.

Reads game resources; never changes the installation or a save. Only selected short
labels are written, not the language archive. UI bindings are not inferred as proven.
Run with the Python environment used for fmsave (or Python 3.14's compression.zstd).
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

try:
    from compression import zstd
except ImportError:
    from fmsave._container import zstd


# Select by translation key AND context, never by an English string alone.
# Alternate position-type strings coexist with player-role strings in this build.
ROLE_KEYS = {
    'goalkeeper': (688068, []),
    'ball_playing_goalkeeper': (688113, [696150]),
    'no_nonsense_goalkeeper': (688114, [696151]),
    'sweeper_keeper': (688070, [696159]),
    'line_holding_keeper': (688069, [696160]),
    'centre_back': (688071, [696145]),
    'ball_playing_centre_back': (688116, [696153]),
    'no_nonsense_center_back': (688129, []),
    'covering_centre_back': (688072, [696162]),
    'full_back': (688077, []),
    'pressing_full_back': (688079, [696165]),
    'holding_full_back': (688078, [696166]),
    'wing_back': (688080, []),
    'pressing_wing_back': (688082, [696167]),
    'holding_wing_back': (688081, []),
    'defensive_midfielder': (688083, []),
    'deep_lying_playmaker': (688119, []),
    'screening_defensive_midfielder': (688086, [696170]),
    'central_midfielder': (688088, []),
    'midfield_playmaker': (688146, []),
    'pressing_central_midfielder': (688089, [696172]),
    'screening_central_midfielder': (688090, [696173]),
    'wide_covering_central_midfielder': (688091, [696174]),
    'attacking_midfielder': (688095, []),
    'advanced_playmaker': (688125, []),
    'channel_midfielder': (688111, [696148]),
    'tracking_attacking_midfielder': (688098, [696175]),
    'free_role': (688131, []),
    'second_striker': (688140, []),
    'winger': (688102, []),
    'inside_winger': (688110, [696158]),
    'inside_forward': (688109, [696147]),
    'playmaking_winger': (688141, []),
    'wide_forward': (696156, []),
    'tracking_winger': (688100, [696180]),
    'wide_midfielder': (688108, []),
    'tracking_wide_midfielder': (688092, [696178]),
    'centre_forward': (688103, [696149]),
    'tracking_centre_forward': (688104, [696183]),
    'central_outlet_centre_forward': (688105, [696184]),
    'channel_forward': (688635, [696155]),
    'target_forward': (688126, []),
    'deep_lying_forward': (688112, []),
    'false_nine': (688139, []),
    'poacher': (688127, []),
}

# Some Standard strings are shared and lack a specific context in example.ltf.
# Keep those bindings explicitly provisional; an archive string isn't a UI trace.
STANDARD = 682178
PLAYER_KEYS = {
    'passing_risk_ip': (703122, {'Standard':703116, 'Take More Risks':703148, 'Take Fewer Risks':703147}),
    'dribbling_frequency_ip': (683124, {'Standard':STANDARD, 'Dribble More':343596, 'Dribble Less':343595}),
    'shoot_ip': (703121, {'Standard':STANDARD, 'Shoot More Often':344809, 'Shoot Less Often':344808}),
    'forward_runs_ip': (683125, {'Standard':STANDARD, 'Make More Runs':703135, 'Make Fewer Runs':683146}),
    'freedom_of_movement_ip': (683161, {'Follow Tactical Position':683162, 'Roam From Position':683147}),
    'hold_up_ball_ip': (683171, {'Yes':651226, 'No':651227}),
    'pressing_oop': (702986, {'Standard':703067, 'More Often':703069, 'Less Often':703070}),
    'tackling_oop': (702988, {'Standard':703065, 'Tackle Harder':703071, 'Ease Off Tackles':703072}),
}
TEAM_KEYS = {
    'passing_directness': (394530, {'Standard':STANDARD, 'Much Shorter':470495, 'Shorter':470496, 'More Direct':470499, 'Much More Direct':470501}),
    'tempo': (230057, {'Standard':STANDARD, 'Much Lower':470752, 'Lower':682711, 'Higher':470756, 'Much Higher':682724}),
    'build_up_strategy_ip': (683796, {'Play Through Press':683797, 'Balanced':683806, 'Bypass Press':683807}),
    'pass_reception_ip': (682328, {'Balanced':682664, 'Pass to Feet':701791, 'Pass Into Space':297481}),
    'attacking_transition_ip': (683205, {'Standard':683426, 'Hold Shape':468709, 'Counter-Attack':683423}),
    'line_of_engagement_oop': (682322, {'High Press':683182, 'Mid Block':683184, 'Low Block':683183}),
    'defensive_line_oop': (650479, {'Standard':696019, 'Much Lower':470753, 'Lower':470754, 'Higher':394442, 'Much Higher':470755}),
    'trigger_press_oop': (534818, {'Standard':STANDARD, 'Much Less Often':526793, 'Less Often':526794, 'More Often':526795, 'Much More Often':526796}),
    'defensive_transition_oop': (682317, {'Standard':STANDARD, 'Regroup':468710, 'Counter-Press':465736}),
}
OPTION_ALIASES = {
    ('team','build_up_strategy_ip','Bypass Press'): [688370],
    ('team','pass_reception_ip','Pass to Feet'): [683195],
    ('team','pass_reception_ip','Balanced'): [682315],
    ('player','hold_up_ball_ip','Yes'): [688217],
    ('player','hold_up_ball_ip','No'): [688216],
}
EN_OVERRIDES = {'line_holding_keeper':'Line-Holding Goalkeeper',
                'no_nonsense_center_back':'No-Nonsense Centre-Back'}
PROPERTY_OVERRIDES = {'shoot_ip':'Shooting', 'pressing_oop':'Trigger Press'}


def u32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def text_at(data, offset):
    size = u32(data, offset)
    end = offset + 4 + size
    if size > 2_000_000 or end > len(data):
        raise ValueError('Invalid string bounds')
    return data[offset+4:end].decode('utf-8'), end


def archive_files(data):
    if data[:6] != b'\x02\x01fmf.':
        raise ValueError('Unsupported FMF header')
    trailer = struct.unpack_from('<Q', data, 9)[0]
    start = data.find(b'\x28\xb5\x2f\xfd', trailer, trailer+64)
    if start < 0:
        raise ValueError('FMF directory not found')
    directory = zstd.decompress(data[start:])
    root, pos = text_at(directory, 0)
    if root != 'languages':
        raise ValueError('Expected languages archive')
    count = u32(directory, pos); pos += 4
    if not 1 <= count <= 100:
        raise ValueError('Unexpected language count')
    result = {}
    for _ in range(count):
        name, pos = text_at(directory, pos)
        extension, pos = text_at(directory, pos)
        offset, size, plain_size, _, _ = struct.unpack_from('<5Q', directory, pos)
        pos += 40; offset += 26
        if offset+size > start or plain_size > 150_000_000:
            raise ValueError('Invalid FMF entry bounds')
        result[name+extension] = (offset, size, plain_size)
    return result


def extract(data, entry):
    offset, size, plain_size = entry
    result = zstd.decompress(data[offset:offset+size])
    if len(result) != plain_size:
        raise ValueError('Language decompression size mismatch')
    return result


def ltc_index(data):
    if data[:6] != b'\x03\x01ctl.':
        raise ValueError('Unsupported LTC header')
    pos = struct.unpack_from('<Q', data, 8)[0]+8
    count = u32(data, pos)
    if count > 1_000_000 or pos+4+8*count > len(data):
        raise ValueError('Invalid LTC index')
    return {token:(offset & 0x7fffffff)+8 for token,offset in struct.iter_unpack('<II',data[pos+4:pos+4+8*count])}


def forms(data, offset):
    count = data[offset]; pos = offset+1
    if not 1 <= count <= 20:
        raise ValueError('Unexpected LTC form count')
    result = []
    for _ in range(count):
        value, pos = text_at(data, pos); result.append(value)
    return result


def clean(value):
    return re.sub(r'\[%[^\]]+\]', '', value).strip()


def normalize(value):
    return re.sub('[^a-z0-9]', '', clean(value).lower())


def generate(archive, template, build, version):
    data = archive.read_bytes(); entries = archive_files(data)
    english = extract(data, entries['english.ltc'])
    latam = extract(data, entries['spanish (latam).ltc'])
    en_index, es_index = ltc_index(english), ltc_index(latam)
    selected = {k for k,aliases in ROLE_KEYS.values() for k in [k,*aliases]}
    for groups in (PLAYER_KEYS,TEAM_KEYS):
        for prop,options in groups.values():selected.update([prop,*options.values()])
    for aliases in OPTION_ALIASES.values():selected.update(aliases)
    contexts = {}
    with template.open(encoding='utf-8-sig') as stream:
        for line in stream:
            match = re.match(r'KEY-(\d+):', line)
            if match and int(match[1]) in selected and '[COMMENT' in line:
                contexts[int(match[1])] = line.split('[COMMENT',1)[1].lstrip(' :-').rstrip().rstrip(']')

    def label(key, expected=None):
        token = 0x10000000 | key
        en = forms(english,en_index[token]); es = forms(latam,es_index[token])
        if expected and normalize(en[0]) != normalize(expected):
            raise ValueError(f'Key {key}: expected {expected!r}, found {en[0]!r}; review this build')
        if not clean(es[0]) or '[%' in clean(es[0]):
            raise ValueError(f'Invalid label {key}')
        return {'key':key, 'token':token, 'offset':es_index[token], 'english':clean(en[0]),
                'text':clean(es[0]), 'forms':[clean(s) for s in es], 'raw_forms':es,
                'context':contexts.get(key,''), 'resource_verified':True, 'runtime_verified':False}

    roles = {}
    for stem,(key,aliases) in ROLE_KEYS.items():
        expected = EN_OVERRIDES.get(stem,stem.replace('_',' '))
        roles[stem] = {**label(key,expected), 'aliases':[label(k) for k in aliases]}
    catalog = json.loads((Path(__file__).resolve().parents[1]/'fm_app/data/fm26_catalog.json').read_text(encoding='utf-8'))
    output = {}
    for kind,groups in [('player',PLAYER_KEYS),('team',TEAM_KEYS)]:
        refs = {r['id']:r for r in catalog[f'{kind}_instructions']}
        output[kind] = {}
        for name,(prop,options) in groups.items():
            if not set(options) <= set(refs[name]['options']):
                raise ValueError(f'Invalid catalog options for {name}')
            item = {'property':label(prop,PROPERTY_OVERRIDES.get(name,refs[name]['label'])), 'options':{}}
            for value,key in options.items():
                item['options'][value] = {**label(key,value), 'binding_status':'provisional' if key in {STANDARD,682664} else 'context_selected',
                    'aliases':[label(k) for k in OPTION_ALIASES.get((kind,name,value),[])]}
            output[kind][name] = item
    return {'locale':'es-419', 'language':'Español latinoamericano', 'game_version':version,
            'steam_build':build, 'source':'languages.fmf / spanish (latam).ltc',
            'sha256':{'archive':hashlib.sha256(data).hexdigest(), 'english':hashlib.sha256(english).hexdigest(),
                      'latam':hashlib.sha256(latam).hexdigest(), 'template':hashlib.sha256(template.read_bytes()).hexdigest()},
            'verification':'Resource strings and translator contexts; no complete runtime menu trace.',
            'roles':roles, **output}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True)
    parser.add_argument('--template',type=Path,required=True)
    parser.add_argument('--build',required=True)
    parser.add_argument('--version',required=True)
    parser.add_argument('--output',type=Path,default=Path('fm_app/data/fm26_es419.json'))
    args = parser.parse_args()
    result = generate(args.archive,args.template,args.build,args.version)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Extracted {len(result['roles'])} roles and {len(result['player'])+len(result['team'])} instruction groups to {args.output}")
