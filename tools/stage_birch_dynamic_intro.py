#!/usr/bin/env python3
"""Exact-source dynamic intro for Birch: never replace PLAYER/KUN with fixed names.

The upstream KUN placeholder is empty for both genders, but its runtime control
FD 05 MUST remain intact. PLAYER is bounded by seven character cells. Refuse
unfamiliar placeholders, any source/control mismatch or an overlong line.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from stage_source_map_translations import patch_labeled_block
from verify_compiled_source_strings import extract_asm_payload

OWNER="data/text/birch_speech.inc"
LABELS=("gText_Birch_SoItsPlayer","gText_Birch_YourePlayer")
PLACEHOLDERS={"PLAYER":(b"\xFD\x01",7),"KUN":(b"\xFD\x05",0)}
PAGE={r"\n":0xFE,r"\p":0xFB,r"\l":0xFA}
MARKER=re.compile(r"\{[^{}]+\}|\\[npl]")

def tokens(s:str)->tuple[str,...]:
    seq=tuple(a.group(0) for a in MARKER.finditer(s))
    unmarked=MARKER.sub("",s)
    if any(c in unmarked for c in "{}\\"):
        raise ValueError("unknown control or unbalanced placeholder")
    return seq

def verify_engine(charmap:str,strings_c:str)->None:
    for name,(value,_) in PLACEHOLDERS.items():
        expected=f"{value[0]:02X} {value[1]:02X}"
        if not re.search(r"(?m)^"+name+r"\s*=\s*"+re.escape(expected)+r"\b",charmap):
            raise ValueError("unverified "+name+" charmap byte")
    for sex in ("Kun","Chan"):
        pattern=r'(?m)^const u8 gText_ExpandedPlaceholder_'+sex+r'\[\]\s*=\s*_\(""\);'
        if len(re.findall(pattern,strings_c))!=1:
            raise ValueError("KUN suffix not empty for both genders")

def encode(s:str,glyphs:dict[str,int])->bytes:
    if unicodedata.normalize("NFC",s)!=s:raise ValueError("non-NFC text")
    if not s.endswith("$") or s.count("$")!=1:raise ValueError("FF terminator")
    result=bytearray()
    cells=0
    i=0
    while i<len(s):
        if s[i]=="$":
            result.append(0xFF)
            i+=1
            continue
        if s[i:i+2] in PAGE:
            result.append(PAGE[s[i:i+2]])
            cells=0
            i+=2
            continue
        if s[i]=="{":
            right=s.find("}",i+1)
            name=s[i+1:right] if right>=0 else ""
            if name not in PLACEHOLDERS:raise ValueError("unsupported placeholder")
            payload,width=PLACEHOLDERS[name]
            result.extend(payload)
            cells+=width
            i=right+1
        else:
            ch=s[i]
            if ch in "{}\\" or ch in "\n\r\t":
                raise ValueError("literal newline/control")
            code=glyphs.get(ch)
            if code is None or not 0<=code<0xFA:
                raise ValueError("missing/colliding Vietnamese glyph: "+repr(ch))
            result.append(code)
            cells+=1
            i+=1
        if cells>26:raise ValueError("expanded PLAYER line exceeds 26 cells")
    if result.count(0xFF)!=1 or result[-1]!=0xFF:
        raise ValueError("bad terminal FF")
    return bytes(result)

def stage(plan:list[dict],src:str,charmap:str,strings_c:str,
          glyphs:dict[str,int])->tuple[str,list[dict]]:
    verify_engine(charmap,strings_c)
    out=src
    rows=[]
    for label in LABELS:
        candidates=[r for r in plan if r.get("source_label")==label]
        if len(candidates)!=1:raise ValueError("missing/ambiguous "+label)
        r=candidates[0]
        if r.get("category")!="system-text" or r.get("source_file")!=OWNER:
            raise ValueError("unexpected source owner for "+label)
        english=r["english"]
        vi=r["vietnamese"]
        expected=tokens(english)
        if (expected!=tokens(vi) or
            expected.count("{PLAYER}")!=1 or expected.count("{KUN}")!=1):
            raise ValueError("changed placeholder/pagination signature "+label)
        data=encode(vi,glyphs)
        out=patch_labeled_block(out,label,english,data)
        rows.append({"label":label,"source_file":OWNER,"english":english,
                     "vietnamese":vi,"payload_hex":data.hex(),
                     "control_signature":list(expected),"name_width_max":7,
                     "KUN_expansion_width":0})
    return out,rows

def check_linker(rom:bytes,symbols:str,src:str,rows:list[dict])->list[dict]:
    result=[]
    for row in rows:
        name=row["label"]
        matches=re.findall(r"(?m)^([0-9a-fA-F]+)\s+\w\s+"+name+r"$",symbols)
        if len(matches)!=1:raise ValueError("unresolved/ambiguous linker label "+name)
        addr=int(matches[0],16)
        if not 0x08000000<=addr<0x0A000000:raise ValueError("symbol outside GBA ROM")
        offset=addr-0x08000000
        payload=bytes.fromhex(row["payload_hex"])
        if rom[offset:offset+len(payload)]!=payload:
            raise ValueError("wrong translated text at runtime pointer "+name)
        if extract_asm_payload(src,name)!=payload:
            raise ValueError("staged assembly does not match linked payload "+name)
        if payload.count(b"\xFD\x01")!=1 or payload.count(b"\xFD\x05")!=1:
            raise ValueError("runtime placeholder bytes missing")
        result.append({"label":name,"rom_offset":f"0x{offset:08X}",
                       "payload_sha256":hashlib.sha256(payload).hexdigest(),
                       "tokens_verified":True})
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--plan",type=Path)
    p.add_argument("--codebook",type=Path)
    p.add_argument("--apply",action="store_true")
    p.add_argument("--rom",type=Path)
    p.add_argument("--sym",type=Path)
    a=p.parse_args()
    workspace=a.workspace.resolve()
    owner=(workspace/OWNER).resolve()
    if not owner.is_relative_to(workspace) or not owner.is_file():
        p.error("missing/unsafe source owner")
    if a.rom:
        if not a.sym or a.apply or not a.report.is_file():
            p.error("--rom needs --sym and an existing staged report")
        record=json.loads(a.report.read_text(encoding="utf-8"))
        if record.get("mode")!="apply" or record.get("labels_staged")!=2:
            p.error("untrusted stage report")
        linked=check_linker(a.rom.read_bytes(),a.sym.read_text(encoding="utf-8"),
                            owner.read_text(encoding="utf-8"),record["translated"])
        record.update({"linked_ROM_payloads_verified":True,
                       "linked_symbols":linked,"release_ready":False})
    else:
        if not a.plan or not a.codebook:p.error("--plan and --codebook required")
        plan=json.loads(a.plan.read_text(encoding="utf-8"))
        book=json.loads(a.codebook.read_text(encoding="utf-8"))["glyph_bytes"]
        glyphs={c:int(v,16) for c,v in book.items()}
        converted,rows=stage(plan,owner.read_text(encoding="utf-8"),
                             (workspace/"charmap.txt").read_text(encoding="utf-8"),
                             (workspace/"src/strings.c").read_text(encoding="utf-8"),
                             glyphs)
        if a.apply:owner.write_text(converted,encoding="utf-8")
        record={"mode":"apply" if a.apply else "dry-run","labels_staged":2,
                "translated":rows,"category":"system-text","source_file":OWNER,
                "PLAYER_max_width":7,"KUN_runtime_width":0,
                "control_and_placeholder_order_verified":True,
                "linked_ROM_payloads_verified":False,
                "emulator_tested":False,"release_ready":False}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
