#!/usr/bin/env python3
"""Re-attest 5969 original labels plus optional literal-LF system additions.

The verification runs on the actual newly linked ROM/ELF. Zero new labels
is a valid, explicitly reported result, never silently counted as progress.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from stage_static_zero_page_dialogues import zero_page_words
from verify_compiled_source_strings import (
    extract_asm_payload, validate_byte_string, validate_stages,
)
from verify_zero_page_system_additive import (
    MAP_REPORTS, SYSTEM_REPORTS, read_reports, verify,
)

STAGE = "SOURCE_LITERAL_LF_SYSTEM_ADDITIVE_STAGE.json"


def attest(workspace: Path, artifacts: Path, rom_path: Path, sym_path: Path,
           font_path: Path, headroom_path: Path) -> dict:
    # Checks every previously compiled system + map owner again in this ROM.
    previous = verify(
        workspace, artifacts, rom_path, sym_path, font_path, headroom_path
    )
    if (previous["combined_source_compiled_labels"] != 5969
            or previous["verified_source_owned_system_labels"] != 1160
            or previous["verified_source_owned_map_labels"] != 2867):
        raise ValueError("previous source integration baseline changed")
    stage = json.loads((artifacts / STAGE).read_text(encoding="utf-8"))
    rows = stage.get("translated")
    if (stage.get("mode") != "apply" or not isinstance(rows, list)
            or stage.get("labels_staged") != len(rows)
            or not 0 <= len(rows) <= 500
            or stage.get("previously_compiled_system_owner_exclusions") != 1160
            or not stage.get("source_control_signature_verified")
            or stage.get("page_breaks_added") != 0
            or stage.get("runtime_variables_admitted")
            or stage.get("raw_ROM_pointer_writes") != 0):
        raise ValueError("new literal LF integration report is unsafe")
    old_owners = {
        (row.get("source_file") or row.get("file"), row["label"])
        for report in read_reports(artifacts, SYSTEM_REPORTS, "data/text/")
        for row in report["translated"]
    }
    if len(old_owners) != 1160:
        raise ValueError("prior system owner count does not match verified sources")
    unique = set()
    for row in rows:
        owner = (row.get("source_file"), row.get("label"))
        if (not all(owner) or not owner[0].startswith("data/text/")
                or owner in old_owners or owner in unique):
            raise ValueError(f"duplicate or unexpected new source owner: {owner}")
        unique.add(owner)
        english, original = row["english"], row["authored_vietnamese"]
        norm, compiled = row["normalized_vietnamese"], row["vietnamese"]
        if (row.get("literal_LF_count") != original.count("\n")
                or original.count("\n") < 1
                or norm != original.replace("\n", r"\n")
                or row.get("source_page_breaks") != 0
                or row.get("authored_page_breaks") != 0
                or zero_page_words(english, norm) != zero_page_words(english, compiled)):
            raise ValueError(f"changed native layout or Vietnamese words: {owner}")
    if rows:
        result = validate_stages(workspace, {"system-text": stage})
        if result["checked_unique_source_labels"] != len(rows):
            raise ValueError("new source payload stage QA mismatch")
    rom = rom_path.read_bytes()
    syms = {}
    for address, name in re.findall(
        r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_path.read_text()
    ):
        syms.setdefault(name, []).append(int(address, 16))
    for file, label in unique:
        path = (workspace / file).resolve()
        if not path.is_relative_to(workspace.resolve()):
            raise ValueError(f"source owner escaped workspace: {file}")
        payload = extract_asm_payload(path.read_text(encoding="utf-8"), label)
        validate_byte_string(payload, label)
        addresses = syms.get(label, [])
        if len(addresses) != 1:
            raise ValueError(f"missing/ambiguous compiled symbol {label}")
        offset = addresses[0] - 0x08000000
        if offset < 0 or rom[offset:offset + len(payload)] != payload:
            raise ValueError(f"source-to-ROM binary mismatch {label}")
    n = len(rows)
    return {
        "previous_source_compiled_labels": 5969,
        "new_native_LF_normalized_system_labels": n,
        "total_source_compiled_labels": 5969 + n,
        "original_system_labels_revalidated": 1160,
        "original_map_labels_revalidated": 2867,
        "all_new_native_control_signatures_and_words_preserved": True,
        "all_new_source_labels_relinked_and_verified": n,
        "source_ROM_sha256": previous["source_rom_sha256"],
        "rom_contiguous_tail_bytes": previous["rom_contiguous_tail_bytes"],
        "approved_v04_visual_font_grafted": False,
        "emulator_QA_passed": False,
        "release_ready": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--artifact", type=Path, required=True)
    p.add_argument("--rom", type=Path, required=True)
    p.add_argument("--sym", type=Path, required=True)
    p.add_argument("--font-audit", type=Path, required=True)
    p.add_argument("--headroom", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = attest(
        a.workspace, a.artifact, a.rom, a.sym, a.font_audit, a.headroom
    )
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
