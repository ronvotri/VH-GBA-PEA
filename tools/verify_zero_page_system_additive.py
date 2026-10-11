#!/usr/bin/env python3
"""Attest additive system zero-page strings and every prior map/system owner.

Fails closed on duplicate owners, absent ELF labels, ROM mismatches, non-stock
font banks, or unsafe page/dynamic markup. Not a gameplay or font-art approval.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from stage_static_zero_page_dialogues import zero_page_words
from verify_compiled_source_strings import (
    extract_asm_payload, validate_byte_string, validate_stages,
)

SYSTEM_REPORTS = (
    "SOURCE_SYSTEM_TEXT_STAGE.json",
    "SOURCE_BIRCH_NARRATIVE_STAGE.json",
    "SOURCE_BIRCH_DYNAMIC_STAGE.json",
    "SOURCE_SYSTEM_TEXT_SECOND_STAGE.json",
    "SOURCE_SYSTEM_SCROLL_REFLOW_STAGE.json",
    "SOURCE_PAGED_SYSTEM_ADDITIVE_STAGE.json",
    "SOURCE_ZERO_PAGE_SYSTEM_ADDITIVE_STAGE.json",
)
MAP_REPORTS = (
    "SOURCE_LEVEL_VIETNAMESE_PILOT.json",
    "SOURCE_EXPANDED_MAP_STAGE.json",
    "SOURCE_EXPANDED_MAP_LF_STAGE.json",
    "SOURCE_MAP_SCROLL_REFLOW_STAGE.json",
    "SOURCE_LEVEL_DYNAMIC_PILOT.json",
    "SOURCE_ADDITIVE_LITERAL_LF_SCROLL_STAGE.json",
    "SOURCE_ZERO_PAGE_MAP_ADDITIVE_STAGE.json",
    "SOURCE_PAGED_MAP_ADDITIVE_STAGE.json",
)


def read_reports(root: Path, names: tuple[str, ...], prefix: str) -> list[dict]:
    reports = []
    for name in names:
        report = json.loads((root / name).read_text(encoding="utf-8"))
        rows = report.get("translated", report.get("accepted"))
        if report.get("mode") != "apply" or not isinstance(rows, list):
            raise ValueError(f"invalid prior report: {name}")
        if report.get("labels_staged") != len(rows):
            raise ValueError(f"source rows mismatch: {name}")
        for row in rows:
            file = row.get("source_file") or row.get("file")
            if not file or not file.startswith(prefix):
                raise ValueError(f"unsafe source owner: {name}")
            if not row.get("label"):
                raise ValueError(f"unnamed source owner: {name}")
        reports.append(report)
    return reports


def verify(workspace: Path, artifacts: Path, rom_path: Path, sym_path: Path,
           font_path: Path, headroom_path: Path) -> dict:
    prior = json.loads(
        (artifacts / "SOURCE_PAGED_SYSTEM_ADDITIVE_ATTESTATION.json").read_text()
    )
    if (prior.get("total_unique_source_compiled_labels") != 5967
            or prior.get("all_source_owned_system_rom_byte_arrays_verified") != 1158
            or prior.get("prior_map_dialogue_ROM_bytes_verified") != 2867):
        raise ValueError("5967 source gate not verified")

    system = read_reports(artifacts, SYSTEM_REPORTS, "data/text/")
    maps = read_reports(artifacts, MAP_REPORTS, "data/maps/")
    staged = system[-1]
    additions = staged["translated"]
    n = len(additions)
    if (not 1 <= n <= 750
            or staged.get("previously_compiled_system_owner_exclusions") != 1158
            or staged.get("page_breaks_added") != 0
            or staged.get("raw_ROM_pointer_writes") != 0
            or staged.get("runtime_variables_admitted")
            or staged.get("unsupported_controls_admitted")):
        raise ValueError("new system zero-page batch outside safe contract")
    for row in additions:
        if (row.get("source_page_breaks") != 0
                or row.get("authored_page_breaks") != 0
                or row.get("word_count", 0) < 1):
            raise ValueError(f"page/word contract drift: {row['label']}")
        if zero_page_words(row["english"], row["vietnamese"]) != (
                zero_page_words(row["english"], row["authored_vietnamese"])):
            raise ValueError(f"authored Vietnamese changed: {row['label']}")
    check = validate_stages(workspace, {"system-text": staged})
    if check["checked_unique_source_labels"] != n:
        raise ValueError("new source stage is not byte-attested")

    font = json.loads(font_path.read_text())
    head = json.loads(headroom_path.read_text())
    if (font.get("glyph_blocks_matched_clean") != 5
            or font.get("source_rom_sha256") != head.get("source_ROM_sha256")
            or head.get("linker_free_bytes", -1) < 1048576):
        raise ValueError("font/layout/headroom safety gate failed")
    rom = rom_path.read_bytes()
    symbols = sym_path.read_text()
    addresses = {}
    for addr, name in re.findall(
        r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        symbols
    ):
        addresses.setdefault(name, []).append(int(addr, 16))

    owners = set()
    source_cache = {}
    counts = {}
    for scope, reports in (("system", system), ("map", maps)):
        count = 0
        for report in reports:
            for row in report.get("translated", report.get("accepted")):
                file = row.get("source_file") or row.get("file")
                label = row["label"]
                owner = (file, label)
                if owner in owners:
                    raise ValueError(f"duplicate compiled owner: {owner}")
                owners.add(owner)
                path = (workspace / file).resolve()
                if not path.is_relative_to(workspace.resolve()):
                    raise ValueError(f"unsafe source file {file}")
                if file not in source_cache:
                    source_cache[file] = path.read_text(encoding="utf-8")
                payload = extract_asm_payload(source_cache[file], label)
                validate_byte_string(payload, label)
                matched = addresses.get(label, [])
                if len(matched) != 1:
                    raise ValueError(f"ambiguous ELF owner {label}: {matched}")
                offset = matched[0] - 0x08000000
                if offset < 0 or rom[offset:offset + len(payload)] != payload:
                    raise ValueError(f"ELF/GBA payload mismatch: {owner}")
                count += 1
        counts[scope] = count
    if counts["system"] != 1158 + n or counts["map"] != 2867:
        raise ValueError(f"prior coverage changed: {counts}")
    return {
        "previously_compiled_source_labels": 5967,
        "new_static_zero_page_system_labels": n,
        "combined_source_compiled_labels": 5967 + n,
        "verified_source_owned_system_labels": counts["system"],
        "verified_source_owned_map_labels": counts["map"],
        "all_authored_zero_page_words_preserved": True,
        "all_elf_gba_payloads_verified": True,
        "stock_font_banks_verified": 5,
        "source_rom_sha256": head["source_ROM_sha256"],
        "rom_contiguous_tail_bytes": head["linker_free_bytes"],
        "private_approved_v04_font_imported": False,
        "emulator_visual_gameplay_qa": False,
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
    result = verify(a.workspace, a.artifact, a.rom, a.sym,
                    a.font_audit, a.headroom)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
