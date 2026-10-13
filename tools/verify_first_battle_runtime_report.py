#!/usr/bin/env python3
"""Fail-closed first-Birch-battle runtime QA record validator.

No ROMs, saves, donor art or user-specific paths are uploaded. A CI green
source build is not a gameplay pass. A release candidate requires real,
independent gameplay observations (clean, approved v0.4, candidate) using
an identical emulator build and settings, plus in-game battery save/load.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{64}$")
KNOWN_REJECTED = {
    "0bf451fda75f1e32c5b2fc865386009f02b6339d191c721d1346bacd8807e11b",
}
CLEAN_SHA = "a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b"
V04_SHA = "c500bb1cdb0f2cf43d24c04a943854bbd9b1b83b0569f0a5f9c8d13480be83f9"


def validate_report(data: dict) -> dict:
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("invalid gameplay report schema")
    entries = data.get("runs")
    if not isinstance(entries, list) or len(entries) != 3:
        raise ValueError("require exactly clean, v0.4 and candidate emulator runs")
    expected = {"clean", "v04", "candidate"}
    by_variant = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("invalid gameplay run")
        variant = entry.get("variant")
        if variant not in expected or variant in by_variant:
            raise ValueError("missing/duplicated ROM comparison variant")
        digest = entry.get("rom_sha256")
        if not isinstance(digest, str) or not SHA.fullmatch(digest):
            raise ValueError("invalid ROM SHA")
        if digest in KNOWN_REJECTED:
            raise ValueError("known freeze-regressed +341 candidate is rejected")
        for key in ("emulator", "emulator_version", "sound_output", "save_sha256"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                raise ValueError(f"missing runtime evidence: {key}")
        if not SHA.fullmatch(entry["save_sha256"]):
            raise ValueError("invalid pre-battle battery-save digest")
        if entry.get("save_type") != "battery_sav":
            raise ValueError("save states are not an in-game .sav battery checkpoint")
        if entry.get("tested_in_emulator") is not True:
            raise ValueError("not observed in a real emulator")
        for key in ("battle_started", "battle_completed", "returned_to_overworld",
                    "moved_after_battle", "save_load_passed"):
            if type(entry.get(key)) is not bool:
                raise ValueError(f"missing observed boolean: {key}")
        by_variant[variant] = entry
    if by_variant["clean"]["rom_sha256"] != CLEAN_SHA:
        raise ValueError("wrong original ROM hash")
    if by_variant["v04"]["rom_sha256"] != V04_SHA:
        raise ValueError("wrong user-approved v0.4 donor hash")
    signatures = {
        (r["emulator"], r["emulator_version"], r["sound_output"], r["save_sha256"])
        for r in entries
    }
    if len(signatures) != 1:
        raise ValueError("A/B observations did not use identical emulator/settings/save")
    all_pass = all(
        all(row[k] is True for k in (
            "battle_started", "battle_completed", "returned_to_overworld",
            "moved_after_battle", "save_load_passed"))
        for row in entries
    )
    return {
        "runtime_evidence_present": True,
        "same_emulator_settings_and_battery_save": True,
        "known_rejected_candidate_refused": True,
        "first_battle_runtime_gate": "PASS" if all_pass else "FAIL",
        "emulator": by_variant["candidate"]["emulator"],
        "sound_output": by_variant["candidate"]["sound_output"],
        "release_ready": False,
        "note": "First-battle PASS is necessary but not sufficient for full-game release.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    result = validate_report(json.loads(args.report.read_text(encoding="utf-8")))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered)
    return None if result["first_battle_runtime_gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
