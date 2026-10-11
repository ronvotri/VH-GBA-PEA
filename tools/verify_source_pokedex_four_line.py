#!/usr/bin/env python3
"""Attest source-owned four-line Pokédex text in the actual relinked GBA ROM.

The latest 6648 source labels are independently rechecked first. Every new
Pokédex C symbol must have a unique ELF owner and exact bytes in that ROM.
The original user-approved v0.4 bitmap glyphs are NOT present in this build.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from stage_source_map_translations import encode_text
from stage_source_pokedex_text import (
    FILE, LABEL, reflow_four_lines,
)
from verify_compiled_source_strings import (
    extract_c_payload, validate_byte_string,
)
from verify_map_multi_dynamic_line_slots import audit as audit_prior

REPORT = "SOURCE_POKEDEX_FOUR_LINE_STAGE.json"


def audit(workspace: Path, artifact: Path, rom_path: Path,
          sym_path: Path, font_report: Path, headroom_report: Path,
          codebook: Path) -> dict:
    previous = audit_prior(
        workspace, artifact, rom_path, sym_path,
        font_report, headroom_report, codebook)
    if (previous.get("total_verified_source_labels") != 6648
            or previous.get("new_multi_dynamic_source_map_labels") != 0):
        raise ValueError("6648-source compiled previous baseline changed")
    report = json.loads((artifact / REPORT).read_text(encoding="utf-8"))
    rows = report.get("translated")
    n = len(rows) if isinstance(rows, list) else -1
    if (report.get("mode") != "apply"
            or report.get("category") != "system-ui"
            or report.get("source_file") != FILE
            or report.get("selection") != "exact_four_line_Pokedex_text_C_initializers"
            or not 0 <= n <= 450
            or report.get("labels_staged") != n
            or not report.get("original_four_line_boxes_preserved")
            or not report.get("all_translated_words_preserved")
            or report.get("dynamic_engine_tokens_admitted")
            or report.get("font_raster_modified")
            or report.get("raw_rom_pointer_writes") != 0):
        raise ValueError("unsafe or incomplete source Pokédex stage")

    book = json.loads(codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs = {char: int(value, 16) for char, value in book.items()}
    src_path = (workspace / FILE).resolve()
    if not src_path.is_relative_to(workspace.resolve()):
        raise ValueError("Pokédex source path outside workspace")
    source = src_path.read_text(encoding="utf-8")
    rom = rom_path.read_bytes()
    symbols = {}
    for address, name in re.findall(
        r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_path.read_text(encoding="utf-8"),
    ):
        symbols.setdefault(name, []).append(int(address, 16))

    unique = set()
    word_reflows = 0
    for row in rows:
        name = row.get("label")
        if (not isinstance(name, str) or not LABEL.fullmatch(name)
                or row.get("source_file") != FILE or name in unique
                or row.get("four_visible_lines") is not True
                or row.get("page_words_unchanged") is not True
                or row.get("max_line_cells") != 40):
            raise ValueError(f"untrusted or duplicate Pokédex C owner {name}")
        unique.add(name)
        original = row["authored_vietnamese"]
        rendered = reflow_four_lines(original, 40)
        if (row.get("vietnamese") != rendered
                or row.get("word_boundary_reflowed") != (rendered != original)
                or row.get("encoded_bytes") !=
                len(encode_text(rendered + "$", glyphs, 40))):
            raise ValueError(f"Pokédex words/line count changed {name}")
        payload = encode_text(rendered + "$", glyphs, 40)
        if (rendered.count(r"\n") != 3
                or any(len(line) > 40 for line in rendered.split(r"\n"))
                or rendered.replace(r"\n", " ").split() !=
                   original.replace(r"\n", " ").split()):
            raise ValueError(f"Pokédex four-line integrity failed {name}")
        assembled = extract_c_payload(source, name)
        validate_byte_string(assembled, name)
        if assembled != payload:
            raise ValueError(f"Pokédex C initializer bytes do not match: {name}")
        locations = symbols.get(name, [])
        if len(locations) != 1:
            raise ValueError(f"Pokédex symbol missing or ambiguous: {name}")
        offset = locations[0] - 0x08000000
        if offset < 0 or rom[offset:offset + len(payload)] != payload:
            raise ValueError(f"Pokédex linked ROM bytes do not match: {name}")
        word_reflows += int(rendered != original)

    if word_reflows != report.get("reflowed_labels"):
        raise ValueError("Pokédex report's reflow count changed")
    return {
        "prior_verified_source_labels": 6648,
        "new_exact_Pokedex_source_labels": n,
        "total_verified_source_labels": 6648 + n,
        "original_system_source_labels_revalidated": 1552,
        "original_map_source_labels_revalidated": 3154,
        "new_C_Pokedex_GBA_ELF_payloads_verified": n,
        "reflowed_Pokedex_four_line_labels": word_reflows,
        "all_four_line_text_and_words_preserved": True,
        "source_ROM_sha256": previous["source_ROM_sha256"],
        "source_ROM_tail_free_bytes": previous["ROM_tail_headroom_bytes"],
        "approved_v04_Vietnamese_font_imported": False,
        "emulator_rendering_QA": False,
        "release_ready": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("workspace", "artifact", "rom", "sym", "font-audit",
                "headroom", "codebook", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    result = audit(
        a.workspace, a.artifact, a.rom, a.sym, a.font_audit,
        a.headroom, a.codebook)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
