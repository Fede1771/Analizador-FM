"""Read-only extraction of tactical reference texts for the 2026-10-25 report.

Uses the existing audited FMF/LTC reader; never writes game or application data.
The presence of a resource is not proof of its availability in a runtime menu.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_fm26_locale import archive_files, extract, ltc_index, forms

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/relevamiento-fm26-2026-10-25'
GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Football Manager 26')
ARCHIVE = GAME / 'data/game_simulation/languages.fmf'
TEMPLATE = GAME / 'data/game_simulation/templates/user_folder/languages/example.ltf'


def clean(text):
    text = re.sub(r'\[COMMENT[\s\S]*', '', text)
    text = re.sub(r'\[%[^\]]+\]', '', text)
    return text.replace(r'\n', '\n').replace(r'\"', '"').strip()


def template_records():
    """LTF values can continue on physical lines, including their COMMENT."""
    current = None
    chunks = []
    with TEMPLATE.open(encoding='utf-8-sig') as stream:
        for number, line in enumerate(stream, 1):
            boundary = re.match(r'(?:KEY-\d+(?:-[A-Z]+)?|STR-\d+):', line)
            if boundary:
                if current is not None:
                    yield (*current, ''.join(chunks).rstrip())
                current, chunks = None, []
                m = re.match(r'KEY-(\d+):\s*(.*)', line)
                if m:
                    current = (int(m[1]), number)
                    chunks = [m[2] + '\n']
            elif current is not None:
                chunks.append(line)
    if current is not None:
        yield (*current, ''.join(chunks).rstrip())


def main():
    raw = ARCHIVE.read_bytes()
    members = archive_files(raw)
    en = extract(raw, members['english.ltc'])
    es = extract(raw, members['spanish (latam).ltc'])
    indices = {'en': ltc_index(en), 'es': ltc_index(es)}
    languages = {'en': en, 'es': es}
    rows = []
    for key, line_number, value in template_records():
        context = value.split('[COMMENT', 1)[1].rstrip(']') if '[COMMENT' in value else ''
        ctx = context.lower().replace('_', ' ')
        # Include all contextual player/team instruction texts and modern role block.
        if not ('player instructions' in ctx or 'team instructions' in ctx
                or 'individual player instruction' in ctx
                or 'player tactics role' in ctx or 'player roles' in ctx
                or 688068 <= key <= 688146 or key in {688635, 690528}
                or 696020 <= key <= 696185):
            continue
        token = 0x10000000 | key
        row = {'key': key, 'template_line': line_number, 'context': context,
               'template_english': clean(value), 'evidence': 'installed_resource',
               'runtime_verified': False}
        for lang in ('en', 'es'):
            offset = indices[lang].get(token)
            row[lang] = [clean(v) for v in forms(languages[lang], offset)] if offset is not None else []
            row[lang + '_offset'] = offset
        rows.append(row)
    result = {
        'date': '2026-10-25', 'source_archive': str(ARCHIVE),
        'source_template': str(TEMPLATE), 'locale': 'es-419',
        'sha256': {'archive': hashlib.sha256(raw).hexdigest(),
                   'english_ltc': hashlib.sha256(en).hexdigest(),
                   'spanish_latam_ltc': hashlib.sha256(es).hexdigest(),
                   'template': hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()},
        'limitations': ['Resources can include unused or legacy strings.',
                        'No resource key is a save-format role or instruction identifier.',
                        'No availability, locking or engine weights inferred from strings.'],
        'records': rows,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'textos-instalacion.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'records': len(rows), 'missing_spanish': sum(not r['es'] for r in rows),
                      'path': str(OUT / 'textos-instalacion.json')}, ensure_ascii=False))
    for r in rows:
        if 696020 <= r['key'] <= 696185:
            print(r['key'], r['template_english'][:85], '|', (r['es'] or ['MISSING'])[0][:85])


if __name__ == '__main__':
    main()
