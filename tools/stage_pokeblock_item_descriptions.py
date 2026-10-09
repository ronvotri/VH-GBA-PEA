#!/usr/bin/env python3
"""Source-stage only fixed native {POKEBLOCK} item text (16 pinned labels).

The source charmap expands the symbol to FIVE native glyph bytes 55..59.
Only v0.6 codebook is permitted: no Vietnamese glyph may occupy those codes.
No pointers, symbols, runtime variable commands or ROM bytes are overwritten.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from stage_source_map_translations import encode_text
from stage_source_descriptions import replace_description

EXPECTED_SOURCE="src/data/text/item_descriptions.h"
NATIVE_BYTES=bytes([0x55,0x56,0x57,0x58,0x59])
PLACEHOLDER="{POKEBLOCK}"


def pinned_pokeblock_bytes(charmap:str)->bytes:
    english=charmap.split("@ Hiragana",1)[0]
    tokens=re.findall(r"(?m)^POKEBLOCK\s*=\s*([0-9A-Fa-f ]+)\s*$",english)
    if len(tokens)!=1:
        raise ValueError("missing or duplicate source Pokéblock control")
    value=bytes(int(v,16) for v in tokens[0].split())
    if value!=NATIVE_BYTES:
        raise ValueError("native Pokéblock control byte sequence changed")
    return value


def encode_item_pokeblock(text:str,codes:dict[str,int],
                          token:bytes,max_cells:int=26)->bytes:
    if not text or text.count(PLACEHOLDER)!=1:
        raise ValueError("exactly one native Pokéblock token required")
    if any(symbol in text.replace(PLACEHOLDER,"") for symbol in ("{","}")):
        raise ValueError("unknown dynamic token")
    if any(sym in text for sym in (r"\p",r"\l")):
        raise ValueError("page/scroll controls not supported")
    if text.count(r"\n")!=2:
        raise ValueError("Pokéblock items require exactly three visible lines")
    if text.endswith("$"):
        raise ValueError("raw item authoring must omit literal $ terminator")
    for line in text.split(r"\n"):
        expanded=line.replace(PLACEHOLDER,"X"*len(token))
        if len(expanded)>max_cells or not expanded:
            raise ValueError("item Pokéblock visible line exceeds box width")
    parts=text.split(PLACEHOLDER)
    result=bytearray()
    for i,part in enumerate(parts):
        if part:
            result.extend(encode_text(part+"$",codes,max_cells)[:-1])
        if i==0:
            result.extend(token)
    result.append(0xFF)
    if result.count(b"\xFF")!=1 or result[-1]!=0xFF or result.count(b"\xFE")!=2:
        raise ValueError("unexpected FF/newline in native byte encoding")
    if result.count(token)!=1:
        raise ValueError("native Pokéblock byte sequence altered")
    return bytes(result)


def stage_pokeblock(rows:list[dict],source:str,codes:dict[str,int],
                    token:bytes,max_cells:int=26)->tuple[str,list,dict]:
    accepted=[]
    skipped=Counter()
    for row in rows:
        if row.get("source_file")!=EXPECTED_SOURCE or row.get("category")!="system-ui":
            continue
        en=row.get("english","")
        vi=row.get("vietnamese","")
        if PLACEHOLDER not in en and PLACEHOLDER not in vi:
            continue
        label=row.get("source_label","")
        if not re.fullmatch(r"s[A-Za-z0-9_]+Desc",label):
            skipped["unsupported C item label"]+=1;continue
        if en.count(PLACEHOLDER)!=1 or vi.count(PLACEHOLDER)!=1:
            skipped["source token signature differs"]+=1;continue
        if en.count(r"\n")!=vi.count(r"\n") or en.count(r"\n")!=2:
            skipped["source three-line layout mismatch"]+=1;continue
        try:
            payload=encode_item_pokeblock(vi,codes,token,max_cells)
            changed=replace_description(source,label,en,payload,"item")
        except ValueError as exc:
            skipped[str(exc)]+=1;continue
        source=changed
        accepted.append({"label":label,"source_file":EXPECTED_SOURCE,
                         "english":en,"vietnamese":vi,
                         "encoded_bytes":len(payload),
                         "native_token_occurrences":1,
                         "native_token_bytes":token.hex(),
                         "visible_lines":3})
    return source,accepted,dict(skipped)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--codebook",type=Path,required=True)
    p.add_argument("--charmap",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    book=json.loads(a.codebook.read_text(encoding="utf-8"))
    if book.get("schema_version")!=3:
        raise SystemExit("REFUSED: Pokéblock sources require collision-safe v0.6 mapping")
    codes={ch:int(v,16) for ch,v in book["glyph_bytes"].items()}
    if any(b in NATIVE_BYTES for ch,b in codes.items() if ord(ch)>127):
        raise SystemExit("REFUSED: native Pokéblock glyph byte still aliased")
    if codes.get("đ")!=0x33 or codes.get("ì")!=0x37:
        raise SystemExit("REFUSED: wrong đ/ì source byte mapping")
    token=pinned_pokeblock_bytes(a.charmap.read_text(encoding="utf-8"))
    root=a.workspace.resolve()
    file=(root/EXPECTED_SOURCE).resolve()
    if not file.is_relative_to(root) or not file.is_file():
        raise SystemExit("REFUSED: source item header missing")
    rows=json.loads(a.plan.read_text(encoding="utf-8"))
    source=file.read_text(encoding="utf-8")
    transformed,accepted,skipped=stage_pokeblock(rows,source,codes,token)
    if a.apply:
        file.write_text(transformed,encoding="utf-8")
    report={"mode":"apply" if a.apply else "dry-run",
            "source_file":EXPECTED_SOURCE,
            "labels_staged":len(accepted),"translated":accepted,
            "skipped_reasons":skipped,
            "native_byte_sequence_pinned":True,
            "font_artwork_grafted":False,
            "runtime_qa_pass":False}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="translated"},
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
