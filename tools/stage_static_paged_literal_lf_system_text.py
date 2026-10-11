#!/usr/bin/env python3
"""Integrate system dialogue pages containing authoring-time literal LF.

Only literal-newline repairs that preserve the original English source's
ordered \n/\l/\p controls can be recompiled. The original authored page
boundaries and the words within each page are immutable. Source matching,
glyph encoding and ROM linker symbols fail closed; no guessed pointers,
synthetic glyphs, or font ROM writes.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

from stage_source_map_translations import (
    normalize_authored_linefeeds, patch_labeled_block, prioritized_rows,
)
from stage_static_paged_map_dialogues import compile_paged, page_words
from stage_static_paged_system_text import exclude_source_owners


def stage_paged_lf(
    rows:list[dict], sources:dict[str,str], glyphs:dict[str,int],
    limit:int=300, width:int=26,
) -> tuple[dict[str,str],list[dict],dict]:
    if not 1 <= limit <= 1000 or not 10 <= width <= 30:
        raise ValueError("invalid limit or width")
    applied, skipped = [], Counter()
    seen = set()
    priorities = [
        "data/text/birch_speech.inc", "data/text/pkmn_center_nurse.inc",
        "data/text/trainers.inc", "data/text/cable_club.inc",
    ]
    for r in prioritized_rows(rows, priorities):
        if len(applied) >= limit:
            break
        path=r.get("source_file","")
        label=r.get("source_label","")
        en=r.get("english","")
        vi=r.get("vietnamese","")
        if (r.get("category")!="system-text"
                or not path.startswith("data/text/") or not path.endswith(".inc")
                or not label or not en or not vi or en==vi
                or "\n" not in vi or r"\p" not in en):
            continue
        identity=(path,label)
        if identity in seen:
            raise ValueError(f"duplicate source owner: {identity}")
        seen.add(identity)
        if path not in sources:
            skipped["missing authorized source file"] += 1
            continue
        try:
            if "\r" in vi or "\t" in vi:
                raise ValueError("unapproved literal CR or TAB")
            normalized=normalize_authored_linefeeds(en,vi)
            if normalized!=vi.replace("\n",r"\n"):
                raise ValueError("normalization changed more than literal LF")
            if normalized==en:
                raise ValueError("translation equals English")
            authored=page_words(en,normalized)
            rendered,payload=compile_paged(en,normalized,glyphs,width)
            if page_words(en,rendered)!=authored:
                raise ValueError("page-local word sequence differs")
            if rendered.count(r"\p")!=en.count(r"\p"):
                raise ValueError("page count drift")
            patched=patch_labeled_block(sources[path],label,en,payload)
        except ValueError as error:
            skipped[str(error)] += 1
            continue
        sources[path]=patched
        applied.append({
            "source_file":path,"label":label,"english":en,
            "authored_vietnamese":vi,"normalized_vietnamese":normalized,
            "vietnamese":rendered,"raw_LF_count":vi.count("\n"),
            "authored_page_count":len(authored),
            "page_word_counts":[len(w) for w in authored],
            "source_page_count":en.count(r"\p")+1,
            "source_control_signature_preserved":True,
            "authored_page_words_preserved":True,
            "encoded_bytes":len(payload),
        })
    return sources,applied,dict(skipped)


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--codebook",type=Path,required=True)
    p.add_argument("--exclude-report",type=Path,action="append",required=True)
    p.add_argument("--limit",type=int,default=300)
    p.add_argument("--width",type=int,default=26)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    root=a.workspace.resolve()
    rows=json.loads(a.plan.read_text(encoding="utf-8"))
    previous=[json.loads(f.read_text(encoding="utf-8"))
              for f in a.exclude_report]
    remaining,excluded=exclude_source_owners(rows,previous)
    cb=json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs={char:int(byte,16) for char,byte in cb.items()}
    wanted={
        r.get("source_file") for r in remaining
        if r.get("category")=="system-text"
        and r.get("source_file","").startswith("data/text/")
        and r.get("source_file","").endswith(".inc")
        and "\n" in r.get("vietnamese","")
        and r"\p" in r.get("english","")
    }
    sources={}
    for file in sorted(wanted):
        pth=(root/file).resolve()
        if not pth.is_relative_to(root):
            raise ValueError("source path escapes workspace")
        if pth.is_file():
            sources[file]=pth.read_text(encoding="utf-8")
    original=dict(sources)
    updated,staged,rejected=stage_paged_lf(
        remaining,sources,glyphs,a.limit,a.width)
    if a.apply:
        for filename,txt in updated.items():
            if txt!=original[filename]:
                (root/filename).write_text(txt,encoding="utf-8")
    report={
        "mode":"apply" if a.apply else "dry-run",
        "category":"system-text",
        "selection":"strict_literal_LF_native_control_paged_system",
        "labels_staged":len(staged),
        "previously_compiled_system_owner_exclusions":excluded,
        "files_staged":sum(updated[k]!=original[k] for k in original),
        "source_control_signature_verified":True,
        "all_authored_page_words_preserved":True,
        "raw_ROM_pointer_writes":0,
        "runtime_variables_admitted":False,
        "unapproved_glyphs_admitted":False,
        "v04_donor_font_applied":False,
        "emulator_QA":False,"release_ready":False,
        "skipped_reasons":rejected,"translated":staged,
    }
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                        encoding="utf-8")
    print(json.dumps({key:value for key,value in report.items()
                      if key!="translated"},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
