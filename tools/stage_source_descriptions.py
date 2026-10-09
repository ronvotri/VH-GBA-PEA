#!/usr/bin/env python3
"""Safely stage two/three-line Move and Item C descriptions from source.

Move descriptions: one \n and two visible rows.
Item descriptions: one or two \n controls; up to three visible rows.
Never alter per-move or per-item pointer arrays. Exact source English and label
attestation is required. Dynamic tokens and unsupported glyphs are rejected.
This tool writes ONLY the user's private source build checkout, never a ROM.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from stage_source_map_translations import encode_text

SOURCES={
    "move":"src/data/text/move_descriptions.h",
    "item":"src/data/text/item_descriptions.h",
}
LABELS={
    "move":re.compile(r"s[A-Za-z0-9_]+Description"),
    "item":re.compile(r"s[A-Za-z0-9_]+Desc"),
}
FIRST=re.compile(
    r'(?m)^(?P<pre>[ \t]*static const u8 (?P<label>s[A-Za-z0-9_]+)'
    r'\[\] = )_\([ \t]*\r?\n'
)
FRAGMENT=re.compile(r'^[ \t]*"((?:\\.|[^"\\])*)"[ \t]*$')
FINAL_FRAGMENT=re.compile(r'^[ \t]*"((?:\\.|[^"\\])*)"\);[ \t]*(?://[^\r\n]*)?$')
CLOSE=re.compile(r'^[ \t]*\);[ \t]*(?://[^\r\n]*)?$')


def find_description_block(source:str,label:str):
    """Return exact C initializer, original escaped English, and source span."""
    matches=[m for m in FIRST.finditer(source) if m.group("label")==label]
    if len(matches)!=1:
        raise ValueError(f"{label}: missing or duplicate C initializer")
    m=matches[0]
    after=source[m.end():]
    parts=[]
    ending=None
    cursor=0
    for line in after.splitlines(keepends=True):
        stripped=line.rstrip("\r\n")
        if CLOSE.fullmatch(stripped):
            ending=m.end()+cursor+len(line)
            break
        final_fragment=FINAL_FRAGMENT.fullmatch(stripped)
        if final_fragment:
            parts.append(final_fragment.group(1))
            ending=m.end()+cursor+len(line)
            break
        fragment=FRAGMENT.fullmatch(stripped)
        if not fragment:
            raise ValueError(f"{label}: unsupported multiline C expression")
        parts.append(fragment.group(1))
        cursor+=len(line)
    if ending is None or not parts:
        raise ValueError(f"{label}: unterminated/empty C expression")
    return m.start(),ending,m.group("pre"),"".join(parts)


def replace_description(source:str,label:str,english:str,payload:bytes,kind:str)->str:
    if kind not in SOURCES or not LABELS[kind].fullmatch(label):
        raise ValueError("invalid description label/kind")
    start,end,prefix,original=find_description_block(source,label)
    if original!=english:
        raise ValueError(f"{label}: exact English source drift")
    if len(payload)<2 or payload[-1]!=0xFF or 0xFF in payload[:-1]:
        raise ValueError("invalid compiled FF terminator")
    values=", ".join(f"0x{x:02X}" for x in payload)
    return source[:start]+prefix+"{"+values+"};\n"+source[end:]


def stage_descriptions(
    rows:list[dict], source:str, codes:dict[str,int], kind:str,
    limit:int=350, max_cells:int=26
):
    if kind not in SOURCES or not 10<=max_cells<=30:
        raise ValueError("unsupported description kind or width")
    accepted=[]
    skipped=Counter()
    expected_file=SOURCES[kind]
    for row in rows:
        if len(accepted)>=limit:
            break
        if (row.get("category")!="system-ui" or
                row.get("source_file")!=expected_file):
            continue
        label=row.get("source_label","")
        english=row.get("english","")
        vietnamese=row.get("vietnamese","")
        if not english or english==vietnamese or not vietnamese:
            continue
        if not LABELS[kind].fullmatch(label):
            skipped["invalid source name"]+=1
            continue
        if ("{" in vietnamese or "}" in vietnamese or
                "{" in english or "}" in english):
            skipped["dynamic/control variable left for separate engine"]+=1
            continue
        # This UI uses special strict 2-line and 3-line boxes.
        original_breaks=english.count(r"\n")
        translated_breaks=vietnamese.count(r"\n")
        if original_breaks!=translated_breaks:
            skipped["description line count differs from English"]+=1
            continue
        if (kind=="move" and original_breaks!=1) or (
                kind=="item" and original_breaks not in (1,2)):
            skipped["not a supported description box"]+=1
            continue
        if any(r"\p" in v or r"\l" in v for v in (english,vietnamese)):
            skipped["page or scroll controls in fixed description box"]+=1
            continue
        try:
            with_end=vietnamese if vietnamese.endswith("$") else vietnamese+"$"
            payload=encode_text(with_end,codes,max_cells)
            new_source=replace_description(source,label,english,payload,kind)
        except ValueError as exc:
            skipped[str(exc)]+=1
            continue
        source=new_source
        accepted.append({"label":label,"source_file":expected_file,
                         "english":english,"vietnamese":vietnamese,
                         "encoded_bytes":len(payload),
                         "visible_lines":original_breaks+1})
    return source,accepted,dict(skipped)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace",type=Path,required=True)
    ap.add_argument("--plan",type=Path,required=True)
    ap.add_argument("--codebook",type=Path,required=True)
    ap.add_argument("--kind",choices=sorted(SOURCES),required=True)
    ap.add_argument("--limit",type=int,default=350)
    ap.add_argument("--max-cells",type=int,default=26)
    ap.add_argument("--apply",action="store_true")
    ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args()
    if not 1<=a.limit<=400 or not 10<=a.max_cells<=30:
        ap.error("limit 1..400 and max-cells 10..30")
    rows=json.loads(a.plan.read_text(encoding="utf-8"))
    book=json.loads(a.codebook.read_text(encoding="utf-8"))
    codes={name:int(value,16) for name,value in book["glyph_bytes"].items()}
    root=a.workspace.resolve()
    source_file=(root/SOURCES[a.kind]).resolve()
    if not source_file.is_relative_to(root) or not source_file.is_file():
        raise SystemExit("REFUSED: expected source description file missing")
    original=source_file.read_text(encoding="utf-8")
    result,accepted,skipped=stage_descriptions(
        rows,original,codes,a.kind,a.limit,a.max_cells)
    if a.apply:
        source_file.write_text(result,encoding="utf-8")
    report={"kind":a.kind,"source_file":SOURCES[a.kind],
            "mode":"apply" if a.apply else "dry-run",
            "labels_staged":len(accepted),
            "translated":accepted,
            "skipped_reasons":skipped,
            "line_box_limits_preserved":True,
            "dynamic_tokens_modified":False,
            "font_visual_QA":False,
            "ROM_binary_modified_by_tool":False}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                        encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="translated"},
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
