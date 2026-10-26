from pathlib import Path

p = Path("fm_app/recommendations.py")
c = p.read_text(encoding="utf-8")
target = "'behaviours':r['player_instructions'],"
repl = "'behaviours':r['player_instructions'],\n            'behaviors':r.get('behaviors', []),\n            'subposition_rule':r.get('subposition_rule'),"

assert target in c, "target not found in recommendations.py"
c = c.replace(target, repl, 1)
p.write_text(c, encoding="utf-8")
print("recommendations.py updated successfully")
