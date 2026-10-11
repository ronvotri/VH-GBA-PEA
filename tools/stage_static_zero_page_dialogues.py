#!/usr/bin/env python3
"""Conservative SOURCE-LEVEL integration of static zero-page map dialogues.

This is a special escape from overrestrictive English \n/\l control-signature
matching: both English and authored Vietnamese must have exactly ZERO \p
page breaks, ZERO dynamic tokens and ZERO other escapes. Only the line-wrap
presentation may change. Every Vietnamese word survives byte-exact after
encoding and the original source label/English text is pinned before rewrite.
Never use for menus, dynamic placeholders, battle templates or font glyphs.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from stage_source_map_translations import (
    encode_text, patch_labeled_block, prioritized_rows,
)
from wrap_vietnamese_map_text import auto_wrap_script_text

ESCAPES = re.compile(r"\\(?![nl])")
LAYOUT = re.compile(r"\\[nl]|\n")
SAFE_TOKENS = re.compile(r"\\[nl]")


def zero_page_words(english: str, vietnamese: str) -> list[str]:
    for label, s in (("English", english), ("Vietnamese", vietnamese)):
        if not s.endswith("$") or s.count("$") != 1:
            raise ValueError(f"{label}: not one terminal $")
        if any(c in s for c in ("{", "}", "\r", "\t")):
            raise ValueError(f"{label}: contains dynamic token or control whitespace")
        if r"\p" in s:
            raise ValueError("page-control: not a zero-page dialogue")
        without_safe = SAFE_TOKENS.sub("", s[:-1])
        if "\\" in without_safe:
            raise ValueError(f"{label}: unsupported runtime escape")
        if "\n" in english:
            raise ValueError("English: raw newline not an exact source control")
    raw = vietnamese[:-1]
    if raw.startswith((" ", "\n")) or raw.endswith((" ", "\n")) or "  " in raw:
        raise ValueError("Vietnamese: ambiguous leading/trailing/double whitespace")
    chunks = LAYOUT.split(raw)
    if any(not chunk or chunk.startswith(" ") or chunk.endswith(" ") for chunk in chunks):
        raise ValueError("Vietnamese: empty or spaced line break")
    words = LAYOUT.sub(" ", raw).split(" ")
    if any(not w for w in words):
        raise ValueError("Vietnamese: ambiguous separated spaces")
    if not words:
        raise ValueError("Vietnamese: no display words")
    return words


def compile_zero_page(english: str, vietnamese: str, codes: dict[str, int],
                      width: int = 26) -> tuple[str, bytes]:
    words = zero_page_words(english, vietnamese)
    # Remove only presentation controls. Page breaks and dynamic escapes have
    # already been strictly rejected; hence reflow cannot merge two pages.
    single_line = " ".join(words) + "$"
    compact = auto_wrap_script_text(single_line, width, page_scroll_reflow=True)
    if r"\p" in compact:
        raise ValueError("unexpected automatic pagination")
    after = re.sub(r"\\[nl]", " ", compact[:-1]).split(" ")
    if after != words:
        raise ValueError("authored Vietnamese word order changed")
    payload = encode_text(compact, codes, width)
    if not payload.endswith(b"\xff") or payload.count(b"\xff") != 1:
        raise ValueError("byte terminator changed")
    return compact, payload


def exclude_exact_source_owners(rows: list[dict], reports: list[dict]) -> tuple[list[dict], int]:
    used = set()
    for report in reports:
        accepted = report.get("accepted") if "accepted" in report else report.get("translated")
        if (report.get("mode") != "apply" or not isinstance(accepted, list)
                or len(accepted) != report.get("labels_staged")):
            raise ValueError("unsafe previous-source exclusion report")
        for row in accepted:
            owner = (row.get("source_file") or row.get("file"), row.get("label"))
            if not all(owner) or not owner[0].startswith("data/maps/") or owner in used:
                raise ValueError("duplicate or missing previously compiled map source owner")
            used.add(owner)
    source_owners = {
        (r.get("source_file"), r.get("source_label"))
        for r in rows if r.get("category") == "map-story"
        and r.get("source_file", "").startswith("data/maps/")
    }
    if not used.issubset(source_owners):
        raise ValueError("previous source owner missing from authoritative map plan")
    remaining = [r for r in rows
                 if (r.get("source_file"), r.get("source_label")) not in used]
    return remaining, len(used)


def stage(rows: list[dict], sources: dict[str, str], codes: dict[str, int],
          limit: int = 400, width: int = 26) -> tuple[dict, list[dict], dict]:
    if not 1 <= limit <= 1000 or not 10 <= width <= 30:
        raise ValueError("invalid batch limit or line width")
    accepted = []
    rejects = Counter()
    for row in prioritized_rows(rows, [
        "data/maps/InsideOfTruck/", "data/maps/LittlerootTown/",
        "data/maps/Route101/", "data/maps/OldaleTown/",
        "data/maps/Route102/", "data/maps/PetalburgCity/",
        "data/maps/RustboroCity/",
    ]):
        if len(accepted) >= limit:
            break
        file = row.get("source_file", "")
        en = row.get("english", "")
        vi = row.get("vietnamese", "")
        if row.get("category") != "map-story" or not file.startswith("data/maps/"):
            continue
        if en == vi or not vi or not row.get("source_label"):
            continue
        if file not in sources:
            rejects["missing authorized source file"] += 1
            continue
        try:
            compact, payload = compile_zero_page(en, vi, codes, width)
            changed = patch_labeled_block(sources[file], row["source_label"], en, payload)
        except ValueError as error:
            rejects[str(error)] += 1
            continue
        sources[file] = changed
        accepted.append({
            "source_file": file,
            "label": row["source_label"],
            "english": en,
            "authored_vietnamese": vi,
            "vietnamese": compact,
            "encoded_bytes": len(payload),
            "source_page_breaks": 0,
            "authored_page_breaks": 0,
            "word_count": len(zero_page_words(en, vi)),
            "source_line_layout_changed": compact != vi,
        })
    return sources, accepted, dict(rejects)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--codebook", type=Path, required=True)
    p.add_argument("--exclude-report", type=Path, action="append", required=True)
    p.add_argument("--limit", type=int, default=400)
    p.add_argument("--width", type=int, default=26)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    root = args.workspace.resolve()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    reports = [json.loads(x.read_text(encoding="utf-8")) for x in args.exclude_report]
    rows, excluded = exclude_exact_source_owners(plan, reports)
    codebook = json.loads(args.codebook.read_text(encoding="utf-8"))
    codes = {ch: int(value, 16) for ch, value in codebook["glyph_bytes"].items()}
    files = {r["source_file"] for r in rows
             if r.get("category") == "map-story"
             and r.get("source_file", "").startswith("data/maps/")}
    sources = {}
    for file in sorted(files):
        path = (root / file).resolve()
        if not path.is_relative_to(root):
            raise ValueError("unsafe source file outside workspace")
        if path.is_file():
            sources[file] = path.read_text(encoding="utf-8")
    original = dict(sources)
    updated, translated, skipped = stage(rows, sources, codes, args.limit, args.width)
    if args.apply:
        for name, source in updated.items():
            if source != original[name]:
                (root / name).write_text(source, encoding="utf-8")
    report = {
        "mode": "apply" if args.apply else "dry-run",
        "category": "map-story",
        "source_prefix": "data/maps/",
        "selection": "static_zero_page_source_linker_layout_reflow",
        "labels_staged": len(translated),
        "previously_compiled_map_owner_exclusions": excluded,
        "files_staged": sum(updated[name] != original[name] for name in original),
        "authored_layout_reflowed": sum(r["source_line_layout_changed"] for r in translated),
        "all_source_pages_preserved": True,
        "dynamic_placeholders_admitted": False,
        "unknown_controls_admitted": False,
        "new_ROM_pointer_writes": 0,
        "verified_emulator_rendering": False,
        "release_ready": False,
        "skipped_reasons": skipped,
        "translated": translated,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "translated"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
