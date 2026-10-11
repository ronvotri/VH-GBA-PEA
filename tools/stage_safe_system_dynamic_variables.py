#!/usr/bin/env python3
"""Fail-closed static-footprint-safe system dialogue dynamic placeholders.

Only verified PLAYER/RIVAL/KUN/STR_VAR_1..3 GBA dynamic bytes, with the
same variables in the same original native line/page slots. The translated
static-cell count may NOT exceed the English original in any individual
segment: unknown variable expansions therefore cannot worsen line width.
No speculative variable sizing, page reflow, direct ROM writes or font edits.
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
from stage_static_paged_system_text import exclude_source_owners

VARIABLE_BYTES={
    "PLAYER":b"\xfd\x01","STR_VAR_1":b"\xfd\x02",
    "STR_VAR_2":b"\xfd\x03","STR_VAR_3":b"\xfd\x04",
    "KUN":b"\xfd\x05","RIVAL":b"\xfd\x06",
}
TOKEN=re.compile(r"\{([A-Z_][A-Z0-9_]*)\}")
CONTROL=re.compile(r"(\\[npl])")
PART=re.compile(r"\{[A-Z_][A-Z0-9_]*\}|\\[npl]|." , re.S)


def lines_with_matching_dynamic_slots(en:str,vi:str)->list[dict]:
    for name,value in (("English",en),("Vietnamese",vi)):
        if (not value.endswith("$") or value.count("$")!=1
                or unicodedata.normalize("NFC",value)!=value
                or any(ch in value for ch in ("\n","\r","\t"))):
            raise ValueError(f"{name}: malformed terminal, Unicode or raw whitespace")
    a=CONTROL.split(en[:-1])
    b=CONTROL.split(vi[:-1])
    if len(a)!=len(b) or a[1::2]!=b[1::2]:
        raise ValueError("source-native page/scroll control order changed")
    if any(x in (r"\p",r"\n",r"\l") for x in (a[0],b[0])):
        raise ValueError("unexpected initial control")
    rows=[]
    at_least_one=False
    for i in range(0,len(a),2):
        eng,translated=a[i],b[i]
        if eng.count("{")!=eng.count("}") or translated.count("{")!=translated.count("}"):
            raise ValueError("unbalanced curly placeholder")
        a_names=TOKEN.findall(eng)
        b_names=TOKEN.findall(translated)
        if a_names!=b_names:
            raise ValueError("dynamic token names/order changed within line")
        if any(name not in VARIABLE_BYTES for name in a_names):
            raise ValueError("unapproved runtime variable")
        for phrase in (eng,translated):
            leftover=TOKEN.sub("",phrase)
            if any(c in leftover for c in "{}\\"):
                raise ValueError("unsupported control, escaped token or malformed variable")
        static_en=len(TOKEN.sub("",eng))
        static_vi=len(TOKEN.sub("",translated))
        if static_vi>static_en:
            raise ValueError("Vietnamese static footprint exceeds original line")
        if static_vi>26:
            raise ValueError("unbounded static translated line")
        rows.append({"tokens":a_names,"english_static_cells":static_en,
                     "vietnamese_static_cells":static_vi})
        at_least_one=at_least_one or bool(a_names)
    if not at_least_one:
        raise ValueError("not a dynamic-variable text")
    return rows


def encode(vi:str,glyphs:dict[str,int],tokens:dict[str,bytes])->bytes:
    if unicodedata.normalize("NFC",vi)!=vi or not vi.endswith("$"):
        raise ValueError("invalid normalized Vietnamese terminator")
    result=bytearray()
    body=vi[:-1]
    chunks=PART.findall(body)
    if "".join(chunks)!=body:
        raise ValueError("unsupported non-token raw text")
    for chunk in chunks:
        if chunk in (r"\n",r"\l",r"\p"):
            result.append({r"\n":0xFE,r"\l":0xFA,r"\p":0xFB}[chunk])
        elif chunk.startswith("{"):
            name=chunk[1:-1]
            if tokens.get(name)!=VARIABLE_BYTES.get(name):
                raise ValueError(f"unverified charmap variable {name}")
            result.extend(tokens[name])
        else:
            n=glyphs.get(chunk)
            if n is None or not 0<=n<0xFA:
                raise ValueError(f"missing/unsafe glyph {chunk!r}")
            result.append(n)
    result.append(0xFF)
    if result.count(0xFF)!=1:
        raise ValueError("embedded GBA terminator")
    return bytes(result)


def stage(rows:list[dict],sources:dict[str,str],glyphs:dict[str,int],
          tokens:dict[str,bytes],limit:int=750)->tuple[dict,list[dict],dict]:
    if not 1<=limit<=1000:
        raise ValueError("invalid batch limit")
    for k,v in VARIABLE_BYTES.items():
        if tokens.get(k)!=v:
            raise ValueError(f"pinned charmap does not match engine variable {k}")
    result=[];skipped=Counter();seen=set()
    priorities=[
        "data/text/birch_speech.inc","data/text/pkmn_center_nurse.inc",
        "data/text/trainers.inc","data/text/match_call.inc",
    ]
    for row in prioritized_rows(rows,priorities):
        if len(result)>=limit:break
        path=row.get("source_file","")
        label=row.get("source_label","")
        en=row.get("english","")
        vi=row.get("vietnamese","")
        if (row.get("category")!="system-text"
                or not path.startswith("data/text/")
                or not path.endswith(".inc")
                or not label or not en or not vi or en==vi
                or "{" not in en):
            continue
        owner=(path,label)
        if owner in seen:raise ValueError(f"duplicate source manifest owner: {owner}")
        seen.add(owner)
        if path not in sources:
            skipped["missing authorized source file"]+=1
            continue
        try:
            matched=lines_with_matching_dynamic_slots(en,vi)
            payload=encode(vi,glyphs,tokens)
            src=patch_labeled_block(sources[path],label,en,payload)
        except ValueError as e:
            skipped[str(e)]+=1
            continue
        sources[path]=src
        result.append({
            "source_file":path,"label":label,"english":en,
            "vietnamese":vi,"segments":matched,
            "native_control_order_unchanged":True,
            "dynamic_variable_slots_preserved":True,
            "static_cells_never_exceed_original":True,
            "encoded_bytes":len(payload),
        })
    return sources,result,dict(skipped)


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--codebook",type=Path,required=True)
    p.add_argument("--exclude-report",type=Path,action="append",required=True)
    p.add_argument("--limit",type=int,default=750)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    root=a.workspace.resolve()
    plan=json.loads(a.plan.read_text(encoding="utf-8"))
    earlier=[json.loads(f.read_text(encoding="utf-8")) for f in a.exclude_report]
    remaining,already=exclude_source_owners(plan,earlier)
    chars=json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
    glyphs={x:int(y,16) for x,y in chars.items()}
    _,tokens=parse_charmap(root/"charmap.txt")
    files={
        r.get("source_file") for r in remaining
        if r.get("category")=="system-text"
        and r.get("source_file","").startswith("data/text/")
        and r.get("source_file","").endswith(".inc")
        and "{" in r.get("english","")
    }
    sources={}
    for file in sorted(files):
        path=(root/file).resolve()
        if not path.is_relative_to(root):
            raise ValueError("unsafe file path")
        if path.is_file():
            sources[file]=path.read_text(encoding="utf-8")
    prior=dict(sources)
    updated,added,skipped=stage(remaining,sources,glyphs,tokens,a.limit)
    if a.apply:
        for file,value in updated.items():
            if value!=prior[file]:
                (root/file).write_text(value,encoding="utf-8")
    report={
        "mode":"apply" if a.apply else "dry-run",
        "category":"system-text",
        "selection":"source_exact_system_dynamic_nonexpanding_per_native_line",
        "labels_staged":len(added),
        "previously_compiled_system_owner_exclusions":already,
        "files_changed":sum(updated[k]!=prior[k] for k in prior),
        "variable_bytes_pinned_to_source_charmap":True,
        "variable_names_and_native_lines_preserved":True,
        "static_line_expansion_admitted":False,
        "raw_rom_pointer_writes":0,
        "font_art_modified":False,
        "emulator_QA":False,"release_ready":False,
        "skipped_reasons":skipped,"translated":added,
    }
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                        encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="translated"},
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
