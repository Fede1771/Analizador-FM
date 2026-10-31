"""Robust patches for fmsave reader when saves contain repeated team blocks or duplicate markers."""
import struct

_PATCHED = False


def apply_fmsave_patches() -> None:
    """Patch fmsave.readers.tactics to properly resolve team blocks when duplicate matches exist."""
    global _PATCHED
    if _PATCHED:
        return
    try:
        import fmsave.readers.tactics as rt
    except ImportError:
        return

    orig_block_starts = rt._block_starts
    orig_stored_block_starts = rt._stored_block_starts

    def robust_stored_block_starts(section, layout, file_name):
        starts = orig_stored_block_starts(section, layout, file_name)
        _selector, header_blocks = rt.read_tactics_header(section, layout, file_name)
        # When duplicate blocks exist further down the section (e.g. match engine snapshots),
        # keep only the active club blocks indicated by the header.
        if header_blocks > 0 and len(starts) > header_blocks and starts[:1] == [layout.first_block_offset]:
            return starts[:header_blocks]
        return starts

    def robust_block_starts(section, club_team_ids, layout):
        starts = orig_block_starts(section, club_team_ids, layout)
        missing = [t for t in club_team_ids if t not in starts]
        if not missing:
            return starts
        # If any team was dropped by orig_block_starts due to duplicate needle matches in the section,
        # recover its genuine block from structurally verified stored_block_starts.
        stored = rt._stored_block_starts(section, layout, "tactics")
        for t_id in missing:
            match = next((s for s in stored if struct.unpack("<I", section[s : s + 4])[0] == t_id), None)
            if match is not None:
                starts[t_id] = match
        return starts

    rt._stored_block_starts = robust_stored_block_starts
    rt._block_starts = robust_block_starts
    _PATCHED = True
