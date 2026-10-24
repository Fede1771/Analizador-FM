"""Read a local FM26 snapshot and export Brighton with auditable sanity checks."""
import argparse
import csv
from collections import Counter
from dataclasses import asdict, fields
from datetime import date, datetime
import hashlib
import json
import sys
from pathlib import Path
import warnings

import fmsave


def serial(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def statuses():
    result = {}
    for model in (fmsave.Player, fmsave.Attributes, fmsave.Positions, fmsave.Ability):
        for field in fields(model):
            try:
                result[f"{model.__name__}.{field.name}"] = fmsave.field_status(model, field.name)
            except KeyError:
                pass  # Nested groups have statuses on their individual fields.
    return result


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("save", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/output"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with args.save.open("rb") as stream:
        digest_before = hashlib.file_digest(stream, "sha256").hexdigest()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        with fmsave.open(args.save) as career:
            print("Reading managed clubs...", flush=True)
            managed = career.managed_clubs()
            print(managed.to_dicts(), flush=True)
            clubs = career.clubs()
            managed_uids = {c.club_uid for c in managed}
            selected = [c for c in clubs if c.uid in managed_uids]
            if len(selected) != 1:
                raise RuntimeError(f"Expected one managed club, found: {selected!r}")
            club = selected[0]
            print(f"Reading players for {club.name} ({club.uid})...", flush=True)
            players = career.players()
            squad = players.where(club_uid=club.uid)
            loaned_out = players.filter(lambda p: p.loan_parent_club_uid == club.uid and p.club_uid != club.uid)
            squad.write_json(args.output / "brighton_full.json")
            squad.write_csv(args.output / "brighton_full.csv")
            loaned_out.write_json(args.output / "brighton_loaned_out.json")
            errors = []
            missing = Counter()
            for p in squad:
                for field in ("name", "age", "birth_date", "attributes", "positions"):
                    if getattr(p, field) is None:
                        missing[field] += 1
                if p.age is not None and not 12 <= p.age <= 65:
                    errors.append(f"Unusual age: {p.name}: {p.age}")
                for field in fields(p.attributes):
                    value = getattr(p.attributes, field.name)
                    if not isinstance(value, int) or not 1 <= value <= 20:
                        errors.append(f"Attribute outside 1-20: {p.name}/{field.name}={value}")
                for field in fields(p.positions):
                    value = getattr(p.positions, field.name)
                    if not isinstance(value, int) or not 1 <= value <= 20:
                        errors.append(f"Position outside 1-20: {p.name}/{field.name}={value}")
            if len({p.uid for p in squad}) != len(squad):
                errors.append("Duplicate player record IDs")
            with args.save.open("rb") as stream:
                digest_after = hashlib.file_digest(stream, "sha256").hexdigest()
            if digest_before != digest_after:
                errors.append("Snapshot changed while reading")
            report = {
                "library": fmsave.__version__, "save_sha256": digest_before,
                "game": career.info.game, "build": career.info.build,
                "known_build": career.info.known_build, "game_date": career.info.game_date,
                "snapshot_unchanged": digest_before == digest_after,
                "managed_clubs": managed.to_dicts(), "club": asdict(club),
                "all_players_count": len(players), "brighton_count": len(squad),
                "loaned_out_count": len(loaned_out),
                "team_slots": dict(Counter(str(p.team_slot) for p in squad)),
                "attributes_per_player": len(fields(fmsave.Attributes)),
                "missing_required_fields": dict(missing), "sanity_errors": errors,
                "reader_warnings": [str(w.message) for w in captured],
                "field_status": statuses(),
                "limitations": ["Sanity checks do not establish agreement with the game UI.",
                                "Team slots are stored indices; reserve/youth labels are not confirmed.",
                                "Full exports include hidden attributes and current/potential ability."]
            }
            (args.output / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=serial), encoding="utf-8")
            visible_attributes = [f.name for f in fields(fmsave.Attributes)
                                  if f.name not in {"dirtiness", "consistency", "important_matches", "injury_proneness", "versatility"}]
            columns = ["name", "age", "birth_date", "team_slot", "on_loan", "natural_positions", "accomplished_positions", "left_foot", "right_foot"]
            columns += [f"attributes_{name}" for name in visible_attributes]
            with (args.output / "brighton_visible.csv").open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=columns)
                writer.writeheader()
                for p in squad:
                    row = {name: getattr(p, name) for name in columns if not name.startswith("attributes_")}
                    row.update({f"attributes_{name}": getattr(p.attributes, name) for name in visible_attributes})
                    writer.writerow(row)
            print(json.dumps({k: report[k] for k in ("brighton_count", "loaned_out_count", "team_slots", "missing_required_fields", "sanity_errors", "reader_warnings")}, ensure_ascii=False, indent=2), flush=True)
            for p in sorted(squad, key=lambda p: (p.team_slot if p.team_slot is not None else 99, p.name or "")):
                a = p.attributes
                print(f"slot={p.team_slot} | {p.name} | {p.age} | {p.natural_positions} | passing={a.passing} technique={a.technique} pace={a.pace} finishing={a.finishing}", flush=True)


if __name__ == "__main__":
    main()
