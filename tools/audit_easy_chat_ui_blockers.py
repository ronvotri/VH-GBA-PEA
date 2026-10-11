#!/usr/bin/env python3
"""Read-only Easy Chat eligibility audit; never invent UI capacity or font art.

Separate authored width, unsupported glyph, and source-ownership blockers
per category. This is diagnostic and does not certify runtime clipping.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from stage_easy_chat_word_groups import FILE_RE, LABEL_RE, compile_word

def audit(rows, glyphs):
    classes = defaultdict(Counter)
    examples = defaultdict(list)
    owners = set()
    for row in rows:
        file, label = row.get("source_file"), row.get("source_label")
        if not isinstance(file, str) or not FILE_RE.fullmatch(file):
            continue
        if not isinstance(label, str) or not LABEL_RE.fullmatch(label):
            continue
        key = (file, label)
        if key in owners:
            raise ValueError(f"duplicate Easy Chat source owner: {key}")
        owners.add(key)
        en, vi = row.get("english"), row.get("vietnamese")
        group = Path(file).stem.replace("easy_chat_group_", "")
        c = classes[group]
        c["candidate_owners"] += 1
        if not isinstance(en, str) or not isinstance(vi, str):
            cause = "malformed_entry"
        elif en == vi or not vi:
            cause = "unchanged_or_empty"
        elif len(vi) > len(en):
            cause = "translated_longer_than_english"
        elif len(vi) > 15:
            cause = "translated_over_15_cells"
        else:
            try:
                compile_word(en, vi, glyphs, 15)
                cause = "eligible_with_current_codebook"
            except ValueError as exc:
                if "missing" in str(exc).lower() or "glyph" in str(exc).lower():
                    cause = "glyph_not_in_experimental_codebook"
                else:
                    cause = "other_encoding_or_layout_blocker"
        c[cause] += 1
        if cause != "eligible_with_current_codebook" and len(examples[cause]) < 10:
            examples[cause].append({
                "file": file, "label": label,
                "english": en, "vietnamese": vi,
                "english_cells": len(en) if isinstance(en, str) else None,
                "vietnamese_cells": len(vi) if isinstance(vi, str) else None,
            })
    totals = Counter()
    for group in classes.values():
        totals.update(group)
    return {
        "mode": "read_only",
        "note": "Length is Unicode character count, not proven pixel width. Do not treat this as emulator or v0.4-font QA.",
        "distinct_easy_chat_owners": len(owners),
        "totals": dict(totals),
        "by_group": {k: dict(v) for k,v in sorted(classes.items())},
        "representative_blockers": dict(examples),
        "source_text_modified": False, "font_art_generated": False,
        "safe_to_expand_UI_width_without_renderer_proof": False,
        "release_ready": False,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan",type=Path,required=True)
    ap.add_argument("--codebook",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    rows=json.loads(a.plan.read_text(encoding="utf-8"))
    book=json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    codes={k:int(v,16) for k,v in book.items()}
    result=audit(rows,codes)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"distinct_easy_chat_owners":result["distinct_easy_chat_owners"],
                      "totals":result["totals"]},ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
