#!/usr/bin/env python3
"""Add only source-owned static, zero-page system dialogues.

Existing system source reports are exclusions; the original English owner
and exact .string bytes must match before any source rewrite. The tool never
writes raw ROM offsets, graphics, fonts, or unverified pointers.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from stage_source_map_translations import patch_labeled_block, prioritized_rows
from stage_static_paged_system_text import exclude_source_owners
from stage_static_zero_page_dialogues import compile_zero_page, zero_page_words


def stage_system_zero_page(
    rows: list[dict], sources: dict[str, str], glyphs: dict[str, int],
    limit: int = 750, width: int = 26,
) -> tuple[dict[str, str], list[dict], dict]:
    if not 1 <= limit <= 1000 or not 10 <= width <= 30:
        raise ValueError("invalid batch limit or line width")
    accepted = []
    rejected = Counter()
    attempted = set()
    priorities = [
        "data/text/birch_speech.inc", "data/text/pkmn_center_nurse.inc",
        "data/text/trainers.inc", "data/text/cable_club.inc",
        "data/text/berries.inc",
    ]
    for row in prioritized_rows(rows, priorities):
        if len(accepted) >= limit:
            break
        path = row.get("source_file", "")
        label = row.get("source_label", "")
        en = row.get("english", "")
        vi = row.get("vietnamese", "")
        if (row.get("category") != "system-text"
                or not path.startswith("data/text/")
                or not path.endswith(".inc")
                or not label or not en or not vi or en == vi):
            continue
        owner = (path, label)
        if owner in attempted:
            raise ValueError(f"duplicated system manifest owner: {owner}")
        attempted.add(owner)
        if path not in sources:
            rejected["missing authorized source file"] += 1
            continue
        try:
            rendered, payload = compile_zero_page(en, vi, glyphs, width)
            updated = patch_labeled_block(sources[path], label, en, payload)
        except ValueError as error:
            rejected[str(error)] += 1
            continue
        sources[path] = updated
        accepted.append({
            "source_file": path, "label": label, "english": en,
            "authored_vietnamese": vi, "vietnamese": rendered,
            "encoded_bytes": len(payload),
            "word_count": len(zero_page_words(en, vi)),
            "source_page_breaks": 0, "authored_page_breaks": 0,
            "source_layout_changed": rendered != vi,
        })
    return sources, accepted, dict(rejected)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--codebook", type=Path, required=True)
    parser.add_argument("--exclude-report", type=Path, action="append", required=True)
    parser.add_argument("--limit", type=int, default=750)
    parser.add_argument("--width", type=int, default=26)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    previous = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in args.exclude_report
    ]
    remaining, excluded = exclude_source_owners(plan, previous)
    codebook = json.loads(args.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs = {letter: int(value, 16) for letter, value in codebook.items()}
    files = {
        r.get("source_file") for r in remaining
        if r.get("category") == "system-text"
        and r.get("source_file", "").startswith("data/text/")
        and r.get("source_file", "").endswith(".inc")
    }
    sources = {}
    for name in sorted(files):
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise ValueError("system source path escapes workspace")
        if path.is_file():
            sources[name] = path.read_text(encoding="utf-8")
    before = dict(sources)
    updated, accepted, rejected = stage_system_zero_page(
        remaining, sources, glyphs, args.limit, args.width
    )
    if args.apply:
        for name, value in updated.items():
            if value != before[name]:
                (root / name).write_text(value, encoding="utf-8")
    report = {
        "mode": "apply" if args.apply else "dry-run",
        "category": "system-text",
        "selection": "source_exact_static_zero_page_system_text",
        "labels_staged": len(accepted),
        "previously_compiled_system_owner_exclusions": excluded,
        "files_staged": sum(updated[name] != before[name] for name in before),
        "authored_words_preserved": True,
        "page_breaks_added": 0,
        "runtime_variables_admitted": False,
        "unsupported_controls_admitted": False,
        "raw_ROM_pointer_writes": 0,
        "approved_v04_font_applied": False,
        "emulator_verified": False,
        "release_ready": False,
        "skipped_reasons": rejected,
        "translated": accepted,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(
        {key: value for key, value in report.items() if key != "translated"},
        ensure_ascii=False, indent=2
    ))


if __name__ == "__main__":
    main()
