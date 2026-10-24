export function defaults(data) {
  return {primary_slot: data.default_primary_slot, labels: {}, excluded: [], style: 'possession', prompt: '', overrides: {}, formation: 'auto'};
}

export function reconcile(data, saved) {
  const base = defaults(data);
  if (!saved || typeof saved !== 'object') return base;
  const ids = new Set(data.players.map(p => p.uid));
  const slots = new Set(data.slots.map(String));
  const options = data.instruction_options || {};
  return {...base,
    primary_slot: data.slots.includes(saved.primary_slot ?? saved.primary) ? (saved.primary_slot ?? saved.primary) : base.primary_slot,
    style: data.styles[saved.style] ? saved.style : base.style,
    prompt: typeof saved.prompt === 'string' ? saved.prompt.slice(0, 2000) : '',
    formation: saved.formation === 'auto' || data.formations_catalog.some(f => f.id === saved.formation) ? saved.formation : 'auto',
    labels: Object.fromEntries(Object.entries(saved.labels || {}).filter(([k,v]) => slots.has(k) && typeof v === 'string').map(([k,v]) => [k,v.slice(0,40)])),
    excluded: Array.isArray(saved.excluded) ? [...new Set(saved.excluded.filter(id => ids.has(id)))] : [],
    overrides: Object.fromEntries(Object.entries(saved.overrides || {}).filter(([k,v]) => options[k]?.some(o => (o.value ?? o) === v)))};
}

export function preferenceKey(data) { return 'touchline:career:' + data.career_id; }

export function contextKey(data, prefs) {
  return JSON.stringify([data.id, prefs.primary_slot, prefs.style, [...prefs.excluded].sort((a,b)=>a-b), prefs.prompt, Object.entries(prefs.overrides).sort()]);
}

export function filteredPlayers(rows, {query = '', group = 'all', order = 'score'}, profiles = {}) {
  const normal = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const term = normal(query);
  return rows.filter(p => (group === 'all' || String(p.team_slot) === group) && normal(p.name + ' ' + p.natural_positions.join(' ')).includes(term))
    .sort((a,b) => order === 'age' ? (a.age ?? 99)-(b.age ?? 99) : order === 'name' ? a.name.localeCompare(b.name, 'es') : (profiles[b.uid]?.score ?? 0)-(profiles[a.uid]?.score ?? 0));
}
