#!/usr/bin/env python3
r"""Source-owned dynamic map/NPC strings: preserve the English variable budget.

Reuses the independently tested static-budget STR_VAR reflow compiler used by
system strings. No guessed STR_VAR expansion width, modified Vietnamese
words, page crossing, raw GBA pointer edits or donor-font modifications.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_birch_dynamic_intro import verify_engine
from stage_safe_system_dynamic_variables import VARIABLE_BYTES
from stage_source_map_translations import patch_labeled_block, prioritized_rows
from stage_static_zero_page_dialogues import exclude_exact_source_owners
from stage_system_dynamic_static_budget_reflow import compile_dynamic


PRIORITY = [
    "data/maps/InsideOfTruck/", "data/maps/LittlerootTown/",
    "data/maps/Route101/", "data/maps/OldaleTown/",
    "data/maps/Route102/", "data/maps/PetalburgCity/",
    "data/maps/RustboroCity/", "data/maps/Route104/",
]


def stage(rows: list[dict], sources: dict[str, str],
          glyphs: dict[str, int], tokens: dict[str, bytes],
          limit: int = 800, width: int = 26) -> tuple[dict, list[dict], dict]:
    if not 1 <= limit <= 1000 or not 12 <= width <= 30:
        raise ValueError("invalid batch limit or display width")
    if any(tokens.get(k) != v for k, v in VARIABLE_BYTES.items()):
        raise ValueError("unpinned GBA variable bytes")
    accepted, rejected, seen = [], Counter(), set()
    for row in prioritized_rows(rows, PRIORITY):
        if len(accepted) >= limit:
            break
        relative = row.get("source_file", "")
        label = row.get("source_label", "")
        english = row.get("english", "")
        vietnamese = row.get("vietnamese", "")
        if (row.get("category") != "map-story"
                or not relative.startswith("data/maps/")
                or not relative.endswith(".inc")
                or not label or not english or not vietnamese
                or english == vietnamese or "{" not in english):
            continue
        owner = relative, label
        if owner in seen:
            raise ValueError(f"duplicate plan map owner: {owner}")
        seen.add(owner)
        if relative not in sources:
            rejected["source map file missing"] += 1
            continue
        try:
            reflowed, payload, pages = compile_dynamic(
                english, vietnamese, glyphs, tokens, width)
            updated = patch_labeled_block(
                sources[relative], label, english, payload)
        except ValueError as err:
            rejected[str(err)] += 1
            continue
        sources[relative] = updated
        accepted.append({
            "source_file": relative,
            "label": label,
            "english": english,
            "authored_vietnamese": vietnamese,
            "vietnamese": reflowed,
            "pages": pages,
            "page_count": len(pages),
            "source_native_page_count": english.count(r"\p") + 1,
            "source_variable_line_static_budget_preserved": True,
            "authored_words_preserved_within_pages": True,
            "unknown_STR_VAR_runtime_width_guessed": False,
            "encoded_bytes": len(payload),
        })
    return sources, accepted, dict(rejected)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--codebook", type=Path, required=True)
    p.add_argument("--exclude-report", type=Path, action="append", required=True)
    p.add_argument("--limit", type=int, default=800)
    p.add_argument("--width", type=int, default=26)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()

    root = a.workspace.resolve()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    previous = [json.loads(path.read_text(encoding="utf-8"))
                for path in a.exclude_report]
    remaining, excluded = exclude_exact_source_owners(plan, previous)
    _, tokens = parse_charmap(root / "charmap.txt")
    verify_engine(
        (root / "charmap.txt").read_text(encoding="utf-8"),
        (root / "src/strings.c").read_text(encoding="utf-8"))
    book = json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs = {character: int(value, 16)
              for character, value in book.items()}
    wanted = {
        row.get("source_file") for row in remaining
        if row.get("category") == "map-story"
        and row.get("source_file", "").startswith("data/maps/")
        and row.get("source_file", "").endswith(".inc")
        and "{" in row.get("english", "")
    }
    sources = {}
    for relative in sorted(wanted):
        file = (root / relative).resolve()
        if not file.is_relative_to(root):
            raise ValueError("map source path escapes workspace")
        if file.is_file():
            sources[relative] = file.read_text(encoding="utf-8")
    before = dict(sources)
    updated, accepted, rejected = stage(
        remaining, sources, glyphs, tokens, a.limit, a.width)
    if a.apply:
        for relative, content in updated.items():
            if content != before[relative]:
                (root / relative).write_text(content, encoding="utf-8")
    result = {
        "mode": "apply" if a.apply else "dry-run",
        "category": "map-story",
        "source_prefix": "data/maps/",
        "selection": "page_local_dynamic_original_static_budget",
        "labels_staged": len(accepted),
        "previously_compiled_map_owner_exclusions": excluded,
        "source_files_staged": sum(
            updated[k] != before[k] for k in before),
        "runtime_variable_bytes_pinned": True,
        "source_line_static_budgets_preserved": True,
        "authored_page_boundaries_and_words_preserved": True,
        "unknown_runtime_width_assumed": False,
        "pointer_writes": 0,
        "font_glyph_art_modified": False,
        "emulator_QA": False,
        "release_ready": False,
        "skipped_reasons": rejected,
        "translated": accepted,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items()
                      if k != "translated"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
