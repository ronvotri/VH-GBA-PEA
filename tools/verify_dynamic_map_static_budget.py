#!/usr/bin/env python3
"""Attest all 6361 source labels and any new dynamic map/NPC labels in GBA.

Reuses the existing independent 6361-byte verification; no synthetic glyphs
or pointer guesses are ever considered proof of gameplay/rendering readiness.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_safe_system_dynamic_variables import VARIABLE_BYTES
from stage_system_dynamic_static_budget_reflow import compile_dynamic
from verify_system_dynamic_static_budget_reflow import (
    audit as audit_baseline, PREVIOUS_REPORTS as PREVIOUS_SYSTEM,
    REPORT as LAST_SYSTEM,
)
from verify_zero_page_system_additive import (
    SYSTEM_REPORTS, MAP_REPORTS, read_reports,
)
from verify_compiled_source_strings import (
    validate_stages, extract_asm_payload, validate_byte_string,
)

NEW_MAP_REPORT = "SOURCE_MAP_DYNAMIC_STATIC_BUDGET_STAGE.json"


def audit(workspace: Path, artifacts: Path, rom_file: Path,
          sym_file: Path, font_report: Path, headroom_report: Path,
          codebook: Path) -> dict:
    earlier = audit_baseline(
        workspace, artifacts, rom_file, sym_file,
        font_report, headroom_report, codebook)
    if (earlier.get("combined_source_compiled_labels") != 6361
            or earlier.get("new_original_budget_dynamic_system_labels") != 271):
        raise ValueError("6361 source-compiled baseline not proved")

    system_reports = read_reports(
        artifacts, PREVIOUS_SYSTEM + (LAST_SYSTEM,), "data/text/")
    map_reports = read_reports(artifacts, MAP_REPORTS, "data/maps/")
    prev_system = {
        (row["source_file"], row["label"])
        for report in system_reports for row in report["translated"]
    }
    prev_map = {
        (row.get("source_file") or row.get("file"), row["label"])
        for report in map_reports
        for row in report.get("translated", report.get("accepted"))
    }
    if len(prev_system) != 1552 or len(prev_map) != 2867:
        raise ValueError("old owned system/map label sets drifted")

    record = json.loads((artifacts / NEW_MAP_REPORT).read_text(encoding="utf-8"))
    new_rows = record.get("translated")
    n = len(new_rows) if isinstance(new_rows, list) else -1
    if (record.get("mode") != "apply" or record.get("category") != "map-story"
            or not 0 <= n <= 800 or record.get("labels_staged") != n
            or record.get("previously_compiled_map_owner_exclusions") != 2867
            or not record.get("runtime_variable_bytes_pinned")
            or not record.get("source_line_static_budgets_preserved")
            or not record.get("authored_page_boundaries_and_words_preserved")
            or record.get("unknown_runtime_width_assumed") is not False
            or record.get("pointer_writes") != 0
            or record.get("font_glyph_art_modified")):
        raise ValueError("unsafe newly staged dynamic map report")
    if n:
        checked = validate_stages(workspace, {"map": record})
        if checked.get("checked_unique_source_labels") != n:
            raise ValueError("source-level map bytes were not all checked")

    codes = {
        char: int(code, 16)
        for char, code in json.loads(
            codebook.read_text(encoding="utf-8"))["glyph_bytes"].items()
    }
    _, tokens = parse_charmap(workspace / "charmap.txt")
    if any(tokens.get(name) != data
           for name, data in VARIABLE_BYTES.items()):
        raise ValueError("runtime variable codes differ from source engine")
    symbols = {}
    for hexaddr, name in re.findall(
        r"(?m)^([0-9a-fA-F]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_file.read_text(encoding="utf-8"),
    ):
        symbols.setdefault(name, []).append(int(hexaddr, 16))
    rom = rom_file.read_bytes()
    new_owners = set()
    for row in new_rows:
        name = (row.get("source_file"), row.get("label"))
        if (not name[0] or not name[1]
                or not name[0].startswith("data/maps/")
                or name in new_owners or name in prev_map or name in prev_system):
            raise ValueError(f"duplicate or unauthorized map source label: {name}")
        new_owners.add(name)
        rendered, encoded, segments = compile_dynamic(
            row["english"], row["authored_vietnamese"], codes, tokens, 26)
        if (rendered != row.get("vietnamese")
                or segments != row.get("pages")
                or row.get("page_count") != len(segments)
                or row.get("source_native_page_count") !=
                    row["english"].count(r"\p") + 1
                or not row.get("source_variable_line_static_budget_preserved")
                or not row.get("authored_words_preserved_within_pages")
                or row.get("unknown_STR_VAR_runtime_width_guessed") is not False):
            raise ValueError(f"page-local dynamic map content drift: {name}")
        src = (workspace / name[0]).resolve()
        if not src.is_relative_to(workspace.resolve()):
            raise ValueError("unsafe source owner path")
        assembled = extract_asm_payload(
            src.read_text(encoding="utf-8"), name[1])
        validate_byte_string(assembled, name[1])
        if assembled != encoded:
            raise ValueError(f"wrong assembler encoding {name}")
        addrs = symbols.get(name[1], [])
        if len(addrs) != 1:
            raise ValueError(f"ambiguous ELF/ROM source label {name}")
        offset = addrs[0] - 0x08000000
        if offset < 0 or rom[offset:offset + len(encoded)] != encoded:
            raise ValueError(f"actual GBA ROM bytes differ: {name}")

    return {
        "previous_compiled_source_labels": 6361,
        "new_dynamic_map_source_labels": n,
        "total_source_compiled_labels": 6361 + n,
        "revalidated_system_source_owners": 1552,
        "revalidated_map_source_owners": 2867,
        "new_map_label_ROM_ELF_payloads_verified": n,
        "all_authored_page_words_and_source_controls_preserved": True,
        "dynamic_variable_runtime_width_not_assumed": True,
        "all_five_stock_font_banks_still_verified": True,
        "source_rom_sha256": earlier["source_ROM_sha256"],
        "rom_contiguous_tail_bytes": earlier["rom_contiguous_tail_bytes"],
        "approved_v04_font_art_present": False,
        "emulator_gameplay_QA": False,
        "release_ready": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for field in ("workspace", "artifact", "rom", "sym", "font-audit",
                  "headroom", "codebook", "out"):
        p.add_argument("--" + field, type=Path, required=True)
    a = p.parse_args()
    result = audit(
        a.workspace, a.artifact, a.rom, a.sym,
        a.font_audit, a.headroom, a.codebook)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
