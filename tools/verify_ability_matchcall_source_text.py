#!/usr/bin/env python3
"""Attest 6954 proven source labels plus bounded Ability/Match Call C UI text.

Rechecks full prior Pokédex source compilation in the actual new GBA ROM.
For every additional exact C source owner, recomputes the intended bytes,
checks unique ELF symbol address, source initializer and physical GBA bytes.
The source still uses stock English glyph rasters, not the approved v0.4 art.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from stage_ability_matchcall_source_text import (
    FILES, compile_one,
)
from verify_compiled_source_strings import (
    extract_c_payload, validate_byte_string,
)
from verify_source_pokedex_four_line import audit as audit_previous

REPORT = "SOURCE_ABILITY_MATCHCALL_ONE_LINE_STAGE.json"


def audit(workspace: Path, artifact: Path, rom_file: Path,
          sym_file: Path, font_report: Path,
          headroom_report: Path, codebook: Path) -> dict:
    prev = audit_previous(
        workspace, artifact, rom_file, sym_file,
        font_report, headroom_report, codebook)
    if (prev.get("total_verified_source_labels") != 6954
            or prev.get("new_exact_Pokedex_source_labels") != 306):
        raise ValueError("original 6954 source baseline not proved")
    record = json.loads((artifact / REPORT).read_text(encoding="utf-8"))
    rows = record.get("translated")
    count = len(rows) if isinstance(rows, list) else -1
    if (record.get("mode") != "apply"
            or record.get("category") != "system-ui"
            or record.get("selection") != "exact_ability_matchcall_one_line_source"
            or not 0 <= count <= 450
            or record.get("labels_staged") != count
            or record.get("max_translated_display_cells") != 32
            or not record.get("english_static_cell_budget_never_exceeded")
            or not record.get("user_vietnamese_content_byte_identical")
            or record.get("dynamic_engine_tokens_admitted")
            or record.get("unapproved_glyphs_admitted")
            or record.get("raw_rom_pointer_writes") != 0
            or record.get("font_art_modified")):
        raise ValueError("untrusted Ability/Match Call source report")
    glyphs = {
        character: int(byte, 16)
        for character, byte in json.loads(
            codebook.read_text(encoding="utf-8"))["glyph_bytes"].items()
    }
    rom = rom_file.read_bytes()
    syms = {}
    for hexaddr, name in re.findall(
        r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_file.read_text(encoding="utf-8")
    ):
        syms.setdefault(name, []).append(int(hexaddr, 16))
    seen = set()
    counter = {file: 0 for file in FILES}
    for row in rows:
        file, label = row.get("source_file"), row.get("label")
        owner = file, label
        if (file not in FILES or not isinstance(label, str)
                or not FILES[file].fullmatch(label)
                or owner in seen):
            raise ValueError(f"duplicate or invalid source UI owner {owner}")
        seen.add(owner)
        english = row["english"]
        vi = row["authored_vietnamese"]
        if (row.get("vietnamese") != vi
                or row.get("original_static_cells") != len(english)
                or row.get("translated_static_cells") != len(vi)
                or not row.get("source_static_line_budget_preserved")
                or not row.get("source_symbol_exact")):
            raise ValueError(f"Vietnamese UI content/width changed: {owner}")
        expected = compile_one(english, vi, glyphs, 32)
        if len(expected) != row.get("encoded_bytes"):
            raise ValueError(f"encoded C UI byte count mismatch {owner}")
        source_path = (workspace / file).resolve()
        if (not source_path.is_relative_to(workspace.resolve())
                or not source_path.is_file()):
            raise ValueError(f"C UI source path unauthorized {owner}")
        actual = extract_c_payload(
            source_path.read_text(encoding="utf-8"), label)
        validate_byte_string(actual, label)
        if actual != expected:
            raise ValueError(f"compiled C UI bytes differ: {owner}")
        linked = syms.get(label, [])
        if len(linked) != 1:
            raise ValueError(f"missing or duplicate C UI ELF label {owner}")
        offset = linked[0] - 0x08000000
        if offset < 0 or rom[offset:offset + len(expected)] != expected:
            raise ValueError(f"ROM ELF byte mismatch for C UI owner {owner}")
        counter[file] += 1
    return {
        "previous_source_compiled_labels": 6954,
        "new_ability_matchcall_source_labels": count,
        "total_source_compiled_labels": 6954 + count,
        "new_source_labels_individually_verified": count,
        "additional_file_owner_counts": counter,
        "all_prior_source_labels_reverified": True,
        "all_original_UI_width_budgets_preserved": True,
        "all_authored_Vietnamese_words_unchanged": True,
        "source_rom_sha256": prev["source_ROM_sha256"],
        "rom_contiguous_tail_bytes": prev["source_ROM_tail_free_bytes"],
        "approved_v04_art_installed": False,
        "visual_gameplay_QA": False,
        "release_ready": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("workspace", "artifact", "rom", "sym", "font-audit",
                "headroom", "codebook", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    result = audit(
        a.workspace, a.artifact, a.rom, a.sym,
        a.font_audit, a.headroom, a.codebook)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
