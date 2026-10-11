#!/usr/bin/env python3
"""Compile translation-manifest Easy Chat word groups as exact C source owners.

No font art creation, no ROM pointer writes, no guessed UI line wrapping.
Accept only exact original, single-line gEasyChatWord_ symbols in the stock
src/data/easy_chat/easy_chat_group_*.h owner files. The Vietnamese text must
fit both the original English cell count and a conservative 15-cell menu slot.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from stage_source_map_translations import encode_text

FILE_RE = re.compile(r"src/data/easy_chat/easy_chat_group_[a-z_]+\.h\Z")
LABEL_RE = re.compile(r"gEasyChatWord_[A-Za-z0-9_]+\Z")
C_DECL = re.compile(
    r'(?m)^(?P<head>[ \t]*(?:(?:static|const)\s+)*const\s+u8\s+'
    r'(?P<label>gEasyChatWord_[A-Za-z0-9_]+)\[\]\s*=\s*)'
    r'_\("(?P<english>(?:\\.|[^"\\])*)"\);(?P<trail>[^\r\n]*)$'
)


def compile_word(english: str, vietnamese: str,
                 glyphs: dict[str, int], max_cells: int = 15) -> bytes:
    if not 6 <= max_cells <= 20:
        raise ValueError("invalid Easy Chat menu cell budget")
    if not isinstance(english, str) or not isinstance(vietnamese, str):
        raise ValueError("malformed Easy Chat word")
    if not english or not vietnamese or english == vietnamese:
        raise ValueError("unchanged/empty translation")
    if (unicodedata.normalize("NFC", vietnamese) != vietnamese
            or vietnamese != vietnamese.strip() or "  " in vietnamese
            or any(char in vietnamese for char in "{}$\\\r\n\t")
            or any(char in english for char in "{}$\\\r\n\t")):
        raise ValueError("unsafe Easy Chat control or ambiguous spacing")
    if len(vietnamese) > len(english):
        raise ValueError("translated Easy Chat cells exceed original source")
    if len(vietnamese) > max_cells:
        raise ValueError("translated Easy Chat exceeds conservative menu slot")
    return encode_text(vietnamese + "$", glyphs, max_cells)


def replace_exact(source: str, file: str, label: str,
                  english: str, encoded: bytes) -> str:
    if not FILE_RE.fullmatch(file) or not LABEL_RE.fullmatch(label):
        raise ValueError("unapproved Easy Chat C owner")
    matches = [m for m in C_DECL.finditer(source)
               if m.group("label") == label]
    if len(matches) != 1:
        raise ValueError("ambiguous or missing Easy Chat C symbol")
    old = matches[0]
    if old.group("english") != english:
        raise ValueError("English original Easy Chat literal differs")
    if not encoded or encoded[-1] != 0xFF or 0xFF in encoded[:-1]:
        raise ValueError("unsafe compiled GBA text byte terminator")
    new = (old.group("head") + "{"
           + ", ".join(f"0x{byte:02X}" for byte in encoded)
           + "};" + old.group("trail"))
    return source[:old.start()] + new + source[old.end():]


def stage(rows: list[dict], sources: dict[str, str],
          glyphs: dict[str, int], limit: int = 1200,
          max_cells: int = 15) -> tuple[dict[str, str], list[dict], dict]:
    if not 1 <= limit <= 1500:
        raise ValueError("invalid Easy Chat batch size")
    accepted, skipped, owners = [], Counter(), set()
    for row in rows:
        if len(accepted) >= limit:
            break
        file = row.get("source_file", "")
        label = row.get("source_label", "")
        if (row.get("category") != "system-ui"
                or not isinstance(file, str) or not FILE_RE.fullmatch(file)
                or not isinstance(label, str)
                or not LABEL_RE.fullmatch(label)):
            continue
        owner = file, label
        if owner in owners:
            raise ValueError(f"duplicate Easy Chat source owner: {owner}")
        owners.add(owner)
        english = row.get("english", "")
        vietnamese = row.get("vietnamese", "")
        if english == vietnamese or not vietnamese:
            continue
        if file not in sources:
            skipped["missing pinned Easy Chat source file"] += 1
            continue
        try:
            encoded = compile_word(english, vietnamese, glyphs, max_cells)
            updated = replace_exact(
                sources[file], file, label, english, encoded)
        except ValueError as error:
            skipped[str(error)] += 1
            continue
        sources[file] = updated
        accepted.append({
            "source_file": file, "label": label, "english": english,
            "authored_vietnamese": vietnamese,
            "vietnamese": vietnamese,
            "source_static_cells": len(english),
            "translated_static_cells": len(vietnamese),
            "source_cell_budget_preserved": True,
            "source_symbol_exact": True,
            "encoded_bytes": len(encoded),
        })
    return sources, accepted, dict(skipped)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--codebook", type=Path, required=True)
    p.add_argument("--limit", type=int, default=1200)
    p.add_argument("--max-cells", type=int, default=15)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    root = a.workspace.resolve()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    glyphbook = json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs = {char: int(value, 16) for char, value in glyphbook.items()}
    files = {
        row.get("source_file") for row in plan
        if row.get("category") == "system-ui"
        and isinstance(row.get("source_file"), str)
        and FILE_RE.fullmatch(row["source_file"])
    }
    sources = {}
    for file in sorted(files):
        path = (root / file).resolve()
        if not path.is_relative_to(root):
            raise ValueError("unapproved source filepath")
        if path.is_file():
            sources[file] = path.read_text(encoding="utf-8")
    originals = dict(sources)
    output, added, skipped = stage(
        plan, sources, glyphs, a.limit, a.max_cells)
    if a.apply:
        for file, body in output.items():
            if body != originals[file]:
                (root / file).write_text(body, encoding="utf-8")
    report = {
        "mode": "apply" if a.apply else "dry-run",
        "selection": "source_exact_easy_chat_single_word_UI",
        "category": "system-ui",
        "labels_staged": len(added),
        "max_display_cells": a.max_cells,
        "source_files_staged": sum(
            originals[k] != output[k] for k in originals),
        "source_length_and_menu_cell_budgets_preserved": True,
        "authored_Vietnamese_unmodified": True,
        "raw_ROM_pointer_writes": 0,
        "font_art_changed": False,
        "approved_v04_font_imported": False,
        "emulator_QA": False,
        "release_ready": False,
        "skipped_reasons": skipped,
        "translated": added,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k != "translated"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
