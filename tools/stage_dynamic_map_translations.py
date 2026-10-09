#!/usr/bin/env python3
"""Source-level Vietnamese with ONLY pinned PLAYER/RIVAL dynamic placeholders.

No ROM patching, no arbitrary string pointer rewriting. Preserves exactly
the source placeholder sequence and page-control count. Conservatively assumes
at most PLAYER_NAME_LENGTH=7 glyphs for each displayed player/rival name.
Requires pinned pokeemerald charmap for actual game control byte sequences.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from resolve_shipping_catalog import parse_charmap
from stage_source_map_translations import patch_labeled_block, prioritized_rows
from wrap_dynamic_map_text import wrap_dynamic_text

ALLOWED = {"PLAYER": 7, "RIVAL": 7}
EXPECTED_CONTROL_BYTES = {"PLAYER": b"\xFD\x01", "RIVAL": b"\xFD\x06"}
CONTROLS = {r"\n": 0xFE, r"\p": 0xFB, r"\l": 0xFA}
PLACEHOLDER = re.compile(r"\{([^{}]+)\}")


def signature(text: str) -> tuple[str, ...]:
    if text.count("{") != text.count("}") or "{" in PLACEHOLDER.sub("",text) or "}" in PLACEHOLDER.sub("",text):
        raise ValueError("unbalanced placeholder syntax")
    return tuple(PLACEHOLDER.findall(text))


def encode_dynamic(text: str, glyphs: dict[str, int],
                   tokens: dict[str, bytes], max_segment: int = 26) -> bytes:
    if unicodedata.normalize("NFC",text) != text:
        raise ValueError("non-NFC Vietnamese")
    if not text.endswith("$") or text.count("$") != 1:
        raise ValueError("missing or early end marker")
    out=bytearray()
    cell_count=0
    i=0
    while i<len(text):
        if text.startswith(tuple(CONTROLS),i):
            ctrl=text[i:i+2]
            out.append(CONTROLS[ctrl])
            cell_count=0
            i+=2
            continue
        ch=text[i]
        if ch=="$":
            out.append(0xFF)
            i+=1
            continue
        if ch=="{":
            end=text.find("}",i+1)
            if end<0:
                raise ValueError("unbalanced dynamic placeholder")
            name=text[i+1:end]
            if name not in ALLOWED:
                raise ValueError(f"unsupported dynamic token {name}")
            blob=tokens.get(name)
            if blob != EXPECTED_CONTROL_BYTES[name]:
                raise ValueError(f"unverified charmap token {name}")
            out.extend(blob)
            cell_count+=ALLOWED[name]
            i=end+1
        else:
            if ch in "}\\\r\n\t":
                raise ValueError("unexpected control or brace")
            value=glyphs.get(ch)
            if value is None:
                raise ValueError(f"missing Vietnamese glyph {ch!r}")
            if not 0<=value<=255 or value>=0xFA:
                raise ValueError(f"glyph/control collision {ch!r}")
            out.append(value)
            cell_count+=1
            i+=1
        if cell_count>max_segment:
            raise ValueError(f"dynamic line exceeds {max_segment} cells")
    return bytes(out)


def stage(rows: list[dict], sources: dict[str, str], glyphs: dict[str, int],
          tokens: dict[str, bytes], prefix: str, limit: int = 30,
          max_segment: int = 26, auto_wrap: bool = False,
          priority_prefixes: list[str]|None = None):
    results=[]
    skipped=Counter()
    for row in prioritized_rows(rows, priority_prefixes or []):
        if len(results)>=limit:
            break
        if row.get("category")!="map-story":
            continue
        file=row.get("source_file","")
        if not file.startswith(prefix) or file not in sources:
            continue
        original=row.get("english","")
        vietnamese=row.get("vietnamese","")
        if not original or not vietnamese or original==vietnamese or "{" not in vietnamese:
            continue
        try:
            en_sig=signature(original)
            vi_sig=signature(vietnamese)
            if not vi_sig or en_sig!=vi_sig:
                raise ValueError("dynamic token sequence differs from English source")
            if any(s not in ALLOWED for s in vi_sig):
                raise ValueError("source uses unapproved variable type")
            if original.count(r"\p")!=vietnamese.count(r"\p"):
                raise ValueError("page-control count changed")
            try:
                encoded=encode_dynamic(vietnamese,glyphs,tokens,max_segment)
                compiled=vietnamese
            except ValueError as exc:
                if not auto_wrap or not str(exc).startswith("dynamic line exceeds "):
                    raise
                compiled=wrap_dynamic_text(vietnamese,max_segment)
                encoded=encode_dynamic(compiled,glyphs,tokens,max_segment)
            changed=patch_labeled_block(
                sources[file],row["source_label"],original,encoded)
        except ValueError as exc:
            skipped[str(exc)]+=1
            continue
        sources[file]=changed
        results.append({"label":row["source_label"],"file":file,
                        "dynamic":list(vi_sig),"bytes":len(encoded),
                        "english":original,"vietnamese":vietnamese,
                        "compiled_vietnamese":compiled,
                        "auto_wrapped":compiled!=vietnamese})
    return sources,results,dict(skipped)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace",type=Path,required=True)
    ap.add_argument("--plan",type=Path,required=True)
    ap.add_argument("--codebook",type=Path,required=True)
    ap.add_argument("--charmap",type=Path,required=True)
    ap.add_argument("--source-prefix",default="data/maps/")
    ap.add_argument("--limit",type=int,default=30)
    ap.add_argument("--max-segment",type=int,default=26)
    ap.add_argument("--auto-wrap",action="store_true",help="Safe name-aware word reflow for overlong strings")
    ap.add_argument("--priority-source-prefix",action="append",default=[],help="Prioritize earliest-game script sources; repeatable")
    ap.add_argument("--apply",action="store_true")
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    if not 1<=args.limit<=200 or not 12<=args.max_segment<=30:
        ap.error("limit 1..200; max-segment 12..30")
    plan=json.loads(args.plan.read_text(encoding="utf-8"))
    cb=json.loads(args.codebook.read_text(encoding="utf-8"))
    glyphs={ch:int(value,16) for ch,value in cb["glyph_bytes"].items()}
    _,tokens=parse_charmap(args.charmap)
    for token,expected in [("PLAYER",b"\xFD\x01"),("RIVAL",b"\xFD\x06")]:
        if tokens.get(token)!=expected:
            raise SystemExit(f"REFUSED: unexpected pinned control token {token}")
    base=args.workspace.resolve()
    eligible_files={row.get("source_file","") for row in plan
                    if row.get("category")=="map-story" and
                    row.get("source_file","").startswith(args.source_prefix) and
                    "{" in row.get("vietnamese","")}
    sources={}
    for rel in sorted(eligible_files):
        path=(base/rel).resolve()
        if not path.is_relative_to(base) or not path.is_file():
            continue
        sources[rel]=path.read_text(encoding="utf-8")
    originals=dict(sources)
    sources,accepted,rejected=stage(
        plan,sources,glyphs,tokens,args.source_prefix,args.limit,args.max_segment,args.auto_wrap,args.priority_source_prefix)
    if args.apply:
        for rel,modified in sources.items():
            if modified!=originals[rel]:
                (base/rel).write_text(modified,encoding="utf-8")
    report={
        "mode":"apply" if args.apply else "dry-run",
        "labels_staged":len(accepted),
        "files_changed":sum(sources[k]!=originals[k] for k in sources),
        "auto_wrapped_labels":sum(r["auto_wrapped"] for r in accepted),
        "source_symbol_labels_unchanged":True,
        "placeholder_order_preserved":True,
        "source_control_bytes_pinned":True,
        "max_name_glyphs":7,
        "rejected":rejected,
        "accepted":accepted,
        "font_visual_qa":False,
        "gameplay_qa":False,
    }
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="accepted"},
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
