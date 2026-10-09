#!/usr/bin/env python3
"""Stage a bounded SOURCE-LEVEL map text smoke build, not a GBA ROM patch.

Labels stay unchanged so assembler/linker reallocate text and pointers. Strictly
check the pinned English .string bytes, codebook and line-length threshold.
The font/glyph table is still experimental; no runtime certification.
"""
from __future__ import annotations
import argparse, json, re, unicodedata
from collections import Counter
from pathlib import Path
from wrap_vietnamese_map_text import auto_wrap_script_text

LINE = re.compile(r'^(?P<indent>\s*)\.string\s+"(?P<value>.*)"\s*$')
CONTROLS = {"\\n":0xFE,"\\p":0xFB,"\\l":0xFA}


def encode_text(s: str, codes: dict[str,int], max_segment: int) -> bytes:
    if unicodedata.normalize("NFC",s) != s:
        raise ValueError("non-NFC text; review combining accents")
    encoded=bytearray(); i=0; segment=0
    while i<len(s):
        if s[i:i+2] in CONTROLS:
            encoded.append(CONTROLS[s[i:i+2]]); i+=2; segment=0
            continue
        if s[i]=="$":
            if i!=len(s)-1: raise ValueError("early terminator")
            encoded.append(0xFF); i+=1; continue
        if s[i] in "{}\\":
            raise ValueError(f"unsupported dynamic/escape token at {i}")
        ch=s[i]
        if ch not in codes: raise ValueError(f"missing Vietnamese glyph {ch!r}")
        value=codes[ch]
        if value in (0xFA,0xFB,0xFC,0xFD,0xFE,0xFF):
            raise ValueError(f"glyph {ch!r} collides with control byte")
        encoded.append(value);segment+=1;i+=1
        if segment>max_segment: raise ValueError(f"line exceeds {max_segment} encoded cells")
    if not encoded or encoded[-1]!=0xFF:
        raise ValueError("missing terminal $")
    return bytes(encoded)


def patch_labeled_block(source: str,label: str,expected_en: str,encoded: bytes)->str:
    lines=source.splitlines(keepends=True)
    indices=[i for i,line in enumerate(lines) if re.match(
        r"^"+re.escape(label)+r":{1,2}\s*(?:@[^\r\n]*)?$",line.strip())]
    if len(indices)!=1: raise ValueError(f"{label}: {len(indices)} source labels")
    start=indices[0]+1; pos=start; fragments=[]
    while pos<len(lines):
        match=LINE.match(lines[pos].rstrip("\r\n"))
        if not match:break
        fragments.append(match.group("value"));pos+=1
    if not fragments:raise ValueError(f"{label}: no contiguous .string directives")
    if "".join(fragments)!=expected_en:
        raise ValueError(f"{label}: English source is not exact pinned match")
    replacement=["\t.byte "+", ".join(f"0x{v:02X}" for v in encoded[j:j+16])+"\n"
                 for j in range(0,len(encoded),16)]
    lines[start:pos]=replacement
    return "".join(lines)


def plan_rows(rows:list,codes:dict[str,int],src_prefix:str,max_segment:int,limit:int,auto_wrap:bool=False):
    chosen=[]; rejected=Counter()
    for row in rows:
        if len(chosen)>=limit:break
        if row.get("category")!="map-story" or not row.get("source_file","").startswith(src_prefix):
            continue
        english,vietnamese=row.get("english",""),row.get("vietnamese","")
        if not vietnamese or english==vietnamese or not row.get("source_label"):continue
        try:payload=encode_text(vietnamese,codes,max_segment)
        except ValueError as exc:
            if auto_wrap and str(exc).startswith("line exceeds "):
                try:
                    wrapped=auto_wrap_script_text(vietnamese,max_segment)
                    payload=encode_text(wrapped,codes,max_segment)
                except ValueError as wrap_exc:
                    rejected["auto-wrap: "+str(wrap_exc)]+=1
                    continue
                row=dict(row)
                row["authored_vietnamese"]=vietnamese
                row["vietnamese"]=wrapped
                row["auto_wrapped"]=True
            else:
                rejected[str(exc)]+=1
                continue
        chosen.append((row,payload))
    return chosen,dict(rejected)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--codebook",type=Path,required=True)
    p.add_argument("--source-prefix",default="data/maps/LittlerootTown/")
    p.add_argument("--limit",type=int,default=20)
    p.add_argument("--max-segment",type=int,default=26)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--apply",action="store_true")
    p.add_argument("--auto-wrap",action="store_true",help="Only word-boundary newline/scroll conversion for overlong non-dynamic text")
    a=p.parse_args()
    if a.limit<1 or a.limit>250 or not 10<=a.max_segment<=30:
        p.error("limit 1..250 and max-segment 10..30")
    plan=json.loads(a.plan.read_text(encoding="utf-8"))
    raw=json.loads(a.codebook.read_text(encoding="utf-8"))
    codes={c:int(v,16) for c,v in raw["glyph_bytes"].items()}
    selected, skipped=plan_rows(plan,codes,a.source_prefix,a.max_segment,a.limit,a.auto_wrap)
    skipped=Counter(skipped); changes={}; accepted=[]
    for row, encoded in selected:
        relative=row["source_file"]
        filepath=(a.workspace/relative).resolve()
        if not filepath.is_relative_to(a.workspace.resolve()) or not filepath.is_file():
            skipped["missing/unsafe source file"]+=1;continue
        if filepath not in changes:
            changes[filepath]=filepath.read_text(encoding="utf-8")
        try:changed=patch_labeled_block(changes[filepath],row["source_label"],row["english"],encoded)
        except ValueError as exc:
            skipped[str(exc)]+=1;continue
        changes[filepath]=changed
        accepted.append({"label":row["source_label"],"source_file":relative,
                         "encoded_bytes":len(encoded),
                         "english":row["english"],"vietnamese":row["vietnamese"],
                         "authored_vietnamese":row.get("authored_vietnamese",row["vietnamese"]),
                         "auto_wrapped":bool(row.get("auto_wrapped"))})
    if a.apply:
        for filepath,updated in changes.items():
            filepath.write_text(updated,encoding="utf-8")
    report={"mode":"apply" if a.apply else "dry-run",
            "source_prefix":a.source_prefix,"labels_staged":len(accepted),
            "files_staged":len(changes),
            "auto_wrapped_labels":sum(1 for row in accepted if row["auto_wrapped"]),
            "skipped_reasons":dict(skipped),
            "translated":accepted,"font_rendering_emulator_certified":False,
            "shipping_ROM_changed":False,
            "source_build_is_not_verified_shipping_layout":True}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="translated"},ensure_ascii=False,indent=2))


if __name__=="__main__":main()
