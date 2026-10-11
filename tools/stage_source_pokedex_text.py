#!/usr/bin/env python3
r"""Bulk source-compile Pokédex four-line descriptions, without font changes.

Only exact English C-owned initializers in src/data/pokemon/pokedex_text.h
are replaced. Four original \n-delimited rows remain exactly four rows.
Long Vietnamese lines may be word-boundary rebalanced inside that same box,
without deleting/changing any word or introducing unsupported glyphs.
No source pointers, inferred ROM locations or graphics are edited.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path

from stage_source_map_translations import encode_text

FILE = "src/data/pokemon/pokedex_text.h"
LABEL = re.compile(r"g[A-Za-z0-9_]+PokedexText")
FIRST = re.compile(
    r"(?m)^(?P<decl>[ \t]*(?:static[ \t]+)?const[ \t]+u8[ \t]+"
    r"(?P<label>g[A-Za-z0-9_]+PokedexText)\[\][ \t]*=[ \t]*)"
    r"_\([ \t]*\r?\n")
PART = re.compile(r'^[ \t]*"((?:\\.|[^"\\])*)"[ \t]*$')
FINAL = re.compile(r'^[ \t]*"((?:\\.|[^"\\])*)"\);[ \t]*$')


def find_dex_block(source: str, label: str):
    if not LABEL.fullmatch(label):
        raise ValueError("unsafe Pokédex C symbol")
    found = [m for m in FIRST.finditer(source) if m.group("label") == label]
    if len(found) != 1:
        raise ValueError(f"{label}: missing or ambiguous C initializer")
    m = found[0]
    parts = []
    used = 0
    for line in source[m.end():].splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        last = FINAL.fullmatch(stripped)
        if last is not None:
            parts.append(last.group(1))
            used += len(line)
            break
        fragment = PART.fullmatch(stripped)
        if fragment is None:
            raise ValueError(f"{label}: unexpected C expression inside Pokédex")
        parts.append(fragment.group(1))
        used += len(line)
    else:
        raise ValueError(f"{label}: Pokédex initializer not terminated")
    if len(parts) != 4:
        raise ValueError(f"{label}: expected exactly four source rows")
    return m.start(), m.end() + used, m.group("decl"), "".join(parts)


def reflow_four_lines(authored: str, max_width: int = 40) -> str:
    if not 25 <= max_width <= 46:
        raise ValueError("unsafe Pokédex width")
    if (not isinstance(authored, str)
            or unicodedata.normalize("NFC", authored) != authored
            or authored.count(r"\n") != 3
            or any(c in authored for c in "{}$\r\t")
            or r"\l" in authored or r"\p" in authored or "\n" in authored):
        raise ValueError("not a four-line static native Pokédex description")
    original = authored.split(r"\n")
    if (any(not line or line.startswith(" ") or line.endswith(" ")
            or "  " in line for line in original)):
        raise ValueError("ambiguous authored whitespace")
    if any("\\" in line for line in original):
        raise ValueError("unknown backslash control")
    if all(len(line) <= max_width for line in original):
        return authored

    words = " ".join(original).split(" ")
    if any(not word or len(word) > max_width for word in words):
        raise ValueError("unbreakable long word in Pokédex")
    n = len(words)
    if n < 4:
        raise ValueError("not enough visible words for four lines")
    @lru_cache(None)
    def fit(start: int, remaining: int):
        if remaining == 0:
            return (0, ()) if start == n else None
        best = None
        rendered = ""
        for end in range(start + 1, n - remaining + 2):
            rendered = " ".join(words[start:end])
            if len(rendered) > max_width:
                break
            after = fit(end, remaining - 1)
            if after is None:
                continue
            loss = (max_width - len(rendered)) ** 2 + after[0]
            choice = loss, (rendered,) + after[1]
            if best is None or choice[0] < best[0]:
                best = choice
        return best
    found = fit(0, 4)
    if found is None:
        raise ValueError("authored words cannot fit original four-line box")
    rearranged = r"\n".join(found[1])
    if (len(found[1]) != 4
            or any(len(line) > max_width for line in found[1])
            or rearranged.replace(r"\n", " ").split()
                != authored.replace(r"\n", " ").split()):
        raise ValueError("Pokédex line reflow changed authored words")
    return rearranged


def replace_dex(source: str, label: str, english: str, payload: bytes):
    start, end, prefix, original = find_dex_block(source, label)
    if original != english:
        raise ValueError(f"{label}: English source changed")
    if (not payload or payload[-1] != 0xFF
            or 0xFF in payload[:-1]):
        raise ValueError("invalid GBA Pokédex text terminator")
    data = ", ".join(f"0x{value:02X}" for value in payload)
    return source[:start] + prefix + "{" + data + "};\n" + source[end:]


def stage(rows: list[dict], source: str, glyphs: dict[str, int],
          limit: int = 450, width: int = 40):
    if not 1 <= limit <= 450:
        raise ValueError("invalid Pokédex batch size")
    accepted = []
    skipped = Counter()
    seen = set()
    for row in rows:
        if len(accepted) >= limit:
            break
        if (row.get("category") != "system-ui"
                or row.get("source_file") != FILE):
            continue
        label = row.get("source_label", "")
        english = row.get("english", "")
        vi = row.get("vietnamese", "")
        if not isinstance(label, str) or not LABEL.fullmatch(label):
            skipped["not a sourced Pokédex text owner"] += 1
            continue
        if label in seen:
            raise ValueError(f"duplicate Pokédex source label {label}")
        seen.add(label)
        if not isinstance(english, str) or not isinstance(vi, str) or not vi or english == vi:
            continue
        try:
            if english.count(r"\n") != 3:
                raise ValueError("unexpected English Pokédex row count")
            rendered = reflow_four_lines(vi, width)
            payload = encode_text(rendered + "$", glyphs, width)
            updated = replace_dex(source, label, english, payload)
        except ValueError as error:
            skipped[str(error)] += 1
            continue
        source = updated
        accepted.append({
            "source_file": FILE,
            "label": label,
            "english": english,
            "authored_vietnamese": vi,
            "vietnamese": rendered,
            "four_visible_lines": True,
            "page_words_unchanged": True,
            "word_boundary_reflowed": rendered != vi,
            "max_line_cells": width,
            "encoded_bytes": len(payload),
        })
    return source, accepted, dict(skipped)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--codebook", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=450)
    ap.add_argument("--width", type=int, default=40)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    root = a.workspace.resolve()
    source_path = (root / FILE).resolve()
    if not source_path.is_relative_to(root) or not source_path.is_file():
        raise ValueError("missing exact source-owned Pokédex C header")
    original = source_path.read_text(encoding="utf-8")
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    book = json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs = {char: int(value, 16) for char, value in book.items()}
    result, accepted, skipped = stage(
        plan, original, glyphs, a.limit, a.width)
    if a.apply and result != original:
        source_path.write_text(result, encoding="utf-8")
    report = {
        "mode": "apply" if a.apply else "dry-run",
        "category": "system-ui",
        "source_file": FILE,
        "selection": "exact_four_line_Pokedex_text_C_initializers",
        "labels_staged": len(accepted),
        "reflowed_labels": sum(x["word_boundary_reflowed"] for x in accepted),
        "original_four_line_boxes_preserved": True,
        "all_translated_words_preserved": True,
        "dynamic_engine_tokens_admitted": False,
        "font_raster_modified": False,
        "raw_rom_pointer_writes": 0,
        "emulator_QA": False, "release_ready": False,
        "skipped_reasons": skipped, "translated": accepted,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items()
                      if key != "translated"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
