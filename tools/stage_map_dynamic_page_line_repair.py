#!/usr/bin/env python3
r"""Source-map dynamic page reflow with control-layout repair, not new glyphs.

For previously uncompiled NPC pages where Vietnamese \n/\l controls differ
from source English controls. Both must have the same original \p page
boundaries. Supports exactly ONE source native line containing variables per
page, with the identical ordered engine variables in Vietnamese. Uses the
original variable-bearing line's static cell budget; it never estimates a
STR_VAR runtime value length. Every authored word stays in its original page.
No font bitmaps or ROM pointers are touched.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_birch_dynamic_intro import verify_engine
from stage_source_map_translations import patch_labeled_block, prioritized_rows
from stage_static_zero_page_dialogues import exclude_exact_source_owners
from stage_safe_system_dynamic_variables import VARIABLE_BYTES, TOKEN, encode
from stage_system_dynamic_static_budget_reflow import (
    LAYOUT, text_ok, segment_reflow, plain_wrap,
)

MAX_LINES_PER_PAGE = 12


def compile_line_repaired_page(en: str, vi: str, codes: dict[str, int],
                               tokens: dict[str, bytes], width: int = 26):
    if not 12 <= width <= 30:
        raise ValueError("unsafe dynamic page width")
    text_ok(en)
    text_ok(vi)
    eng_pages = en[:-1].split(r"\p")
    vn_pages = vi[:-1].split(r"\p")
    if len(eng_pages) != len(vn_pages):
        raise ValueError("native page count changed")
    pages = []
    details = []
    any_variables = False
    for source_page, authored_page in zip(eng_pages, vn_pages):
        if (authored_page.startswith(" ") or authored_page.endswith(" ")
                or "  " in authored_page
                or any(mark in authored_page for mark in
                       (r" \n", r"\n ", r" \l", r"\l "))):
            raise ValueError("ambiguous authored whitespace around native controls")
        source_lines = LAYOUT.split(source_page)
        source_variable_lines = [
            line for line in source_lines if TOKEN.findall(line)
        ]
        authored_words = LAYOUT.sub(" ", authored_page).split()
        translated_flat = " ".join(authored_words)
        if not translated_flat or not source_page:
            raise ValueError("empty source or translated page")
        if (TOKEN.findall(source_page) != TOKEN.findall(translated_flat)):
            raise ValueError("runtime variable sequence differs within page")
        if len(source_variable_lines) > 1:
            raise ValueError("multiple variable-bearing native lines in page")
        if source_variable_lines:
            any_variables = True
            src = source_variable_lines[0]
            lines, proof = segment_reflow(src, translated_flat, width)
        else:
            if TOKEN.search(translated_flat):
                raise ValueError("new variable in static source page")
            lines = plain_wrap(authored_words, width)
            proof = {
                "tokens": [],
                "source_static_budget": 0,
                "dynamic_static_cells": 0,
                "segments_rendered": len(lines),
            }
        if not lines or len(lines) > MAX_LINES_PER_PAGE:
            raise ValueError("too many native lines to scroll safely")
        reflow = lines[0] + "".join(
            (r"\n" if i == 1 else r"\l") + line
            for i, line in enumerate(lines[1:], 1))
        if (LAYOUT.sub(" ", reflow).split() != authored_words
                or TOKEN.findall(reflow) != TOKEN.findall(source_page)):
            raise ValueError("authored page words or variables changed")
        pages.append(reflow)
        details.append({
            "original_native_lines": len(source_lines),
            "compiled_native_lines": len(lines),
            "authored_word_count": len(authored_words),
            "source_variable_bearing_lines": len(source_variable_lines),
            "original_variable_line_budget": proof["source_static_budget"],
            "compiled_variable_line_static_cells": proof["dynamic_static_cells"],
            "variables": proof["tokens"],
        })
    if not any_variables:
        raise ValueError("not a dynamic source map dialogue")
    result = r"\p".join(pages) + "$"
    if result.count(r"\p") != en.count(r"\p"):
        raise ValueError("changed page breaks")
    return result, encode(result, codes, tokens), details


def stage(rows: list[dict], sources: dict[str, str],
          codes: dict[str, int], tokens: dict[str, bytes],
          limit: int = 650, width: int = 26):
    if not 1 <= limit <= 1000:
        raise ValueError("invalid batch limit")
    if any(tokens.get(k) != b for k, b in VARIABLE_BYTES.items()):
        raise ValueError("unverified GBA runtime variable byte")
    accepted = []
    rejected = Counter()
    seen = set()
    priorities = [
        "data/maps/LittlerootTown/", "data/maps/Route101/",
        "data/maps/OldaleTown/", "data/maps/Route102/",
        "data/maps/PetalburgCity/", "data/maps/RustboroCity/",
    ]
    for row in prioritized_rows(rows, priorities):
        if len(accepted) >= limit:
            break
        file = row.get("source_file", "")
        label = row.get("source_label", "")
        english = row.get("english", "")
        authored = row.get("vietnamese", "")
        if (row.get("category") != "map-story"
                or not file.startswith("data/maps/")
                or not file.endswith(".inc") or not label
                or not english or not authored or authored == english
                or "{" not in english):
            continue
        owner = (file, label)
        if owner in seen:
            raise ValueError(f"duplicate dynamic source owner {owner}")
        seen.add(owner)
        if file not in sources:
            rejected["source file absent"] += 1
            continue
        try:
            rendered, encoded, proof = compile_line_repaired_page(
                english, authored, codes, tokens, width)
            changed = patch_labeled_block(
                sources[file], label, english, encoded)
        except ValueError as err:
            rejected[str(err)] += 1
            continue
        sources[file] = changed
        accepted.append({
            "source_file": file,
            "label": label,
            "english": english,
            "authored_vietnamese": authored,
            "vietnamese": rendered,
            "pages": proof,
            "source_page_count": english.count(r"\p") + 1,
            "authored_page_count": len(proof),
            "page_words_and_engine_variable_sequence_preserved": True,
            "original_variable_line_static_budget_preserved": True,
            "dynamic_runtime_expansion_width_guessed": False,
            "encoded_bytes": len(encoded),
        })
    return sources, accepted, dict(rejected)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--codebook", type=Path, required=True)
    ap.add_argument("--exclude-report", type=Path, action="append", required=True)
    ap.add_argument("--limit", type=int, default=650)
    ap.add_argument("--width", type=int, default=26)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = a.workspace.resolve()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    previous = [
        json.loads(ref.read_text(encoding="utf-8"))
        for ref in a.exclude_report
    ]
    plan, excluded = exclude_exact_source_owners(plan, previous)
    _, tokens = parse_charmap(root / "charmap.txt")
    verify_engine(
        (root / "charmap.txt").read_text(encoding="utf-8"),
        (root / "src/strings.c").read_text(encoding="utf-8"))
    book = json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    codes = {ch: int(val, 16) for ch, val in book.items()}
    files = {
        row.get("source_file") for row in plan
        if row.get("category") == "map-story"
        and row.get("source_file", "").startswith("data/maps/")
        and row.get("source_file", "").endswith(".inc")
        and "{" in row.get("english", "")
    }
    sources = {}
    for relative in sorted(files):
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("unsafe source path")
        if path.is_file():
            sources[relative] = path.read_text(encoding="utf-8")
    original = dict(sources)
    updated, accepted, skipped = stage(
        plan, sources, codes, tokens, a.limit, a.width)
    if a.apply:
        for name, content in updated.items():
            if original[name] != content:
                (root / name).write_text(content, encoding="utf-8")
    report = {
        "category": "map-story",
        "mode": "apply" if a.apply else "dry-run",
        "selection": "page_local_line_repair_with_original_variable_static_budget",
        "labels_staged": len(accepted),
        "previously_compiled_map_owner_exclusions": excluded,
        "source_files_staged": sum(
            original[k] != updated[k] for k in original),
        "page_count_and_authored_words_preserved": True,
        "source_variable_placement_budget_preserved": True,
        "unknown_dynamic_runtime_width_assumed": False,
        "raw_ROM_pointer_writes": 0,
        "font_art_replaced": False,
        "emulator_QA": False,
        "release_ready": False,
        "skipped_reasons": skipped,
        "translated": accepted,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps(
        {k: v for k, v in report.items() if k != "translated"},
        ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
