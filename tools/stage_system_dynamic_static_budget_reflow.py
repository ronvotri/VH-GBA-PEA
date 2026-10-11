#!/usr/bin/env python3
r"""Reflow source-owned system STR_VAR lines without guessing variable width.

Each translated variable-bearing line retains the original English variable
sequence and never exceeds that same line's original *static* display cells.
Extra translated words go to separate native \n/\l scroll lines within the
same \p page. Variable value lengths are NEVER guessed or claimed bounded.
No page boundaries, Vietnamese words, source pointers or fonts are changed.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_birch_dynamic_intro import verify_engine
from stage_safe_system_dynamic_variables import VARIABLE_BYTES, TOKEN, encode
from stage_source_map_translations import prioritized_rows, patch_labeled_block
from stage_static_paged_system_text import exclude_source_owners

LAYOUT = re.compile(r"\\[nl]")
ALL_CONTROLS = re.compile(r"\\[npl]")
MAX_LINES_PER_PAGE = 12


def text_ok(text: str) -> None:
    if (not text.endswith("$") or text.count("$") != 1
            or unicodedata.normalize("NFC", text) != text
            or any(ch in text for ch in "\n\r\t")):
        raise ValueError("malformed native text or Unicode")
    remainder = TOKEN.sub("", ALL_CONTROLS.sub("", text[:-1]))
    if any(ch in remainder for ch in "{}\\"):
        raise ValueError("unsupported source control or malformed variable")


def plain_wrap(words: list[str], width: int) -> list[str]:
    lines = []
    current = ""
    for word in words:
        if len(word) > width:
            raise ValueError("unbreakable static word exceeds width")
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def static_len(text: str) -> int:
    return len(TOKEN.sub("", text))


def segment_reflow(english: str, vietnamese: str, width: int = 26) -> tuple[list[str], dict]:
    if not english or not vietnamese:
        raise ValueError("empty source/native line")
    if (vietnamese.startswith(" ") or vietnamese.endswith(" ")
            or "  " in vietnamese):
        raise ValueError("ambiguous translated whitespace")
    en_tokens = TOKEN.findall(english)
    vi_tokens = TOKEN.findall(vietnamese)
    if en_tokens != vi_tokens:
        raise ValueError("dynamic variable identity/order drift within native line")
    if any(token not in VARIABLE_BYTES for token in en_tokens):
        raise ValueError("unverified source dynamic variable")
    words = vietnamese.split(" ")
    if any(not word for word in words):
        raise ValueError("empty word introduced")
    if not en_tokens:
        lines = plain_wrap(words, width)
        return lines, {
            "tokens": [], "source_static_budget": min(width, len(english)),
            "dynamic_static_cells": 0, "segments_rendered": len(lines),
        }
    positions = [i for i, word in enumerate(words) if TOKEN.search(word)]
    if not positions:
        raise ValueError("missing original dynamic variable")
    first, last = positions[0], positions[-1]
    left = words[:first]
    core = words[first:last + 1]
    right = words[last + 1:]
    budget = min(width, static_len(english))
    dynamic = " ".join(core)
    if static_len(dynamic) > budget:
        raise ValueError("dynamic core cannot fit original English static budget")
    # Known names may render at <=7 cells, but STR_VAR substitutions are not
    # guaranteed bounded: never rely on a guessed variable length.
    while left:
        trial = left[-1] + " " + dynamic
        if static_len(trial) > budget:
            break
        dynamic = trial
        left.pop()
    while right:
        trial = dynamic + " " + right[0]
        if static_len(trial) > budget:
            break
        dynamic = trial
        right.pop(0)
    lines = plain_wrap(left, width) + [dynamic] + plain_wrap(right, width)
    if TOKEN.findall(dynamic) != en_tokens or static_len(dynamic) > budget:
        raise ValueError("variable line exceeds source static budget")
    if " ".join(lines).split() != words:
        raise ValueError("authored Vietnamese words reordered or missing")
    continuations = plain_wrap(left, width) + plain_wrap(right, width)
    if any("{" in line or "}" in line for line in continuations):
        raise ValueError("variable leaked to static continuation")
    return lines, {
        "tokens": en_tokens, "source_static_budget": budget,
        "dynamic_static_cells": static_len(dynamic),
        "segments_rendered": len(lines),
    }


def compile_dynamic(en: str, vi: str, glyphs: dict[str, int],
                    tokens: dict[str, bytes], width: int = 26) -> tuple[str, bytes, list[dict]]:
    if not 12 <= width <= 30:
        raise ValueError("unsafe display width")
    text_ok(en)
    text_ok(vi)
    en_pages = en[:-1].split(r"\p")
    vi_pages = vi[:-1].split(r"\p")
    if len(en_pages) != len(vi_pages):
        raise ValueError("GBA page boundaries changed")
    rendered_pages = []
    details = []
    dynamic_found = False
    for en_page, vi_page in zip(en_pages, vi_pages):
        if LAYOUT.findall(en_page) != LAYOUT.findall(vi_page):
            raise ValueError("native line control signature changed")
        en_segments = LAYOUT.split(en_page)
        vi_segments = LAYOUT.split(vi_page)
        if len(en_segments) != len(vi_segments):
            raise ValueError("original native line count changed")
        per_page = []
        per_segment = []
        for english_segment, translated_segment in zip(en_segments, vi_segments):
            lines, proof = segment_reflow(english_segment, translated_segment, width)
            dynamic_found = dynamic_found or bool(proof["tokens"])
            per_page.extend(lines)
            per_segment.append(proof)
        if not per_page or len(per_page) > MAX_LINES_PER_PAGE:
            raise ValueError("too many native scroll lines or empty page")
        compiled_page = per_page[0] + "".join(
            (r"\n" if i == 1 else r"\l") + line
            for i, line in enumerate(per_page[1:], 1))
        def words(text: str) -> list[str]:
            return LAYOUT.sub(" ", text).split()
        if words(compiled_page) != words(vi_page):
            raise ValueError("source page's Vietnamese words changed")
        if TOKEN.findall(compiled_page) != TOKEN.findall(en_page):
            raise ValueError("source page's runtime variables reordered")
        rendered_pages.append(compiled_page)
        details.append({
            "source_native_segments": len(en_segments),
            "result_scroll_lines": len(per_page),
            "per_segment_static_budgets": per_segment,
            "page_word_count": len(words(vi_page)),
        })
    if not dynamic_found:
        raise ValueError("not a dynamic system dialogue")
    compiled = r"\p".join(rendered_pages) + "$"
    if compiled.count(r"\p") != en.count(r"\p"):
        raise ValueError("native page count drifted")
    payload = encode(compiled, glyphs, tokens)
    return compiled, payload, details


def stage(rows: list[dict], sources: dict[str, str], glyphs: dict[str, int],
          tokens: dict[str, bytes], limit: int = 900, width: int = 26):
    if not 1 <= limit <= 1000:
        raise ValueError("invalid batch limit")
    if any(tokens.get(k) != v for k, v in VARIABLE_BYTES.items()):
        raise ValueError("source charmap dynamic bytes are not pinned")
    accepted = []
    skipped = Counter()
    seen = set()
    for row in prioritized_rows(rows, [
        "data/text/birch_speech.inc", "data/text/pkmn_center_nurse.inc",
        "data/text/trainers.inc", "data/text/match_call.inc",
    ]):
        if len(accepted) >= limit:
            break
        file = row.get("source_file", "")
        label = row.get("source_label", "")
        english = row.get("english", "")
        vi = row.get("vietnamese", "")
        if (row.get("category") != "system-text"
                or not file.startswith("data/text/") or not file.endswith(".inc")
                or not label or not english or not vi or english == vi
                or "{" not in english):
            continue
        owner = (file, label)
        if owner in seen:
            raise ValueError(f"duplicate source manifest owner {owner}")
        seen.add(owner)
        if file not in sources:
            skipped["source file not present"] += 1
            continue
        try:
            rendered, payload, proof = compile_dynamic(english, vi, glyphs, tokens, width)
            changed = patch_labeled_block(sources[file], label, english, payload)
        except ValueError as error:
            skipped[str(error)] += 1
            continue
        sources[file] = changed
        accepted.append({
            "source_file": file, "label": label, "english": english,
            "authored_vietnamese": vi, "vietnamese": rendered,
            "pages": proof, "page_count": len(proof),
            "source_native_page_count": english.count(r"\p") + 1,
            "static_variable_line_never_exceeds_english": True,
            "native_page_words_preserved": True,
            "encoded_bytes": len(payload),
        })
    return sources, accepted, dict(skipped)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--codebook", type=Path, required=True)
    p.add_argument("--exclude-report", type=Path, action="append", required=True)
    p.add_argument("--limit", type=int, default=900)
    p.add_argument("--width", type=int, default=26)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    root = a.workspace.resolve()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    reports = [json.loads(path.read_text(encoding="utf-8"))
               for path in a.exclude_report]
    rows, excluded = exclude_source_owners(plan, reports)
    _, tokens = parse_charmap(root / "charmap.txt")
    verify_engine(
        (root / "charmap.txt").read_text(encoding="utf-8"),
        (root / "src/strings.c").read_text(encoding="utf-8"))
    book = json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs = {k: int(v, 16) for k, v in book.items()}
    wanted = {
        row.get("source_file") for row in rows
        if row.get("category") == "system-text"
        and row.get("source_file", "").startswith("data/text/")
        and row.get("source_file", "").endswith(".inc")
        and "{" in row.get("english", "")
    }
    sources = {}
    for file in sorted(wanted):
        path = (root / file).resolve()
        if not path.is_relative_to(root):
            raise ValueError("source path outside workspace")
        if path.is_file():
            sources[file] = path.read_text(encoding="utf-8")
    before = dict(sources)
    output, accepted, skipped = stage(rows, sources, glyphs, tokens, a.limit, a.width)
    if a.apply:
        for file, value in output.items():
            if value != before[file]:
                (root / file).write_text(value, encoding="utf-8")
    report = {
        "mode": "apply" if a.apply else "dry-run",
        "category": "system-text",
        "selection": "preserve_original_VAR_static_cell_budget_within_pages",
        "labels_staged": len(accepted),
        "previously_compiled_system_owner_exclusions": excluded,
        "files_staged": sum(output[x] != before[x] for x in before),
        "engine_variable_bytes_verified": True,
        "all_dynamic_source_line_static_budgets_preserved": True,
        "all_authored_page_words_and_variable_order_preserved": True,
        "runtime_STR_VAR_display_width_assumed": False,
        "raw_ROM_pointer_writes": 0, "font_art_modified": False,
        "emulator_QA": False, "release_ready": False,
        "skipped_reasons": skipped, "translated": accepted,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps(
        {k: v for k, v in report.items() if k != "translated"},
        ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
