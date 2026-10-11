#!/usr/bin/env python3
"""Re-attest 7091 labels plus each accepted Easy Chat ELF/GBA source owner.

Every byte must match fresh independent Vietnamese encoding and the unique
linked symbol. No Playable ROM, user-approved v0.4 donor glyph or test results
are inferred from stock-font data.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from stage_easy_chat_word_groups import FILE_RE, LABEL_RE, compile_word
from verify_ability_matchcall_source_text import audit as verify_previous
from verify_compiled_source_strings import extract_c_payload, validate_byte_string

REPORT = "SOURCE_EASY_CHAT_WORD_GROUPS_STAGE.json"


def audit(workspace: Path, artifacts: Path, rom_file: Path,
          sym_file: Path, font_report: Path, headroom_report: Path,
          codebook: Path) -> dict:
    prev = verify_previous(
        workspace, artifacts, rom_file, sym_file,
        font_report, headroom_report, codebook)
    if (prev["total_source_compiled_labels"] != 7091
            or prev["new_ability_matchcall_source_labels"] != 137):
        raise ValueError("7091 source-built baseline is not proven")

    record = json.loads((artifacts / REPORT).read_text(encoding="utf-8"))
    rows = record.get("translated")
    count = len(rows) if isinstance(rows, list) else -1
    if (record.get("mode") != "apply"
            or record.get("category") != "system-ui"
            or record.get("selection") != "source_exact_easy_chat_single_word_UI"
            or not 0 <= count <= 1200
            or record.get("labels_staged") != count
            or record.get("max_display_cells") != 15
            or not record.get("source_length_and_menu_cell_budgets_preserved")
            or not record.get("authored_Vietnamese_unmodified")
            or record.get("raw_ROM_pointer_writes") != 0
            or record.get("font_art_changed")
            or record.get("approved_v04_font_imported")):
        raise ValueError("Easy Chat C source stage failed safety requirements")

    glyphs = {
        key: int(byte, 16)
        for key, byte in json.loads(codebook.read_text(encoding="utf-8"))[
            "glyph_bytes"].items()
    }
    symbols = {}
    for hex_addr, label in re.findall(
        r"(?m)^([0-9A-Fa-f]+)\s+\w\s+([A-Za-z_][A-Za-z0-9_]*)$",
        sym_file.read_text(encoding="utf-8")
    ):
        symbols.setdefault(label, []).append(int(hex_addr, 16))
    rom = rom_file.read_bytes()
    owners = set()
    files = set()
    for row in rows:
        file, label = row.get("source_file"), row.get("label")
        owner = (file, label)
        if (not isinstance(file, str) or not FILE_RE.fullmatch(file)
                or not isinstance(label, str) or not LABEL_RE.fullmatch(label)
                or owner in owners):
            raise ValueError(f"unapproved/duplicate Easy Chat source symbol {owner}")
        owners.add(owner)
        vi, en = row["authored_vietnamese"], row["english"]
        if (row.get("vietnamese") != vi
                or row.get("source_static_cells") != len(en)
                or row.get("translated_static_cells") != len(vi)
                or not row.get("source_cell_budget_preserved")
                or not row.get("source_symbol_exact")):
            raise ValueError(f"original Easy Chat source budget/words changed {owner}")
        expected = compile_word(en, vi, glyphs, 15)
        if row.get("encoded_bytes") != len(expected):
            raise ValueError(f"wrong expected C string length {owner}")
        source = (workspace / file).resolve()
        if not source.is_relative_to(workspace.resolve()) or not source.is_file():
            raise ValueError(f"source escaped pinned Easy Chat workspace {owner}")
        actual = extract_c_payload(source.read_text(encoding="utf-8"), label)
        validate_byte_string(actual, label)
        if actual != expected:
            raise ValueError(f"source C initializer differs from Vietnamese bytes {owner}")
        addrs = symbols.get(label, [])
        if len(addrs) != 1:
            raise ValueError(f"missing/ambiguous ELF C symbol {owner}")
        offset = addrs[0] - 0x08000000
        if offset < 0 or rom[offset:offset + len(expected)] != expected:
            raise ValueError(f"Easy Chat ROM bytes differ at ELF location {owner}")
        files.add(file)

    return {
        "previously_compiled_source_labels": 7091,
        "new_easy_chat_source_labels": count,
        "total_compiled_source_labels": 7091 + count,
        "previous_source_labels_revalidated": 7091,
        "new_owner_labels_individually_ROM_ELF_verified": count,
        "new_Easy_Chat_groups_changed": len(files),
        "all_authored_Easy_Chat_word_bytes_preserved": True,
        "no_source_cell_or_menu_width_expansion": True,
        "source_ROM_sha256": prev["source_rom_sha256"],
        "rom_tail_free_bytes": prev["rom_contiguous_tail_bytes"],
        "approved_v04_font_grafted": False,
        "emulator_QA": False,
        "release_ready": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ("workspace", "artifact", "rom", "sym", "font-audit",
                "headroom", "codebook", "out"):
        p.add_argument("--" + arg, type=Path, required=True)
    a = p.parse_args()
    result = audit(a.workspace, a.artifact, a.rom, a.sym,
                   a.font_audit, a.headroom, a.codebook)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
