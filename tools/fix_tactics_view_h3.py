from pathlib import Path

p = Path("web/tactics-view.js")
c = p.read_text(encoding="utf-8")

old_str = "<h3>${esc(role.name)} ${badge ? `<span class=\"role-abbrev-tag\">${esc(badge)}</span>` : ''}</h3><small>${esc(role.english)}</small>"
new_str = "<h3>${esc(role.name)}</h3><small>${badge ? `<span class=\"role-abbrev-tag\">${esc(badge)}</span> · ` : ''}${esc(role.english)}</small>"

assert old_str in c, "old_str not found in tactics-view.js"
c = c.replace(old_str, new_str, 1)
p.write_text(c, encoding="utf-8")
print("tactics-view.js updated successfully")
