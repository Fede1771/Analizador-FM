from pathlib import Path

p = Path("web/app.js")
c = p.read_text(encoding="utf-8")
c_norm = c.replace("\r\n", "\n")

# Find copy-match-instructions block
start_str = "if(name==='copy-match-instructions') {"
idx1 = c_norm.find(start_str)
assert idx1 != -1, "copy-match-instructions start not found"
end_str = "if(name==='close-dialog')"
idx2 = c_norm.find(end_str, idx1)
assert idx2 != -1, "close-dialog not found"

new_copy_block = """if(name==='copy-match-instructions') {
    const isCurrent = state.view === 'current' && state.currentResult;
    const tactic = state.prefs?.formation==='auto' ? state.analysis?.requested_tactic||state.analysis?.tactics?.[0] : state.simulation;
    const nameLabel = isCurrent ? state.currentResult.name : (tactic?.name || state.prefs?.formation || '4-3-3');
    const styleLabel = isCurrent ? (state.data?.styles?.[state.currentResult.style]?.name || state.currentResult.style) : (state.data?.styles?.[state.prefs?.style]?.name || 'Posesión');
    const sourceAdvice = isCurrent ? (state.currentResult?.advice || []) : (tactic?.tactical_recommendations || []);
    const acts = sourceAdvice
      .filter(a => a.action)
      .map(a => `• ${a.title}: ${a.action} (${a.phase_label || (a.phase==='ip'?'Con posesión':a.phase==='oop'?'Sin posesión':'Equipo')})`);
    const text = [
      `📋 TOUCHLINE FM26 - AJUSTES PARA EL PARTIDO (${state.data?.club || 'Club'}):`,
      `Esquema: ${nameLabel} | Estilo: ${styleLabel}`,
      '',
      ...(acts.length ? acts : ['• Confirmá el once titular y roles en FM.']),
      '',
      `Generado por Touchline · ${date(state.data?.date)}`
    ].join('\\n');
    try {
      await navigator.clipboard.writeText(text);
      toast('¡Ajustes copiados al portapapeles!');
    } catch(e) {
      download('ajustes-partido-fm.txt', text, 'text/plain;charset=utf-8');
      toast('Ajustes descargados.');
    }
    return;
  }
  """

c_norm = c_norm[:idx1] + new_copy_block + c_norm[idx2:]

# Find check block
chk_start = "if(input.dataset.companionCheck) {"
idx_chk1 = c_norm.find(chk_start)
assert idx_chk1 != -1, "companionCheck start not found"
chk_end = "if(input.id==='scouting-sort') {"
idx_chk2 = c_norm.find(chk_end, idx_chk1)
assert idx_chk2 != -1, "scouting-sort not found"

new_check_block = """if(input.dataset.companionCheck || input.dataset.auditCheck) {
      const key = input.dataset.companionCheck || input.dataset.auditCheck;
      const isChecked = input.checked;
      try { localStorage.setItem('touchline:chk:' + key, isChecked ? '1' : '0'); } catch {}

      document.querySelectorAll(`input[data-companion-check="${key}"], input[data-audit-check="${key}"]`).forEach(el => {
        el.checked = isChecked;
        el.closest('.companion-check-item')?.classList.toggle('checked', isChecked);
        const label = el.closest('label.checklist-item');
        if (label) {
          label.classList.toggle('checked', isChecked);
          const badge = label.querySelector('.check-state-badge');
          if (badge) {
            badge.className = 'check-state-badge ' + (isChecked ? 'state-done' : 'state-pending');
            badge.textContent = isChecked ? '✓ Marcado como aplicado' : 'Pendiente en FM';
          }
        }
      });

      const allChecks = document.querySelectorAll('input[data-audit-check]');
      if (allChecks.length) {
        const checkedCount = Array.from(allChecks).filter(c => c.checked).length;
        const counter = $('#checklist-counter');
        if (counter) counter.textContent = `${checkedCount} de ${allChecks.length} aplicados por vos`;
        const pill = counter?.closest('.checklist-status-pill');
        if (pill) pill.className = 'checklist-status-pill ' + (checkedCount === allChecks.length ? 'status-ready' : 'status-pending');
        const banner = $('#checklist-complete-banner');
        if (banner) banner.hidden = (checkedCount !== allChecks.length);
      }
      return;
    }
    """

c_norm = c_norm[:idx_chk1] + new_check_block + c_norm[idx_chk2:]

p.write_text(c_norm, encoding="utf-8")
print("app.js updated successfully")
