#!/usr/bin/env python3
"""Re-attest 6090-source trial, then verify static-budget dynamic reflow in ROM."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_safe_system_dynamic_variables import VARIABLE_BYTES
from stage_system_dynamic_static_budget_reflow import compile_dynamic
from verify_page_bounded_system_dynamic import verify as verify_baseline
from verify_zero_page_system_additive import read_reports, SYSTEM_REPORTS, MAP_REPORTS
from verify_compiled_source_strings import (
    validate_stages, extract_asm_payload, validate_byte_string,
)

PREVIOUS_REPORTS = SYSTEM_REPORTS + (
    "SOURCE_LITERAL_LF_SYSTEM_ADDITIVE_STAGE.json",
    "SOURCE_PAGED_LITERAL_LF_SYSTEM_ADDITIVE_STAGE.json",
    "SOURCE_SAFE_DYNAMIC_SYSTEM_ADDITIVE_STAGE.json",
    "SOURCE_PAGE_BOUNDED_SYSTEM_DYNAMIC_STAGE.json",
)
REPORT = "SOURCE_STATIC_BUDGET_DYNAMIC_REFLOW_STAGE.json"


def audit(workspace: Path, artifact: Path, rom_file: Path, sym_file: Path,
          font_report: Path, headroom_report: Path, codebook_path: Path) -> dict:
    base = verify_baseline(
        workspace, artifact, rom_file, sym_file, font_report,
        headroom_report, codebook_path)
    if (base.get("combined_source_compiled_labels") != 6090
            or base.get("new_bounded_name_system_labels") != 85
            or base.get("prior_system_source_owners_revalidated") != 1196):
        raise ValueError("6090 source baseline not proved")
    old_system = {
        (item["source_file"], item["label"])
        for report in read_reports(artifact, PREVIOUS_REPORTS, "data/text/")
        for item in report["translated"]
    }
    old_map = {
        (item.get("source_file") or item.get("file"), item["label"])
        for report in read_reports(artifact, MAP_REPORTS, "data/maps/")
        for item in report.get("translated", report.get("accepted"))
    }
    if len(old_system) != 1281 or len(old_map) != 2867:
        raise ValueError("source owner history mismatch")
    report = json.loads((artifact / REPORT).read_text(encoding="utf-8"))
    rows = report.get("translated")
    n = len(rows) if isinstance(rows, list) else -1
    if (report.get("mode") != "apply" or not 0 <= n <= 900
            or report.get("labels_staged") != n
            or report.get("previously_compiled_system_owner_exclusions") != 1281
            or not report.get("engine_variable_bytes_verified")
            or not report.get("all_dynamic_source_line_static_budgets_preserved")
            or not report.get("all_authored_page_words_and_variable_order_preserved")
            or report.get("runtime_STR_VAR_display_width_assumed") is not False
            or report.get("raw_ROM_pointer_writes") != 0
            or report.get("font_art_modified")):
        raise ValueError("unsafe runtime STR_VAR source stage")
    if rows:
        result = validate_stages(workspace, {"system-text": report})
        if result["checked_unique_source_labels"] != n:
            raise ValueError("new source proof count mismatch")
    _, tokens = parse_charmap(workspace / "charmap.txt")
    if any(tokens.get(key) != value for key, value in VARIABLE_BYTES.items()):
        raise ValueError("invalid game-engine placeholder codebook")
    glyphs = {
        ch: int(code, 16) for ch, code in
        json.loads(codebook_path.read_text(encoding="utf-8"))["glyph_bytes"].items()
    }
    rom = rom_file.read_bytes()
    syms = {}
    for address, label in re.findall(
        r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_file.read_text(encoding="utf-8")
    ):
        syms.setdefault(label, []).append(int(address, 16))
    seen = set()
    for row in rows:
        owner = (row.get("source_file"), row.get("label"))
        if (not owner[0] or not owner[1] or not owner[0].startswith("data/text/")
                or owner in seen or owner in old_system or owner in old_map):
            raise ValueError(f"duplicate or mismatched system owner {owner}")
        seen.add(owner)
        en = row["english"]
        vi = row["authored_vietnamese"]
        rendered, payload, proof = compile_dynamic(en, vi, glyphs, tokens, 26)
        if (rendered != row["vietnamese"] or proof != row["pages"]
                or row.get("page_count") != len(proof)
                or row.get("source_native_page_count") != en.count(r"\p") + 1
                or not row.get("static_variable_line_never_exceeds_english")
                or not row.get("native_page_words_preserved")):
            raise ValueError(f"page/variable/word proof changed for {owner}")
        src = (workspace / owner[0]).resolve()
        if not src.is_relative_to(workspace.resolve()):
            raise ValueError("source path escaped workspace")
        actual = extract_asm_payload(src.read_text(encoding="utf-8"), owner[1])
        validate_byte_string(actual, owner[1])
        if actual != payload:
            raise ValueError(f"wrong assembled dynamic source bytes {owner}")
        addresses = syms.get(owner[1], [])
        if len(addresses) != 1:
            raise ValueError(f"symbol missing or ambiguous {owner}")
        offset = addresses[0] - 0x08000000
        if offset < 0 or rom[offset:offset + len(payload)] != payload:
            raise ValueError(f"linked ROM dynamic payload mismatch {owner}")
    return {
        "previously_verified_compiled_source_labels": 6090,
        "new_original_budget_dynamic_system_labels": n,
        "combined_source_compiled_labels": 6090 + n,
        "old_system_source_owners_revalidated": 1281,
        "old_map_source_owners_revalidated": 2867,
        "new_source_GBA_linked_bytes_verified": n,
        "unknown_runtime_variable_width_not_guessed": True,
        "original_dynamic_line_static_cell_budget_preserved": True,
        "all_native_page_boundaries_and_authored_words_preserved": True,
        "source_ROM_sha256": base["source_rom_sha256"],
        "rom_contiguous_tail_bytes": base["rom_tail_headroom_bytes"],
        "approved_v04_visual_font_imported": False,
        "gameplay_or_font_visual_QA": False,
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
    p.add_argument("--codebook", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = audit(
        a.workspace, a.artifact, a.rom, a.sym,
        a.font_audit, a.headroom, a.codebook)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
