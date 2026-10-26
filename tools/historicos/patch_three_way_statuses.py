"""Applies the precise three-way availability status (editable_verified, locked_verified, unverified)
and cleans remaining hardcoded names in advice."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 1. Update fm_app/fm26.py
fm26_path = ROOT / 'fm_app' / 'fm26.py'
fm26_code = fm26_path.read_text(encoding='utf-8')

old_pi_logic = """        if has_context:
            if key in locks:
                i['locked'] = True
                i['editable'] = False
                locked_val = locks[key]
                i['locked_value'] = locked_val
                i['availability_source'] = f"Capturas del menú FM26 ({ctx.get('evidence', '')})"
                if locked_val is not None:
                    i.update(instruction('player', key, locked_val, 'Valor bloqueado por el rol en las capturas: cambiar el rol para modificarlo.', 'role'))
                else:
                    i['locked_value'] = None
                    i['value_en'] = None
                    i['value'] = 'Desconocido (tapado por ayuda emergente en FM26)'
                    i['origin'] = 'role'
                    i['reason'] = 'Valor bloqueado en el juego pero tapado en las capturas por ayuda emergente (pendiente de certificación).'
            elif key in editable_list:
                i['locked'] = False
                i['editable'] = True
                i['locked_value'] = None
                i['availability_source'] = f"Control editable comprobado en capturas FM26 ({ctx.get('evidence', '')})"
            else:
                i['locked'] = False
                i['editable'] = True
                i['locked_value'] = None
                i['availability_source'] = f"Control observado en FM26 ({ctx.get('evidence', '')})"
        else:
            i['locked'] = None
            i['editable'] = None
            i['locked_value'] = None
            i['availability_source'] = 'Disponibilidad no comprobada en las capturas de este rol'"""

new_pi_logic = """        if has_context:
            if key in locks:
                i['locked'] = True
                i['editable'] = False
                i['availability_status'] = 'locked_verified'
                i['status_label'] = 'Bloqueado comprobado'
                locked_val = locks[key]
                i['locked_value'] = locked_val
                i['availability_source'] = f"Bloqueo comprobado en capturas FM26 ({ctx.get('evidence', '')})"
                if locked_val is not None:
                    i.update(instruction('player', key, locked_val, 'Valor bloqueado por el rol en las capturas: cambiar el rol para modificarlo.', 'role'))
                else:
                    i['locked_value'] = None
                    i['value_en'] = None
                    i['value'] = 'Desconocido (tapado por ayuda emergente en FM26)'
                    i['origin'] = 'role'
                    i['reason'] = 'Valor bloqueado en el juego pero tapado en las capturas por ayuda emergente (pendiente de certificación).'
            elif key in editable_list:
                i['locked'] = False
                i['editable'] = True
                i['availability_status'] = 'editable_verified'
                i['status_label'] = 'Editable comprobado'
                i['locked_value'] = None
                i['availability_source'] = f"Control editable comprobado en capturas FM26 ({ctx.get('evidence', '')})"
            else:
                i['locked'] = None
                i['editable'] = True
                i['availability_status'] = 'unverified'
                i['status_label'] = 'Disponibilidad no verificada'
                i['locked_value'] = None
                i['availability_source'] = f"Disponibilidad no verificada en FM para este contexto ({ctx.get('evidence', '')})"
        else:
            i['locked'] = None
            i['editable'] = True
            i['availability_status'] = 'unverified'
            i['status_label'] = 'Disponibilidad no verificada'
            i['locked_value'] = None
            i['availability_source'] = 'Disponibilidad no comprobada en las capturas de este rol'"""

assert old_pi_logic in fm26_code, 'old_pi_logic not found in fm26.py'
fm26_code = fm26_code.replace(old_pi_logic, new_pi_logic)
fm26_path.write_text(fm26_code, encoding='utf-8')
print('Updated fm_app/fm26.py')

# 2. Update fm_app/current_tactic.py
ct_path = ROOT / 'fm_app' / 'current_tactic.py'
ct_code = ct_path.read_text(encoding='utf-8')

old_vuskovic = """            is_vuskovic = 'vuskovic' in p['name'].lower()
            action_text = 'En Vušković: cambiar Presión a «Normal» (para hacer cobertura y que Cubarsí anticipe)' if is_vuskovic else 'Monitorear salida: Cubarsí anticipa mientras Vušković hace la cobertura'"""
new_vuskovic = """            action_text = f'En {p["name"]}: evaluar cambiar Presión a «Normal» para escalonar la zaga y hacer cobertura'"""

assert old_vuskovic in ct_code, 'old_vuskovic not found in current_tactic.py'
ct_code = ct_code.replace(old_vuskovic, new_vuskovic)
ct_path.write_text(ct_code, encoding='utf-8')
print('Updated fm_app/current_tactic.py')

# 3. Update web/tactics-view.js
tv_path = ROOT / 'web' / 'tactics-view.js'
tv_code = tv_path.read_text(encoding='utf-8')

old_status_badge = """      const statusBadge = i.locked ? (i.locked_value == null ? '<span class="inst-badge-masked">🔒 Bloqueada (tapada por tooltip)</span>' : '<span class="inst-badge-lock">🔒 Bloqueada por rol</span>') : (i.editable ? '<span class="inst-badge-edit">⚙️ Editable</span>' : '<span class="inst-badge-unverified">ℹ️ No comprobado</span>');"""
new_status_badge = """      const statusBadge = i.availability_status === 'locked_verified' || i.locked
        ? (i.locked_value == null ? '<span class="inst-badge-masked">🔒 Bloqueado (tapado)</span>' : '<span class="inst-badge-lock">🔒 Bloqueado comprobado</span>')
        : (i.availability_status === 'editable_verified' || (i.editable && i.locked === false && i.availability_status !== 'unverified')
          ? '<span class="inst-badge-edit">⚙️ Editable comprobado</span>'
          : '<span class="inst-badge-unverified" title="Disponibilidad no verificada en FM (no comprobado en este contexto)">❓ Disponibilidad no verificada</span>');"""

assert old_status_badge in tv_code, 'old_status_badge not found in tactics-view.js'
tv_code = tv_code.replace(old_status_badge, new_status_badge)
tv_path.write_text(tv_code, encoding='utf-8')
print('Updated web/tactics-view.js')

# 4. Update web/current-view.js
cv_path = ROOT / 'web' / 'current-view.js'
cv_code = cv_path.read_text(encoding='utf-8')

old_lock_section = """                if (id in ctx.locked_values) {
                  isDisabled = true;
                  const lockedVal = ctx.locked_values[id];
                  if (lockedVal === null) {
                    lockBadge = '<span class="inst-badge-masked" title="Tapado por ayuda emergente en captura de FM26">🔒 Bloqueada (valor tapado)</span>';
                    selectedVal = null;
                  } else {
                    selectedVal = lockedVal;
                    titleAttr = `title="Bloqueada por el rol en FM26 (${ctx.evidence})"`;
                    lockBadge = `<span class="inst-badge-lock" ${titleAttr}>🔒 Bloqueada</span>`;
                  }
                } else if (ctx.editable_groups?.includes(id)) {
                  titleAttr = `title="Comprobado editable en FM26 (${ctx.evidence})"`;
                  lockBadge = `<span class="inst-badge-edit" ${titleAttr}>⚙️ Editable</span>`;
                } else {
                  lockBadge = '<span class="inst-badge-unverified" title="Fuera de panel comprobado para este rol">No disponible</span>';
                }
              } else {
                lockBadge = '<span class="inst-badge-unverified" title="Disponibilidad no comprobada en capturas">ℹ️ No comprobado</span>';
              }"""

new_lock_section = """                if (id in ctx.locked_values) {
                  isDisabled = true;
                  const lockedVal = ctx.locked_values[id];
                  if (lockedVal === null) {
                    lockBadge = '<span class="inst-badge-masked" title="Tapado por ayuda emergente en captura de FM26">🔒 Bloqueado (valor tapado)</span>';
                    selectedVal = null;
                  } else {
                    selectedVal = lockedVal;
                    titleAttr = `title="Bloqueado comprobado por el rol en FM26 (${ctx.evidence})"`;
                    lockBadge = `<span class="inst-badge-lock" ${titleAttr}>🔒 Bloqueado comprobado</span>`;
                  }
                } else if (ctx.editable_groups?.includes(id)) {
                  titleAttr = `title="Editable comprobado en FM26 (${ctx.evidence})"`;
                  lockBadge = `<span class="inst-badge-edit" ${titleAttr}>⚙️ Editable comprobado</span>`;
                } else {
                  titleAttr = 'title="Disponibilidad no verificada en FM para este contexto específico (edición permitida en borrador)"';
                  lockBadge = `<span class="inst-badge-unverified" ${titleAttr}>❓ Disponibilidad no verificada</span>`;
                }
              } else {
                titleAttr = 'title="Disponibilidad no verificada en capturas para este rol (edición permitida en borrador)"';
                lockBadge = `<span class="inst-badge-unverified" ${titleAttr}>❓ Disponibilidad no verificada</span>`;
              }"""

assert old_lock_section in cv_code, 'old_lock_section not found in current-view.js'
cv_code = cv_code.replace(old_lock_section, new_lock_section)
cv_path.write_text(cv_code, encoding='utf-8')
print('Updated web/current-view.js')
