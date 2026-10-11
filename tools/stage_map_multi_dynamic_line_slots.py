#!/usr/bin/env python3
r"""Restore NPC native line controls with multiple variable-bearing source lines.

Accept only page-local, 1:1 original-source/translated *line slot* alignment,
even when \n vs \l byte choices differ. Each corresponding native line retains
the exact ordered runtime variable list, static text surrounding those
variables never exceeds the original English line's static cell budget, and
all original Vietnamese words stay in their original page. No guessed
STR_VAR value widths, pointer edits, synthetic glyphs, or changed v0.4 art.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_birch_dynamic_intro import verify_engine
from stage_safe_system_dynamic_variables import VARIABLE_BYTES, TOKEN, encode
from stage_source_map_translations import patch_labeled_block, prioritized_rows
from stage_static_zero_page_dialogues import exclude_exact_source_owners
from stage_system_dynamic_static_budget_reflow import (
    LAYOUT, text_ok, segment_reflow, plain_wrap,
)

MAX_PAGE_LINES = 12


def compile_aligned_multi_dynamic(en: str, vi: str,
                                  glyphs: dict[str, int],
                                  variables: dict[str, bytes],
                                  width: int = 26) -> tuple[str, bytes, list[dict]]:
    if not 12 <= width <= 30:
        raise ValueError("unsafe native line width")
    text_ok(en)
    text_ok(vi)
    english_pages = en[:-1].split(r"\p")
    vietnamese_pages = vi[:-1].split(r"\p")
    if len(english_pages) != len(vietnamese_pages):
        raise ValueError("authored GBA page boundaries changed")
    if not any(
        sum(bool(TOKEN.findall(line))
            for line in LAYOUT.split(page)) >= 2
        for page in english_pages
    ):
        raise ValueError("not a multi-variable-source-line page")
    complete = []
    proofs = []
    for en_page, vi_page in zip(english_pages, vietnamese_pages):
        for page in (en_page, vi_page):
            if (page.startswith(" ") or page.endswith(" ") or "  " in page
                    or any(term in page for term in
                           (r" \n", r"\n ", r" \l", r"\l "))):
                raise ValueError("ambiguous authored whitespace")
        source_slots = LAYOUT.split(en_page)
        translated_slots = LAYOUT.split(vi_page)
        if len(source_slots) != len(translated_slots):
            raise ValueError("variable line-slot count differs from English")
        original_words = LAYOUT.sub(" ", vi_page).split()
        lines = []
        slot_proofs = []
        dynamic_slot_count = 0
        for eng, translated in zip(source_slots, translated_slots):
            if not eng or not translated:
                raise ValueError("empty original native line")
            en_tokens = TOKEN.findall(eng)
            vi_tokens = TOKEN.findall(translated)
            if en_tokens != vi_tokens:
                raise ValueError("variable identity/order changed in source line slot")
            if en_tokens:
                dynamic_slot_count += 1
                rewritten, contract = segment_reflow(
                    eng, translated, width)
            else:
                if TOKEN.search(translated):
                    raise ValueError("unexpected variable in static line")
                rewritten = plain_wrap(translated.split(), width)
                contract = {
                    "tokens": [], "source_static_budget": 0,
                    "dynamic_static_cells": 0,
                    "segments_rendered": len(rewritten),
                }
            if not rewritten:
                raise ValueError("empty reflow result")
            lines.extend(rewritten)
            slot_proofs.append({
                "source_variables": en_tokens,
                "translated_variables": vi_tokens,
                "source_static_budget": contract["source_static_budget"],
                "compiled_dynamic_static_cells": contract["dynamic_static_cells"],
                "compiled_native_lines": len(rewritten),
            })
        if not lines or len(lines) > MAX_PAGE_LINES:
            raise ValueError("too many GBA scroll lines")
        native_page = lines[0] + "".join(
            (r"\n" if i == 1 else r"\l") + line
            for i, line in enumerate(lines[1:], 1)
        )
        if (LAYOUT.sub(" ", native_page).split() != original_words
                or TOKEN.findall(native_page) != TOKEN.findall(en_page)):
            raise ValueError("page-local authored words or engine variables changed")
        complete.append(native_page)
        proofs.append({
            "source_native_line_slots": len(source_slots),
            "variable_line_slots": dynamic_slot_count,
            "compiled_native_lines": len(lines),
            "authored_word_count": len(original_words),
            "per_source_slot": slot_proofs,
        })
    result = r"\p".join(complete) + "$"
    if result.count(r"\p") != en.count(r"\p"):
        raise ValueError("source page count changed")
    return result, encode(result, glyphs, variables), proofs


def stage(rows: list[dict], sources: dict[str, str],
          glyphs: dict[str, int], variables: dict[str, bytes],
          limit: int = 450, width: int = 26):
    if not 1 <= limit <= 1000:
        raise ValueError("invalid limit")
    if any(variables.get(name) != value
           for name, value in VARIABLE_BYTES.items()):
        raise ValueError("unverified engine dynamic placeholders")
    accepted = []
    skipped = Counter()
    seen = set()
    priority = ["data/maps/LittlerootTown/", "data/maps/Route101/",
                "data/maps/OldaleTown/", "data/maps/Route102/",
                "data/maps/PetalburgCity/", "data/maps/RustboroCity/"]
    for row in prioritized_rows(rows, priority):
        if len(accepted) >= limit:
            break
        relative = row.get("source_file", "")
        label = row.get("source_label", "")
        en = row.get("english", "")
        vi = row.get("vietnamese", "")
        if (row.get("category") != "map-story"
                or not relative.startswith("data/maps/")
                or not relative.endswith(".inc")
                or not label or not en or not vi or en == vi
                or "{" not in en):
            continue
        owner = (relative, label)
        if owner in seen:
            raise ValueError(f"duplicate source owner {owner}")
        seen.add(owner)
        if relative not in sources:
            skipped["missing authorized source map"] += 1
            continue
        try:
            rendered, payload, proof = compile_aligned_multi_dynamic(
                en, vi, glyphs, variables, width)
            changed = patch_labeled_block(
                sources[relative], label, en, payload)
        except ValueError as exc:
            skipped[str(exc)] += 1
            continue
        sources[relative] = changed
        accepted.append({
            "source_file": relative,
            "label": label,
            "english": en,
            "authored_vietnamese": vi,
            "vietnamese": rendered,
            "pages": proof,
            "page_count": len(proof),
            "source_page_count": en.count(r"\p") + 1,
            "each_source_variable_line_slot_preserved": True,
            "authored_words_preserved_within_source_pages": True,
            "dynamic_widths_not_guessed": True,
            "encoded_bytes": len(payload),
        })
    return sources, accepted, dict(skipped)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--codebook", type=Path, required=True)
    ap.add_argument("--exclude-report", type=Path, action="append", required=True)
    ap.add_argument("--limit", type=int, default=450)
    ap.add_argument("--width", type=int, default=26)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = a.workspace.resolve()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    past = [json.loads(ref.read_text(encoding="utf-8"))
            for ref in a.exclude_report]
    remaining, excluded = exclude_exact_source_owners(plan, past)
    _, variables = parse_charmap(root / "charmap.txt")
    verify_engine(
        (root / "charmap.txt").read_text(encoding="utf-8"),
        (root / "src/strings.c").read_text(encoding="utf-8"))
    codebook = json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs = {char: int(code, 16) for char, code in codebook.items()}
    files = {
        row.get("source_file") for row in remaining
        if row.get("category") == "map-story"
        and row.get("source_file", "").startswith("data/maps/")
        and row.get("source_file", "").endswith(".inc")
        and "{" in row.get("english", "")
    }
    sources = {}
    for rel in sorted(files):
        src = (root / rel).resolve()
        if not src.is_relative_to(root):
            raise ValueError("source map file escaped working directory")
        if src.is_file():
            sources[rel] = src.read_text(encoding="utf-8")
    before = dict(sources)
    updated, accepted, skipped = stage(
        remaining, sources, glyphs, variables, a.limit, a.width)
    if a.apply:
        for rel, data in updated.items():
            if data != before[rel]:
                (root / rel).write_text(data, encoding="utf-8")
    report = {
        "mode": "apply" if a.apply else "dry-run",
        "category": "map-story",
        "selection": "aligned_multiple_dynamic_source_line_slots",
        "labels_staged": len(accepted),
        "previously_compiled_map_owner_exclusions": excluded,
        "files_staged": sum(updated[rel] != before[rel] for rel in before),
        "engine_tokens_byte_exact": True,
        "variable_order_per_original_source_line_preserved": True,
        "page_words_and_boundaries_unchanged": True,
        "runtime_dynamic_widths_assumed": False,
        "raw_rom_pointer_writes": 0,
        "approved_v04_font_modified": False,
        "emulator_QA": False, "release_ready": False,
        "skipped_reasons": skipped,
        "translated": accepted,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "translated"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
