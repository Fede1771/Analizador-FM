// Requirements are normalized from the original observation by the backend.
export function matchesObservedContext(observation, rows, index, phase) {
  const required = observation?.requirements;
  if (!required?.position || !required.scope) return false;
  const row = rows[index];
  const position = row[phase + '_position'];
  const scope = row.instruction_scope === 'Personalizada' ? 'player'
    : !row.instruction_scope || row.instruction_scope === 'Posición' ? 'position' : null;
  const peers = rows.map((r,i) => r[phase + '_position'] === position ? i : -1).filter(i => i >= 0);
  const rank = peers.indexOf(index);
  const side = peers.length === 1 ? null : rank === 0 ? 'left' : rank === peers.length - 1 ? 'right' : 'centre';
  return required.position === position && required.scope === scope
    && (required.side == null || required.side === side)
    && (required.count == null || required.count === peers.length);
}
