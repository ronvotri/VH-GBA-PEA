#!/usr/bin/env python3
"""Conservative page-preserving source integration for data/text/*.inc.

Reuses the tested map paginated page-words encoder. It does NOT admit
runtime placeholders, non-ASCII-encoded missing glyphs, or any unsupported
control. Source English strings and individual owner labels must match.
Neither direct ROM pointer edits nor font pixel changes are performed.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from stage_source_map_translations import patch_labeled_block, prioritized_rows
from stage_static_paged_map_dialogues import compile_paged, page_words


def exclude_source_owners(rows: list[dict], reports: list[dict]) -> tuple[list[dict],int]:
    owners = set()
    plan_owners = {(r.get("source_file"), r.get("source_label"))
                   for r in rows if r.get("category")=="system-text"
                   and r.get("source_file","").startswith("data/text/")}
    for report in reports:
        translated = report.get("translated")
        if (report.get("mode")!="apply" or not isinstance(translated,list)
                or report.get("labels_staged")!=len(translated)):
            raise ValueError("invalid earlier system source report")
        for r in translated:
            identity=(r.get("source_file"),r.get("label"))
            if (not identity[0] or not identity[1]
                    or not identity[0].startswith("data/text/")
                    or identity in owners):
                raise ValueError("duplicate/missing prior system owner")
            owners.add(identity)
    if not owners.issubset(plan_owners):
        raise ValueError("previous system source owner missing from manifest")
    return [r for r in rows
            if (r.get("source_file"),r.get("source_label")) not in owners],len(owners)


def stage_system_pages(rows:list[dict],sources:dict[str,str],
                       glyphs:dict[str,int],limit:int=500,width:int=26):
    if not 1<=limit<=1000 or not 10<=width<=30:
        raise ValueError("invalid batch limit or width")
    accepted=[];skipped=Counter()
    priorities=["data/text/birch_speech.inc",
                "data/text/pkmn_center_nurse.inc",
                "data/text/trainers.inc",
                "data/text/cable_club.inc",
                "data/text/berries.inc"]
    for row in prioritized_rows(rows,priorities):
        if len(accepted)>=limit:
            break
        path=row.get("source_file","")
        en=row.get("english","")
        vi=row.get("vietnamese","")
        label=row.get("source_label","")
        if (row.get("category")!="system-text"
                or not path.startswith("data/text/")
                or not path.endswith(".inc")
                or not en or not vi or en==vi or not label):
            continue
        if path not in sources:
            skipped["missing authorized source file"]+=1
            continue
        try:
            rendered,payload=compile_paged(en,vi,glyphs,width)
            new_source=patch_labeled_block(sources[path],label,en,payload)
        except ValueError as e:
            skipped[str(e)]+=1
            continue
        sources[path]=new_source
        parts=page_words(en,vi)
        accepted.append({
            "source_file":path,"label":label,"english":en,
            "authored_vietnamese":vi,"vietnamese":rendered,
            "encoded_bytes":len(payload),"page_count":len(parts),
            "page_word_counts":[len(x) for x in parts],
            "page_word_order_preserved":True,
            "source_layout_changed":rendered!=vi,
        })
    return sources,accepted,dict(skipped)


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--codebook",type=Path,required=True)
    p.add_argument("--exclude-report",type=Path,action="append",required=True)
    p.add_argument("--limit",type=int,default=500)
    p.add_argument("--width",type=int,default=26)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    root=a.workspace.resolve()
    rows=json.loads(a.plan.read_text(encoding="utf-8"))
    old=[json.loads(p.read_text(encoding="utf-8")) for p in a.exclude_report]
    remaining,excluded=exclude_source_owners(rows,old)
    codebook=json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs={c:int(v,16) for c,v in codebook.items()}
    files={r.get("source_file") for r in remaining
           if r.get("category")=="system-text"
           and r.get("source_file","").startswith("data/text/")
           and r.get("source_file","").endswith(".inc")}
    sources={}
    for name in sorted(files):
        src=(root/name).resolve()
        if not src.is_relative_to(root):
            raise ValueError("unsafe system source path")
        if src.is_file():
            sources[name]=src.read_text(encoding="utf-8")
    before=dict(sources)
    updated,accepted,skipped=stage_system_pages(
        remaining,sources,glyphs,a.limit,a.width)
    if a.apply:
        for filename,content in updated.items():
            if content!=before[filename]:
                (root/filename).write_text(content,encoding="utf-8")
    report={
        "mode":"apply" if a.apply else "dry-run",
        "category":"system-text",
        "selection":"source_exact_paged_static_system_dialogue",
        "source_prefix":"data/text/",
        "labels_staged":len(accepted),
        "previously_compiled_system_owner_exclusions":excluded,
        "files_staged":sum(updated[f]!=before[f] for f in updated),
        "page_count_and_page_words_preserved":True,
        "runtime_variables_admitted":False,
        "unknown_escapes_admitted":False,
        "raw_ROM_pointer_writes":0,
        "approved_v04_font_applied":False,
        "emulator_verified":False,
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
