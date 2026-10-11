#!/usr/bin/env python3
"""Stage source-owned system text with safely normalizable literal LF.

A literal LF in the Vietnamese manifest is converted to the GBA \n control
only when the *entire ordered* native English \n/\l/\p signature already
agrees. No dynamic variable, arbitrary control, source symbol or font edit.
The local page's authored Vietnamese words remain byte-exact in Unicode.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from stage_source_map_translations import (
    normalize_authored_linefeeds, patch_labeled_block, prioritized_rows,
)
from stage_static_paged_system_text import exclude_source_owners
from stage_static_zero_page_dialogues import compile_zero_page, zero_page_words


def stage_literal_lf(
    rows: list[dict], sources: dict[str, str], glyphs: dict[str, int],
    limit: int = 500, width: int = 26,
) -> tuple[dict[str, str], list[dict], dict]:
    if not 1 <= limit <= 1000 or not 10 <= width <= 30:
        raise ValueError("invalid batch limit or width")
    done, skipped = [], Counter()
    owners = set()
    for row in prioritized_rows(rows, [
        "data/text/birch_speech.inc", "data/text/pkmn_center_nurse.inc",
        "data/text/trainers.inc", "data/text/cable_club.inc",
    ]):
        if len(done) >= limit:
            break
        file = row.get("source_file", "")
        label = row.get("source_label", "")
        en = row.get("english", "")
        vi = row.get("vietnamese", "")
        if (row.get("category") != "system-text"
                or not file.startswith("data/text/")
                or not file.endswith(".inc")
                or not label or not en or not vi or en == vi
                or "\n" not in vi):
            continue
        owner = (file, label)
        if owner in owners:
            raise ValueError(f"duplicated source manifest owner: {owner}")
        owners.add(owner)
        if file not in sources:
            skipped["missing authorized source file"] += 1
            continue
        try:
            if "\r" in vi or "\t" in vi:
                raise ValueError("control whitespace not limited to literal LF")
            normalized = normalize_authored_linefeeds(en, vi)
            if normalized != vi.replace("\n", r"\n"):
                raise ValueError("unexpected newline normalization")
            if normalized == en:
                raise ValueError("normalization equals English source")
            # No page or dynamic tokens may pass through this static mode.
            original_words = vi[:-1].replace("\n", " ").replace(r"\n", " ")
            if ("{" in original_words or "}" in original_words
                    or r"\p" in normalized):
                raise ValueError("dynamic variable or page control disallowed")
            rendered, payload = compile_zero_page(en, normalized, glyphs, width)
            wordlist = zero_page_words(en, normalized)
            if zero_page_words(en, rendered) != wordlist:
                raise ValueError("Vietnamese word drift after wrapping")
            updated = patch_labeled_block(sources[file], label, en, payload)
        except ValueError as err:
            skipped[str(err)] += 1
            continue
        sources[file] = updated
        done.append({
            "source_file": file, "label": label, "english": en,
            "authored_vietnamese": vi,
            "normalized_vietnamese": normalized,
            "vietnamese": rendered,
            "literal_LF_count": vi.count("\n"),
            "source_page_breaks": 0, "authored_page_breaks": 0,
            "word_count": len(wordlist), "encoded_bytes": len(payload),
            "authored_words_preserved": True,
            "native_control_signature_preserved": True,
        })
    return sources, done, dict(skipped)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--codebook", type=Path, required=True)
    p.add_argument("--exclude-report", type=Path, action="append", required=True)
    p.add_argument("--limit", type=int, default=500)
    p.add_argument("--width", type=int, default=26)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    root = a.workspace.resolve()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    previous = [json.loads(f.read_text(encoding="utf-8"))
                for f in a.exclude_report]
    remaining, prior = exclude_source_owners(plan, previous)
    book = json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs = {ch: int(code, 16) for ch, code in book.items()}
    files = {
        row["source_file"] for row in remaining
        if row.get("category") == "system-text"
        and row.get("source_file", "").startswith("data/text/")
        and row.get("source_file", "").endswith(".inc")
        and "\n" in row.get("vietnamese", "")
    }
    sources = {}
    for file in sorted(files):
        path = (root / file).resolve()
        if not path.is_relative_to(root):
            raise ValueError("source file outside workspace")
        if path.is_file():
            sources[file] = path.read_text(encoding="utf-8")
    originals = dict(sources)
    output, rows, skipped = stage_literal_lf(
        remaining, sources, glyphs, a.limit, a.width
    )
    if a.apply:
        for file, data in output.items():
            if data != originals[file]:
                (root / file).write_text(data, encoding="utf-8")
    record = {
        "mode": "apply" if a.apply else "dry-run",
        "category": "system-text",
        "selection": "strict_native_signature_literal_lf_zero_page",
        "labels_staged": len(rows),
        "previously_compiled_system_owner_exclusions": prior,
        "files_staged": sum(output[name] != originals[name] for name in originals),
        "raw_LF_normalized": sum(r["literal_LF_count"] for r in rows),
        "source_control_signature_verified": True,
        "page_breaks_added": 0, "runtime_variables_admitted": False,
        "raw_ROM_pointer_writes": 0, "approved_v04_font_applied": False,
        "emulator_verified": False, "release_ready": False,
        "skipped_reasons": skipped, "translated": rows,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({key: value for key, value in record.items()
                      if key != "translated"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
