#!/usr/bin/env python3
"""Stage previously-unintegrated, static, source-owned paginated NPC/map text.

This stage is opt-in and fail-closed. It accepts a translation only if both
English source and Vietnamese translation have the SAME number of literal
GBA \p page breaks. It preserves every Vietnamese word INSIDE its authored
page; only non-semantic \n/\l window layout may be reflowed by the standard
engine scrolling rules. Dynamic tokens and unapproved escapes are refused.
No direct GBA ROM edits, pointer guesses, or font edits occur.
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
from stage_static_zero_page_dialogues import (
    exclude_exact_source_owners, zero_page_words,
)
from wrap_vietnamese_map_text import auto_wrap_script_text

DISPLAY_CONTROLS = re.compile(r"\\[nl]")


def page_words(english: str, vietnamese: str) -> list[list[str]]:
    for label, value in (("English", english), ("Vietnamese", vietnamese)):
        if not value.endswith("$") or value.count("$") != 1:
            raise ValueError(f"{label}: exactly one terminal $ required")
    english_pages = english[:-1].split(r"\p")
    vi_pages = vietnamese[:-1].split(r"\p")
    if len(english_pages) < 2:
        raise ValueError("English: not a paginated dialogue")
    if len(english_pages) != len(vi_pages):
        raise ValueError("source/authored page-count drift")
    if any(not en or not vi for en, vi in zip(english_pages, vi_pages)):
        raise ValueError("empty source/authored page")
    return [zero_page_words(en+"$", vi+"$")
            for en,vi in zip(english_pages, vi_pages)]


def compile_paged(english: str, vietnamese: str,
                  glyphs: dict[str,int], width: int = 26) -> tuple[str, bytes]:
    pages = page_words(english, vietnamese)
    output = []
    for words in pages:
        # Process separately: NEVER pull words across a page boundary.
        page = auto_wrap_script_text(
            " ".join(words)+"$", width, page_scroll_reflow=True)
        actual = DISPLAY_CONTROLS.sub(" ", page[:-1]).split()
        if actual != words:
            raise ValueError("Vietnamese words drifted inside page")
        output.append(page[:-1])
    compiled = r"\p".join(output)+"$"
    if page_words(english, compiled) != pages:
        raise ValueError("Vietnamese authored page sequence changed")
    if compiled.count(r"\p") != english.count(r"\p"):
        raise ValueError("English pagination changed")
    return compiled,encode_text(compiled,glyphs,width)


def stage(rows:list[dict],sources:dict[str,str],glyphs:dict[str,int],
          limit:int=750,width:int=26):
    if not 1<=limit<=1000 or not 10<=width<=30:
        raise ValueError("invalid batch limit or width")
    accepted=[]; rejected=Counter()
    priority=[
        "data/maps/InsideOfTruck/","data/maps/LittlerootTown/",
        "data/maps/Route101/","data/maps/OldaleTown/",
        "data/maps/Route102/","data/maps/PetalburgCity/",
        "data/maps/RustboroCity/",
    ]
    for row in prioritized_rows(rows,priority):
        if len(accepted)>=limit:
            break
        file=row.get("source_file","")
        label=row.get("source_label","")
        en=row.get("english","")
        vi=row.get("vietnamese","")
        if (row.get("category")!="map-story" or
            not file.startswith("data/maps/") or
            not label or not en or not vi or en==vi):
            continue
        if file not in sources:
            rejected["missing authorized source file"]+=1
            continue
        try:
            compiled,payload=compile_paged(en,vi,glyphs,width)
            new_source=patch_labeled_block(sources[file],label,en,payload)
        except ValueError as exc:
            rejected[str(exc)]+=1
            continue
        sources[file]=new_source
        pages=page_words(en,vi)
        accepted.append({
            "source_file":file,"label":label,"english":en,
            "authored_vietnamese":vi,"vietnamese":compiled,
            "encoded_bytes":len(payload),"page_count":len(pages),
            "page_word_counts":[len(words) for words in pages],
            "authored_page_count_preserved":True,
            "authored_page_word_order_preserved":True,
            "source_layout_changed":compiled!=vi,
        })
    return sources,accepted,dict(rejected)


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--codebook",type=Path,required=True)
    p.add_argument("--exclude-report",type=Path,action="append",required=True)
    p.add_argument("--limit",type=int,default=750)
    p.add_argument("--width",type=int,default=26)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    root=a.workspace.resolve()
    plan=json.loads(a.plan.read_text(encoding="utf-8"))
    previous=[json.loads(path.read_text(encoding="utf-8")) for path in a.exclude_report]
    remaining,excluded=exclude_exact_source_owners(plan,previous)
    raw=json.loads(a.codebook.read_text(encoding="utf-8"))
    glyphs={ch:int(value,16) for ch,value in raw["glyph_bytes"].items()}
    relevant={row.get("source_file") for row in remaining
              if row.get("category")=="map-story"
              and row.get("source_file","").startswith("data/maps/")}
    sources={}
    for file in sorted(relevant):
        path=(root/file).resolve()
        if not path.is_relative_to(root):
            raise ValueError("unsafe map file outside source")
        if path.is_file():
            sources[file]=path.read_text(encoding="utf-8")
    original=dict(sources)
    updated,accepted,skipped=stage(remaining,sources,glyphs,a.limit,a.width)
    if a.apply:
        for file in updated:
            if updated[file]!=original[file]:
                (root/file).write_text(updated[file],encoding="utf-8")
    report={
        "mode":"apply" if a.apply else "dry-run",
        "category":"map-story",
        "source_prefix":"data/maps/",
        "selection":"strict_authored_multi_page_word_and_page_preserving",
        "labels_staged":len(accepted),
        "previously_compiled_map_owner_exclusions":excluded,
        "files_staged":sum(updated[x]!=original[x] for x in original),
        "total_new_authored_pages":sum(x["page_count"] for x in accepted),
        "new_labels_with_layout_reflow":sum(x["source_layout_changed"] for x in accepted),
        "page_count_and_words_preserved":True,
        "unknown_controls_or_dynamic_allowed":False,
        "pointer_writes":0,
        "font_or_emulator_approved":False,
        "release_ready":False,
        "skipped_reasons":skipped,
        "translated":accepted,
    }
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="translated"},
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
