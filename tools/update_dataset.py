import re
from pathlib import Path

p = Path("fm_app/dataset.py")
content = p.read_text(encoding="utf-8")

old_roles = "'roles':{key:{'name':r['name'],'phase':r['phase'],'positions':r['positions']} for key,r in ROLES.items()}"
new_roles = """'observed_contexts':OBSERVED_CONTEXTS,
                'team_views_current':CATALOG.get('team_views_current', []),
                'roles':{key:{
                    'name':r['name'],
                    'phase':r['phase'],
                    'positions':r['positions'],
                    'abbreviation':r.get('abbreviation', 'ROL'),
                    'behaviors':r.get('behaviors', []),
                    'subposition_rule':r.get('subposition_rule'),
                    'english':r.get('english', ''),
                    'spanish_status':r.get('spanish_status', '')
                } for key,r in ROLES.items()}"""

old_meth = "'roles':{key:{'name':v['name'],'english':v['english'],'positions':v['positions'],'phase':v['phase'],'weights':v['weights'],'source':v['source']} for key,v in ROLES.items()}"
new_meth = """'roles':{key:{
                               'name':v['name'],
                               'english':v['english'],
                               'positions':v['positions'],
                               'phase':v['phase'],
                               'weights':v['weights'],
                               'source':v['source'],
                               'abbreviation':v.get('abbreviation', 'ROL'),
                               'behaviors':v.get('behaviors', []),
                               'subposition_rule':v.get('subposition_rule'),
                               'key_attributes_ui_verified':v.get('key_attributes_ui_verified', False)
                           } for key,v in ROLES.items()}"""

assert old_roles in content, "old_roles target not found"
assert old_meth in content, "old_meth target not found"

content = content.replace(old_roles, new_roles, 1)
content = content.replace(old_meth, new_meth, 1)

p.write_text(content, encoding="utf-8")
print("dataset.py updated successfully")
