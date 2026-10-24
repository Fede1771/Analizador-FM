export const esc = value => String(value ?? '—').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const positions = {GK:'POR',DL:'LI',DR:'LD',DC:'DFC',WBL:'CRI',WBR:'CRD',DM:'MCD',MC:'MC',ML:'MI',MR:'MD',AMC:'MPC',AML:'EI',AMR:'ED',STC:'DC'};
export const pos = value => positions[String(value).toUpperCase()] || value;
export const number = (value, decimals = 1) => value == null ? '—' : Number(value).toLocaleString('es-AR', {minimumFractionDigits: decimals, maximumFractionDigits: decimals});
export const score = value => `<span class="score">${number(value)}<small>/100</small></span>`;
export function date(value, time = false) {
  if (!value) return 'Sin fecha';
  const parsed = new Date(time ? value : value.slice(0,10) + 'T12:00:00Z');
  if (Number.isNaN(parsed.getTime())) return 'Sin fecha';
  return new Intl.DateTimeFormat('es-AR', {day:'numeric',month:'short',year:'numeric', ...(time ? {hour:'2-digit',minute:'2-digit'} : {timeZone:'UTC'})}).format(parsed);
}
export const groupName = (data,prefs,slot) => prefs.labels[slot] || data.slot_labels[slot] || `Grupo ${slot}`;
export const playerButton = p => `<button class="player-link" data-player="${p.uid}"><span class="avatar" aria-hidden="true">${esc(p.name.split(' ').slice(0,2).map(x=>x[0]).join(''))}</span><span><strong>${esc(p.name)}</strong><small>${p.age ?? '—'} años · ${esc(p.natural_positions.map(pos).join(' / '))}</small></span></button>`;
