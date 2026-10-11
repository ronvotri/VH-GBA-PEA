#!/usr/bin/env python3
"""Integrate source-owned single-line Ability and Match Call C descriptions.

Unlike arbitrary C string rewriting, this requires a unique original symbol,
byte-for-byte exact English initializer, no dynamic variables/controls, NFC
Vietnamese, all glyph bytes present in the pinned codebook, and NO greater
static width than the English UI text originally rendered. Does not alter
other source symbols, raw ROM pointers or the user-approved v0.4 font art.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from stage_source_map_translations import encode_text

FILES = {
    "src/data/text/abilities.h": re.compile(r"s[A-Za-z0-9_]+Description"),
    "src/data/text/match_call_messages.h": re.compile(r"gText_MatchCall[A-Za-z0-9_]+"),
}
DECL = re.compile(
    r'(?m)^(?P<pre>[ \t]*(?:(?:static|const)\s+)*const\s+u8\s+'
    r'(?P<label>[A-Za-z_][A-Za-z0-9_]*)\[\]\s*=\s*)'
    r'_\("(?P<english>(?:\\.|[^"\\])*)"\);(?P<tail>[^\r\n]*)$'
)


def replace_owned_literal(source: str, file: str, label: str, english: str,
                          encoded: bytes) -> str:
    if file not in FILES or not FILES[file].fullmatch(label):
        raise ValueError("unsupported source-owned C label")
    matches = [
        match for match in DECL.finditer(source)
        if match.group("label") == label
    ]
    if len(matches) != 1:
        raise ValueError("C symbol is missing or ambiguous")
    m = matches[0]
    if m.group("english") != english:
        raise ValueError("English original C initializer drifted")
    if not encoded or encoded[-1] != 0xFF or 0xFF in encoded[:-1]:
        raise ValueError("C initializer text terminator unsafe")
    patch = (
        m.group("pre") + "{"
        + ", ".join(f"0x{b:02X}" for b in encoded)
        + "};" + m.group("tail")
    )
    return source[:m.start()] + patch + source[m.end():]


def compile_one(english: str, authored: str, glyphs: dict[str, int],
                width: int = 32) -> bytes:
    if not 18 <= width <= 40:
        raise ValueError("unsafe single-line UI window")
    if not isinstance(english, str) or not isinstance(authored, str):
        raise ValueError("malformed C source string")
    if (not english or not authored or english == authored
            or unicodedata.normalize("NFC", authored) != authored
            or authored != authored.strip()
            or "  " in authored
            or any(char in authored for char in "{}$\\\r\n\t")
            or any(char in english for char in "{}$\\\r\n\t")):
        raise ValueError("dynamic/control text or ambiguous Unicode/whitespace")
    if len(authored) > len(english):
        raise ValueError("Vietnamese static cells exceed original English UI")
    if len(authored) > width:
        raise ValueError("translation cannot fit conservative original UI width")
    return encode_text(authored + "$", glyphs, width)


def stage(rows: list[dict], sources: dict[str, str], glyphs: dict[str, int],
          limit: int = 450, width: int = 32):
    if not 1 <= limit <= 600:
        raise ValueError("unsupported source batch limit")
    accepted = []
    skipped = Counter()
    owners = set()
    for row in rows:
        if len(accepted) >= limit:
            break
        file = row.get("source_file", "")
        label = row.get("source_label", "")
        if row.get("category") != "system-ui" or file not in FILES:
            continue
        if not isinstance(label, str) or not FILES[file].fullmatch(label):
            skipped["wrong C UI symbol type"] += 1
            continue
        owner = file, label
        if owner in owners:
            raise ValueError(f"duplicate C owner in translation plan {owner}")
        owners.add(owner)
        english = row.get("english", "")
        authored = row.get("vietnamese", "")
        if not english or not authored or english == authored:
            continue
        if file not in sources:
            skipped["missing pinned source C file"] += 1
            continue
        try:
            payload = compile_one(english, authored, glyphs, width)
            changed = replace_owned_literal(
                sources[file], file, label, english, payload)
        except ValueError as error:
            skipped[str(error)] += 1
            continue
        sources[file] = changed
        accepted.append({
            "source_file": file, "label": label,
            "english": english, "authored_vietnamese": authored,
            "vietnamese": authored, "original_static_cells": len(english),
            "translated_static_cells": len(authored),
            "source_static_line_budget_preserved": True,
            "source_symbol_exact": True,
            "encoded_bytes": len(payload),
        })
    return sources, accepted, dict(skipped)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--codebook", type=Path, required=True)
    p.add_argument("--limit", type=int, default=450)
    p.add_argument("--width", type=int, default=32)
    p.add_argument("--apply", action="store_true")
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    root = a.workspace.resolve()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    book = json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs = {c: int(b, 16) for c, b in book.items()}
    sources = {}
    for name in FILES:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"missing/unsafe source owner {name}")
        sources[name] = path.read_text(encoding="utf-8")
    original = dict(sources)
    updated, accepted, rejected = stage(plan, sources, glyphs, a.limit, a.width)
    if a.apply:
        for name, source in updated.items():
            if source != original[name]:
                (root / name).write_text(source, encoding="utf-8")
    report = {
        "mode": "apply" if a.apply else "dry-run",
        "category": "system-ui",
        "selection": "exact_ability_matchcall_one_line_source",
        "labels_staged": len(accepted),
        "max_translated_display_cells": a.width,
        "sources_changed": sum(updated[p] != original[p] for p in FILES),
        "english_static_cell_budget_never_exceeded": True,
        "user_vietnamese_content_byte_identical": True,
        "dynamic_engine_tokens_admitted": False,
        "unapproved_glyphs_admitted": False,
        "raw_rom_pointer_writes": 0,
        "font_art_modified": False,
        "emulator_QA": False, "release_ready": False,
        "skipped_reasons": rejected, "translated": accepted,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps(
        {key: value for key, value in report.items() if key != "translated"},
        ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
