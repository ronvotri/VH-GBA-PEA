#!/usr/bin/env python3
"""Experimental SOURCE LINKER re-layout: no ROM pointer surgery or font edits.

Arena 0.13.0 deliberately shifts the original pokeemerald's fixed animation
and graphic section anchors to 0x08C00000 / 0x08D00000. The pinned original
ld_script.ld explicitly states the declarations and their references may
be removed to eliminate gaps. Only an isolated source checkout may be patched.
The produced ROM is NOT a shipping/visual-tested patch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DECLARATIONS = (
    ("__anim_mon_load_address = 0x8c00000;", "__anim_mon_load_address"),
    ("__gfx_load_address = 0x8d00000;", "__gfx_load_address"),
)
SECTIONS = (
    ("anim_mon_front_pic_data __anim_mon_load_address :",
     "anim_mon_front_pic_data :"),
    ("gfx_data __gfx_load_address :", "gfx_data :"),
)


def compact_linker_text(source: str) -> str:
    if "/* Modify the following load addresses as needed to make more room." not in source:
        raise ValueError("unrecognized original pokeemerald linker comment")
    for definition, symbol in DECLARATIONS:
        if source.count(definition) != 1 or source.count(symbol) != 2:
            raise ValueError(f"{symbol}: expected exact Arena 0.13.0 fixed anchor pair")
    for old, _ in SECTIONS:
        if source.count(old) != 1:
            raise ValueError(f"unrecognized Arena section anchor {old}")
    replacement = source
    for definition, _ in DECLARATIONS:
        replacement = replacement.replace(definition + "\n", "")
    for old, new in SECTIONS:
        replacement = replacement.replace(old, new)
    if any(symbol in replacement for _, symbol in DECLARATIONS):
        raise ValueError("unremoved fixed graphics anchor reference")
    if replacement == source:
        raise ValueError("no linker section layout change")
    return replacement


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    root = a.workspace.resolve()
    ld = (root / "ld_script.ld").resolve()
    if not ld.is_relative_to(root) or not ld.is_file():
        raise SystemExit("REFUSED: missing pinned source linker script")
    original = ld.read_text(encoding="utf-8")
    compact = compact_linker_text(original)
    if a.apply:
        ld.write_text(compact, encoding="utf-8")
    result = {
        "schema_version": 1,
        "mode": "apply" if a.apply else "dry-run",
        "source_file": "ld_script.ld",
        "original_linker_sha256": hashlib.sha256(original.encode()).hexdigest(),
        "compacted_linker_sha256": hashlib.sha256(compact.encode()).hexdigest(),
        "unfixed_graphics_anchor_symbols": 2,
        "moved_sections": ["anim_mon_front_pic_data", "gfx_data"],
        "original_sections_preserved": True,
        "source_strings_or_glyphs_modified_by_tool": False,
        "raw_ROM_or_pointer_writes": 0,
        "compiler_linker_must_reallocate_all_references": True,
        "emulator_runtime_certified": False,
        "release_ready": False,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
