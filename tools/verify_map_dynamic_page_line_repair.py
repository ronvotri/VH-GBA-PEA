#!/usr/bin/env python3
"""Verify dynamic NPC native-line repair against exact compiled ELF/GBA bytes."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_safe_system_dynamic_variables import VARIABLE_BYTES
from stage_map_dynamic_page_line_repair import compile_line_repaired_page
from verify_dynamic_map_static_budget import audit as audit_baseline, NEW_MAP_REPORT
from verify_zero_page_system_additive import MAP_REPORTS, read_reports
from verify_compiled_source_strings import (
    validate_stages, extract_asm_payload, validate_byte_string,
)

NEW = "SOURCE_MAP_DYNAMIC_PAGE_LINE_REPAIR_STAGE.json"


def audit(workspace: Path, artifacts: Path, rom_path: Path,
          sym_path: Path, font_report: Path, headroom_report: Path,
          codebook_path: Path) -> dict:
    prior = audit_baseline(
        workspace, artifacts, rom_path, sym_path, font_report,
        headroom_report, codebook_path)
    if (prior["total_source_compiled_labels"] != 6528
            or prior["new_dynamic_map_source_labels"] != 167):
        raise ValueError("6528 source-built baseline is unverified")
    previous_map = read_reports(
        artifacts, MAP_REPORTS + (NEW_MAP_REPORT,), "data/maps/")
    prior_owners = {
        (row.get("source_file") or row.get("file"), row["label"])
        for report in previous_map
        for row in report.get("translated", report.get("accepted"))
    }
    if len(prior_owners) != 3034:
        raise ValueError("3034 prior map source owners not unique")
    record = json.loads((artifacts / NEW).read_text(encoding="utf-8"))
    rows = record.get("translated")
    n = len(rows) if isinstance(rows, list) else -1
    if (record.get("mode") != "apply" or record.get("category") != "map-story"
            or not 0 <= n <= 650 or record.get("labels_staged") != n
            or record.get("previously_compiled_map_owner_exclusions") != 3034
            or not record.get("page_count_and_authored_words_preserved")
            or not record.get("source_variable_placement_budget_preserved")
            or record.get("unknown_dynamic_runtime_width_assumed") is not False
            or record.get("raw_ROM_pointer_writes") != 0
            or record.get("font_art_replaced")):
        raise ValueError("new map line-repair batch failed source safety contract")
    if n:
        source_verified = validate_stages(workspace, {"map": record})
        if source_verified["checked_unique_source_labels"] != n:
            raise ValueError("new source code has unverified map labels")

    book = json.loads(codebook_path.read_text(encoding="utf-8"))["glyph_bytes"]
    codes = {char: int(value, 16) for char, value in book.items()}
    _, tokens = parse_charmap(workspace / "charmap.txt")
    if any(tokens.get(k) != value for k, value in VARIABLE_BYTES.items()):
        raise ValueError("runtime charmap differs from pinned GBA engine")
    symbols = {}
    for addr, label in re.findall(
        r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_path.read_text(encoding="utf-8")
    ):
        symbols.setdefault(label, []).append(int(addr, 16))
    rom = rom_path.read_bytes()
    unique = set()
    for row in rows:
        owner = (row.get("source_file"), row.get("label"))
        if (not owner[0] or not owner[1]
                or not owner[0].startswith("data/maps/")
                or owner in prior_owners or owner in unique):
            raise ValueError(f"unowned or duplicated new source label {owner}")
        unique.add(owner)
        eng, vn = row["english"], row["authored_vietnamese"]
        formatted, payload, details = compile_line_repaired_page(
            eng, vn, codes, tokens)
        if (row["vietnamese"] != formatted
                or row["pages"] != details
                or row["source_page_count"] != eng.count(r"\p") + 1
                or row["authored_page_count"] != len(details)
                or not row.get("page_words_and_engine_variable_sequence_preserved")
                or not row.get("original_variable_line_static_budget_preserved")
                or row.get("dynamic_runtime_expansion_width_guessed") is not False):
            raise ValueError(f"page-local translated content changed: {owner}")
        path = (workspace / owner[0]).resolve()
        if not path.is_relative_to(workspace.resolve()):
            raise ValueError("source file escapes working tree")
        actual = extract_asm_payload(
            path.read_text(encoding="utf-8"), owner[1])
        validate_byte_string(actual, owner[1])
        if payload != actual:
            raise ValueError(f"re-encoded string differs from source {owner}")
        addrs = symbols.get(owner[1], [])
        if len(addrs) != 1:
            raise ValueError(f"missing or ambiguous ELF owner {owner}")
        offset = addrs[0] - 0x08000000
        if offset < 0 or rom[offset:offset + len(payload)] != payload:
            raise ValueError(f"new string wrong in real GBA ROM {owner}")

    return {
        "prior_source_compiled_labels": 6528,
        "new_page_local_map_dynamic_labels": n,
        "source_compiled_labels": 6528 + n,
        "prior_system_source_labels_revalidated": 1552,
        "prior_map_source_labels_revalidated": 3034,
        "new_map_source_ELF_ROM_byte_payloads_verified": n,
        "all_authored_page_words_and_variable_sequences_preserved": True,
        "original_runtime_variable_static_footprint_never_increased": True,
        "unknown_STR_VAR_value_width_not_guessed": True,
        "source_ROM_sha256": prior["source_rom_sha256"],
        "rom_tail_free_bytes": prior["rom_contiguous_tail_bytes"],
        "v04_approved_font_grafted": False,
        "emulator_QA": False,
        "release_ready": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--artifact", type=Path, required=True)
    ap.add_argument("--rom", type=Path, required=True)
    ap.add_argument("--sym", type=Path, required=True)
    ap.add_argument("--font-audit", type=Path, required=True)
    ap.add_argument("--headroom", type=Path, required=True)
    ap.add_argument("--codebook", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    result = audit(
        a.workspace, a.artifact, a.rom, a.sym, a.font_audit,
        a.headroom, a.codebook)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
