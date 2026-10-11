#!/usr/bin/env python3
"""Attest 6648 previous ROM labels and aligned multi-variable map additions."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_safe_system_dynamic_variables import VARIABLE_BYTES
from stage_map_multi_dynamic_line_slots import compile_aligned_multi_dynamic
from verify_map_dynamic_page_line_repair import (
    audit as audit_prior, NEW as PAGE_REPAIR_REPORT,
)
from verify_dynamic_map_static_budget import NEW_MAP_REPORT
from verify_zero_page_system_additive import MAP_REPORTS, read_reports
from verify_compiled_source_strings import (
    validate_stages, extract_asm_payload, validate_byte_string,
)

NEW = "SOURCE_MAP_MULTI_DYNAMIC_LINE_SLOTS_STAGE.json"


def audit(workspace: Path, artifacts: Path, rom_file: Path,
          sym_file: Path, font_report: Path, headroom_report: Path,
          codebook: Path) -> dict:
    proof = audit_prior(
        workspace, artifacts, rom_file, sym_file, font_report,
        headroom_report, codebook)
    if (proof.get("source_compiled_labels") != 6648
            or proof.get("new_page_local_map_dynamic_labels") != 120):
        raise ValueError("prior 6648 source ROM is not verified")
    prior_reports = read_reports(
        artifacts, MAP_REPORTS + (NEW_MAP_REPORT, PAGE_REPAIR_REPORT),
        "data/maps/")
    previous_owners = {
        (row.get("source_file") or row.get("file"), row["label"])
        for record in prior_reports
        for row in record.get("translated", record.get("accepted"))
    }
    if len(previous_owners) != 3154:
        raise ValueError("3154 map source owners are not unique")
    record = json.loads((artifacts / NEW).read_text(encoding="utf-8"))
    rows = record.get("translated")
    n = len(rows) if isinstance(rows, list) else -1
    if (record.get("mode") != "apply" or record.get("category") != "map-story"
            or not 0 <= n <= 450 or record.get("labels_staged") != n
            or record.get("previously_compiled_map_owner_exclusions") != 3154
            or not record.get("engine_tokens_byte_exact")
            or not record.get("variable_order_per_original_source_line_preserved")
            or not record.get("page_words_and_boundaries_unchanged")
            or record.get("runtime_dynamic_widths_assumed") is not False
            or record.get("raw_rom_pointer_writes") != 0
            or record.get("approved_v04_font_modified")):
        raise ValueError("untrusted multi-variable NPC source stage")
    if rows:
        compiled = validate_stages(workspace, {"map": record})
        if compiled["checked_unique_source_labels"] != n:
            raise ValueError("new source files' independently verified count mismatch")

    book = json.loads(codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs = {ch: int(value, 16) for ch, value in book.items()}
    _, variables = parse_charmap(workspace / "charmap.txt")
    if any(variables.get(key) != value for key, value in VARIABLE_BYTES.items()):
        raise ValueError("source runtime variable table differs from pinned engine")
    symbols = {}
    for addr, name in re.findall(
        r"(?m)^([0-9a-fA-F]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_file.read_text(encoding="utf-8")
    ):
        symbols.setdefault(name, []).append(int(addr, 16))
    rom = rom_file.read_bytes()
    new_owners = set()
    for row in rows:
        owner = row.get("source_file"), row.get("label")
        if (not owner[0] or not owner[1]
                or not owner[0].startswith("data/maps/")
                or owner in previous_owners or owner in new_owners):
            raise ValueError(f"duplicated/unauthorized source map owner {owner}")
        new_owners.add(owner)
        rendered, expected, details = compile_aligned_multi_dynamic(
            row["english"], row["authored_vietnamese"], glyphs, variables, 26)
        if (rendered != row.get("vietnamese")
                or details != row.get("pages")
                or row.get("page_count") != len(details)
                or row.get("source_page_count") != row["english"].count(r"\p") + 1
                or not row.get("each_source_variable_line_slot_preserved")
                or not row.get("authored_words_preserved_within_source_pages")
                or not row.get("dynamic_widths_not_guessed")):
            raise ValueError(f"authored page word or variable reflow drifted {owner}")
        source_path = (workspace / owner[0]).resolve()
        if not source_path.is_relative_to(workspace.resolve()):
            raise ValueError("source map file escapes workspace")
        payload = extract_asm_payload(
            source_path.read_text(encoding="utf-8"), owner[1])
        validate_byte_string(payload, owner[1])
        if expected != payload:
            raise ValueError(f"source's assembled data differs {owner}")
        addresses = symbols.get(owner[1], [])
        if len(addresses) != 1:
            raise ValueError(f"missing/ambiguous linked ELF symbol {owner}")
        offset = addresses[0] - 0x08000000
        if offset < 0 or rom[offset:offset + len(payload)] != payload:
            raise ValueError(f"linked GBA map dialogue byte mismatch {owner}")
    return {
        "prior_compiled_source_labels": 6648,
        "new_multi_dynamic_source_map_labels": n,
        "total_verified_source_labels": 6648 + n,
        "prior_system_labels_reverified": 1552,
        "prior_map_labels_reverified": 3154,
        "new_independently_relinked_map_labels": n,
        "authored_source_page_words_and_dynamic_slots_preserved": True,
        "dynamic_variable_expansion_not_assumed": True,
        "source_ROM_sha256": proof["source_ROM_sha256"],
        "ROM_tail_headroom_bytes": proof["rom_tail_free_bytes"],
        "approved_v04_font_imported": False,
        "emulator_QA": False, "release_ready": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ("workspace", "artifact", "rom", "sym", "font-audit",
                "headroom", "codebook", "out"):
        p.add_argument("--" + arg, type=Path, required=True)
    a = p.parse_args()
    result = audit(
        a.workspace, a.artifact, a.rom, a.sym,
        a.font_audit, a.headroom, a.codebook)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
